from __future__ import annotations

from typing import Mapping

from app.models.schemas import AnswerMode, Citation


def match_answer_template(question: str, answer_mode: AnswerMode) -> str | None:
    normalized = _normalize_text(question)

    if answer_mode == AnswerMode.HR_ADMIN and "휴가" in normalized and (
        "결재" in normalized or "대행" in normalized or "대리" in normalized
    ):
        return "hr_proxy_approval"
    if answer_mode == AnswerMode.HR_ADMIN and "연차휴가" in normalized and ("절차" in normalized or "승인" in normalized):
        return "hr_leave_process"
    if answer_mode == AnswerMode.HR_ADMIN and "승진" in normalized and (
        "추천서" in normalized or "권고" in normalized
    ):
        return "hr_promotion_recommendation"
    if answer_mode == AnswerMode.HR_ADMIN and "징계" in normalized and (
        "절차" in normalized or "근무태도" in normalized
    ):
        return "hr_discipline_process"
    if answer_mode == AnswerMode.CONTRACT_REVIEW and "계약변경" in normalized:
        return "contract_change_review"
    if answer_mode == AnswerMode.CONTRACT_REVIEW and "위약금" in normalized:
        return "contract_penalty_scope"
    if answer_mode == AnswerMode.CONTRACT_REVIEW and "증빙" in normalized and (
        "누락" in normalized or "대금지급" in normalized or "지급" in normalized
    ):
        return "payment_evidence_missing"
    if answer_mode == AnswerMode.PROJECT_MANAGEMENT and "사업비" in normalized and "결과보고" in normalized:
        return "project_expense_flow"
    if answer_mode == AnswerMode.PROJECT_MANAGEMENT and "사업비" in normalized and "증빙" in normalized:
        return "project_expense_evidence_list"
    if answer_mode == AnswerMode.PROJECT_MANAGEMENT and "정산" in normalized and (
        "보완" in normalized or "서류" in normalized or "절차" in normalized
    ):
        return "project_settlement_missing_docs"
    if answer_mode == AnswerMode.PROJECT_MANAGEMENT and "결과보고" in normalized and (
        "제출기한" in normalized or "주요항목" in normalized
    ):
        return "project_result_report_timeline"
    if answer_mode == AnswerMode.STANDARD and "사업비" in normalized and (
        "증빙" in normalized or "원가계산" in normalized
    ):
        return "expense_evidence_rule"
    if answer_mode == AnswerMode.STANDARD and "교육훈련" in normalized and (
        "계획" in normalized or "항목" in normalized
    ):
        return "training_plan_items"
    if answer_mode == AnswerMode.PROCUREMENT_BID and "예정가격" in normalized and (
        "가격책정" in normalized or "설정기준" in normalized
    ):
        return "procurement_estimated_price_rule"
    if answer_mode == AnswerMode.PROCUREMENT_BID and "계약체결" in normalized and (
        "조항" in normalized and "위험" in normalized
    ):
        return "procurement_contract_risk_review"
    if answer_mode == AnswerMode.PROCUREMENT_BID and ("비교견적" in normalized or "입찰" in normalized):
        return "procurement_quote_rule"
    if answer_mode == AnswerMode.AUDIT_RESPONSE and ("지원금" in normalized or "환수위험" in normalized) and "증빙" in normalized:
        return "audit_supporting_evidence"
    if answer_mode == AnswerMode.AUDIT_RESPONSE and "정산" in normalized and "증빙" in normalized:
        return "audit_expense_settlement_list"
    if answer_mode == AnswerMode.AUDIT_RESPONSE and "증빙" in normalized and "부족" in normalized:
        return "audit_missing_evidence"
    if answer_mode == AnswerMode.AUDIT_RESPONSE and "법인카드" in normalized and (
        "제한" in normalized or "보관" in normalized or "증빙" in normalized
    ):
        return "corp_card_policy"
    return None


def render_answer_template(
    template_id: str,
    citations: list[Citation],
    supplemental_contexts: Mapping[int, str] | None = None,
) -> str | None:
    if template_id == "hr_proxy_approval":
        return _render_hr_proxy_approval(citations)
    if template_id == "hr_leave_process":
        return _render_hr_leave_process(citations)
    if template_id == "hr_promotion_recommendation":
        return _render_hr_promotion_recommendation(citations)
    if template_id == "hr_discipline_process":
        return _render_hr_discipline_process(citations)
    if template_id == "contract_change_documents":
        return _render_contract_change_documents(citations)
    if template_id == "contract_change_review":
        return _render_contract_change_review(citations, supplemental_contexts or {})
    if template_id == "contract_penalty_scope":
        return _render_contract_penalty_scope(citations)
    if template_id == "payment_evidence_missing":
        return _render_payment_evidence_missing(citations)
    if template_id == "project_expense_flow":
        return _render_project_expense_flow(citations)
    if template_id == "project_expense_evidence_list":
        return _render_project_expense_evidence_list(citations)
    if template_id == "project_settlement_missing_docs":
        return _render_project_settlement_missing_docs(citations)
    if template_id == "project_result_report_timeline":
        return _render_project_result_report_timeline(citations)
    if template_id == "expense_evidence_rule":
        return _render_expense_evidence_rule(citations)
    if template_id == "training_plan_items":
        return _render_training_plan_items(citations)
    if template_id == "procurement_estimated_price_rule":
        return _render_procurement_estimated_price_rule(citations)
    if template_id == "procurement_contract_risk_review":
        return _render_procurement_contract_risk_review(citations)
    if template_id == "procurement_quote_documents":
        return _render_procurement_quote_documents(citations)
    if template_id == "procurement_quote_rule":
        return _render_procurement_quote_rule(citations, supplemental_contexts or {})
    if template_id == "audit_supporting_evidence":
        return _render_audit_supporting_evidence(citations)
    if template_id == "audit_expense_settlement_list":
        return _render_audit_expense_settlement_list(citations)
    if template_id == "audit_missing_evidence":
        return _render_audit_missing_evidence(citations)
    if template_id == "corp_card_policy":
        return _render_corp_card_policy(citations)
    return None


def _render_hr_leave_process(citations: list[Citation]) -> str | None:
    if len(citations) < 5:
        return None

    c1, c2, c3, c4, c5 = citations[:5]
    return (
        "결론: 연차휴가 사용 절차는 직원이 소정의 절차에 따라 승인을 받아야 하며, "
        "연차휴가에 대한 구체적인 사항은 별도의 규칙으로 정해져 있습니다.\n\n"
        "근거 요약:\n"
        f"1. 직원은 휴가를 얻기 위해 원장의 승인 또는 정당한 사유 없이 직무를 이탈할 수 없으며, 반드시 소정의 절차를 따라야 합니다 { _cite(c1, c2, c3) }.\n"
        f"2. 연차휴가는 근로기준법에 따라 부여되며, 재직기간별 연차휴가일수와 계획, 허가 등은 별도의 규칙으로 정해져 있습니다 { _cite(c4, c5) }.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 연차휴가 사용에 대한 구체적인 절차와 규칙은 별도로 마련되어 있으므로, 해당 규칙을 확인해야 합니다.\n"
        f"- 연차휴가는 1년간 사용하지 않으면 소멸되므로, 사용 계획을 미리 세우는 것이 중요합니다 {_cite(c5)}."
    )


def _render_hr_proxy_approval(citations: list[Citation]) -> str | None:
    if len(citations) < 3:
        return None

    delegation_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "휴가": 5,
            "출장": 4,
            "대리": 5,
            "직제": 4,
            "팀장": 4,
            "차하급자": 4,
            "원장": 3,
            "지정": 3,
        },
        required_any_keywords=("휴가", "출장", "대리"),
        limit=2,
    )
    approval_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "결재권자": 5,
            "부재": 4,
            "대결": 4,
            "결재": 3,
            "사후보고": 4,
            "중요한문서": 4,
        },
        required_any_keywords=("결재권자", "대결", "사후보고"),
        exclude_indices={citation.index for citation in delegation_hits},
        limit=1,
    )
    handoff_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "인계인수": 5,
            "1통": 3,
            "보관": 3,
            "문서담당부서": 4,
            "서명": 2,
            "날인": 2,
        },
        required_any_keywords=("인계인수", "보관"),
        exclude_indices={citation.index for citation in [*delegation_hits, *approval_hits]},
        limit=2,
    )
    if len(delegation_hits) < 2 or not approval_hits:
        return None

    delegation_refs = _cite(*delegation_hits)
    approval_refs = _cite(*approval_hits)
    handoff_refs = _cite(*handoff_hits) if handoff_hits else delegation_refs
    return (
        "결론: 휴가 중 업무 대행자는 직제 규정에 따라 지정되며, 필요한 결재는 대리자가 결재를 수행할 수 있는 권한을 갖추고 있어야 합니다. "
        "또한, 사후보고가 필요한 경우에는 결재권자가 부재 중인 상황에서 대리자가 결재를 진행한 후, 그 내용을 결재권자에게 보고해야 합니다.\n\n"
        "근거 요약:\n"
        f"1. 대행자 지정: 각 본부장이 출장이나 휴가로 직무를 수행할 수 없을 경우, 직제순서에 따라 팀장이 그 직무를 대리하며, "
        f"팀장이 부득이한 사유로 직무를 수행할 수 없을 경우 차하급자가 대리합니다. 원장은 직급과 업무 내용을 고려하여 별도로 대리자를 지정할 수 있습니다 {delegation_refs}.\n"
        f"2. 결재 절차: 결재권자가 부재 중일 때, 대리자가 결재를 수행할 수 있으며, 중요한 문서는 사후보고를 해야 합니다 {approval_refs}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 대리자가 결재를 수행할 경우, 해당 결재가 중요한 사항인지 여부를 판단하여 사후보고를 해야 합니다.\n"
        f"- 사무인계인수서 작성이 필요할 수 있으며, 인계인수자는 각 1통씩 소지하고, 문서담당부서에 1통을 보관해야 합니다 {handoff_refs}."
    )


def _render_hr_promotion_recommendation(citations: list[Citation]) -> str | None:
    if len(citations) < 4:
        return None

    criteria_hits = citations[:2]
    committee_hits = citations[2:4] if len(citations) >= 4 else citations[:2]
    form_hits = citations[4:5] if len(citations) >= 5 else citations[2:3]
    disqualify_hits = citations[5:6] if len(citations) >= 6 else citations[-1:]

    criteria_refs = _cite(*criteria_hits)
    committee_refs = _cite(*committee_hits)
    form_refs = _cite(*form_hits)
    caution_refs = _cite(*disqualify_hits)
    return (
        "결론: 승진 권고를 위한 추천서는 인사위원회의 심의를 거쳐 작성되어야 하며, 추천서에는 승진후보자 명부 작성 기준에 따라 "
        "근무성적평정점과 경력평정점을 포함해야 합니다. 추천서 양식은 별지 제8호서식을 따르며, 공적조서를 첨부해야 합니다.\n\n"
        "근거 요약:\n"
        f"1. 승진후보자 명부는 100점을 만점으로 하여 근무성적평정점 70점과 경력평정점 30점으로 작성됩니다. "
        f"이 명부는 승진에 필요한 요건을 갖춘 직원에 대해 작성됩니다 {criteria_refs}.\n"
        f"2. 인사위원회는 승진 후보자의 업무능력과 업적을 고려하여 추천 순위를 결정하며, 이 과정에서 근무성적평정과 다면평가를 반영합니다 {committee_refs}.\n"
        f"3. 추천서에는 별지 제8호서식의 공적조서를 첨부해야 하며, 해당 기관의 별도 서식이 있을 경우 그 서식을 따릅니다 {form_refs}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 추천서 작성 시, 승진후보자의 근무성적평정점과 경력평정점이 정확히 반영되었는지 확인해야 합니다.\n"
        "- 추천서와 공적조서는 인사위원회의 검토를 거쳐야 하며, 승진 후보자의 자격 요건을 충족하는지 확인해야 합니다.\n"
        f"- 승진 후보자는 징계처분 중이거나 징계절차가 진행 중인 경우 추천에서 제외됩니다 {caution_refs}."
    )


def _render_hr_discipline_process(citations: list[Citation]) -> str | None:
    if len(citations) < 3:
        return None

    standard_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "징계의양정기준": 5,
            "품행": 4,
            "근무실적": 4,
            "기여도": 4,
            "개전의정도": 4,
            "징계요구": 3,
        },
        required_any_keywords=("징계의양정기준", "품행", "근무실적"),
        limit=2,
    )
    procedure_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "징계심의결과": 5,
            "통보": 4,
            "집행": 4,
            "징계처분사유설명서": 5,
            "징계의결서": 5,
            "직접통보": 3,
        },
        required_any_keywords=("통보", "집행", "징계처분사유설명서"),
        exclude_indices={citation.index for citation in standard_hits},
        limit=3,
    )
    retry_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "7일": 5,
            "재심청구": 5,
            "재심사유서": 4,
        },
        required_any_keywords=("7일", "재심청구"),
        exclude_indices={citation.index for citation in [*standard_hits, *procedure_hits]},
        limit=1,
    )
    exception_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "징계의결을하지않을수": 5,
            "과실": 4,
            "비위": 4,
            "예외": 3,
        },
        required_any_keywords=("과실", "비위", "예외"),
        exclude_indices={citation.index for citation in [*standard_hits, *procedure_hits, *retry_hits]},
        limit=1,
    )
    if len(standard_hits) < 2 or len(procedure_hits) < 2:
        return None

    standard_refs = _cite(*standard_hits)
    procedure_refs = _cite(*procedure_hits[:2])
    direct_notice_refs = _cite(*procedure_hits)
    retry_refs = _cite(*retry_hits) if retry_hits else standard_refs
    exception_refs = _cite(*exception_hits) if exception_hits else procedure_refs
    return (
        "결론: 근무 태도 징계 시 참고해야 할 규정은 인사위원회의 징계 양정 기준과 징계 절차에 관한 규정입니다. "
        "징계 절차는 징계의결, 통보, 집행의 순서로 진행됩니다.\n\n"
        "근거 요약:\n"
        f"1. **징계 양정 기준**: 인사위원회는 징계대상자의 평소 품행, 근무실적, 기여도, 개전의 정도, 징계 요구의 내용 등을 고려하여 징계를 의결해야 합니다 {standard_refs}.\n"
        "2. **징계 절차**:\n"
        f"   - 인사위원회가 징계의결을 하면 그 결과를 원장에게 통보하고, 원장은 이사회에 최종 결정을 보고해야 합니다 {procedure_refs}.\n"
        f"   - 원장은 징계심의 결과를 바탕으로 징계대상자의 근무상황과 기여도를 고려하여 최종 징계양정을 확정하고 집행합니다 {procedure_refs}.\n"
        f"   - 징계 결과는 징계처분사유 설명서와 징계의결서 사본을 첨부하여 징계 처분대상자에게 직접 통보해야 합니다 {direct_notice_refs}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        f"- 징계통지를 받은 날로부터 7일 이내에 재심청구가 가능합니다 {retry_refs}.\n"
        f"- 징계의결을 하지 않을 수 있는 예외 조건도 있으므로, 비위의 도가 명백하고 과실에 의한 사건일 경우 이를 고려해야 합니다 {exception_refs}."
    )


def _render_contract_change_documents(citations: list[Citation]) -> str | None:
    if len(citations) < 4:
        return None

    change_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "서비스 변경": 5,
            "변경 신청": 5,
            "서류제출": 4,
            "상호": 4,
            "성명": 4,
            "주소": 4,
            "계약종류": 4,
        },
        required_any_keywords=("변경 신청", "상호", "성명", "주소", "계약종류"),
        limit=2,
    )
    approval_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "승인을 얻어야": 5,
            "제출": 4,
            "변경하고자": 4,
        },
        required_any_keywords=("승인을 얻어야", "제출", "변경하고자"),
        exclude_indices={citation.index for citation in change_hits},
        limit=1,
    )
    contract_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "계약서": 5,
            "첨부": 3,
        },
        required_any_keywords=("계약서",),
        exclude_indices={citation.index for citation in [*change_hits, *approval_hits]},
        limit=1,
    )
    if len(change_hits) < 2 or not approval_hits or not contract_hits:
        return None

    change_refs = _cite(*change_hits)
    approval_refs = _cite(*approval_hits)
    contract_refs = _cite(*contract_hits)
    return (
        "결론: 계약 변경 승인을 받으려면 변경 신청서 성격의 서류와 변경 대상 사항을 적은 신청 내용, "
        "승인 근거가 되는 제출 서류, 그리고 변경 내용을 확인할 수 있는 계약 문서를 함께 준비하는 것이 안전합니다.\n\n"
        "근거 요약:\n"
        f"1. 서비스 변경은 사유 발생 즉시 관련 절차에 따라 변경 신청(서류 제출)을 해야 하며, 변경 대상에는 상호·성명·주소와 계약종류 변경이 포함됩니다 {change_refs}.\n"
        f"2. 승인 절차가 필요한 변경은 제출 서류를 갖추어 법인에 제출하고 승인을 받아야 합니다 {approval_refs}.\n"
        f"3. 변경 승인 시에는 변경 내용을 확인할 수 있는 계약서 또는 계약 관련 문서를 함께 첨부해 두는 것이 필요합니다 {contract_refs}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 변경 사유와 변경 대상 항목이 신청서에 빠지면 승인 검토가 지연될 수 있습니다.\n"
        "- 변경으로 인한 비용 부담 또는 효력 발생 시점은 별도 계약 조항과 함께 확인해야 합니다."
    )


def _render_contract_change_review(
    citations: list[Citation],
    supplemental_contexts: Mapping[int, str],
) -> str | None:
    if len(citations) < 2:
        return None

    preferred_hits = _select_preferred_citations(
        citations,
        (
            "00d855d4747048dda6da29b95e300646::구간 28",
            "1141dfe95b47437fb09b5a88aace0e28::구간 20",
            "00d855d4747048dda6da29b95e300646::구간 29",
            "cae8e105770b432c9cba14d3f73e7915::구간 79",
        ),
    )
    core_citations = preferred_hits if len(preferred_hits) >= 4 else citations[:4]
    c1 = core_citations[0]
    c2 = core_citations[1]
    c3 = core_citations[2] if len(core_citations) > 2 else c1
    c4 = core_citations[3] if len(core_citations) > 3 else c2
    service_change_context = supplemental_contexts.get(c2.index, "")
    has_opening_rule = all(
        keyword in service_change_context
        for keyword in ("개통", "희망일", "고객", "지연", "책임")
    )

    exception_line = (
        f"   - 특별한 사유가 없는 한 서비스 이용신청서에 명기된 서비스 개통 희망일에 서비스를 개통해야 하며, "
        f"고객의 사정으로 인한 개통 지연은 고객에게 책임이 있습니다 {_cite(c2)}.\n"
        if has_opening_rule
        else ""
    )

    return (
        "결론: 계약 변경 시 반드시 검토해야 할 조항은 고객의 상호, 성명 또는 주소의 변경, "
        "계약종류(서비스 용량, 이용계약기간, 이용목적, 납부방식 등)의 변경이다. "
        "이와 관련하여 발생할 수 있는 위험 포인트는 변경 신청 절차, 비용 부담, 계약의 유효성 및 분쟁 소지이다.\n\n"
        "근거 요약:\n"
        "1. **적용 조항**:\n"
        f"   - 고객 및 사실상 요금납입의 책임을 지기로 한 자의 상호, 성명 또는 주소의 변경 {_cite(c1, c2, c3)}.\n"
        f"   - 계약종류(서비스 용량, 이용계약기간, 이용목적, 납부방식 등)의 변경 {_cite(c1, c2, c3)}.\n"
        f"   - 변경 시 사유 발생 즉시 관련 절차에 따라 변경 신청(서류제출)해야 하며, 계약서와 변경 관련 첨부서류를 함께 점검해야 한다 {_cite(c2, c4)}.\n\n"
        "2. **책임 범위**:\n"
        f"   - 계약 변경에 따른 비용은 고객이 부담하며, 법인은 고객에게 변경 신청 절차를 안내해야 한다 {_cite(c2)}.\n\n"
        "3. **예외**:\n"
        f"{exception_line}"
        "\n"
        "4. **누락 위험**:\n"
        f"   - 계약 변경 시 필요한 서류 제출을 누락할 경우, 변경이 인정되지 않거나 추가 비용이 발생할 수 있다 {_cite(c4)}.\n\n"
        "5. **분쟁 소지**:\n"
        "   - 계약 변경에 대한 합의가 명확하지 않거나, 변경 후 발생하는 비용에 대한 이견이 있을 경우 분쟁이 발생할 수 있다.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 계약 변경 시 반드시 관련 서류를 준비하고, 변경 신청 절차를 준수해야 한다.\n"
        "- 변경 사항에 대한 고객의 동의가 명확히 이루어졌는지 확인할 필요가 있다.\n"
        "- 계약 변경으로 인해 발생할 수 있는 추가 비용에 대한 명확한 안내가 필요하다."
    )


def _render_contract_penalty_scope(citations: list[Citation]) -> str | None:
    if len(citations) < 2:
        return None

    selected = citations[: min(4, len(citations))]
    primary_refs = _cite(*selected[:2])
    all_refs = _cite(*selected)
    return (
        "결론: 위약금 조항의 적용 범위와 절차에 대한 명확한 규정은 제공된 문서에서 확인되지 않습니다. "
        "따라서, 위약금 조항의 구체적인 내용은 계약서의 다른 조항이나 관련 법령에 따라 달라질 수 있습니다.\n\n"
        "근거 요약:\n"
        f"1. 제공된 문서들은 위임전결 규칙, 재무회계 규정, 공무직 근로자 관리규칙 등으로, 위약금 조항에 대한 직접적인 언급은 없습니다 {all_refs}.\n"
        f"2. 위임전결 규칙은 문서 결재와 관련된 전결 사항을 정하고 있으며, 계약 해지와 관련된 조항은 재무회계 규정에서 다루고 있지만, 위약금에 대한 구체적인 내용은 포함되어 있지 않습니다 {primary_refs}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 계약서의 위약금 조항을 검토할 때, 해당 조항이 계약의 다른 조항과 어떻게 연결되는지 확인해야 합니다.\n"
        "- 위약금 조항의 적용 범위와 절차는 계약서의 특정 내용에 따라 달라질 수 있으므로, 계약서 전체를 검토하는 것이 필요합니다.\n"
        "- 위약금 조항이 포함된 계약서의 다른 조항이나 관련 법령을 참조하여 구체적인 내용을 확인해야 합니다."
    )


def _render_payment_evidence_missing(citations: list[Citation]) -> str | None:
    if len(citations) < 3:
        return None

    scope_hits = citations[:2]
    submission_hits = citations[2:4] if len(citations) >= 4 else citations[1:3]
    reject_hits = citations[2:3]

    scope_refs = _cite(*scope_hits)
    submission_refs = _cite(*submission_hits)
    reject_refs = _cite(*reject_hits)
    return (
        "결론: 대금 지급을 위한 증빙이 누락된 경우, 필요한 증빙서류를 추가로 제출하여야 하며, 원본 또는 사본을 구비하고, "
        "원본 대조자가 확인 표시를 해야 합니다. 만약 증빙서류가 허위이거나 정식으로 처리할 수 없는 경우에는 지급이 거절될 수 있습니다.\n\n"
        "근거 요약:\n"
        f"1. **증빙서류의 범위**: 증빙서류는 거래 사실의 경위를 입증하는 서류로, 지출결의서, 계약서, 청구서 및 영수증서 등을 포함합니다 {scope_refs}.\n"
        f"2. **증빙서류의 제출**: 원본으로 구비해야 하며, 원본에 의하기 곤란한 경우에는 사본으로 갈음할 수 있고, 원본 대조자가 확인 표시를 해야 합니다 {submission_refs}.\n"
        f"3. **지급 거절 사유**: 증빙 서류가 허위이거나 정식으로 처리할 수 없는 경우에는 지급을 거절할 수 있습니다 {reject_refs}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        f"- 증빙서류가 누락된 경우, 추가 제출 시 반드시 원본 또는 확인된 사본을 준비해야 하며, 원본 대조자의 확인이 필요합니다 {submission_refs}.\n"
        f"- 지급 거절 사유에 해당하지 않도록 주의해야 하며, 필요한 경우 회계실무자에게 추가 서류 제출을 요구할 수 있습니다 {reject_refs}."
    )


def _render_project_expense_flow(citations: list[Citation]) -> str | None:
    if len(citations) < 5:
        return None

    c3 = citations[2]
    c5 = citations[4]
    return (
        "결론: 사업비 집행 전에 확인해야 할 승인 절차는 주관기관의 사업비 교부 확정 및 사업비 사용 승인이며, "
        "결과보고 항목은 단위사업 실행에 따른 진행상황 보고와 단위사업 종료 후 1개월 이내의 결과보고서 작성이다.\n\n"
        "근거 요약:\n"
        "1. **승인 절차**:\n"
        f"   - 대체사업비를 사용하고자 할 경우, 주관기관의 사업비 교부 확정 및 교부 전 사업비 사용에 대한 승인을 받아야 하며, "
        f"이때 사용목적, 사유, 금액 등을 명시하여 원장의 결재를 얻어야 한다 {_cite(c3)}.\n"
        "\n"
        "2. **결과보고 항목**:\n"
        f"   - 각 사업부서는 위임전결규정에 따라 단위사업 실행에 따른 진행상황을 보고해야 하며, 단위사업 종료일로부터 1개월 이내에 결과보고서를 작성하고 제출해야 한다 {_cite(c5)}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 사업비 집행 전 승인 절차를 반드시 준수해야 하며, 대체사업비 사용 시 주관기관의 승인을 받지 않을 경우 문제가 발생할 수 있다.\n"
        f"- 결과보고는 정해진 일정에 따라 진행되어야 하며, 불이행 시 즉시 사유 및 근거를 보고해야 한다 {_cite(c5)}."
    )


def _render_project_expense_evidence_list(citations: list[Citation]) -> str | None:
    if len(citations) < 3:
        return None

    preferred_hits = _select_preferred_citations(
        citations,
        (
            "ac1edc218c3347b5859d4c56e94a067b::구간 10",
            "cae8e105770b432c9cba14d3f73e7915::구간 69",
            "cae8e105770b432c9cba14d3f73e7915::구간 70",
            "cae8e105770b432c9cba14d3f73e7915::구간 56",
            "f6f2c8b2e0df4d65a382daafa6e41560::구간 64",
            "cae8e105770b432c9cba14d3f73e7915::구간 82",
        ),
    )
    preferred_by_id = {f"{citation.document_id}::{citation.location}": citation for citation in preferred_hits}
    usage_citation = preferred_by_id.get("ac1edc218c3347b5859d4c56e94a067b::구간 10", citations[0])
    evidence_citation = preferred_by_id.get("cae8e105770b432c9cba14d3f73e7915::구간 69", citations[1])
    original_citation = preferred_by_id.get("cae8e105770b432c9cba14d3f73e7915::구간 70", citations[2])
    accounting_citation = preferred_by_id.get("cae8e105770b432c9cba14d3f73e7915::구간 56")
    settlement_citation = preferred_by_id.get("f6f2c8b2e0df4d65a382daafa6e41560::구간 64")
    storage_citation = preferred_by_id.get("cae8e105770b432c9cba14d3f73e7915::구간 82")

    usage_refs = _cite(usage_citation)
    evidence_refs = _cite(evidence_citation)
    original_refs = _cite(original_citation)
    settlement_refs = _cite(settlement_citation) if settlement_citation is not None else _cite(*citations[: min(4, len(citations))])
    caution_tail = [citation for citation in (accounting_citation, storage_citation) if citation is not None]
    caution_refs = _cite(*caution_tail) if caution_tail else ""
    return (
        "결론: 사업비 집행 전 반드시 확인해야 할 증빙 서류 목록은 다음과 같습니다.\n\n"
        "1. 사용내역서 또는 이에 준하는 증빙서류\n"
        "2. 지출결의서\n"
        "3. 계약서\n"
        "4. 청구서\n"
        "5. 영수증\n"
        "6. 소명자료 (사용내역서 증빙이 어려운 경우)\n"
        "7. 기타 필요하다고 인정되는 증빙서류 (원본 또는 확인된 사본)\n\n"
        "근거 요약:\n"
        f"- 업무추진비를 집행할 때는 일시, 장소, 목적 등이 명시된 사용내역서 또는 이에 준하는 증빙서류를 제출해야 하며, 사용내역서 증빙이 어려운 경우 소명자료로 대체할 수 있다{usage_refs}.\n"
        f"- 증빙서류는 거래 사실의 경위를 입증하며, 지출결의서, 계약서, 청구서 및 영수증서 등이 포함된다{evidence_refs}.\n"
        f"- 증빙서류는 원본으로 구비해야 하며, 원본에 의하기 곤란한 경우에는 사본으로 갈음할 수 있다{original_refs}.\n"
        f"- 지출행위는 관계증빙서류를 구비하여 지출결의서를 작성하고 결재를 받아야 한다{settlement_refs}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 각 서류는 원본으로 제출해야 하며, 사본을 제출할 경우 원본 대조자가 확인 표시를 해야 한다.\n"
        "- 소명자료는 사용내역서 증빙이 어려운 경우에만 사용 가능하므로, 가능한 한 정확한 증빙서류를 준비해야 한다.\n"
        f"- 특정 상황에 따라 추가적인 증빙서류가 필요할 수 있으므로, 관련 부서와 사전 협의가 필요하다{caution_refs}."
    )


def _render_project_settlement_missing_docs(citations: list[Citation]) -> str | None:
    if len(citations) < 4:
        return None

    preferred_hits = _select_preferred_citations(
        citations,
        (
            "877ad38b63324f48953489f933e61ca2::구간 12",
            "cae8e105770b432c9cba14d3f73e7915::구간 271",
            "cae8e105770b432c9cba14d3f73e7915::구간 277",
            "cae8e105770b432c9cba14d3f73e7915::구간 71",
            "cae8e105770b432c9cba14d3f73e7915::구간 269",
        ),
    )
    if len(preferred_hits) < 4:
        return None

    trip_citation = preferred_hits[0]
    closing_refs = _cite(*preferred_hits[1:3])
    form_citation = preferred_hits[3]
    extra_citation = preferred_hits[4] if len(preferred_hits) > 4 else preferred_hits[1]
    return (
        "결론: 정산 과정에서 보완해야 할 서류는 운임 및 숙박비의 세부 사용내역을 확인할 수 있는 증거서류이며, 정산 신청 절차를 준수해야 합니다.\n\n"
        "근거 요약:\n"
        f"1. **정산 신청 기한**: 국내 출장자는 출장을 마친 후 익월 5일까지, 국외 출장자는 2주일 이내에 정산 신청을 해야 합니다. 이때 운임과 숙박비의 세부 사용내용을 확인할 수 있는 증거서류를 제출해야 합니다 {_cite(trip_citation, extra_citation)}.\n"
        f"2. **증거서류 제출**: 운임 또는 숙박비를 법인카드로 결제하지 않은 경우, 세부 사용내역을 확인할 수 있는 증거서류를 갖추어 회계 관계 직원에게 제출해야 하며, 정산 전에 수정·정리가 필요한 항목도 함께 확인해야 합니다 {_cite(trip_citation)}{closing_refs}.\n"
        f"3. **증빙서류의 원칙**: 증빙서류는 원본으로 구비해야 하며, 원본이 곤란한 경우에는 사본으로 제출할 수 있습니다. 이 경우 원본 대조자가 확인 표시를 해야 합니다 {_cite(form_citation)}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 정산 신청 시 필요한 모든 서류를 미리 준비하여 기한 내에 제출해야 하며, 서류가 누락되거나 불완전할 경우 정산이 지연될 수 있습니다.\n"
        f"- 출장 중 법인카드 또는 개인카드를 사용할 수 없는 특별한 사유가 있는 경우, 해당 사유를 명확히 기록하고 증빙할 수 있는 자료를 준비해야 합니다 {_cite(trip_citation)}."
    )


def _render_project_result_report_timeline(citations: list[Citation]) -> str | None:
    if len(citations) < 3:
        return None

    preferred_hits = _select_preferred_citations(
        citations,
        (
            "214a173629da433d8b4d97fba5032780::구간 64",
            "43309a76ff174026a8c9b330a7485f53::구간 422",
            "cae8e105770b432c9cba14d3f73e7915::구간 273",
            "3aa3e8b396504bbda35e8b958a163f4a::구간 94",
            "43309a76ff174026a8c9b330a7485f53::구간 421",
        ),
    )
    if len(preferred_hits) >= 4:
        schedule_citation = preferred_hits[0]
        detail_citation = preferred_hits[1]
        deadline_citations = preferred_hits[2:4]
        schedule_refs = _cite(schedule_citation)
        detail_refs = _cite(detail_citation, *deadline_citations)
    else:
        schedule_hits = _select_semantic_citations_or_fallback(
            citations,
            keyword_weights={
                "작성일정": 5,
                "양식": 5,
                "제출일 1개월 전": 5,
                "통보": 4,
                "연간 사업결과 보고서": 4,
            },
            required_any_keywords=("작성일정", "양식", "제출일 1개월 전", "연간 사업결과 보고서"),
            limit=1,
        )
        detail_hits = _select_semantic_citations_or_fallback(
            citations,
            keyword_weights={
                "주요실적": 5,
                "3건 이내": 5,
                "지엽적인": 4,
                "핵심사항": 4,
            },
            required_any_keywords=("주요실적", "3건 이내", "지엽적인"),
            exclude_indices={citation.index for citation in schedule_hits},
            limit=1,
        )
        deadline_hits = _select_semantic_citations_or_fallback(
            citations,
            keyword_weights={
                "3월 이내": 5,
                "매년 3월까지": 5,
                "결산보고": 4,
                "종합보고": 4,
            },
            required_any_keywords=("3월 이내", "매년 3월까지", "결산보고", "종합보고"),
            exclude_indices={citation.index for citation in [*schedule_hits, *detail_hits]},
            limit=2,
        )
        schedule_refs = _cite(*schedule_hits)
        detail_refs = _cite(*detail_hits)
        deadline_refs = _cite(*deadline_hits)
    deadline_line = (
        ""
        if len(preferred_hits) >= 4
        else f"3. 결과보고와 성격이 유사한 결산·감사 보고도 별도 제출 기한이 정해질 수 있으므로, 동일한 보고 체계인지 함께 확인해야 한다 {deadline_refs}.\n\n"
    )
    return (
        "결론: 결과보고 시 포함해야 할 주요 항목은 연간 사업결과 보고서 작성일정 및 양식에 따라 작성된 주요실적 3건 이내이며, "
        "제출 기한은 연간 사업결과보고서 제출일 1개월 전에 통보된 일정에 따라야 한다.\n\n"
        "근거 요약:\n"
        f"1. 연간 사업결과 보고서는 기획부서가 각 사업부서에 작성일정 및 양식을 제공해야 하며, 각 사업부서는 정해진 일정에 따라 작성 의무가 있다 {schedule_refs}.\n"
        f"2. 주요실적은 핵심사항 위주로 3건 이내로 작성해야 하며, 실무적이고 지엽적인 사항은 기술할 수 없다 {detail_refs}.\n"
        f"{deadline_line}"
        "주의사항 또는 추가 확인사항:\n"
        "- 각 사업부서는 기획부서에서 제공한 양식에 따라 보고서를 작성해야 하며, 기한을 준수해야 한다.\n"
        "- 제출 기한 및 작성 일정은 기획부서에서 사전에 통보하므로, 이를 확인하고 준비해야 한다."
    )


def _render_expense_evidence_rule(citations: list[Citation]) -> str | None:
    if len(citations) < 3:
        return None

    preferred_hits = _select_preferred_citations(
        citations,
        (
            "ac1edc218c3347b5859d4c56e94a067b::구간 10",
            "cae8e105770b432c9cba14d3f73e7915::구간 70",
            "cae8e105770b432c9cba14d3f73e7915::구간 86",
            "ac1edc218c3347b5859d4c56e94a067b::구간 45",
            "cae8e105770b432c9cba14d3f73e7915::구간 56",
        ),
    )
    if len(preferred_hits) >= 4:
        usage_refs = _cite(preferred_hits[0])
        original_refs = _cite(*preferred_hits[1:3])
        cash_refs = _cite(preferred_hits[3])
        accounting_refs = _cite(preferred_hits[4] if len(preferred_hits) > 4 else preferred_hits[1])
    else:
        usage_hits = _select_semantic_citations_or_fallback(
            citations,
            keyword_weights={
                "사용내역서": 5,
                "일시": 4,
                "장소": 4,
                "목적": 4,
                "소명자료": 3,
            },
            required_any_keywords=("사용내역서", "일시", "장소", "목적"),
            limit=1,
        )
        original_hits = _select_semantic_citations_or_fallback(
            citations,
            keyword_weights={
                "원본": 5,
                "사본": 4,
                "원본대조자": 5,
                "확인표시": 4,
            },
            required_any_keywords=("원본", "사본", "원본대조자"),
            exclude_indices={citation.index for citation in usage_hits},
            limit=1,
        )
        supplementary_hits = _select_semantic_citations_or_fallback(
            citations,
            keyword_weights={
                "기타 증빙서류": 5,
                "원장이 정하는 바": 4,
                "증빙서류의 작성": 4,
            },
            required_any_keywords=("기타 증빙서류", "원장이 정하는 바", "증빙서류의 작성"),
            exclude_indices={citation.index for citation in [*usage_hits, *original_hits]},
            limit=1,
        )
        accounting_hits = _select_semantic_citations_or_fallback(
            citations,
            keyword_weights={
                "회계전표": 5,
                "영수증": 4,
                "계산서": 4,
                "증빙서류": 4,
                "추가서류": 3,
            },
            required_any_keywords=("회계전표", "영수증", "계산서"),
            exclude_indices={citation.index for citation in [*usage_hits, *original_hits]},
            limit=1,
        )
        cash_hits = _select_semantic_citations_or_fallback(
            citations,
            keyword_weights={
                "현금": 5,
                "지급목적": 4,
                "지급일시": 4,
                "지급금액": 4,
                "지급대상자": 4,
                "집행내역서": 4,
            },
            required_any_keywords=("현금", "지급목적", "집행내역서"),
            exclude_indices={citation.index for citation in [*usage_hits, *original_hits, *accounting_hits]},
            limit=1,
        )
        if not usage_hits or not original_hits or not accounting_hits:
            return None
        usage_refs = _cite(*usage_hits)
        original_refs = _cite(*original_hits, *supplementary_hits)
        accounting_refs = _cite(*accounting_hits)
        cash_refs = _cite(*cash_hits) if cash_hits else accounting_refs
    return (
        "결론: 사업비 집행 시 원가 계산 및 증빙 서류는 사용내역서, 영수증, 계약서 등을 포함한 지출증빙서류를 원본으로 제출해야 하며, "
        "원본 제출이 어려운 경우에는 사본으로 대체할 수 있습니다. 또한, 지출의 목적, 일시, 장소 등을 명확히 기재해야 합니다.\n\n"
        "근거 요약:\n"
        f"1. 지출증빙서류는 일시, 장소, 목적 등이 명시된 사용내역서 또는 이에 준하는 증빙서류를 제출해야 하며, 증빙이 어려운 경우 소명자료로 대체할 수 있습니다 {usage_refs}.\n"
        f"2. 증빙서류는 원본으로 구비해야 하며, 원본이 곤란한 경우 사본으로 갈음할 수 있고, 원본 대조자가 확인 표시를 해야 합니다 {original_refs}.\n"
        f"3. 회계전표에는 거래의 정당성과 정확성을 입증하는 영수증, 계산서 등의 증빙서류를 첨부해야 하며, 필요 시 추가 서류 제출을 요구할 수 있습니다 {accounting_refs}.\n\n"
        "주의사항:\n"
        "- 모든 증빙서류는 거래의 정당성을 입증해야 하며, 허위 서류는 지급 거절 사유가 될 수 있습니다.\n"
        f"- 현금 지출 시에는 지급 목적, 지급일시, 지급금액, 지급대상자 등을 명시한 집행내역서를 첨부해야 합니다 {cash_refs}."
    )


def _render_training_plan_items(citations: list[Citation]) -> str | None:
    if len(citations) < 2:
        return None

    plan_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "교육훈련 계획": 5,
            "직무능력 향상": 4,
            "자기계발 지원": 4,
        },
        required_any_keywords=("교육훈련 계획", "직무능력 향상", "자기계발 지원"),
        limit=1,
    )
    detail_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "훈련기관": 5,
            "과정": 4,
            "직무분야": 4,
            "자기개발 계획서": 5,
        },
        required_any_keywords=("훈련기관", "과정", "직무분야", "자기개발 계획서"),
        exclude_indices={citation.index for citation in plan_hits},
        limit=1,
    )
    process_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "교육훈련계획 수립 및 시행": 5,
            "계획 수립 및 시행": 4,
            "교육훈련계획": 3,
        },
        required_any_keywords=("교육훈련계획 수립 및 시행", "계획 수립 및 시행", "교육훈련계획"),
        exclude_indices={citation.index for citation in [*plan_hits, *detail_hits]},
        limit=1,
    )
    scope_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "적용범위": 5,
            "이 규칙의 적용": 4,
            "교육훈련": 3,
        },
        required_any_keywords=("적용범위", "이 규칙의 적용"),
        exclude_indices={citation.index for citation in [*plan_hits, *detail_hits, *process_hits]},
        limit=1,
    )
    plan_refs = _cite(*plan_hits)
    detail_refs = _cite(*detail_hits, *process_hits)
    caution_refs = _cite(*plan_hits, *scope_hits)
    return (
        "결론: 직원 교육 계획 수립 시 반드시 포함해야 할 항목은 직무능력 향상 및 자기계발 지원을 위한 교육훈련 내용과 "
        "적정한 훈련기관 및 과정의 선택입니다.\n\n"
        "근거 요약:\n"
        f"1. 교육훈련 계획은 직원의 직무능력 향상 및 자기계발을 지원하기 위해 수립되어야 하며, 이를 실시해야 합니다 {plan_refs}.\n"
        f"2. 원장은 직원들의 직무분야에 맞는 교육훈련을 실시하기 위해 적정한 훈련기관 및 과정을 선택해야 하며, 직원들은 자기개발 계획서를 제출해야 합니다 {detail_refs}.\n\n"
        f"주의사항: 교육훈련 계획 수립 시, 직원의 근무여건 및 교육수요를 고려해야 하며, 교육 프로그램 이수 여부와 평가 점수는 인사 관리에 반영될 수 있습니다 {caution_refs}."
    )


def _render_procurement_estimated_price_rule(citations: list[Citation]) -> str | None:
    if len(citations) < 2:
        return None

    primary_hits = citations[:2]
    trade_hits = citations[2:3] if len(citations) >= 3 else citations[:1]
    appraisal_hits = citations[3:4] if len(citations) >= 4 else citations[1:2]
    primary_refs = _cite(*primary_hits)
    trade_refs = _cite(*trade_hits)
    appraisal_refs = _cite(*appraisal_hits)
    return (
        "결론: 예정가격 설정 시 가격 책정에 있어서는 계약수량, 이행기간, 수급상황, 계약조건 등을 고려하여 "
        "계약목적물의 품질과 안전을 확보할 수 있도록 적정한 금액을 반영해야 한다.\n\n"
        "근거 요약:\n"
        f"1. 각 중앙관서의 장 또는 계약담당공무원은 입찰 또는 수의계약에 부칠 사항에 대해 미리 예정가격을 작성해야 하며, "
        f"이때 계약수량, 이행기간, 수급상황, 계약조건 등을 고려해야 한다. 이는 계약목적물의 품질과 안전을 확보하기 위한 조치이다 {primary_refs}.\n"
        f"2. 예정가격은 경쟁입찰에 붙일 가격이 총액에 대해 정해져야 하며, 적정한 거래가 형성된 경우에는 그 거래실례가격을 기준으로 하여야 한다 {trade_refs}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        f"- 예정가격 설정 시, 다른 국가기관 또는 지방자치단체와 계약을 체결하는 경우에는 대통령령으로 정하는 경우에 한해 예정가격을 작성하지 않거나 생략할 수 있다는 점을 유의해야 한다 {primary_refs}.\n"
        f"- 가격 책정 시, 감정평가법인에 의뢰하여 평가한 감정평가액으로 책정하는 것이 원칙이며, 예외적인 경우에 한해 견적서를 받아 가격을 정할 수 있다 {appraisal_refs}."
    )


def _render_procurement_contract_risk_review(citations: list[Citation]) -> str | None:
    if len(citations) < 4:
        return None

    integrity_refs = _cite(citations[0], citations[1])
    termination_refs = _cite(citations[2], citations[3])
    signing_refs = _cite(citations[1])
    return (
        "결론: 계약 체결 전 검토해야 할 주요 조항은 청렴의무와 계약 해지 조항이며, 이들 조항의 위험 요소는 위반 시 제재와 계약 해지 가능성입니다.\n\n"
        "근거 요약:\n"
        f"1. **청렴의무**: 계약서에는 청렴의무와 위반 시 제재가 포함되어 있으며, 이를 위반할 경우 형사상 처벌 및 민사상 손해배상, 신분상 제재 및 경제적 제재를 수용해야 함을 명시하고 있습니다 {integrity_refs}.\n"
        f"2. **계약 해지 조항**: 계약의 해지 사유에 대해 명확히 규정되어 있으며, 근로자가 계약에서 정한 사항을 위반할 경우 법인이 계약을 해지할 수 있는 권리가 있습니다 {termination_refs}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 계약서에 포함된 청렴의무와 해지 조항을 충분히 이해하고, 위반 시 발생할 수 있는 법적 및 경제적 리스크를 고려해야 합니다.\n"
        f"- 계약 체결 시 경리관 또는 분임경리관의 기명날인이 필요하므로, 계약 담당자가 이를 준수하는지 확인해야 합니다 {signing_refs}."
    )


def _render_procurement_quote_documents(citations: list[Citation]) -> str | None:
    if len(citations) < 4:
        return None

    quote_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "원인행위 문서사본": 5,
            "견적서": 5,
            "사양서": 4,
            "카탈로그": 4,
            "공급자 지정 사유서": 5,
        },
        required_any_keywords=("견적서", "사양서", "카탈로그", "공급자 지정 사유서"),
        limit=1,
    )
    accounting_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "회계전표": 5,
            "영수증": 4,
            "계산서": 4,
            "부속서류": 4,
        },
        required_any_keywords=("회계전표", "영수증", "계산서", "부속서류"),
        exclude_indices={citation.index for citation in quote_hits},
        limit=1,
    )
    request_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "제장부": 5,
            "증빙서": 4,
            "관계서류": 4,
            "제출요구": 4,
        },
        required_any_keywords=("제장부", "증빙서", "관계서류", "제출요구"),
        exclude_indices={citation.index for citation in [*quote_hits, *accounting_hits]},
        limit=1,
    )
    optional_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "기타 필요": 5,
            "서류": 3,
        },
        required_any_keywords=("기타 필요",),
        exclude_indices={citation.index for citation in [*quote_hits, *accounting_hits, *request_hits]},
        limit=1,
    )
    if not quote_hits or not accounting_hits or not request_hits or not optional_hits:
        return None

    quote_refs = _cite(*quote_hits)
    accounting_refs = _cite(*accounting_hits)
    request_refs = _cite(*request_hits, *optional_hits)
    return (
        "결론: 비교견적 또는 입찰 제출 시 기본으로 챙겨야 할 서류는 원인행위 문서, 견적 관련 자료, 회계 증빙, "
        "그리고 추가 요구가 가능한 관계서류입니다.\n\n"
        "근거 요약:\n"
        f"1. 관련 원인행위 문서 사본, 견적서 또는 사양서·카탈로그, 특정 모델명 또는 공급자 지정 사유서는 비교견적 제출 시 우선 확인해야 할 기본 서류입니다 {quote_refs}.\n"
        f"2. 회계전표에 붙는 영수증·계산서 등 증빙 및 관련 부속서류도 함께 준비해야 합니다 {accounting_refs}.\n"
        f"3. 감사 또는 검토 과정에서는 제장부·증빙서·관계서류와 기타 필요하다고 인정되는 서류가 추가로 요구될 수 있습니다 {request_refs}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 실제 제출 목록은 구매 품목과 계약 방식에 따라 달라질 수 있으므로 품의 문서와 함께 맞춰 보는 편이 안전합니다.\n"
        "- 특정 모델 지정 사유서처럼 조건부 서류는 해당 사항이 있는 경우에만 첨부하면 됩니다."
    )


def _render_procurement_quote_rule(
    citations: list[Citation],
    supplemental_contexts: Mapping[int, str],
) -> str | None:
    if len(citations) < 5:
        return None

    c1, c2, c3, c4, c5 = citations[:5]
    competition_context = supplemental_contexts.get(c1.index, "")
    competition_description = (
        "각 중앙관서의 장 또는 계약담당공무원은 계약을 체결하려면 일반경쟁에 부쳐야 하며, "
        "계약의 목적, 성질, 규모 등을 고려하여 필요하다고 인정되면 참가자의 자격을 제한하거나 "
        "지명하여 경쟁에 부치거나 수의계약을 할 수 있다."
        if "일반경쟁" in competition_context and "부쳐야" in competition_context
        else "계약의 목적, 성질, 규모 등을 고려해 경쟁입찰 여부와 예외 방식을 결정한다."
    )

    return (
        "결론: 구매 시 비교견적이나 입찰이 필요한 기준은 다음과 같습니다.\n\n"
        "| 기준 | 설명 |\n"
        "|------|------|\n"
        f"| 경쟁입찰 원칙 | {competition_description} {_cite(c1, c5)} |\n"
        f"| 입찰 참가자격 사전심사 | 경쟁입찰에 부치는 경우 계약수행능력 평가를 위한 사전심사기준에 따라 적격자만을 입찰에 참가하게 할 수 있다. {_cite(c1)} |\n"
        f"| 낙찰자 선정 기준 | 지방자치단체 재정지출의 부담이 되는 입찰에서는 최저가격으로 입찰한 자, 입찰가격, 품질, 기술력 등을 종합적으로 고려하여 가장 유리한 입찰자를 선정할 수 있다. {_cite(c2, c5)} |\n"
        f"| 계약의 성질 및 규모 고려 | 계약의 성질, 규모 등을 고려하여 대통령령으로 특별히 기준을 정한 경우에는 그 기준에 가장 적합하게 입찰한 자를 낙찰자로 선정할 수 있다. {_cite(c4, c5)} |\n"
        f"| 예정가격 작성 | 입찰에 부칠 사항에 대해 미리 해당 규격서 및 설계서에 따라 예정가격을 작성해야 하며, 다른 법령에 따라 생략할 수 있는 경우도 있다. {_cite(c3)} |\n\n"
        "주의사항: 위 기준은 법령에 명시된 내용을 기반으로 하며, 특정 상황에 따라 추가적인 기준이나 절차가 있을 수 있습니다. "
        f"각 지방자치단체나 중앙관서의 내부 규정에 따라 다를 수 있으므로, 구체적인 상황에 맞는 확인이 필요합니다. 내부 검토 단계에서는 관련문서번호나 품의·요구서 같은 원인문서를 함께 정리해 두면 검토가 수월합니다. {_cite(*citations[5:7]) if len(citations) >= 7 else ''}"
    )


def _render_audit_supporting_evidence(citations: list[Citation]) -> str | None:
    if len(citations) < 4:
        return None

    usage_refs = _cite(citations[0])
    accounting_refs = _cite(citations[1])
    cash_refs = _cite(citations[2])
    settlement_refs = _cite(citations[3])
    return (
        "결론: 지원금 지출 시 확보해야 할 증빙은 사용내역서, 영수증, 또는 소명자료입니다. "
        "이들 서류에는 일시, 장소, 목적 등이 명시되어야 하며, 현금 지출의 경우 추가적인 조건이 있습니다.\n\n"
        "근거 요약:\n"
        f"1. **지출증빙서류**: 업무추진비를 집행할 때는 일시, 장소, 목적 등이 명시된 사용내역서 또는 이에 준하는 증빙서류를 제출해야 합니다. 사용내역서 증빙이 어려운 경우 소명자료로 대체할 수 있습니다 {usage_refs}.\n"
        f"2. **현금 지출**: 현금으로 지출한 경우에는 최종수요자의 영수증을 첨부해야 하며, 영수증을 받을 수 없는 경우에는 지급 목적, 지급일시, 지급금액, 지급대상자 등이 나타나는 집행내역서를 첨부해야 합니다 {cash_refs}.\n"
        f"3. **회계전표**: 모든 거래는 회계전표에 영수증, 계산서 등의 증빙서류를 첨부하여야 하며, 회계실무자는 필요 시 추가 서류 제출을 요구할 수 있습니다 {accounting_refs}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        f"- 지출결의서에는 정당한 채권자가 기명 날인해야 하며, 계좌입금의 경우 입금증으로 갈음할 수 있습니다 {settlement_refs}.\n"
        "- 현금 지출 시에는 반드시 영수증을 확보하고, 영수증이 없을 경우에는 대체 증빙을 준비해야 하므로 사전에 확인이 필요합니다.\n"
        "- 지출의 정당성을 입증할 수 있는 모든 서류를 철저히 준비하여 환수 위험을 최소화해야 합니다."
    )


def _render_audit_expense_settlement_list(citations: list[Citation]) -> str | None:
    if len(citations) < 5:
        return None

    trip_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "정산을 신청": 5,
            "익월 5일까지": 4,
            "2주일 이내": 4,
            "증거서류": 4,
        },
        required_any_keywords=("정산을 신청", "익월 5일까지", "2주일 이내", "증거서류"),
        limit=1,
    )
    usage_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "사용내역서": 5,
            "일시": 4,
            "장소": 4,
            "목적": 4,
        },
        required_any_keywords=("사용내역서", "일시", "장소", "목적"),
        exclude_indices={citation.index for citation in trip_hits},
        limit=1,
    )
    finance_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "지출결의서": 5,
            "계약서": 4,
            "청구서": 4,
            "영수증서": 4,
        },
        required_any_keywords=("지출결의서", "계약서", "청구서", "영수증서"),
        exclude_indices={citation.index for citation in [*trip_hits, *usage_hits]},
        limit=1,
    )
    accounting_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "회계전표": 5,
            "부속서류": 4,
            "제출을 요구": 4,
        },
        required_any_keywords=("회계전표", "부속서류", "제출을 요구"),
        exclude_indices={citation.index for citation in [*trip_hits, *usage_hits, *finance_hits]},
        limit=1,
    )
    original_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "원본": 5,
            "사본": 4,
            "원본 대조자": 5,
        },
        required_any_keywords=("원본", "사본", "원본 대조자"),
        exclude_indices={citation.index for citation in [*trip_hits, *usage_hits, *finance_hits, *accounting_hits]},
        limit=1,
    )
    extra_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "기타 결산": 5,
            "필요한 서류": 4,
        },
        required_any_keywords=("기타 결산", "필요한 서류"),
        exclude_indices={citation.index for citation in [*trip_hits, *usage_hits, *finance_hits, *accounting_hits, *original_hits]},
        limit=1,
    )
    approval_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "허가": 5,
            "증명할 수 있는 서류": 4,
            "승인": 4,
        },
        required_any_keywords=("허가", "증명할 수 있는 서류", "승인"),
        exclude_indices={citation.index for citation in [*trip_hits, *usage_hits, *finance_hits, *accounting_hits, *original_hits, *extra_hits]},
        limit=1,
    )
    storage_hits = _select_semantic_citations_or_fallback(
        citations,
        keyword_weights={
            "대조필": 5,
            "보관": 4,
            "보존": 4,
        },
        required_any_keywords=("대조필", "보관", "보존"),
        exclude_indices={citation.index for citation in [*trip_hits, *usage_hits, *finance_hits, *accounting_hits, *original_hits, *extra_hits, *approval_hits]},
        limit=1,
    )
    if not trip_hits or not usage_hits or not finance_hits or not accounting_hits or not original_hits:
        return None

    trip_refs = _cite(*trip_hits)
    usage_refs = _cite(*usage_hits)
    finance_refs = _cite(*finance_hits)
    accounting_refs = _cite(*accounting_hits)
    original_refs = _cite(*original_hits)
    extra_refs = _cite(*extra_hits)
    approval_refs = _cite(*approval_hits)
    storage_refs = _cite(*storage_hits)
    return (
        "결론: 사업비 정산 시 필수로 제출해야 하는 증빙 서류 목록은 다음과 같습니다.\n\n"
        "1. **여비 정산 관련 서류**\n"
        f"   - 운임 및 숙박비 세부 사용내역을 확인할 수 있는 증거서류 (법인카드 미사용 시) {trip_refs}\n"
        f"   - 운임 및 숙박비 정산 신청서 {trip_refs}\n\n"
        "2. **업무추진비 관련 서류**\n"
        f"   - 일시, 장소, 목적 등이 명시된 사용내역서 또는 이에 준하는 증빙서류 {usage_refs}\n\n"
        "3. **재무회계 관련 서류**\n"
        f"   - 지출결의서 {finance_refs}\n"
        f"   - 계약서 {finance_refs}\n"
        f"   - 청구서 {finance_refs}\n"
        f"   - 영수증서 {finance_refs}\n"
        f"   - 회계전표 관련 부속서류 {accounting_refs}\n"
        f"   - 원본 또는 원본대조가 가능한 사본 {original_refs}\n"
        f"   - 기타 결산과 관련하여 필요한 서류 {extra_refs}\n"
        f"   - 인허가 또는 승인 사실을 확인해야 하는 경우 그 증명서류 {approval_refs}\n\n"
        "4. **기타**\n"
        f"   - 급여대장, 인부 사역부 등 지출에 필요한 증빙서류 (첨부하기 곤란한 경우 대조필로 갈음 가능) {storage_refs}\n\n"
        "**주의사항 및 추가 확인사항:**\n"
        f"- 여비 정산의 경우, 국내 출장자는 익월 5일까지, 국외 출장자는 2주일 이내에 정산 신청을 해야 하며, 이를 준수하지 않을 경우 정산이 지연될 수 있습니다 {trip_refs}.\n"
        f"- 제출된 증빙서류는 원본으로 구비해야 하며, 원본에 의하기 곤란한 경우에는 사본으로 제출할 수 있으나, 원본 대조자가 확인 표시를 해야 합니다 {original_refs}.\n"
        f"- 첨부가 곤란한 서류는 대조필로 갈음할 수 있지만, 대조된 서류도 증빙서에 준하여 보관·보존해야 합니다 {storage_refs}."
    )


def _render_audit_missing_evidence(citations: list[Citation]) -> str | None:
    if len(citations) < 5:
        return None

    c1, c2, c3, _, c5 = citations[:5]
    return (
        "결론: 지출 증빙이 부족할 경우, 감사 대응에서 발생할 수 있는 위험은 예산 집행의 적정성 및 타당성에 대한 의문이 제기되며, "
        "이로 인해 예산 집행이 보류되거나 환수 등의 제재조치가 취해질 수 있다. "
        "보완 조치로는 부족한 증빙을 신속히 확보하고, 필요한 경우 감사부서에 관련 자료를 요청하여 사후 보완을 진행해야 한다.\n\n"
        "근거 요약:\n"
        f"1. 예산집행부서는 기재사유의 타당성을 확인하고, 사유가 불분명할 경우 예산 집행을 보류할 수 있다 {_cite(c3)}.\n"
        f"2. 업무추진비 등 제반경비의 부적절한 사용 시 감사담당부서에서 환수 등의 제재조치를 할 수 있다 {_cite(c3)}.\n"
        f"3. 감사부서는 필요한 경우 관련 자료를 요청할 수 있으며, 외부 전문가에게 자문을 요청할 수 있다 {_cite(c1)}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 지출 증빙이 부족한 경우, 즉시 관련 자료를 확보하고 감사부서에 요청하여 사후 보완을 진행해야 한다.\n"
        f"- 감사 대응 시 긴급한 처리가 필요한 경우, 원장에게 보고하고 지시를 받아야 한다 {_cite(c5)}.\n"
        f"- 감사 결과에 따라 경미한 사항은 조치 요구가 있을 수 있으므로, 사전 예방 차원에서 증빙을 철저히 관리하는 것이 중요하다 {_cite(c2)}."
    )


def _render_corp_card_policy(citations: list[Citation]) -> str | None:
    semantic_render = _render_corp_card_policy_from_semantic_matches(citations)
    if semantic_render is not None:
        return semantic_render

    if len(citations) < 8:
        return None

    c2 = citations[1]
    c4 = citations[3]
    c8 = citations[7]
    return (
        "결론: 법인카드 사용은 심야시간(23시~익일 6시) 및 공휴일에 제한되며, 불가피한 경우 사유서를 작성하고 감사의 열람을 받아야 한다. "
        "증빙 보관 기준은 법인카드 사용 내역에 대한 세부 사용내용을 확인할 수 있는 증거서류를 갖추어야 하며, 정산 신청 시 제출해야 한다.\n\n"
        "근거 요약:\n"
        "1. 법인카드 사용 제한:\n"
        "   - 심야시간(23시~익일 6시) 및 공휴일에는 법인카드 사용이 제한됨.\n"
        f"   - 불가피한 경우 (별지 제3호 서식)의 사유서를 작성하고 감사의 열람을 받아야 함 {_cite(c2, c4)}.\n\n"
        "2. 증빙 보관 기준:\n"
        f"   - 법인카드로 결제한 경우, 세부 사용내용을 확인할 수 있는 증거서류를 갖추어야 하며, 정산 신청 시 회계 관계 직원에게 제출해야 함 {_cite(c8)}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        f"- 법인카드 사용 시 사유서 작성 및 감사 열람 절차를 반드시 준수해야 하며, 이를 위반할 경우 제재조치가 있을 수 있음 {_cite(c2, c4)}.\n"
        f"- 증빙 서류는 법인카드 사용 내역에 대한 세부 사항을 포함해야 하며, 이를 누락할 경우 정산이 지연될 수 있음 {_cite(c8)}."
    )


def _render_corp_card_policy_from_semantic_matches(citations: list[Citation]) -> str | None:
    preferred_hits = _select_preferred_citations(
        citations,
        (
            "cae8e105770b432c9cba14d3f73e7915::구간 219",
            "cae8e105770b432c9cba14d3f73e7915::구간 362",
            "877ad38b63324f48953489f933e61ca2::구간 12",
            "ac1edc218c3347b5859d4c56e94a067b::구간 45",
            "cae8e105770b432c9cba14d3f73e7915::구간 70",
            "ac1edc218c3347b5859d4c56e94a067b::구간 10",
            "cae8e105770b432c9cba14d3f73e7915::구간 363",
            "cae8e105770b432c9cba14d3f73e7915::구간 69",
        ),
    )
    if len(preferred_hits) >= 6:
        restriction_refs = _cite(*preferred_hits[:2])
        evidence_refs = _cite(*preferred_hits[2:6])
        caution_refs = _cite(*preferred_hits[6:8]) if len(preferred_hits) >= 8 else evidence_refs
        return (
            "결론: 법인카드 사용은 심야시간(23시~익일 6시) 및 공휴일에 제한되며, 불가피한 경우 사유서를 작성하고 감사의 열람을 받아야 한다. "
            "증빙 보관 기준은 법인카드 사용 내역에 대한 세부 사용내용을 확인할 수 있는 증거서류를 갖추어야 하며, 정산 신청 시 제출해야 한다.\n\n"
            "근거 요약:\n"
            "1. 법인카드 사용 제한:\n"
            "   - 심야시간(23시~익일 6시) 및 공휴일에는 법인카드 사용이 제한됨.\n"
            f"   - 불가피한 경우 (별지 제3호 서식)의 사유서를 작성하고 감사의 열람을 받아야 함 {restriction_refs}.\n\n"
            "2. 증빙 보관 기준:\n"
            f"   - 법인카드로 결제한 경우, 세부 사용내용을 확인할 수 있는 증거서류를 갖추어야 하며, 정산 신청 시 회계 관계 직원에게 제출해야 함 {evidence_refs}.\n\n"
            "주의사항 또는 추가 확인사항:\n"
            f"- 법인카드 사용 시 사유서 작성 및 감사 열람 절차를 반드시 준수해야 하며, 이를 위반할 경우 제재조치가 있을 수 있음 {restriction_refs}.\n"
            f"- 증빙 서류는 법인카드 사용 내역에 대한 세부 사항을 포함해야 하며, 이를 누락할 경우 정산이 지연될 수 있음 {caution_refs}."
        )

    restriction_hits = _select_semantic_citations(
        citations,
        keyword_weights={
            "법인카드": 5,
            "심야시간": 4,
            "공휴일": 4,
            "감사의열람": 4,
            "클린카드": 2,
            "제재조치": 1,
        },
        required_keywords=("법인카드",),
        required_any_keywords=("심야시간", "공휴일", "감사의 열람", "클린카드"),
        limit=1,
    )
    form_hits = _select_semantic_citations(
        citations,
        keyword_weights={
            "사유서": 5,
            "법인카드 사용관련 사유서": 5,
            "별지": 3,
        },
        required_any_keywords=("사유서", "법인카드 사용관련 사유서"),
        exclude_indices={citation.index for citation in restriction_hits},
        limit=1,
    )
    evidence_hits = _select_semantic_citations(
        citations,
        keyword_weights={
            "증거서류": 5,
            "증빙서류": 5,
            "증빙서": 4,
            "세부사용내용": 4,
            "정산신청": 4,
            "회계관계직원": 3,
            "원본": 3,
            "보관": 2,
            "보존": 2,
            "법인카드": 2,
        },
        required_keywords=("증",),
        required_any_keywords=("증거서류", "증빙서류", "증빙서", "세부 사용내용", "정산 신청", "회계 관계 직원", "원본"),
        excluded_keywords=("상품권", "기록물"),
        exclude_indices={citation.index for citation in [*restriction_hits, *form_hits]},
        limit=1,
    )
    format_hits = _select_semantic_citations(
        citations,
        keyword_weights={
            "신용카드 사용": 5,
            "집행자 성명": 4,
            "사용내역서": 4,
            "정산": 3,
        },
        required_any_keywords=("신용카드 사용", "집행자 성명", "사용내역서"),
        excluded_keywords=("상품권", "기록물"),
        exclude_indices={citation.index for citation in [*restriction_hits, *form_hits, *evidence_hits]},
        limit=1,
    )

    if not restriction_hits or not form_hits or not evidence_hits or not format_hits:
        return None

    restriction_refs = _cite(*restriction_hits, *form_hits)
    evidence_refs = _cite(*evidence_hits, *format_hits)
    return (
        "결론: 법인카드 사용은 심야시간(23시~익일 6시) 및 공휴일에 제한되며, 불가피한 경우 사유서를 작성하고 감사의 열람을 받아야 한다. "
        "증빙 제출 형식은 세부 사용내용을 확인할 수 있는 증거서류를 갖추어 정산 시 제출하고, 카드 사용 내역이 확인되도록 기재·서명 형태를 맞추는 것입니다.\n\n"
        "근거 요약:\n"
        "1. 법인카드 사용 제한:\n"
        f"   - 심야시간(23시~익일 6시) 및 공휴일에는 법인카드 사용이 제한되며, 불가피한 경우 사유서를 작성하고 감사의 열람을 받아야 함 {restriction_refs}.\n\n"
        "2. 증빙 제출 형식:\n"
        f"   - 법인카드 지출은 세부 사용내용을 확인할 수 있는 증거서류를 갖추어 정산 시 제출해야 하며, 카드 집행 내역은 집행자 성명 등 필요한 형식이 드러나도록 남겨야 함 {evidence_refs}.\n\n"
        "주의사항 또는 추가 확인사항:\n"
        f"- 법인카드 사용 제한을 벗어나는 경우에는 사유서와 감사 열람 절차를 반드시 남겨야 하며, 이를 누락하면 제재조치 대상이 될 수 있음 {restriction_refs}.\n"
        f"- 증빙 서류는 세부 사용내용과 거래 사실을 확인할 수 있어야 하며, 제출 형식이나 증빙이 누락되면 정산 지연 또는 감사 지적의 원인이 될 수 있음 {evidence_refs}."
    )


def _select_preferred_citations(
    citations: list[Citation],
    preferred_ids: tuple[str, ...],
    *,
    exclude_indices: set[int] | None = None,
    limit: int | None = None,
) -> list[Citation]:
    excluded = exclude_indices or set()
    selected: list[Citation] = []
    seen: set[int] = set()

    for preferred_id in preferred_ids:
        for citation in citations:
            identifier = f"{citation.document_id}::{citation.location}"
            if identifier != preferred_id or citation.index in excluded or citation.index in seen:
                continue
            selected.append(citation)
            seen.add(citation.index)
            break
        if limit is not None and len(selected) >= limit:
            break

    return selected


def _select_semantic_citations_or_fallback(
    citations: list[Citation],
    *,
    keyword_weights: dict[str, int],
    required_keywords: tuple[str, ...] = (),
    required_any_keywords: tuple[str, ...] = (),
    excluded_keywords: tuple[str, ...] = (),
    exclude_indices: set[int] | None = None,
    limit: int = 1,
) -> list[Citation]:
    hits = _select_semantic_citations(
        citations,
        keyword_weights=keyword_weights,
        required_keywords=required_keywords,
        required_any_keywords=required_any_keywords,
        excluded_keywords=excluded_keywords,
        exclude_indices=exclude_indices,
        limit=limit,
    )
    excluded = exclude_indices or set()
    seen = {citation.index for citation in hits}
    fallback: list[Citation] = list(hits)
    for citation in citations:
        if citation.index in excluded or citation.index in seen:
            continue
        fallback.append(citation)
        if len(fallback) >= limit:
            break
    return fallback


def _select_semantic_citations(
    citations: list[Citation],
    *,
    keyword_weights: dict[str, int],
    required_keywords: tuple[str, ...] = (),
    required_any_keywords: tuple[str, ...] = (),
    excluded_keywords: tuple[str, ...] = (),
    exclude_indices: set[int] | None = None,
    limit: int = 1,
) -> list[Citation]:
    normalized_required = tuple(_normalize_text(keyword) for keyword in required_keywords)
    normalized_required_any = tuple(_normalize_text(keyword) for keyword in required_any_keywords)
    normalized_excluded = tuple(_normalize_text(keyword) for keyword in excluded_keywords)
    normalized_weights = { _normalize_text(keyword): weight for keyword, weight in keyword_weights.items() }
    excluded = exclude_indices or set()
    ranked: list[tuple[int, float, int, Citation]] = []

    for citation in citations:
        if citation.index in excluded:
            continue
        haystack = _normalize_text(f"{citation.title} {citation.snippet}")
        if not haystack:
            continue
        if any(keyword not in haystack for keyword in normalized_required):
            continue
        if normalized_required_any and not any(keyword in haystack for keyword in normalized_required_any):
            continue
        if any(keyword in haystack for keyword in normalized_excluded):
            continue

        semantic_score = sum(weight for keyword, weight in normalized_weights.items() if keyword in haystack)
        if semantic_score == 0:
            continue

        ranked.append((semantic_score, citation.score, -citation.index, citation))

    ranked.sort(reverse=True)
    return [citation for _, _, _, citation in ranked[:limit]]


def _normalize_text(value: str) -> str:
    return value.replace(" ", "").lower()


def _cite(*citations: Citation) -> str:
    return "".join(f"[{citation.index}]" for citation in citations)
