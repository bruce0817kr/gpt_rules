import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { HERO_TITLE, SUGGESTED_QUESTIONS } from '../../content/guidebookContent';
import { ChatPanel } from './ChatPanel';

describe('ChatPanel', () => {
  it('renders the guidebook title area and suggested prompts', () => {
    render(
      <ChatPanel
        messages={[]}
        draft=""
        isSubmitting={false}
        errorMessage={null}
        selectedCategories={[]}
        answerMode="standard"
        feedbackSubmittingId={null}
        suggestedQuestions={SUGGESTED_QUESTIONS}
        onDraftChange={vi.fn()}
        onToggleCategory={vi.fn()}
        onAnswerModeChange={vi.fn()}
        onSubmit={vi.fn()}
        onApplySuggestedQuestion={vi.fn()}
        onOpenCitation={vi.fn()}
        onSubmitFeedback={vi.fn()}
      />,
    );

    expect(screen.getByRole('heading', { name: HERO_TITLE })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: SUGGESTED_QUESTIONS[0] })).toBeInTheDocument();
  });
});
