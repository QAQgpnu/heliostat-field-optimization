from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "artifacts"}
BLOCKED_SUFFIXES = {".pdf", ".docx", ".xlsx", ".xls", ".rar", ".zip", ".7z", ".pem", ".key"}
TEXT_SUFFIXES = {
    ".cff",
    ".csv",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
}
PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "generic secret assignment": re.compile(
        r"(?i)\b(password|passwd|api[_-]?key|secret|access[_-]?token)\s*[:=]\s*['\"][^'\"]{8,}"
    ),
    "private source path": re.compile(r"(?i)(?:[A-Z]:\\upanbeifen|C:\\Users\\[^\\\s]+)"),
}


def candidate_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)
    )


def main() -> None:
    failures: list[str] = []
    files = candidate_files()
    for path in files:
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            failures.append(f"blocked artifact type: {relative}")
        if path.stat().st_size > 2 * 1024 * 1024:
            failures.append(f"file exceeds 2 MiB: {relative}")
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"LICENSE", ".gitignore"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            for label, pattern in PATTERNS.items():
                if pattern.search(text):
                    failures.append(f"{label}: {relative}")
    if failures:
        print("Public-safety scan failed:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print(f"Public-safety scan passed for {len(files)} files")


if __name__ == "__main__":
    main()
