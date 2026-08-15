"""Command-line chunking of normalized security documents."""

from pathlib import Path

import argparse
import sys

from sentinelrag.chunks import build_document_chunks, save_document_chunks
from sentinelrag.documents import NormalizedDocument


def chunk_document_file(
    input_path: Path,
    output_directory: Path,
    max_chars: int = 1_000,
    overlap_chars: int = 150,
) -> Path:
    """Load a normalized document, chunk it, and save the results."""

    document_json = input_path.read_text(encoding="utf-8")
    document = NormalizedDocument.model_validate_json(document_json)

    chunks = build_document_chunks(
        document=document,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
    )

    return save_document_chunks(
        chunks=chunks,
        output_directory=output_directory,
    )


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="Split a normalized security document into retrievable chunks."
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to a normalized document JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/chunks"),
        help="Directory where chunk JSON will be saved.",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=1_000,
        help="Maximum characters per chunk.",
    )
    parser.add_argument(
        "--overlap-chars",
        type=int,
        default=150,
        help="Approximate overlap between adjacent chunks.",
    )

    return parser


def main() -> int:
    """Run document chunking from the terminal."""

    arguments = build_parser().parse_args()

    try:
        output_path = chunk_document_file(
            input_path=arguments.input_path,
            output_directory=arguments.output,
            max_chars=arguments.max_chars,
            overlap_chars=arguments.overlap_chars,
        )
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Saved document chunks: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
