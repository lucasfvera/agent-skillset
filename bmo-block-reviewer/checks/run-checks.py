#!/usr/bin/env python3
"""Portable, diff-scoped ast-grep runner for bmo-block-reviewer.

Auto-detects active rule profiles from the target repo's package.json and
tsconfig.json (read-only), runs ast-grep on changed files/lines (or the full
repo with --all), and prints findings in bmo-block-reviewer format.

Exit codes:
  0  Zero [issue] findings (may still report [style] warnings unless --fail-on-style)
  1  At least one [issue] finding (or [style] with --fail-on-style)
  2  ast-grep unavailable or invalid invocation (caller should fall back to prose rules)
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKS_DIR = Path(__file__).resolve().parent
RULES_DIR = CHECKS_DIR / "rules"
SGCONFIG_PATH = CHECKS_DIR / "sgconfig.yml"

SUPPORTED_EXTS = {".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs", ".html", ".css", ".scss"}
IGNORED_PARTS = {".worktrees", "node_modules", "dist", "build", "coverage", ".angular", ".next", ".git"}
ALL_PROFILES = (
    "universal",
    "angular",
    "angular-v19",
    "react",
    "jasmine",
    "testing-library",
    "firestore",
    "zod",
    "path-aliases",
)
PINNED_AST_GREP_PKG = "@ast-grep/cli@0.51.0"


def strip_jsonc(text: str) -> str:
    """Strip // comments, /* */ comments, and trailing commas without touching strings."""
    out: list[str] = []
    i = 0
    n = len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
        elif ch == "/" and i + 1 < n and text[i + 1] == "/":
            i += 2
            while i < n and text[i] != "\n":
                i += 1
        elif ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
        else:
            out.append(ch)
            i += 1
    cleaned = "".join(out)
    return re.sub(r",(\s*[}\]])", r"\1", cleaned)


def load_jsonc(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(strip_jsonc(path.read_text(encoding="utf-8")))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"warning: failed to parse {path.name}: {exc}\n")
        return {}


def parse_major_version(spec: str) -> int | None:
    match = re.search(r"(\d+)", spec or "")
    return int(match.group(1)) if match else None


def collect_deps(repo_root: Path) -> dict[str, str]:
    deps: dict[str, str] = {}
    candidates = [repo_root / "package.json"]
    for sub in ("packages", "apps"):
        subdir = repo_root / sub
        if subdir.is_dir():
            candidates.extend(sorted(subdir.glob("*/package.json")))
    for pkg_path in candidates:
        pkg = load_jsonc(pkg_path)
        for section in ("dependencies", "devDependencies", "peerDependencies"):
            block = pkg.get(section)
            if isinstance(block, dict):
                for name, ver in block.items():
                    if name not in deps and isinstance(ver, str):
                        deps[name] = ver
    return deps


def detect_profiles(repo_root: Path) -> list[str]:
    profiles = ["universal"]
    deps = collect_deps(repo_root)

    angular_ver = deps.get("@angular/core")
    if angular_ver is not None:
        profiles.append("angular")
        major = parse_major_version(angular_ver)
        if major is not None and major >= 19:
            profiles.append("angular-v19")

    if "react" in deps:
        profiles.append("react")

    has_jasmine = any(k in deps for k in ("jasmine", "jasmine-core", "@types/jasmine"))
    has_paths = False
    for name in ("tsconfig.json", "tsconfig.base.json"):
        ts = load_jsonc(repo_root / name)
        opts = ts.get("compilerOptions")
        if isinstance(opts, dict):
            if isinstance(opts.get("paths"), dict) and len(opts["paths"]) > 0:
                has_paths = True
            types = opts.get("types")
            if isinstance(types, list) and "jasmine" in types:
                has_jasmine = True

    if has_jasmine:
        profiles.append("jasmine")

    if any(k.startswith("@testing-library/") for k in deps):
        profiles.append("testing-library")

    if any(k in deps for k in ("firebase", "@angular/fire", "@google-cloud/firestore")):
        profiles.append("firestore")

    if "zod" in deps:
        profiles.append("zod")

    if has_paths:
        profiles.append("path-aliases")

    return profiles


def resolve_ast_grep() -> list[str] | None:
    override = os.environ.get("BMO_AST_GREP_BIN")
    if override:
        if override.lower() == "none":
            return None
        return [override]

    for candidate in ("ast-grep", "sg"):
        binary = shutil.which(candidate)
        if not binary:
            continue
        try:
            probe = subprocess.run(
                [binary, "--version"], capture_output=True, text=True, timeout=5
            )
            if probe.returncode == 0 and "ast-grep" in (probe.stdout + probe.stderr).lower():
                return [binary]
        except (OSError, subprocess.SubprocessError):
            continue

    npx = shutil.which("npx")
    if npx:
        try:
            probe = subprocess.run(
                [npx, "-y", "-p", PINNED_AST_GREP_PKG, "ast-grep", "--version"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if probe.returncode == 0 and "ast-grep" in (probe.stdout + probe.stderr).lower():
                return [npx, "-y", "-p", PINNED_AST_GREP_PKG, "ast-grep"]
        except (OSError, subprocess.SubprocessError):
            pass
    return None


def git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args], capture_output=True, text=True
    )


def git_checked(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    res = git(repo_root, *args)
    if res.returncode != 0:
        detail = res.stderr.strip() or res.stdout.strip() or f"exit {res.returncode}"
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return res


def default_base_ref(repo_root: Path) -> str | None:
    sym = git(repo_root, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if sym.returncode == 0 and sym.stdout.strip():
        return sym.stdout.strip().removeprefix("refs/remotes/")
    for ref in ("origin/main", "origin/master", "main", "master"):
        if git(repo_root, "rev-parse", "--verify", "--quiet", ref).returncode == 0:
            return ref
    return None


def parse_diff_added_lines(diff_text: str) -> dict[str, set[int]]:
    """Return 1-based line numbers added/modified in unified -U0 git diff output."""
    added: dict[str, set[int]] = {}
    current_file: str | None = None
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
            added.setdefault(current_file, set())
        elif line.startswith("+++ /dev/null"):
            current_file = None
        elif current_file and line.startswith("@@ "):
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if match:
                start = int(match.group(1))
                count = 1 if match.group(2) is None else int(match.group(2))
                if count > 0:
                    added[current_file].update(range(start, start + count))
    return added


def collect_diff_targets(
    repo_root: Path, base_ref: str | None, staged_only: bool = False
) -> tuple[list[Path], dict[str, set[int]] | None, str]:
    """Return (existing supported file paths, added 1-based lines map or None, scope label)."""
    added_lines: dict[str, set[int]] = {}
    whole_files: set[str] = set()

    if staged_only:
        res = git_checked(repo_root, "diff", "--cached", "-U0", "--diff-filter=ACMR")
        for rel, lines in parse_diff_added_lines(res.stdout).items():
            added_lines.setdefault(rel, set()).update(lines)
        label = "staged diff"
    else:
        if base_ref:
            merge_base = git_checked(repo_root, "merge-base", base_ref, "HEAD").stdout.strip()
            # Diff merge-base directly against the working tree so committed, staged,
            # and unstaged edits all resolve to exact working-tree line numbers.
            res = git_checked(repo_root, "diff", "-U0", "--diff-filter=ACMR", merge_base)
            diffs = [res.stdout]
        elif git(repo_root, "rev-parse", "--verify", "--quiet", "HEAD").returncode == 0:
            res = git_checked(repo_root, "diff", "-U0", "--diff-filter=ACMR", "HEAD")
            diffs = [res.stdout]
        else:
            diffs = [
                git_checked(repo_root, "diff", "--cached", "-U0", "--diff-filter=ACMR").stdout,
                git_checked(repo_root, "diff", "-U0", "--diff-filter=ACMR").stdout,
            ]
        for text in diffs:
            for rel, lines in parse_diff_added_lines(text).items():
                added_lines.setdefault(rel, set()).update(lines)

        untracked = git_checked(repo_root, "ls-files", "--others", "--exclude-standard")
        for rel in untracked.stdout.splitlines():
            if rel.strip():
                whole_files.add(rel.strip())
        label = f"diff vs {base_ref}" if base_ref else "working tree diff"

    rel_paths = sorted(set(added_lines.keys()) | whole_files)
    targets: list[Path] = []
    filtered_lines: dict[str, set[int]] = {}
    for rel in rel_paths:
        parts = set(Path(rel).parts)
        if parts & IGNORED_PARTS:
            continue
        full = repo_root / rel
        if not full.is_file() or full.suffix.lower() not in SUPPORTED_EXTS:
            continue
        targets.append(full)
        if rel in whole_files:
            line_count = len(full.read_text(encoding="utf-8", errors="ignore").splitlines())
            filtered_lines[rel] = set(range(1, line_count + 1))
        else:
            filtered_lines[rel] = added_lines.get(rel, set())
    return targets, filtered_lines, label


def parse_rule_languages(yaml_text: str) -> list[str]:
    match = re.search(r"^\s*languages:\s*\[([^\]]+)\]", yaml_text, re.M)
    if not match:
        return ["TypeScript"]
    return [item.strip().strip("'\"") for item in match.group(1).split(",") if item.strip()]


def parse_rule_id(yaml_text: str) -> str:
    match = re.search(r"^id:\s*([A-Za-z0-9_-]+)", yaml_text, re.M)
    return match.group(1) if match else ""


def parse_rule_coverage(yaml_text: str) -> str:
    match = re.search(r"^\s*coverage:\s*(full|partial)\b", yaml_text, re.M)
    return match.group(1) if match else "full"


def materialize_rules(profiles: list[str], temp_dir: Path) -> tuple[Path, list[str], list[str]]:
    """Copy active profile rules into temp_dir, expanding multi-language variants.

    Returns (sgconfig_path, full_rule_ids, partial_rule_ids).
    """
    rule_out = temp_dir / "rules"
    rule_out.mkdir(parents=True, exist_ok=True)
    full_ids: list[str] = []
    partial_ids: list[str] = []

    for profile in profiles:
        src_dir = RULES_DIR / profile
        if not src_dir.is_dir():
            continue
        for rule_file in sorted(src_dir.glob("*.yml")):
            raw = rule_file.read_text(encoding="utf-8")
            base_id = parse_rule_id(raw)
            if not base_id:
                continue
            if parse_rule_coverage(raw) == "partial":
                partial_ids.append(base_id)
            else:
                full_ids.append(base_id)
            langs = parse_rule_languages(raw)
            for idx, lang in enumerate(langs):
                if idx == 0:
                    dest = rule_out / f"{base_id}.yml"
                    dest.write_text(raw, encoding="utf-8")
                else:
                    suffix = lang.lower()
                    variant = re.sub(
                        r"^id:\s*[A-Za-z0-9_-]+",
                        f"id: {base_id}__{suffix}",
                        raw,
                        count=1,
                        flags=re.M,
                    )
                    variant = re.sub(
                        r"^language:\s*\S+",
                        f"language: {lang}",
                        variant,
                        count=1,
                        flags=re.M,
                    )
                    dest = rule_out / f"{base_id}__{suffix}.yml"
                    dest.write_text(variant, encoding="utf-8")

    cfg = temp_dir / "sgconfig.yml"
    cfg.write_text("ruleDirs:\n  - rules\n", encoding="utf-8")
    return cfg, sorted(set(full_ids)), sorted(set(partial_ids))


def normalize_rule_id(rule_id: str) -> str:
    return rule_id.split("__", 1)[0]


def tier_from_match(item: dict) -> str:
    meta = item.get("metadata") or {}
    if isinstance(meta, dict) and meta.get("tier") in ("issue", "style"):
        return str(meta["tier"])
    return "issue" if item.get("severity") == "error" else "style"


def run_scan(
    sg_cmd: list[str],
    repo_root: Path,
    profiles: list[str],
    targets: list[Path],
    line_filter: dict[str, set[int]] | None,
) -> tuple[list[dict], list[str], list[str]]:
    if not targets:
        return [], [], []

    with tempfile.TemporaryDirectory(prefix="bmo-ast-grep-") as tmp:
        cfg, full_ids, partial_ids = materialize_rules(profiles, Path(tmp))
        if not full_ids and not partial_ids:
            return [], [], []

        rel_targets = [str(t.relative_to(repo_root)) if t.is_relative_to(repo_root) else str(t) for t in targets]
        cmd = [
            *sg_cmd,
            "scan",
            "-c",
            str(cfg),
            "--json=compact",
            "--include-metadata",
            *rel_targets,
        ]
        proc = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
        if proc.returncode not in (0, 1):
            raise RuntimeError(
                f"ast-grep scan exited {proc.returncode}: {proc.stderr.strip() or proc.stdout.strip()}"
            )
        raw_out = proc.stdout.strip()
        if not raw_out:
            return [], full_ids, partial_ids
        try:
            matches = json.loads(raw_out)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Failed to parse ast-grep JSON output: {exc}\n{proc.stderr}") from exc

    findings: list[dict] = []
    seen: set[tuple[str, str, int, int]] = set()
    for item in matches:
        file_rel = str(item.get("file") or "").removeprefix("./")
        if set(Path(file_rel).parts) & IGNORED_PARTS:
            continue
        start = ((item.get("range") or {}).get("start") or {})
        end = ((item.get("range") or {}).get("end") or {})
        start_line = int(start.get("line", 0)) + 1
        end_line = int(end.get("line", start_line - 1)) + 1
        col = int(start.get("column", 0)) + 1

        if line_filter is not None:
            allowed = line_filter.get(file_rel)
            if allowed is not None and not any(ln in allowed for ln in range(start_line, end_line + 1)):
                continue

        rule_id = normalize_rule_id(str(item.get("ruleId") or ""))
        dedupe_key = (rule_id, file_rel, start_line, col)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        meta = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        findings.append(
            {
                "rule_id": rule_id,
                "tier": tier_from_match(item),
                "domain": str(meta.get("domain") or "core"),
                "file": file_rel,
                "line": start_line,
                "column": col,
                "snippet": str(item.get("lines") or "").strip(),
                "message": str(item.get("message") or "").strip(),
                "note": str(item.get("note") or "").strip(),
            }
        )

    findings.sort(key=lambda f: (0 if f["tier"] == "issue" else 1, f["file"], f["line"], f["rule_id"]))
    return findings, full_ids, partial_ids


def format_markdown(
    findings: list[dict],
    profiles: list[str],
    checked_rules: list[str],
    partial_rules: list[str],
    scope_label: str,
    file_count: int,
) -> str:
    issues = [f for f in findings if f["tier"] == "issue"]
    styles = [f for f in findings if f["tier"] == "style"]
    lines: list[str] = []

    if not findings:
        lines.append("No deterministic findings.")
    else:
        for f in findings:
            loc = f"`{f['file']}:{f['line']}`"
            note = f" Fix: {f['note']}" if f["note"] else ""
            lines.append(f"- [{f['tier']}] [{f['rule_id']}] {loc} — {f['message']}{note}")

    verdict = (
        "block — fix issues"
        if issues
        else ("fix style before ship" if styles else "ship")
    )
    lines.append("")
    lines.append(f"Profiles: {', '.join(profiles)}")
    checked_display = ", ".join(checked_rules) if checked_rules else "none"
    lines.append(f"Checked rules ({len(checked_rules)}): {checked_display}")
    if partial_rules:
        lines.append(f"Partial rules ({len(partial_rules)}, keep semantic AI pass): {', '.join(partial_rules)}")
    lines.append(f"Scope: {scope_label} ({file_count} target(s))")
    lines.append(f"Summary: {len(issues)} issue(s), {len(styles)} style(s)")
    lines.append(f"Verdict: {verdict}")
    return "\n".join(lines)


def self_test() -> int:
    # 1. JSONC stripping with //, /* */, strings containing //, trailing commas
    raw_ts = """{
      // comment with "quotes"
      "compilerOptions": {
        "paths": { "@app/*": ["./src/app/*"], },
        "url": "https://example.com/*", /* block comment */
      },
    }"""
    parsed = json.loads(strip_jsonc(raw_ts))
    assert parsed["compilerOptions"]["paths"] == {"@app/*": ["./src/app/*"]}, parsed
    assert parsed["compilerOptions"]["url"] == "https://example.com/*", parsed

    # 2. Angular major version parsing
    assert parse_major_version("^22.0.0") == 22
    assert parse_major_version("~18.2.3") == 18
    assert parse_major_version(">=19.0.0") == 19
    assert parse_major_version("") is None

    # 3. Unified diff hunk parsing
    diff = (
        "+++ b/src/app/foo.ts\n"
        "@@ -10,0 +11,3 @@\n"
        "+line11\n+line12\n+line13\n"
        "@@ -20,1 +23 @@\n"
        "+line23\n"
        "@@ -30,2 +33,0 @@\n"
        "-deleted\n"
    )
    lines_map = parse_diff_added_lines(diff)
    assert lines_map == {"src/app/foo.ts": {11, 12, 13, 23}}, lines_map

    # 4. Profile detection on synthetic repo
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "package.json").write_text(
            json.dumps(
                {
                    "dependencies": {
                        "@angular/core": "^20.0.0",
                        "firebase": "12.0.0",
                        "react": "^19.0.0",
                        "zod": "^3.24.0",
                    },
                    "devDependencies": {
                        "@types/jasmine": "~5.0.0",
                        "@testing-library/react": "^16.0.0",
                    },
                }
            )
        )
        (root / "tsconfig.json").write_text(
            '{\n  // paths\n  "compilerOptions": { "paths": { "@app/*": ["./src/*"] } }\n}\n'
        )
        profs = detect_profiles(root)
        assert profs == list(ALL_PROFILES), profs
        _, full_ids, partial_ids = materialize_rules(profs, root / "mat")
        assert len(full_ids) + len(partial_ids) == 40, (len(full_ids), len(partial_ids))
        assert not (set(full_ids) & set(partial_ids))

    # 5. Run ast-grep test on all bundled rules
    sg_cmd = resolve_ast_grep()
    if sg_cmd is None:
        sys.stderr.write("ast-grep unavailable; cannot run rule tests\n")
        return 2
    res = subprocess.run(
        [*sg_cmd, "test", "--skip-snapshot-tests", "-c", str(SGCONFIG_PATH)],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        sys.stderr.write(res.stdout + "\n" + res.stderr + "\n")
        return res.returncode

    # 6. Verify every materialized language variant (TS, TSX, JS, HTML, CSS) parses and scans
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a.ts").write_text("const ok = a === b;\n")
        (root / "b.tsx").write_text("export const C = () => <div />;\n")
        (root / "c.js").write_text("const bad = a == b;\n")
        (root / "d.html").write_text('<img src="x.png" width="10" height="10" />\n')
        (root / "e.css").write_text(".box { color: #ff0000; }\n")
        targets = [root / n for n in ("a.ts", "b.tsx", "c.js", "d.html", "e.css")]
        findings, _, _ = run_scan(sg_cmd, root, list(ALL_PROFILES), targets, None)
        hit_ids = {f["rule_id"] for f in findings}
        for expected in (
            "strict-equality",
            "use-ng-optimized-image",
            "preserve-semantic-roles-and-a11y",
            "prefer-design-tokens",
        ):
            assert expected in hit_ids, (expected, hit_ids)

    # 7. Verify diff-line filtering tracks working-tree coordinates when unstaged edits
    #    insert lines above committed branch edits (while still ignoring unchanged base lines)
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        git_checked(repo, "init")
        git_checked(repo, "checkout", "-B", "main")
        sample = repo / "sample.ts"
        sample.write_text("const keep = 1;\nconst preExisting = a == b;\nconst tail = 2;\n")
        git_checked(repo, "add", "sample.ts")
        git_checked(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "base")

        git_checked(repo, "checkout", "-b", "feat")
        sample.write_text(
            "const keep = 1;\nconst preExisting = a == b;\nconst tail = 2;\nconst committedBad = c == d;\n"
        )
        git_checked(repo, "add", "sample.ts")
        git_checked(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "feat")

        # Insert 3 clean lines at the top and 1 unstaged violation at the bottom.
        # preExisting shifts from line 2 -> 5 (must stay ignored);
        # committedBad shifts from line 4 -> 7 (must still be flagged at line 7);
        # unstagedBad is on line 8 (must be flagged at line 8).
        sample.write_text(
            "const top1 = 1;\n"
            "const top2 = 2;\n"
            "const top3 = 3;\n"
            "const keep = 1;\n"
            "const preExisting = a == b;\n"
            "const tail = 2;\n"
            "const committedBad = c == d;\n"
            "const unstagedBad = e == f;\n"
        )
        diff_targets, diff_lines, _ = collect_diff_targets(repo, "main")
        diff_findings, checked_ids, _ = run_scan(sg_cmd, repo, ["universal"], diff_targets, diff_lines)
        eq_lines = sorted(f["line"] for f in diff_findings if f["rule_id"] == "strict-equality")
        assert eq_lines == [7, 8], (eq_lines, diff_lines, diff_findings)
        assert "strict-equality" in checked_ids, checked_ids

        # 8. Verify non-JS/TS-only diff reports zero checked rules (so AI does not skip them)
        git_checked(repo, "checkout", "--", "sample.ts")
        git_checked(repo, "checkout", "-b", "docs-only", "main")
        (repo / "notes.py").write_text("print('hi')\n")
        py_targets, py_lines, _ = collect_diff_targets(repo, "main")
        assert py_targets == [], py_targets
        _, py_checked, py_partial = run_scan(sg_cmd, repo, ["universal"], py_targets, py_lines)
        assert py_checked == [] and py_partial == [], (py_checked, py_partial)

        # 9. Verify failed git diff, unknown profile, missing path, and unavailable ast-grep exit 2
        with contextlib.redirect_stdout(io.StringIO()):
            assert main(["--repo", str(repo), "--base", "nonexistent-ref", "--format", "json"]) == 2
            assert main(["--repo", str(repo), "--profiles", "universal,bogus", "--format", "json"]) == 2
            assert main(["--repo", str(repo), "does-not-exist.ts", "--format", "json"]) == 2

            prev_bin = os.environ.get("BMO_AST_GREP_BIN")
            try:
                os.environ["BMO_AST_GREP_BIN"] = "none"
                assert main(["--repo", str(repo), "--format", "json"]) == 2
            finally:
                if prev_bin is None:
                    os.environ.pop("BMO_AST_GREP_BIN", None)
                else:
                    os.environ["BMO_AST_GREP_BIN"] = prev_bin

    sys.stderr.write(res.stdout.strip() + "\nrun-checks self-test passed\n")
    return 0


def emit_error(msg: str, as_json: bool) -> int:
    if as_json:
        print(json.dumps({"status": "error", "message": msg}))
    else:
        sys.stderr.write(f"error: {msg}\n")
    return 2


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run portable ast-grep checks for bmo-block-reviewer.")
    parser.add_argument("paths", nargs="*", help="Optional files or directories to scan (relative to --repo).")
    parser.add_argument("--repo", default=".", help="Target repository or worktree root (default: cwd).")
    parser.add_argument("--base", default=None, help="Git base ref for diff mode (default: origin/main or HEAD).")
    parser.add_argument("--staged", action="store_true", help="Scan only staged changes.")
    parser.add_argument("--all", action="store_true", help="Scan the entire repository (ignores git diff filter).")
    parser.add_argument("--whole-files", action="store_true", help="Report matches on all lines of changed files, not just diff lines.")
    parser.add_argument("--profiles", default=None, help=f"Comma-separated profile override ({','.join(ALL_PROFILES)}).")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    parser.add_argument("--fail-on-style", action="store_true", help="Exit 1 on [style] findings in addition to [issue].")
    parser.add_argument("--self-test", action="store_true", help="Run built-in unit tests and ast-grep rule tests.")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    as_json = args.format == "json"
    repo_root = Path(args.repo).resolve()
    if not repo_root.is_dir():
        return emit_error(f"repo directory does not exist: {repo_root}", as_json)

    sg_cmd = resolve_ast_grep()
    if sg_cmd is None:
        msg = (
            "ast-grep unavailable (install `@ast-grep/cli` or ensure `npx` is reachable). "
            "Fall back to prose checks in bmo-block-reviewer."
        )
        if as_json:
            print(json.dumps({"status": "unavailable", "message": msg}))
        else:
            print(msg)
        return 2

    if args.profiles:
        profiles = [p.strip() for p in args.profiles.split(",") if p.strip()]
        unknown = [p for p in profiles if p not in ALL_PROFILES]
        if not profiles or unknown:
            return emit_error(
                f"unknown profile(s): {', '.join(unknown) or '(empty)'}; expected subset of {', '.join(ALL_PROFILES)}",
                as_json,
            )
    else:
        profiles = detect_profiles(repo_root)

    line_filter: dict[str, set[int]] | None = None
    try:
        if args.all:
            targets = [repo_root]
            scope_label = "full repo"
        elif args.paths:
            resolved = [(repo_root / p).resolve() if not Path(p).is_absolute() else Path(p) for p in args.paths]
            missing = [str(p) for p in resolved if not p.exists()]
            if missing:
                return emit_error(f"path(s) do not exist: {', '.join(missing)}", as_json)
            targets = resolved
            scope_label = "explicit paths"
        else:
            base_ref = args.base or default_base_ref(repo_root)
            targets, line_filter, scope_label = collect_diff_targets(repo_root, base_ref, staged_only=args.staged)
            if args.whole_files:
                line_filter = None

        findings, checked_rules, partial_rules = run_scan(sg_cmd, repo_root, profiles, targets, line_filter)
    except RuntimeError as exc:
        return emit_error(str(exc), as_json)

    issues_count = sum(1 for f in findings if f["tier"] == "issue")
    styles_count = sum(1 for f in findings if f["tier"] == "style")

    if args.format == "json":
        payload = {
            "status": "ok",
            "repo": str(repo_root),
            "profiles": profiles,
            "checked_rules": checked_rules,
            "partial_rules": partial_rules,
            "scope": scope_label,
            "targets": len(targets),
            "summary": {"issue": issues_count, "style": styles_count},
            "verdict": (
                "block — fix issues"
                if issues_count
                else ("fix style before ship" if styles_count else "ship")
            ),
            "findings": findings,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(format_markdown(findings, profiles, checked_rules, partial_rules, scope_label, len(targets)))

    if issues_count > 0 or (args.fail_on_style and styles_count > 0):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
