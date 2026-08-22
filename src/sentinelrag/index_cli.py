"""Command-line construction of the SentinelRAG vector index."""

from pathlib import Path
import argparse
import sys

from sentinelrag.config import Settings
from sentinelrag.embeddings import (
    OllamaEmbeddingClient,
    OllamaEmbeddingError,
)

from sentinelrag.chunks import load_document_chunks
from sentinelrag.vector_index import (
    EmbeddingClient,
    build_vector_records,
    save_vector_index,
)


def build_index_file(
    chunk_path: Path,
    output_path: Path,
    embedding_client: EmbeddingClient,
    embedding_model: str,
    batch_size: int = 16,
) -> Path:
    """Load chunks, generate embeddings, and save a vector index."""

    chunks = load_document_chunks(chunk_path)

    records = build_vector_records(
        chunks=chunks,
        embedding_client=embedding_client,
        embedding_model=embedding_model,
        batch_size=batch_size,
    )

    return save_vector_index(
        records=records,
        output_path=output_path,
    )


def build_parser() -> argparse.ArgumentParser:
    """Create the vector-index command-line parser."""

    parser = argparse.ArgumentParser(
        description=("Embed validated document chunks and build a vector index.")
    )
    parser.add_argument(
        "chunk_path",
        type=Path,
        help="Path to a persisted chunk JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/index/security-index.json"),
        help="Path where the vector index will be saved.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Number of chunks sent to Ollama per request.",
    )

    return parser


def main() -> int:
    """Build a vector index from the terminal."""

    arguments = build_parser().parse_args()
    settings = Settings()
    embedding_client = OllamaEmbeddingClient(settings=settings)

    try:
        output_path = build_index_file(
            chunk_path=arguments.chunk_path,
            output_path=arguments.output,
            embedding_client=embedding_client,
            embedding_model=settings.ollama_embedding_model,
            batch_size=arguments.batch_size,
        )
    except (OSError, ValueError, OllamaEmbeddingError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Saved vector index: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
