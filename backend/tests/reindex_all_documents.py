from __future__ import annotations

from app.dependencies import get_catalog, get_ingestion_service


def main() -> None:
    catalog = get_catalog()
    ingestion = get_ingestion_service()
    records = catalog.list_documents()

    print(f"Catalog documents: {len(records)}")
    if not records:
        return

    for index, record in enumerate(records, start=1):
        updated = ingestion.reindex_document(record.id)
        print(
            f"[{index}/{len(records)}] {updated.id} | {updated.title} | "
            f"status={updated.status.value} chunks={updated.chunk_count}"
        )


if __name__ == "__main__":
    main()
