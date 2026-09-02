#!/usr/bin/env python3
"""Build a small, text-only Omarchy chat corpus from a source checkout.

This intentionally does not download a repository or access credentials. Fetch
the exact source snapshot separately, inspect it, and pass its local path with
``--source``.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path
from typing import Iterable


IMAGE_MARKER = "[image omitted]"
EXCLUDED_PARTS = {
    ".git",
    ".github",
    "node_modules",
    "vendor",
    "dist",
    "build",
}


def iter_markdown_files(source: Path) -> list[Path]:
    """Return stable, non-empty Markdown files below ``source``."""

    files: list[Path] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".markdown"}:
            continue
        if any(part in EXCLUDED_PARTS for part in path.relative_to(source).parts):
            continue
        if path.read_text(encoding="utf-8").strip():
            files.append(path)
    return files


def sanitize_markdown(text: str) -> str:
    """Remove image payloads while preserving a visible placeholder."""

    # Inline and reference-style Markdown images.
    text = re.sub(r"!\[[^\]]*\]\([^\n)]*\)", IMAGE_MARKER, text)
    text = re.sub(r"!\[[^\]]*\]\[[^\]]*\]", IMAGE_MARKER, text)
    # HTML images, including multiline tags in exported documentation.
    text = re.sub(r"<img\b[^>]*>", IMAGE_MARKER, text, flags=re.IGNORECASE | re.DOTALL)
    # Normalize line endings and excessive blank lines for stable examples.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sections(text: str) -> list[str]:
    """Split Markdown at headings, retaining the heading in each section."""

    chunks = re.split(r"(?=^#{1,6}\s+)", text, flags=re.MULTILINE)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def chunk_document(text: str, max_chars: int) -> list[str]:
    """Create bounded chunks without splitting a Markdown section when possible."""

    output: list[str] = []
    current = ""
    for section in sections(text):
        if len(section) > max_chars:
            paragraphs = re.split(r"\n\s*\n", section)
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                if current and len(current) + len(paragraph) + 2 > max_chars:
                    output.append(current.strip())
                    current = ""
                current = f"{current}\n\n{paragraph}".strip()
            continue
        if current and len(current) + len(section) + 2 > max_chars:
            output.append(current.strip())
            current = ""
        current = f"{current}\n\n{section}".strip()
    if current:
        output.append(current.strip())
    return output


def split_documents(
    files: list[Path], eval_fraction: float, seed: int
) -> tuple[list[Path], list[Path]]:
    """Split whole documents so adjacent sections cannot leak across splits."""

    shuffled = list(files)
    random.Random(seed).shuffle(shuffled)
    eval_count = max(1, round(len(shuffled) * eval_fraction))
    eval_files = sorted(shuffled[:eval_count])
    train_files = sorted(shuffled[eval_count:])
    return train_files, eval_files


def make_examples(files: Iterable[Path], source: Path, max_chars: int) -> list[dict]:
    examples: list[dict] = []
    for path in files:
        clean = sanitize_markdown(path.read_text(encoding="utf-8"))
        for chunk in chunk_document(clean, max_chars=max_chars):
            relative = path.relative_to(source).as_posix()
            title_match = re.search(r"^#{1,6}\s+(.+)$", chunk, flags=re.MULTILINE)
            title = title_match.group(1).strip() if title_match else path.stem
            examples.append(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                "Using the Omarchy manual, explain the following "
                                f"topic ({title}) and include relevant commands or "
                                "configuration details:\n\n{chunk}"
                            ),
                        },
                        {"role": "assistant", "content": chunk},
                    ],
                    "source": relative,
                }
            )
    return examples


def write_jsonl(path: Path, examples: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for example in examples:
            handle.write(json.dumps(example, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Local Omarchy checkout")
    parser.add_argument("--output", type=Path, required=True, help="Output directory for JSONL")
    parser.add_argument("--seed", type=int, default=3407)
    parser.add_argument("--eval-fraction", type=float, default=0.125)
    parser.add_argument("--max-chars", type=int, default=3200)
    args = parser.parse_args()

    source = args.source.resolve()
    files = iter_markdown_files(source)
    if not files:
        raise SystemExit(f"No non-empty Markdown files found under {source}")
    train_files, eval_files = split_documents(files, args.eval_fraction, args.seed)
    train = make_examples(train_files, source, args.max_chars)
    evaluation = make_examples(eval_files, source, args.max_chars)
    write_jsonl(args.output / "train.jsonl", train)
    write_jsonl(args.output / "eval.jsonl", evaluation)

    summary = {
        "source": str(source),
        "markdown_documents": len(files),
        "train_documents": len(train_files),
        "eval_documents": len(eval_files),
        "train_examples": len(train),
        "eval_examples": len(evaluation),
        "seed": args.seed,
        "eval_fraction": args.eval_fraction,
        "max_chars": args.max_chars,
        "image_marker": IMAGE_MARKER,
    }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
