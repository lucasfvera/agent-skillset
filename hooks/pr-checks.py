#!/usr/bin/env python3
"""Stamp green lint/typecheck/test and block `gh pr create` until this HEAD is green."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from shutil import which

STATE_DIR = Path.home() / ".cursor" / "hooks" / "state" / "pr-checks"

SCRIPT_NAMES = {
    "lint": ("lint", "lint:check", "eslint"),
    "typecheck": ("type-check", "typecheck", "tsc", "types"),
    "test": ("test", "test:unit", "test:ci", "test:all"),
}
SKIP_SCRIPTS = {"lint:fix", "test:watch", "test:e2e", "test:coverage"}

_PM = (
    r"(?:npm|pnpm|yarn|bun)(?:\s+--cwd\s+\S+)?\s+(?:run\s+)?"
    r"(?:workspace(?:s)?\s+\S+\s+(?:run\s+)?)?"
)
_NPX = r"(?:npx|pnpm\s+exec|yarn\s+dlx)\s+"


def _cmd_re(*alts: str) -> re.Pattern[str]:
    return re.compile(rf"(?:^|[\s;&|])(?:{'|'.join(alts)})", re.I)


FAMILY_RE = {
    "lint": _cmd_re(
        rf"{_PM}lint(?!:fix)\b",
        rf"{_NPX}eslint\b",
        r"make\s+lint\b",
        r"turbo(?:\s+run)?\s+lint\b",
        r"biome\s+check\b",
        r"golangci-lint\b",
        r"ruff\s+check\b",
    ),
    "typecheck": _cmd_re(
        rf"{_PM}(?:type-check|typecheck|tsc)\b",
        rf"{_NPX}tsc\b",
        r"make\s+(?:type-check|typecheck)\b",
        r"turbo(?:\s+run)?\s+type-check\b",
    ),
    "test": _cmd_re(
        rf"{_PM}test(?!:watch|:e2e|:coverage)\b",
        rf"{_NPX}(?:vitest|jest)\b",
        r"make\s+test\b",
        r"turbo(?:\s+run)?\s+test\b",
        r"go\s+test\b",
        r"pytest\b",
        r"cargo\s+test\b",
    ),
}

PR_CREATE_RE = re.compile(
    r"(?:^|&&|\|\||[;&\n]|\b(?:then|else|do)\b)\s*(?:sudo\s+)?gh\s+pr\s+create\b",
    re.I,
)
PR_CREATE_HELP_RE = re.compile(r"\bgh\s+pr\s+create\b.*(?:-h|--help)\b", re.I)
HEREDOC_RE = re.compile(r"""<<[-]?\s*['\"]?(\w+)['\"]?[\s\S]*?^\s*\1\s*$""", re.M)
QUOTE_RES = (
    re.compile(r"'(?:\\'|[^'])*'"),
    re.compile(r'"(?:\\.|[^"\\])*"'),
)
DIR_RES = (
    re.compile(r"(?:^|[;&|]\s*)cd\s+(['\"]?)([^'\"\s]+)\1"),
    re.compile(r"\bgit\s+-C\s+(['\"]?)([^'\"\s]+)\1"),
)


def effective_shell(command: str) -> str:
    stripped = HEREDOC_RE.sub(" ", command)
    for pattern in QUOTE_RES:
        stripped = pattern.sub(" ", stripped)
    return stripped


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")


def allow() -> int:
    emit({"permission": "allow"})
    return 0


def deny(agent_message: str, user_message: str | None = None) -> int:
    emit(
        {
            "permission": "deny",
            "agent_message": agent_message,
            "user_message": user_message or "PR create blocked: checks are not green on this HEAD.",
        }
    )
    return 0


def tell(message: str) -> int:
    emit({"additional_context": message})
    return 0


def as_dict(value: object) -> dict:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return {}
    return value if isinstance(value, dict) else {}


def command_text(payload: dict) -> str:
    if payload.get("command"):
        return str(payload["command"])
    raw = payload.get("tool_input") or {}
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return raw
    return str(as_dict(raw).get("command") or "")


def command_dirs(command: str) -> list[str]:
    return [match.group(2) for pattern in DIR_RES for match in pattern.finditer(command)]


def tool_cwd(payload: dict) -> str:
    tool_input = as_dict(payload.get("tool_input"))
    candidates = [
        *(str(payload[key]) for key in ("cwd",) if payload.get(key)),
        *(
            str(tool_input[key])
            for key in ("working_directory", "workingDirectory", "cwd")
            if tool_input.get(key)
        ),
        *command_dirs(command_text(payload)),
        *(str(root) for root in (payload.get("workspace_roots") or [])),
        os.getcwd(),
    ]
    return next((path for path in candidates if git_root(path)), candidates[0])


def exit_code(payload: dict) -> int | None:
    raw = payload.get("tool_output")
    data = as_dict(raw) if raw is not None else {}
    for key in ("exitCode", "exit_code", "code"):
        if data.get(key) is not None:
            return int(data[key])
    return None


def git(root: str, *args: str) -> str:
    result = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def git_root(cwd: str) -> str:
    return git(cwd, "rev-parse", "--show-toplevel") if cwd else ""


def stamp_path(root: str, head: str, dirty: str) -> Path:
    key = hashlib.sha256(f"{root}\n{head}\n{dirty}".encode()).hexdigest()[:16]
    return STATE_DIR / key / f"{head}.json"


def empty_stamp(root: str, head: str, dirty: str) -> dict:
    return {"git_root": root, "head": head, "dirty": dirty, "families": {}}


def load_stamp(root: str, head: str, dirty: str) -> dict:
    stamp = empty_stamp(root, head, dirty)
    try:
        data = json.loads(stamp_path(root, head, dirty).read_text())
    except (OSError, json.JSONDecodeError):
        return stamp
    stamp["families"] = as_dict(as_dict(data).get("families"))
    return stamp


def save_stamp(stamp: dict) -> None:
    path = stamp_path(stamp["git_root"], stamp["head"], stamp["dirty"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stamp, indent=2, ensure_ascii=False) + "\n")


def classify(command: str) -> list[str]:
    return [family for family, pattern in FAMILY_RE.items() if pattern.search(command)]


def detect_pm(root: str, package: dict) -> str:
    field = str(package.get("packageManager") or "")
    for name in ("yarn", "pnpm", "bun", "npm"):
        if field.startswith(name):
            return name
    base = Path(root)
    if (base / "yarn.lock").exists():
        return "yarn"
    if (base / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (base / "bun.lockb").exists() or (base / "bun.lock").exists():
        return "bun"
    return "npm"


def discover(root: str) -> list[tuple[str, str]]:
    base = Path(root)
    package = {}
    try:
        package = as_dict(json.loads((base / "package.json").read_text()))
    except (OSError, json.JSONDecodeError):
        pass
    scripts = as_dict(package.get("scripts"))
    if scripts:
        pm = detect_pm(root, package)
        prefix = "npm run " if pm == "npm" else f"{pm} "
        found = []
        for family, names in SCRIPT_NAMES.items():
            name = next((n for n in names if n in scripts and n not in SKIP_SCRIPTS), None)
            if name:
                found.append((family, prefix + name))
        if found:
            return found

    makefile = base / "Makefile"
    if makefile.is_file():
        text = makefile.read_text(errors="ignore")
        found = [
            (family, f"make {target}")
            for family, target in (("lint", "lint"), ("typecheck", "typecheck"), ("test", "test"))
            if re.search(rf"^{re.escape(target)}\b", text, re.M)
        ]
        if not any(family == "typecheck" for family, _ in found) and re.search(
            r"^type-check\b", text, re.M
        ):
            found.append(("typecheck", "make type-check"))
        if found:
            return found

    if (base / "go.mod").is_file():
        checks = [("test", "go test ./...")]
        if which("golangci-lint") or (base / ".golangci.yml").exists():
            checks.append(("lint", "golangci-lint run"))
        return checks
    if (base / "Cargo.toml").is_file():
        return [("test", "cargo test"), ("lint", "cargo clippy -- -D warnings")]
    if (base / "pyproject.toml").is_file() or (base / "pytest.ini").is_file():
        return [("test", "pytest")]
    return []


def snapshot(cwd: str) -> tuple[str, str, str] | None:
    root = git_root(cwd)
    head = git(root, "rev-parse", "HEAD") if root else ""
    if not root or not head:
        return None
    return root, head, git(root, "status", "--porcelain")


def missing_families(root: str, stamp: dict) -> list[tuple[str, str]]:
    required = discover(root)
    green = set(stamp.get("families") or {})
    if required:
        return [(family, command) for family, command in required if family not in green]
    if green:
        return []
    return [("lint", "the repo lint command"), ("test", "the repo test command")]


def format_status(root: str, head: str, stamp: dict) -> str:
    required = discover(root) or missing_families(root, stamp)
    green = stamp.get("families") or {}
    lines = [f"git root: {root}", f"HEAD: {head[:12]}"]
    for family, command in required:
        if family in green:
            lines.append(f"- {family}: green (`{green[family].get('command', command)}`)")
        else:
            lines.append(f"- {family}: missing → `{command}`")
    return "\n".join(lines)


def gate_pr_create(payload: dict) -> int:
    command = command_text(payload)
    effective = effective_shell(command)
    if not PR_CREATE_RE.search(effective) or PR_CREATE_HELP_RE.search(effective):
        return allow()

    snap = snapshot(tool_cwd(payload))
    if snap is None:
        return deny(
            "Run `gh pr create` from the git root (or worktree) you are opening. "
            "The checks hook could not resolve a repository from the command cwd."
        )

    root, head, dirty = snap
    stamp = load_stamp(root, head, dirty)
    missing = missing_families(root, stamp)
    if not missing:
        return allow()

    commands = "\n".join(f"- `{command}`" for _, command in missing)
    return deny(
        "Checks are not green on this committed HEAD, so `gh pr create` stays blocked.\n\n"
        f"{format_status(root, head, stamp)}\n\n"
        "Run every missing command in that git root until each exits 0, then retry "
        "`gh pr create`. If HEAD moves, every check is un-green.\n\n"
        f"Missing:\n{commands}"
    )


def record_check(payload: dict) -> int:
    command = command_text(payload)
    families = classify(command)
    if not families:
        return 0

    snap = snapshot(tool_cwd(payload))
    if snap is None:
        return tell("Checks hook: no git root for that command; nothing recorded.")

    root, head, dirty = snap
    stamp = load_stamp(root, head, dirty)
    code = exit_code(payload)
    if code != 0:
        return tell(
            f"Checks hook: `{command}` exited {code}. Not green.\n{format_status(root, head, stamp)}"
        )

    for family in families:
        stamp.setdefault("families", {})[family] = {"command": command}
    save_stamp(stamp)
    missing = missing_families(root, stamp)
    if missing:
        left = ", ".join(family for family, _ in missing)
        return tell(
            f"Checks hook: recorded green {', '.join(families)} for {root} "
            f"({head[:12]}). Still missing: {left}."
        )
    return tell(
        f"Checks hook: all required checks are green for {root} ({head[:12]}). "
        "`gh pr create` is unblocked."
    )


def dispatch(payload: dict) -> int:
    event = payload.get("hook_event_name") or ""
    if event == "beforeShellExecution":
        return gate_pr_create(payload)
    if event == "postToolUse":
        return record_check(payload)
    return 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        return self_test()
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        if sys.stdin.isatty():
            sys.stderr.write("usage: pr-checks.py reads hook JSON on stdin\n")
            return 1
        return deny("Checks hook received invalid JSON.")
    if not isinstance(payload, dict):
        return deny("Checks hook received a non-object payload.")
    return dispatch(payload)


def self_test() -> int:
    for command, family in (
        ("yarn lint", "lint"),
        ("yarn --cwd packages/shared lint", "lint"),
        ("yarn workspace tx lint", "lint"),
        ("yarn type-check", "typecheck"),
        ("yarn test", "test"),
        ("yarn test:unit", "test"),
    ):
        assert family in classify(command), command
    assert "test" not in classify("yarn test:watch")
    assert "lint" not in classify("yarn lint:fix")
    assert classify("echo hello") == []

    assert PR_CREATE_RE.search(effective_shell("gh pr create --title x"))
    assert PR_CREATE_RE.search(effective_shell("cd /tmp/worktree && gh pr create --title x"))
    assert not PR_CREATE_RE.search(effective_shell("gh pr list"))
    assert not PR_CREATE_RE.search(effective_shell("python3 << 'PY'\nprint('gh pr create')\nPY"))
    assert not PR_CREATE_RE.search(effective_shell("echo 'gh pr create'"))
    assert PR_CREATE_HELP_RE.search("gh pr create --help")
    assert command_dirs("cd /tmp/worktree && gh pr create --title x") == ["/tmp/worktree"]
    assert command_dirs('git -C "/tmp/repo" status') == ["/tmp/repo"]

    for repo in (
        "/Users/lucasferreyravera/roxom/roxtopia",
        "/Users/lucasferreyravera/roxom/roxtarsverse",
    ):
        found = dict(discover(repo))
        assert found["lint"] == "yarn lint", found
        assert found["typecheck"] == "yarn type-check", found
        assert found["test"] == "yarn test", found

    sys.stderr.write("pr-checks self-test passed\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
