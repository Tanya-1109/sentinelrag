"""Command-line validation for the security source manifest."""

import sys
from pathlib import Path

from pydantic import ValidationError

from sentinelrag.sources import load_source_manifest


def validate_manifest(path: Path) -> str:
    """Validate a manifest and return a summary."""

    manifest = load_source_manifest(path)
    enabled_count = sum(source.enabled for source in manifest.sources)

    return f"Valid manifest: {len(manifest.sources)} sources, {enabled_count} enabled."


def main() -> int:
    """Validate a source manifest from the terminal."""

    if len(sys.argv) != 2:
        print("Usage: sentinelrag-sources <manifest-path>")
        return 2

    path = Path(sys.argv[1])

    try:
        summary = validate_manifest(path)
    except FileNotFoundError:
        print(f"Error: manifest not found: {path}", file=sys.stderr)
        return 1
    except (ValidationError, UnicodeError) as exc:
        print(f"Error: invalid manifest: {exc}", file=sys.stderr)
        return 1

    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
