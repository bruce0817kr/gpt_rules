import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { AdminPanel } from './AdminPanel';

describe('AdminPanel', () => {
  it('reads as a secondary workspace while keeping law import visible', () => {
    render(
      <AdminPanel
        documents={[]}
        isUploading={false}
        busyDocumentId={null}
        errorMessage={null}
        onRefresh={vi.fn(async () => {})}
        onUpload={vi.fn(async () => {})}
        onDelete={vi.fn(async () => {})}
        onReindex={vi.fn(async () => {})}
        onMoveCategory={vi.fn(async () => {})}
        onImportLaw={vi.fn(async () => {})}
      />,
    );

    expect(screen.getByRole('heading', { name: '문서 관리' })).toBeInTheDocument();
    expect(screen.getByText('보조 작업 공간')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '법령 추가' })).toBeInTheDocument();
  });
});
