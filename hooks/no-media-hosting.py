#!/usr/bin/env python3
"""beforeShellExecution hook: blocks shell commands that create GitHub releases, tags, or gists.

PR media goes only to PR attachments (see bmo-pr/attach-media.md).
Listing tags (`git tag -l`, `git tag --list`, bare `git tag`) stays allowed.
Run with --self-test to check the patterns.
"""
import json
import re
import sys

BLOCKED = [
    (r"\bgh\s+release\b", "gh release"),
    (r"\bgh\s+gist\b", "gh gist"),
    (r"\bgh\s+api\b[^|;&]*\b(releases|git/refs/tags|git/tags)\b", "gh api releases/tags"),
    (r"\bgit\b(\s+-[cC]\s+\S+)*\s+tag\s+(?!-l\b|--list\b)\S", "git tag (create/delete)"),
    (r"\bgit\b[^|;&]*\s+push\b[^|;&]*(--tags|--follow-tags|refs/tags/)", "git push of tags"),
    (r"\bnpm\s+version\b", "npm version (creates a tag)"),
    (r"\byarn\s+(run\s+)?release:", "yarn release:* (pushes tags)"),
]


def blocked_label(command: str):
    for pattern, label in BLOCKED:
        if re.search(pattern, command):
            return label
    return None


def self_test() -> int:
    for command in (
        "gh release create v1 video.mp4",
        "gh gist create a.png",
        "gh api repos/o/r/releases -f tag_name=x",
        "git tag evidence-1",
        "git -C /tmp/repo tag -d v1",
        "git push origin --tags",
        "git push origin refs/tags/v1",
        "npm version patch",
        "yarn release:prod",
    ):
        assert blocked_label(command), command
    for command in (
        "git tag",
        "git tag -l",
        "git tag --list 'v*'",
        "gh pr create --attach a.mp4",
        "git push -u origin fix/x",
    ):
        assert not blocked_label(command), command
    print("no-media-hosting self-test passed")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        payload = {}
    label = blocked_label(str(payload.get("command", "")) if isinstance(payload, dict) else "")
    if not label:
        print(json.dumps({"permission": "allow"}))
        return 0
    print(json.dumps({
        "permission": "deny",
        "agent_message": (
            f"Blocked: {label}. PR media goes only to PR attachments (gh --attach or gh image); "
            "when neither works, record Skipped. See bmo-pr/attach-media.md."
        ),
        "user_message": f"Blocked {label}: PR media is uploaded only as PR attachments.",
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
