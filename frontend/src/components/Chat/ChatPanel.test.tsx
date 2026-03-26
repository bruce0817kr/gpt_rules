import { fireEvent, render, screen } from '@testing-library/react';
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

  it('applies a suggested question when the quick action is pressed', () => {
    const onApplySuggestedQuestion = vi.fn();

    render(
      <ChatPanel
        messages={[]}
        draft=""
        isSubmitting={false}
        errorMessage={null}
        selectedCategories={[]}
        answerMode="standard"
        feedbackSubmittingId={null}
        suggestedQuestions={[SUGGESTED_QUESTIONS[0]]}
        onDraftChange={vi.fn()}
        onToggleCategory={vi.fn()}
        onAnswerModeChange={vi.fn()}
        onSubmit={vi.fn()}
        onApplySuggestedQuestion={onApplySuggestedQuestion}
        onOpenCitation={vi.fn()}
        onSubmitFeedback={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: SUGGESTED_QUESTIONS[0] }));

    expect(onApplySuggestedQuestion).toHaveBeenCalledWith(SUGGESTED_QUESTIONS[0]);
  });
});
