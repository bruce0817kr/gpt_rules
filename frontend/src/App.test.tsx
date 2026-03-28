import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import indexHtml from '../index.html?raw';
import App from './App';
import { GUIDEBOOK_TITLE } from './content/guidebookContent';

vi.mock('./api/client', () => ({
  api: {
    health: vi.fn().mockResolvedValue({ llm_configured: true }),
    listDocuments: vi.fn().mockResolvedValue([]),
    askQuestion: vi.fn(),
    submitChatFeedback: vi.fn(),
    uploadDocument: vi.fn(),
    reindexDocument: vi.fn(),
    deleteDocument: vi.fn(),
    updateDocumentCategory: vi.fn(),
    importLawByName: vi.fn(),
    getDocumentContent: vi.fn(),
    searchLibrary: vi.fn().mockResolvedValue({ total_documents: 0, results: [] }),
  },
}));

describe('App branding', () => {
  it('keeps the HTML title in sync with the guidebook brand', () => {
    expect(indexHtml).toContain(`<title>${GUIDEBOOK_TITLE}</title>`);
  });

  it('renders the guidebook title in the shell', async () => {
    render(<App />);
    expect(await screen.findByRole('heading', { name: GUIDEBOOK_TITLE })).toBeInTheDocument();
  });
});
