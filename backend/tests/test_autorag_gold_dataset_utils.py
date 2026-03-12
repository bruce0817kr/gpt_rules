from __future__ import annotations

import importlib.util
from pathlib import Path


def load_gold_utils_module():
    module_path = Path(__file__).parent / "autorag" / "gold_dataset_utils.py"
    spec = importlib.util.spec_from_file_location("autorag_gold_dataset_utils", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_finalize_candidate_cases_deduplicates_against_existing_questions() -> None:
    module = load_gold_utils_module()

    candidates = [
        {
            "question": " leave approval route summary ",
            "answer_mode": "hr_admin",
            "categories": ["rule", "guide"],
            "persona_id": "five_year_employee",
            "persona_label": "five year employee",
        },
        {
            "question": "project expense evidence checklist",
            "answer_mode": "project_management",
            "categories": ["rule", "guide", "notice"],
            "persona_id": "five_year_employee",
            "persona_label": "five year employee",
        },
    ]

    finalized = module.finalize_candidate_cases(
        candidates,
        existing_questions=["leave approval route summary"],
    )

    assert len(finalized) == 1
    assert finalized[0]["question"] == "project expense evidence checklist"
    assert finalized[0]["id"].startswith("five_year_employee_project_management_01_")


def test_validate_candidate_case_rejects_invalid_categories() -> None:
    module = load_gold_utils_module()

    try:
        module.validate_candidate_case(
            {
                "question": "contract review notice only",
                "answer_mode": "contract_review",
                "categories": ["notice"],
                "persona_id": "five_year_employee",
                "persona_label": "five year employee",
            }
        )
    except ValueError as exc:
        assert "Invalid categories" in str(exc)
    else:
        raise AssertionError("Expected invalid category validation to fail.")


def test_extract_approved_gold_rows_uses_reviewed_ground_truth() -> None:
    module = load_gold_utils_module()

    rows = module.extract_approved_gold_rows(
        [
            {
                "qid": "case-1",
                "query": "question",
                "answer_mode": "audit_response",
                "categories": ["rule", "guide"],
                "persona_id": "five_year_employee",
                "review_status": "approved",
                "selected_for_gold": False,
                "reviewed_generation_gt": ["reviewed answer"],
                "reviewed_retrieval_gt": [["doc-1::chunk 1"]],
            },
            {
                "qid": "case-2",
                "query": "hold question",
                "answer_mode": "standard",
                "categories": ["rule"],
                "review_status": "pending",
                "selected_for_gold": False,
                "reviewed_generation_gt": ["hold answer"],
                "reviewed_retrieval_gt": [["doc-2::chunk 2"]],
            },
        ]
    )

    assert rows == [
        {
            "qid": "case-1",
            "query": "question",
            "retrieval_gt": [["doc-1::chunk 1"]],
            "generation_gt": ["reviewed answer"],
            "answer_mode": "audit_response",
            "categories": ["rule", "guide"],
            "gold_source": "review_queue",
            "persona_id": "five_year_employee",
        }
    ]


def test_merge_review_rows_prefers_approved_feedback_row() -> None:
    module = load_gold_utils_module()

    rows = module.merge_review_rows(
        [
            {
                "qid": "persona-1",
                "query": "contract change checklist",
                "answer_mode": "contract_review",
                "candidate_source": "persona_agent",
                "persona_id": "five_year_employee",
                "review_status": "pending",
                "reviewed_generation_gt": [],
                "reviewed_retrieval_gt": [],
                "selected_for_gold": False,
            },
            {
                "qid": "feedback-1",
                "query": "contract change checklist",
                "answer_mode": "contract_review",
                "candidate_source": "user_feedback",
                "persona_id": "",
                "review_status": "approved",
                "reviewed_generation_gt": ["reviewed answer"],
                "reviewed_retrieval_gt": [["doc-1::chunk 1"]],
                "selected_for_gold": True,
                "feedback_duplicate_count": 2,
            },
        ]
    )

    assert len(rows) == 1
    assert rows[0]["qid"] == "feedback-1"
    assert rows[0]["merged_qids"] == ["feedback-1", "persona-1"]
    assert rows[0]["merged_sources"] == ["user_feedback", "persona_agent"]
    assert rows[0]["merged_persona_ids"] == ["five_year_employee"]


def test_review_backlog_snapshot_counts_pending_and_gold_ready_rows() -> None:
    module = load_gold_utils_module()

    snapshot = module.review_backlog_snapshot(
        [
            {
                "qid": "case-1",
                "query": "question 1",
                "answer_mode": "standard",
                "candidate_source": "persona_agent",
                "persona_id": "new_employee",
                "review_status": "pending",
                "selected_for_gold": False,
                "merged_qids": ["case-1"],
            },
            {
                "qid": "case-2",
                "query": "question 2",
                "answer_mode": "audit_response",
                "candidate_source": "user_feedback",
                "persona_id": "",
                "review_status": "approved",
                "selected_for_gold": False,
                "merged_qids": ["case-2", "case-3"],
            },
        ]
    )

    assert snapshot["total_rows"] == 2
    assert snapshot["pending_rows"] == 1
    assert snapshot["approved_rows"] == 1
    assert snapshot["gold_ready_rows"] == 1
    assert snapshot["duplicate_clusters"] == 1
    assert snapshot["by_source"] == {"persona_agent": 1, "user_feedback": 1}


def test_build_balanced_review_packets_spreads_modes_across_packets() -> None:
    module = load_gold_utils_module()

    packets = module.build_balanced_review_packets(
        [
            {
                "qid": "feedback-1",
                "query": "audit evidence follow-up checklist",
                "answer_mode": "audit_response",
                "candidate_source": "user_feedback",
                "persona_id": "",
                "review_status": "pending",
                "merged_qids": ["feedback-1", "feedback-2"],
            },
            {
                "qid": "persona-1",
                "query": "audit evidence summary",
                "answer_mode": "audit_response",
                "candidate_source": "persona_agent",
                "persona_id": "five_year_employee",
                "review_status": "pending",
                "merged_qids": ["persona-1"],
            },
            {
                "qid": "persona-2",
                "query": "procurement quote rule summary",
                "answer_mode": "procurement_bid",
                "candidate_source": "persona_agent",
                "persona_id": "team_lead",
                "review_status": "pending",
                "merged_qids": ["persona-2"],
            },
            {
                "qid": "persona-3",
                "query": "contract change document checklist",
                "answer_mode": "contract_review",
                "candidate_source": "persona_agent",
                "persona_id": "finance_officer",
                "review_status": "pending",
                "merged_qids": ["persona-3"],
            },
        ],
        packet_size=3,
    )

    assert len(packets) == 2
    assert packets[0]["row_count"] == 3
    assert packets[0]["rows"][0]["qid"] == "feedback-1"
    assert packets[0]["by_answer_mode"] == {
        "audit_response": 1,
        "contract_review": 1,
        "procurement_bid": 1,
    }
    assert packets[1]["row_count"] == 1
    assert packets[1]["rows"][0]["qid"] == "persona-1"


def test_apply_review_decisions_updates_status_and_gold_fields() -> None:
    module = load_gold_utils_module()

    updated_rows, touched_qids = module.apply_review_decisions(
        [
            {
                "qid": "case-1",
                "review_status": "pending",
                "selected_for_gold": False,
                "review_notes": "",
                "reviewed_generation_gt": ["old answer"],
                "reviewed_retrieval_gt": [["doc-1::chunk 1"]],
            },
            {
                "qid": "case-2",
                "review_status": "pending",
                "selected_for_gold": False,
                "review_notes": "",
            },
        ],
        {
            "case-1": {
                "qid": "case-1",
                "review_status": "approved",
                "selected_for_gold": True,
                "review_notes": "spot checked",
                "reviewed_generation_gt": ["new answer"],
                "reviewed_retrieval_gt": [["doc-2::chunk 2"]],
            }
        },
    )

    assert touched_qids == ["case-1"]
    assert updated_rows[0]["review_status"] == "approved"
    assert updated_rows[0]["selected_for_gold"] is True
    assert updated_rows[0]["review_notes"] == "spot checked"
    assert updated_rows[0]["reviewed_generation_gt"] == ["new answer"]
    assert updated_rows[0]["reviewed_retrieval_gt"] == [["doc-2::chunk 2"]]
    assert updated_rows[1]["review_status"] == "pending"
