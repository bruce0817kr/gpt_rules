import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { GUIDEBOOK_TITLE } from '../../content/guidebookContent';
import { Shell } from './Shell';

describe('Shell', () => {
  it('keeps the support rail lightweight and exposes law shortcuts and evidence', () => {
    render(
      <Shell
        activeView="chat"
        onViewChange={vi.fn()}
        health={null}
        documents={[]}
        sessionUsage={{ questionCount: 0, responseCount: 0, citationCount: 0 }}
        latestCitations={[
          {
            index: 1,
            document_id: 'doc-1',
            title: '근거 문서',
            filename: 'law.pdf',
            category: 'law',
            location: '제3조',
            page_number: 2,
            snippet: '근거 문서 발췌문',
            score: 0.97,
          },
        ]}
        guideTitle={GUIDEBOOK_TITLE}
        guideDescription="경기테크노파크 규정과 관계 법령을 함께 검색해 근거 중심 답변을 제공하는 업무용 가이드북입니다."
        onOpenDocument={vi.fn()}
        onOpenLawImport={vi.fn()}
      >
        <div>chat body</div>
      </Shell>,
    );

    expect(screen.getByRole('heading', { name: GUIDEBOOK_TITLE })).toBeInTheDocument();
    expect(
      screen.getByText('경기테크노파크 규정과 관계 법령을 함께 검색해 근거 중심 답변을 제공하는 업무용 가이드북입니다.'),
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '채팅 안내' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '문서 관리' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '관계 법령 찾기' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '최근 근거' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '법령 추가' })).toBeInTheDocument();
    expect(screen.getByText('근거 문서')).toBeInTheDocument();
    expect(screen.queryByText('Knowledge Status')).not.toBeInTheDocument();
    expect(screen.queryByText('Session Usage')).not.toBeInTheDocument();
  });
});
