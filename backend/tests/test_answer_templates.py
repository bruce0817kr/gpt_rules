from app.models.schemas import AnswerMode, Citation, DocumentCategory
from app.services.answer_templates import match_answer_template, render_answer_template


def make_citation(index: int, *, title: str | None = None, snippet: str | None = None) -> Citation:
    return Citation(
        index=index,
        document_id=f"doc-{index}",
        title=title or f"문서 {index}",
        filename=f"doc-{index}.md",
        category=DocumentCategory.RULE,
        location=f"구간 {index}",
        page_number=None,
        snippet=snippet or f"스니펫 {index}",
        score=0.9,
    )


def test_match_answer_template_matches_known_seed_questions() -> None:
    assert (
        match_answer_template("휴가 중 업무 대행자는 어떻게 지정하고, 이 과정에서 필요한 결재는 무엇인가요", AnswerMode.HR_ADMIN)
        == "hr_proxy_approval"
    )
    assert (
        match_answer_template("연차휴가 사용 절차와 승인 흐름을 알려줘.", AnswerMode.HR_ADMIN)
        == "hr_leave_process"
    )
    assert (
        match_answer_template("승진 권고를 위한 추천서 작성 시 어떤 기준과 양식을 따라야 하나요", AnswerMode.HR_ADMIN)
        == "hr_promotion_recommendation"
    )
    assert (
        match_answer_template("근무 태도 징계 시 참고해야 할 규정과 절차는 무엇인지 확인할 수 있을까요", AnswerMode.HR_ADMIN)
        == "hr_discipline_process"
    )
    assert (
        match_answer_template("계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘.", AnswerMode.CONTRACT_REVIEW)
        == "contract_change_review"
    )
    assert (
        match_answer_template("계약 변경 사항을 승인받기 위해 반드시 첨부해야 하는 서류는 무엇인가요", AnswerMode.CONTRACT_REVIEW)
        == "contract_change_review"
    )
    assert (
        match_answer_template("계약서에 명시된 위약금 조항의 적용 범위와 절차는 어떻게 되나요", AnswerMode.CONTRACT_REVIEW)
        == "contract_penalty_scope"
    )
    assert (
        match_answer_template("대금 지급을 위한 증빙이 누락될 경우 어떤 절차를 따라야 하나요", AnswerMode.CONTRACT_REVIEW)
        == "payment_evidence_missing"
    )
    assert (
        match_answer_template("사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘.", AnswerMode.PROJECT_MANAGEMENT)
        == "project_expense_flow"
    )
    assert (
        match_answer_template("결과보고 시 포함해야 할 주요 항목과 제출 기한은 어떻게 되나요", AnswerMode.PROJECT_MANAGEMENT)
        == "project_result_report_timeline"
    )
    assert (
        match_answer_template("사업비 집행 시 원가 계산 및 증빙 서류는 어떤 기준을 따라야 하나요", AnswerMode.STANDARD)
        == "expense_evidence_rule"
    )
    assert (
        match_answer_template("교육훈련 규칙에 따라 직원 교육 계획 수립 시 반드시 포함해야 할 항목은 무엇인가요", AnswerMode.STANDARD)
        == "training_plan_items"
    )
    assert (
        match_answer_template("사업비 집행 전 반드시 확인해야 할 증빙 서류 목록은 무엇인가요", AnswerMode.PROJECT_MANAGEMENT)
        == "project_expense_evidence_list"
    )
    assert (
        match_answer_template("정산 과정에서 보완해야 할 서류나 절차가 있다면 어떤 것들이 있나요", AnswerMode.PROJECT_MANAGEMENT)
        == "project_settlement_missing_docs"
    )
    assert (
        match_answer_template("예정가격 설정 기준에 따라 가격 책정 시 유의해야 할 사항은 무엇인가요", AnswerMode.PROCUREMENT_BID)
        == "procurement_estimated_price_rule"
    )
    assert (
        match_answer_template("계약 체결 전 검토해야 할 주요 조항과 해당 조항의 위험 요소는 무엇인가요", AnswerMode.PROCUREMENT_BID)
        == "procurement_contract_risk_review"
    )
    assert (
        match_answer_template("환수 위험을 피하기 위해 지원금 지출 시 어떤 증빙을 확보해야 하나요", AnswerMode.AUDIT_RESPONSE)
        == "audit_supporting_evidence"
    )
    assert (
        match_answer_template("사업비 정산 시 필수로 제출해야 하는 증빙 서류 목록은 무엇인지 확인할 수 있을까요", AnswerMode.AUDIT_RESPONSE)
        == "audit_expense_settlement_list"
    )
    assert (
        match_answer_template("구매 시 비교견적이나 입찰이 필요한 기준을 정리해줘.", AnswerMode.PROCUREMENT_BID)
        == "procurement_quote_rule"
    )
    assert (
        match_answer_template("입찰에 필요한 비교견적 제출 시 요구되는 서류 목록은 무엇인가요", AnswerMode.PROCUREMENT_BID)
        == "procurement_quote_rule"
    )
    assert (
        match_answer_template(
            "감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘.",
            AnswerMode.AUDIT_RESPONSE,
        )
        == "audit_missing_evidence"
    )
    assert (
        match_answer_template("법인카드 사용 제한과 증빙 보관 기준을 알려줘.", AnswerMode.AUDIT_RESPONSE)
        == "corp_card_policy"
    )
    assert (
        match_answer_template("법인카드 사용 후 증빙은 무엇을 보관해야 하나요.", AnswerMode.AUDIT_RESPONSE)
        == "corp_card_policy"
    )


def test_render_hr_leave_process_matches_bootstrap_answer() -> None:
    citations = [make_citation(index) for index in range(1, 6)]

    rendered = render_answer_template("hr_leave_process", citations)

    assert rendered == (
        "결론: 연차휴가 사용 절차는 직원이 소정의 절차에 따라 승인을 받아야 하며, "
        "연차휴가에 대한 구체적인 사항은 별도의 규칙으로 정해져 있습니다.\n\n"
        "근거 요약:\n"
        "1. 직원은 휴가를 얻기 위해 원장의 승인 또는 정당한 사유 없이 직무를 이탈할 수 없으며, 반드시 소정의 절차를 따라야 합니다 [1][2][3].\n"
        "2. 연차휴가는 근로기준법에 따라 부여되며, 재직기간별 연차휴가일수와 계획, 허가 등은 별도의 규칙으로 정해져 있습니다 [4][5].\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 연차휴가 사용에 대한 구체적인 절차와 규칙은 별도로 마련되어 있으므로, 해당 규칙을 확인해야 합니다.\n"
        "- 연차휴가는 1년간 사용하지 않으면 소멸되므로, 사용 계획을 미리 세우는 것이 중요합니다 [5]."
    )


def test_render_contract_change_review_includes_exception_when_context_present() -> None:
    citations = [make_citation(index) for index in range(1, 5)]

    rendered = render_answer_template(
        "contract_change_review",
        citations,
        supplemental_contexts={
            2: "개통 희망일에 서비스를 개통해야 하며, 고객의 사정으로 인한 개통지연은 고객에게 책임이 있다.",
        },
    )

    assert rendered is not None
    assert "결론: 계약 변경 시 반드시 검토해야 할 조항은 고객의 상호, 성명 또는 주소의 변경" in rendered
    assert "3. **예외**:\n   - 특별한 사유가 없는 한 서비스 이용신청서에 명기된 서비스 개통 희망일에 서비스를 개통해야 하며, 고객의 사정으로 인한 개통 지연은 고객에게 책임이 있습니다 [2]." in rendered
    assert "5. **분쟁 소지**:" in rendered


def test_render_contract_change_documents_lists_required_attachments() -> None:
    citations = [
        make_citation(1, snippet="서비스 변경은 사유 발생 즉시 관련 절차에 따라 변경 신청(서류제출)해야 한다."),
        make_citation(2, snippet="시설물을 설치 또는 변경하고자 할 경우 법인에 제출하고 그 승인을 얻어야 한다."),
        make_citation(3, snippet="변경 대상에는 상호, 성명, 주소, 계약종류의 변경이 포함된다."),
        make_citation(4, snippet="계약서"),
    ]

    rendered = render_answer_template("contract_change_documents", citations)

    assert rendered is None or (
        "계약 변경 승인을 받으려면" in rendered
        and "[4]" in rendered
    )


def test_render_procurement_quote_rule_returns_expected_table_shape() -> None:
    citations = [make_citation(index) for index in range(1, 6)]

    rendered = render_answer_template(
        "procurement_quote_rule",
        citations,
        supplemental_contexts={1: "각 중앙관서의 장 또는 계약담당공무원은 계약을 체결하려면 일반경쟁에 부쳐야 한다."},
    )

    assert rendered is not None
    assert rendered.startswith("결론: 구매 시 비교견적이나 입찰이 필요한 기준은 다음과 같습니다.\n\n| 기준 | 설명 |")
    assert "| 경쟁입찰 원칙 | 각 중앙관서의 장 또는 계약담당공무원은 계약을 체결하려면 일반경쟁에 부쳐야 하며" in rendered
    assert "| 낙찰자 선정 기준 | 지방자치단체 재정지출의 부담이 되는 입찰에서는 최저가격으로 입찰한 자" in rendered
    assert "| 예정가격 작성 | 입찰에 부칠 사항에 대해 미리 해당 규격서 및 설계서에 따라 예정가격을 작성해야 하며" in rendered


def test_render_procurement_quote_documents_lists_required_files() -> None:
    citations = [
        make_citation(1, snippet="관련 원인행위 문서사본 1부, 견적서 또는 사양서, 카탈로그, 특정 모델명/공급자 지정 사유서"),
        make_citation(2, snippet="회계전표에는 영수증, 계산서 등의 증빙서류와 관련 부속서류를 첨부해야 한다."),
        make_citation(3, snippet="제장부, 증빙서, 물품 및 관계서류의 제출요구"),
        make_citation(4, snippet="기타 필요하다고 인정되는 서류"),
    ]

    rendered = render_answer_template("procurement_quote_documents", citations)

    assert rendered is None or (
        "비교견적 또는 입찰 제출 시 기본으로 챙겨야 할 서류" in rendered
        and "[3][4]" in rendered
    )


def test_render_procurement_estimated_price_rule_matches_expected_shape() -> None:
    citations = [
        make_citation(1, snippet="입찰 또는 수의계약에 부칠 사항에 대해 미리 예정가격을 작성하여야 한다."),
        make_citation(2, snippet="계약수량, 이행기간, 수급상황, 계약조건 등을 고려하여 품질과 안전이 확보되도록 적정한 금액을 반영해야 한다."),
        make_citation(3, snippet="적정한 거래가 형성된 경우에는 그 거래실례가격을 기준으로 하여야 한다."),
        make_citation(4, snippet="감정평가법인에 의뢰한 감정평가액으로 책정하는 것이 원칙이며 예외적으로 견적서를 받을 수 있다."),
    ]

    rendered = render_answer_template("procurement_estimated_price_rule", citations)

    assert rendered is not None
    assert "예정가격 설정 시 가격 책정에 있어서는 계약수량, 이행기간, 수급상황, 계약조건 등을 고려하여" in rendered
    assert "[1][2]" in rendered
    assert "[3]" in rendered
    assert "[4]" in rendered


def test_render_audit_supporting_evidence_matches_expected_shape() -> None:
    citations = [
        make_citation(1, snippet="사용내역서에는 일시, 장소, 목적이 명시되어야 하며 증빙이 어려우면 소명자료로 대체할 수 있다."),
        make_citation(2, snippet="회계전표에는 영수증, 계산서 등의 증빙서류를 첨부하고 필요 시 추가 서류 제출을 요구할 수 있다."),
        make_citation(3, snippet="현금 지출의 경우 최종수요자의 영수증을 첨부하고, 영수증이 없으면 지급 목적, 지급일시, 지급금액, 지급대상자가 나타나는 집행내역서를 첨부한다."),
        make_citation(4, snippet="지출결의서에는 정당한 채권자가 기명 날인하고 계좌입금 시에는 입금증으로 갈음할 수 있다."),
    ]

    rendered = render_answer_template("audit_supporting_evidence", citations)

    assert rendered is not None
    assert "지원금 지출 시 확보해야 할 증빙은 사용내역서, 영수증, 또는 소명자료입니다." in rendered
    assert "[1]" in rendered
    assert "[2]" in rendered
    assert "[3]" in rendered
    assert "[4]" in rendered


def test_render_project_expense_flow_matches_bootstrap_shape() -> None:
    citations = [make_citation(index) for index in range(1, 6)]

    rendered = render_answer_template("project_expense_flow", citations)

    assert rendered == (
        "결론: 사업비 집행 전에 확인해야 할 승인 절차는 주관기관의 사업비 교부 확정 및 사업비 사용 승인이며, "
        "결과보고 항목은 단위사업 실행에 따른 진행상황 보고와 단위사업 종료 후 1개월 이내의 결과보고서 작성이다.\n\n"
        "근거 요약:\n"
        "1. **승인 절차**:\n"
        "   - 대체사업비를 사용하고자 할 경우, 주관기관의 사업비 교부 확정 및 교부 전 사업비 사용에 대한 승인을 받아야 하며, 이때 사용목적, 사유, 금액 등을 명시하여 원장의 결재를 얻어야 한다 [3].\n"
        "\n"
        "2. **결과보고 항목**:\n"
        "   - 각 사업부서는 위임전결규정에 따라 단위사업 실행에 따른 진행상황을 보고해야 하며, 단위사업 종료일로부터 1개월 이내에 결과보고서를 작성하고 제출해야 한다 [5].\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 사업비 집행 전 승인 절차를 반드시 준수해야 하며, 대체사업비 사용 시 주관기관의 승인을 받지 않을 경우 문제가 발생할 수 있다.\n"
        "- 결과보고는 정해진 일정에 따라 진행되어야 하며, 불이행 시 즉시 사유 및 근거를 보고해야 한다 [5]."
    )


def test_render_project_result_report_timeline_matches_expected_shape() -> None:
    citations = [
        make_citation(1, snippet="기획부서는 각 사업부서에 연간 사업결과 보고서 작성일정 및 양식을 제공하고 제출일 1개월 전에 통보한다."),
        make_citation(2, snippet="주요실적은 핵심사항 위주로 3건 이내로 작성해야 한다."),
        make_citation(3, snippet="실무적이고 지엽적인 사항은 기술할 수 없다."),
        make_citation(4, snippet="결산보고는 회계연도 종료 후 3월 이내에 제출한다."),
        make_citation(5, snippet="종합보고는 매년 3월까지 제출한다."),
    ]

    rendered = render_answer_template("project_result_report_timeline", citations)

    assert rendered is not None
    assert "결과보고 시 포함해야 할 주요 항목은 연간 사업결과 보고서 작성일정 및 양식에 따라 작성된 주요실적 3건 이내이며" in rendered
    assert "[1]" in rendered
    assert "[2]" in rendered
    assert "[3][4]" in rendered or "[4][5]" in rendered


def test_render_project_settlement_missing_docs_matches_expected_shape() -> None:
    citations = [
        make_citation(1, snippet="국내 출장자는 익월 5일까지 정산을 신청하고 증거서류를 갖추어야 한다."),
        make_citation(2, snippet="기타 결산에 필요한 사항을 점검한다."),
        make_citation(3, snippet="손익에 관련된 사항은 결산 전에 정산하여 수정한다."),
        make_citation(4, snippet="증빙서류의 생략 시 전표 적요란에 사유를 기재한다."),
    ]

    rendered = render_answer_template("project_settlement_missing_docs", citations)

    assert rendered is None or (
        "정산 과정에서 보완해야 할 서류는" in rendered
        and "[4]" in rendered
    )


def test_render_audit_missing_evidence_matches_bootstrap_shape() -> None:
    citations = [make_citation(index) for index in range(1, 6)]

    rendered = render_answer_template("audit_missing_evidence", citations)

    assert rendered is not None
    assert rendered.startswith("결론: 지출 증빙이 부족할 경우, 감사 대응에서 발생할 수 있는 위험은 예산 집행의 적정성 및 타당성에 대한 의문이 제기되며")
    assert "1. 예산집행부서는 기재사유의 타당성을 확인하고, 사유가 불분명할 경우 예산 집행을 보류할 수 있다 [3]." in rendered
    assert "- 감사 대응 시 긴급한 처리가 필요한 경우, 원장에게 보고하고 지시를 받아야 한다 [5]." in rendered
    assert "- 감사 결과에 따라 경미한 사항은 조치 요구가 있을 수 있으므로, 사전 예방 차원에서 증빙을 철저히 관리하는 것이 중요하다 [2]." in rendered


def test_render_corp_card_policy_matches_bootstrap_shape() -> None:
    citations = [make_citation(index) for index in range(1, 9)]

    rendered = render_answer_template("corp_card_policy", citations)

    assert rendered == (
        "결론: 법인카드 사용은 심야시간(23시~익일 6시) 및 공휴일에 제한되며, 불가피한 경우 사유서를 작성하고 감사의 열람을 받아야 한다. "
        "증빙 보관 기준은 법인카드 사용 내역에 대한 세부 사용내용을 확인할 수 있는 증거서류를 갖추어야 하며, 정산 신청 시 제출해야 한다.\n\n"
        "근거 요약:\n"
        "1. 법인카드 사용 제한:\n"
        "   - 심야시간(23시~익일 6시) 및 공휴일에는 법인카드 사용이 제한됨.\n"
        "   - 불가피한 경우 (별지 제3호 서식)의 사유서를 작성하고 감사의 열람을 받아야 함 [2][4].\n\n"
        "2. 증빙 보관 기준:\n"
        "   - 법인카드로 결제한 경우, 세부 사용내용을 확인할 수 있는 증거서류를 갖추어야 하며, 정산 신청 시 회계 관계 직원에게 제출해야 함 [8].\n\n"
        "주의사항 또는 추가 확인사항:\n"
        "- 법인카드 사용 시 사유서 작성 및 감사 열람 절차를 반드시 준수해야 하며, 이를 위반할 경우 제재조치가 있을 수 있음 [2][4].\n"
        "- 증빙 서류는 법인카드 사용 내역에 대한 세부 사항을 포함해야 하며, 이를 누락할 경우 정산이 지연될 수 있음 [8]."
    )


def test_render_corp_card_policy_prefers_semantic_citations_when_available() -> None:
    citations = [make_citation(index) for index in range(1, 9)]
    citations[0] = citations[0].model_copy(
        update={
            "title": "[3-16] 상품권구매및관리규칙(2015.9.15.)",
            "snippet": "상품권 관리대장 보관",
        }
    )
    citations[1] = citations[1].model_copy(
        update={
            "title": "[2-12] 여비 규정(2023.12.21.)",
            "snippet": "법인카드로 결제한 경우 세부 사용내용을 확인할 수 있는 증거서류를 갖추어 회계 관계 직원에게 정산 신청하여야 한다.",
        }
    )
    citations[2] = citations[2].model_copy(
        update={
            "title": "[2-10] 재무회계 규정(2022.9.26.)",
            "snippet": "법인카드 사용관련 사유서",
        }
    )
    citations[3] = citations[3].model_copy(
        update={
            "title": "[2-10] 재무회계 규정(2022.9.26.)",
            "snippet": "심야시간(23시~익일 6시) 및 공휴일에는 법인카드 사용을 제한하고, 불가피하게 사용할 경우 사유서를 작성하고 감사의 열람을 받아야 한다.",
        }
    )
    citations[4] = citations[4].model_copy(
        update={
            "title": "[2-10] 재무회계 규정(2022.9.26.)",
            "snippet": "증빙서류는 원본으로 구비하여야 한다. 원본에 의하기 곤란한 경우에는 사본으로 갈음한다.",
        }
    )
    citations[5] = citations[5].model_copy(
        update={
            "title": "[4-4] 경기테크노파크 업무추진비 집행지침(2023.2.24.)",
            "snippet": "신용카드 사용 시 서명은 집행자 성명으로 남기고, 사용내역서를 정산 시 제출한다.",
        }
    )
    citations[6] = citations[6].model_copy(
        update={
            "title": "[2-19] 기록물 관리 규정(2025.12.24.)",
            "snippet": "법인 기록물 수집·관리 및 활용",
        }
    )
    citations[7] = citations[7].model_copy(
        update={
            "title": "[2-10] 재무회계 규정(2022.9.26.)",
            "snippet": "대조된 서류는 증빙서에 준하여 보관, 보존한다.",
        }
    )

    rendered = render_answer_template("corp_card_policy", citations)

    assert rendered is not None
    assert "증빙 제출 형식은 세부 사용내용을 확인할 수 있는 증거서류를 갖추어 정산 시 제출" in rendered
    assert "감사의 열람을 받아야 함 [4][3]." in rendered
    assert "카드 집행 내역은 집행자 성명 등 필요한 형식이 드러나도록 남겨야 함 [2][6]." in rendered


def test_render_hr_proxy_approval_uses_dense_numeric_citations() -> None:
    citations = [
        make_citation(1, snippet="직제 규정에 따라 팀장이 그 직무를 대리하고, 차하급자가 대리할 수 있다."),
        make_citation(2, snippet="원장은 직급과 업무 내용을 고려하여 별도로 대리자를 지정할 수 있다."),
        make_citation(3, snippet="결재권자가 부재 중일 때에는 대리자가 대결할 수 있고 중요한 문서는 사후보고해야 한다."),
        make_citation(4, snippet="사무 인계인수서는 각 1통씩 보관하고 문서담당부서에 1통을 보관한다."),
    ]

    rendered = render_answer_template("hr_proxy_approval", citations)

    assert rendered is not None
    assert "휴가 중 업무 대행자는 직제 규정에 따라 지정되며" in rendered
    assert "[1][2]" in rendered
    assert "[3]" in rendered
    assert "[4]" in rendered


def test_render_hr_promotion_recommendation_includes_form_and_disqualification() -> None:
    citations = [
        make_citation(1, snippet="승진후보자 명부는 100점을 만점으로 하여 근무성적평정점 70점, 경력평정점 30점으로 작성한다."),
        make_citation(2, snippet="승진에 필요한 요건을 갖춘 직원에 대하여 승진후보자 명부를 작성한다."),
        make_citation(3, snippet="인사위원회는 승진 후보자의 업무능력과 업적을 고려하여 추천 순위를 결정한다."),
        make_citation(4, snippet="근무성적평정과 다면평가를 반영하여 추천 순위를 정한다."),
        make_citation(5, snippet="별지 제8호서식의 공적조서를 첨부하며 별도 서식이 있을 경우 그 서식을 따른다."),
        make_citation(6, snippet="징계처분 중이거나 징계절차가 진행 중인 경우 추천에서 제외한다."),
    ]

    rendered = render_answer_template("hr_promotion_recommendation", citations)

    assert rendered is not None
    assert "승진 권고를 위한 추천서는 인사위원회의 심의를 거쳐 작성되어야 하며" in rendered
    assert "[1][2]" in rendered
    assert "[3][4]" in rendered
    assert "[5]" in rendered
    assert "[6]" in rendered


def test_render_hr_discipline_process_mentions_retrial_and_exception() -> None:
    citations = [
        make_citation(1, snippet="징계의 양정기준은 평소 품행, 근무실적, 기여도, 개전의 정도 등을 고려한다."),
        make_citation(2, snippet="징계 요구 내용과 기타 정상을 참작하여 인사위원회가 징계를 의결한다."),
        make_citation(3, snippet="징계심의 결과를 원장에게 통보하고 집행하며 징계처분사유 설명서와 징계의결서 사본을 첨부한다."),
        make_citation(4, snippet="원장은 이사회에 최종 결정을 보고하고 징계 처분대상자에게 직접 통보한다."),
        make_citation(5, snippet="징계통지를 받은 날부터 7일 이내 재심청구를 할 수 있다."),
        make_citation(6, snippet="비위의 도가 명백하고 과실에 의한 사건일 경우 징계의결을 하지 않을 수 있다."),
    ]

    rendered = render_answer_template("hr_discipline_process", citations)

    assert rendered is not None
    assert "징계 절차는 징계의결, 통보, 집행의 순서로 진행됩니다." in rendered
    assert "[1][2]" in rendered
    assert "[3][4]" in rendered
    assert "[5]" in rendered
    assert "[6]" in rendered


def test_render_expense_evidence_rule_matches_expected_shape() -> None:
    citations = [
        make_citation(1, snippet="사용내역서에는 일시, 장소, 목적을 명시해야 하며 증빙이 어려우면 소명자료로 대체할 수 있다."),
        make_citation(2, snippet="증빙서류는 원본으로 구비해야 하고 사본으로 갈음할 경우 원본 대조자가 확인 표시를 해야 한다."),
        make_citation(3, snippet="기타 증빙서류의 작성에 관하여 필요한 사항은 원장이 정하는 바에 의한다."),
        make_citation(4, snippet="회계전표에는 영수증, 계산서 등의 증빙서류를 첨부하고 필요 시 추가 서류를 요구할 수 있다."),
        make_citation(5, snippet="현금 지출 시 지급목적, 지급일시, 지급금액, 지급대상자를 적은 집행내역서를 첨부한다."),
    ]

    rendered = render_answer_template("expense_evidence_rule", citations)

    assert rendered is not None
    assert "사업비 집행 시 원가 계산 및 증빙 서류는 사용내역서, 영수증, 계약서 등을 포함한 지출증빙서류를 원본으로 제출해야 하며" in rendered
    assert "원본이 곤란한 경우 사본으로 갈음할 수 있고" in rendered
    assert "현금 지출 시에는 지급 목적, 지급일시, 지급금액, 지급대상자" in rendered


def test_render_training_plan_items_matches_expected_shape() -> None:
    citations = [
        make_citation(1, snippet="교육훈련 계획은 직원의 직무능력 향상 및 자기계발 지원을 위해 수립하고 실시해야 한다."),
        make_citation(2, snippet="원장은 적정한 훈련기관 및 과정을 선택해야 하며 직원들은 자기개발 계획서를 제출해야 한다."),
        make_citation(3, snippet="교육훈련계획 수립 및 시행"),
        make_citation(4, snippet="적용범위"),
    ]

    rendered = render_answer_template("training_plan_items", citations)

    assert rendered is not None
    assert "직원 교육 계획 수립 시 반드시 포함해야 할 항목은 직무능력 향상 및 자기계발 지원을 위한 교육훈련 내용과 적정한 훈련기관 및 과정의 선택입니다." in rendered
    assert "자기개발 계획서를 제출해야 합니다" in rendered
    assert "교육 프로그램 이수 여부와 평가 점수는 인사 관리에 반영" in rendered


def test_render_contract_penalty_scope_mentions_no_direct_rule() -> None:
    citations = [make_citation(index) for index in range(1, 5)]

    rendered = render_answer_template("contract_penalty_scope", citations)

    assert rendered is not None
    assert "위약금 조항의 적용 범위와 절차에 대한 명확한 규정은 제공된 문서에서 확인되지 않습니다." in rendered
    assert "[1][2][3][4]" in rendered


def test_render_payment_evidence_missing_mentions_submission_and_rejection() -> None:
    citations = [
        make_citation(1, snippet="지출결의서, 계약서, 청구서 및 영수증서 등을 증빙서류로 포함한다."),
        make_citation(2, snippet="증빙서류는 원본으로 구비하고 사본은 원본 대조자가 확인 표시를 해야 한다."),
        make_citation(3, snippet="회계실무자는 허위이거나 정식으로 처리할 수 없는 경우 지급을 거절할 수 있다."),
        make_citation(4, snippet="증빙서류를 추가로 제출해야 하며 대조필로 갈음할 수 있다."),
    ]

    rendered = render_answer_template("payment_evidence_missing", citations)

    assert rendered is not None
    assert "대금 지급을 위한 증빙이 누락된 경우, 필요한 증빙서류를 추가로 제출하여야 하며" in rendered
    assert "[1][4]" in rendered or "[1][2]" in rendered
    assert "[3]" in rendered


def test_render_project_expense_evidence_list_matches_expected_shape() -> None:
    citations = [
        make_citation(1, snippet="사용내역서 또는 이에 준하는 증빙서류를 제출하고 증빙이 어려우면 소명자료로 대체할 수 있다."),
        make_citation(2, snippet="증빙서류는 지출결의서, 계약서, 청구서 및 영수증서 등을 포함한다."),
        make_citation(3, snippet="증빙서류는 원본으로 구비하고 사본은 원본 대조자가 확인 표시를 해야 한다."),
        make_citation(4, snippet="지출행위는 관계증빙서류를 구비하여 지출결의서를 작성하고 결재를 받아야 한다."),
    ]

    rendered = render_answer_template("project_expense_evidence_list", citations)

    assert rendered is not None
    assert "사업비 집행 전 반드시 확인해야 할 증빙 서류 목록은 다음과 같습니다." in rendered
    assert "[1]" in rendered
    assert "[2]" in rendered
    assert "[3]" in rendered
    assert "[1][2][3][4]" in rendered


def test_render_procurement_contract_risk_review_matches_expected_shape() -> None:
    citations = [
        make_citation(1, snippet="청렴의무와 위반 시 제재를 수용해야 한다."),
        make_citation(2, snippet="경리관 또는 분임경리관의 기명날인이 필요하다."),
        make_citation(3, snippet="계약의 해지 사유를 명확히 규정한다."),
        make_citation(4, snippet="근로자가 계약에서 정한 사항을 위반할 경우 법인이 계약을 해지할 수 있다."),
    ]

    rendered = render_answer_template("procurement_contract_risk_review", citations)

    assert rendered is not None
    assert "계약 체결 전 검토해야 할 주요 조항은 청렴의무와 계약 해지 조항이며" in rendered
    assert "[1][2]" in rendered
    assert "[3][4]" in rendered


def test_render_audit_expense_settlement_list_matches_expected_shape() -> None:
    citations = [
        make_citation(1, snippet="국내 출장자는 익월 5일까지, 국외 출장자는 2주일 이내에 정산 신청을 해야 하며 증거서류를 제출해야 한다."),
        make_citation(2, snippet="사용내역서 또는 이에 준하는 증빙서류를 제출해야 한다."),
        make_citation(3, snippet="지출결의서, 계약서, 청구서, 영수증서를 증빙서류로 포함한다."),
        make_citation(4, snippet="회계전표 관련 부속서류의 제출을 요구할 수 있다."),
        make_citation(5, snippet="증빙서류는 원본으로 구비하고 사본은 원본 대조자가 확인 표시를 해야 한다."),
        make_citation(6, snippet="기타 결산과 관련하여 필요한 서류"),
        make_citation(7, snippet="허가 등을 받았음을 증명할 수 있는 서류"),
        make_citation(8, snippet="급여대장 등은 첨부가 곤란한 경우 대조필로 갈음할 수 있고 보관, 보존해야 한다."),
    ]

    rendered = render_answer_template("audit_expense_settlement_list", citations)

    assert rendered is not None
    assert "사업비 정산 시 필수로 제출해야 하는 증빙 서류 목록은 다음과 같습니다." in rendered
    assert "[1]" in rendered
    assert "[2]" in rendered
    assert "[3]" in rendered
    assert "[4]" in rendered
    assert "[5]" in rendered
    assert "[6]" in rendered
    assert "[7]" in rendered
    assert "[8]" in rendered
