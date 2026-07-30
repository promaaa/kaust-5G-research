#!/usr/bin/env python3
"""Check public-repository hygiene without third-party dependencies."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]

TEXT_SUFFIXES = {
    ".cfg",
    ".conf",
    ".css",
    ".csv",
    ".exp",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".mmd",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".txt",
    ".yaml",
    ".yml",
}

FORBIDDEN_PATH_PARTS = {
    ".DS_Store",
    ".env",
    ".kilo",
    ".venv",
    "__pycache__",
    "node_modules",
}

FORBIDDEN_PATH_PREFIXES = {
    "docs/.obsidian/plugins/",
    "docs/Other/paper/",
}

ALLOWED_PDFS = {
    "visual-project-recap/presentation.pdf",
}

SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "OpenAI-style secret key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    "subscriber identifier": re.compile(
        r"(?i)\b(?:imsi|supi)\s*[:= _-]*\s*[0-9]{14,16}\b"
    ),
    "SIM authentication secret": re.compile(
        r"(?i)\b(?:ki|opc)\s*[:=]\s*[\"']?[0-9a-f]{16,}\b"
    ),
    "password on command line": re.compile(
        r"(?i)\b(?:sshpass\s+-p|--password(?:=|\s+))\s*[\"']?[^<\s][^\s]*"
    ),
    "assigned credential": re.compile(
        r"""(?ix)
        \b(?:password|passwd|api[_-]?key|access[_-]?token|client[_-]?secret)
        \s*[:=]\s*
        (?![<{$[]|redacted\b|example\b|none\b|null\b)
        [^\s#]{4,}
        """
    ),
}

MARKDOWN_LINK = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
HTML_LINK = re.compile(r"""(?:src|href)=["']([^"']+)["']""", re.IGNORECASE)
OBSIDIAN_EMBED = re.compile(r"!\[\[([^]|#]+)")


def git_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [
        Path(raw.decode("utf-8"))
        for raw in result.stdout.split(b"\0")
        if raw and (ROOT / raw.decode("utf-8")).is_file()
    ]


def read_text(path: Path) -> Optional[str]:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    if path.stat().st_size > 2_000_000:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def local_target(raw_target: str) -> Optional[str]:
    target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
    target = unquote(target)
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or target.startswith("#"):
        return None
    return parsed.path


def resolve_obsidian_embed(source: Path, target: str, files: Iterable[Path]) -> bool:
    decoded = unquote(target)
    direct_candidates = (
        source.parent / decoded,
        ROOT / "docs" / decoded,
        ROOT / decoded,
    )
    if any(candidate.exists() for candidate in direct_candidates):
        return True
    name = Path(decoded).name
    return any(path.name == name for path in files)


def main() -> int:
    files = git_files()
    issues: list[str] = []

    for relative in files:
        posix = relative.as_posix()
        if any(part in FORBIDDEN_PATH_PARTS for part in relative.parts):
            issues.append(f"{posix}: forbidden generated/local path")
        if any(posix.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
            issues.append(f"{posix}: forbidden vendored or third-party path")
        if relative.suffix.lower() == ".pdf" and posix not in ALLOWED_PDFS:
            issues.append(f"{posix}: PDF is not in the explicit allowlist")

        absolute = ROOT / relative
        text = read_text(absolute)
        if text is None:
            continue

        if relative != Path("scripts/check_repository.py"):
            if "/Users/" in text:
                issues.append(f"{posix}: contains a developer-specific /Users path")
            if "cite" in text or re.search(r"\[cite:[^\]]+]", text):
                issues.append(f"{posix}: contains an unportable citation marker")

            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    issues.append(f"{posix}: possible {label}")

        if relative.suffix.lower() not in {".md", ".html"}:
            continue

        for match in MARKDOWN_LINK.finditer(text):
            target = local_target(match.group(1))
            if target is None or target == "":
                continue
            if not (absolute.parent / target).resolve().exists():
                issues.append(
                    f"{posix}: missing local link target {match.group(1)!r}"
                )

        for match in HTML_LINK.finditer(text):
            target = local_target(match.group(1))
            if target is None or target == "":
                continue
            if not (absolute.parent / target).resolve().exists():
                issues.append(
                    f"{posix}: missing local HTML target {match.group(1)!r}"
                )

        for match in OBSIDIAN_EMBED.finditer(text):
            if not resolve_obsidian_embed(absolute, match.group(1), (ROOT / f for f in files)):
                issues.append(
                    f"{posix}: missing Obsidian embed {match.group(1)!r}"
                )

    if issues:
        print("Repository checks failed:", file=sys.stderr)
        for issue in sorted(set(issues)):
            print(f"- {issue}", file=sys.stderr)
        return 1

    print(f"Repository checks passed for {len(files)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
