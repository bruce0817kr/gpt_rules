import type { DocumentRecord } from '../types/api';

export interface LawCollection {
  key: string;
  title: string;
  latestVersion: string | null;
  sourceUrl: string | null;
  documentCount: number;
  items: DocumentRecord[];
}

export function isLawDocument(document: DocumentRecord): boolean {
  return document.category === 'law' || document.tags.includes('law') || Boolean(document.source_id);
}

function buildLawKey(document: DocumentRecord): string {
  return (
    document.source_id?.trim() ||
    document.title.trim().toLowerCase() ||
    document.filename.trim().toLowerCase() ||
    document.id
  );
}

function compareVersion(current: string | null, next: string | null): string | null {
  if (!current) {
    return next;
  }
  if (!next) {
    return current;
  }

  return next.localeCompare(current) > 0 ? next : current;
}

export function formatLawVersion(version: string | null): string | null {
  if (!version) {
    return null;
  }

  if (/^\d{8}$/.test(version)) {
    return `${version.slice(0, 4)}.${version.slice(4, 6)}.${version.slice(6, 8)}`;
  }

  return version;
}

export function buildLawCollections(documents: DocumentRecord[]): LawCollection[] {
  const collections = new Map<string, LawCollection>();

  documents
    .filter(isLawDocument)
    .forEach((document) => {
      const key = buildLawKey(document);
      const existing = collections.get(key);

      if (existing) {
        existing.items.push(document);
        existing.documentCount += 1;
        existing.latestVersion = compareVersion(existing.latestVersion, document.source_version ?? null);
        existing.sourceUrl = existing.sourceUrl ?? document.source_url ?? null;
        return;
      }

      collections.set(key, {
        key,
        title: document.title,
        latestVersion: document.source_version ?? null,
        sourceUrl: document.source_url ?? null,
        documentCount: 1,
        items: [document],
      });
    });

  return [...collections.values()]
    .map((collection) => ({
      ...collection,
      items: [...collection.items].sort(
        (left, right) => new Date(right.updated_at).getTime() - new Date(left.updated_at).getTime(),
      ),
    }))
    .sort((left, right) => left.title.localeCompare(right.title, 'ko'));
}
