# Gold Review Summary goldbatch_20260312_1116_finance_officer

- Candidate file: `/app/data/autorag/candidates/candidate_cases_finance_officer_goldbatch_20260312_1116_finance_officer.json`
- Review queue: `/app/data/autorag/review/review_queue_goldbatch_20260312_1116_finance_officer.json`
- Total candidates: 18
- Suggested `review_new`: 16
- Suggested `review_edit`: 2
- Suggested `merge_or_skip`: 0

## Review Guide

- `review_new`: seed 질문과 겹침이 낮아 새 gold 후보로 우선 검토할 만한 질문
- `review_edit`: 일부 중복/표현 겹침이 있어 wording 조정 후 유지할 가능성이 높은 질문
- `merge_or_skip`: seed 또는 다른 후보와 매우 비슷해 통합 검토가 필요한 질문

## audit_response

- `finance_officer_audit_response_01_027b1741` [review_edit] 법인카드 사용 시 필수적인 증빙 서류의 종류와 각각의 원본 보관 기준은 무엇인가요
  categories=['rule', 'guide'] note=증빙이 부족할 경우 환수 위험을 피하기 위한 필수 정보입니다.
  seed_overlap=0.3833 seed_target=corp_card_policy: 법인카드 사용 제한과 증빙 보관 기준을 알려줘
  peer_overlap=0.5385 peer_target=finance_officer_standard_01_7c6d867c: 정산 신청을 위한 증빙 서류의 종류와 각각의 원본 보관 기준은 어떻게 되나요
  shared_keywords(seed)=['법인카드', '보관', '사용', '증빙'] shared_keywords(peer)=['각각의', '기준은', '보관', '서류의', '원본', '종류와', '증빙']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 219; [2-10] 재무회계 규정(2022.9.26.) / 구간 363
- `finance_officer_audit_response_02_ece74e4d` [review_new] 감사 대응을 위해 필요한 자료는 어떤 것이며, 보완이 가능한 부분은 무엇인지 알고 싶습니다
  categories=['guide', 'rule'] note=감사 지적 시 대응력을 높이기 위한 사전 준비가 필수적입니다.
  seed_overlap=0.2722 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.1553 peer_target=finance_officer_audit_response_04_4ca30bd9: 사업비 정산 시 어떤 증빙 서류가 필요하며, 추가적인 자료 보완이 가능한가요
  shared_keywords(seed)=['감사', '대응을', '어떤', '위해'] shared_keywords(peer)=['보완이', '어떤']
  bootstrap_titles=[2-3] 감사 규정(2021.09.28.) / 구간 33; [3-34] 적극행정지원 규칙(2024.02.21.) / 구간 18
- `finance_officer_audit_response_03_8cbb59c1` [review_new] 정산 신청 기한을 놓쳤을 때 필요한 조치와 그에 따른 환수 위험은 무엇인지 알고 싶습니다
  categories=['rule', 'guide'] note=정산 기한을 준수하지 않으면 발생할 수 있는 문제를 예방하기 위함입니다.
  seed_overlap=0.0500 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.1500 peer_target=finance_officer_audit_response_02_ece74e4d: 감사 대응을 위해 필요한 자료는 어떤 것이며, 보완이 가능한 부분은 무엇인지 알고 싶습니다
  shared_keywords(seed)=[] shared_keywords(peer)=['싶습니다', '알고']
  bootstrap_titles=[2-12] 여비 규정(2023.12.21.) / 구간 12
- `finance_officer_audit_response_04_4ca30bd9` [review_new] 사업비 정산 시 어떤 증빙 서류가 필요하며, 추가적인 자료 보완이 가능한가요
  categories=['guide', 'rule'] note=정확한 증빙 준비로 감사 리스크를 줄이기 위한 질문입니다.
  seed_overlap=0.1167 seed_target=corp_card_policy: 법인카드 사용 제한과 증빙 보관 기준을 알려줘
  peer_overlap=0.1667 peer_target=finance_officer_project_management_01_7ddece88: 사업비 정산 시 꼭 제출해야 하는 증빙 서류의 구체적인 종류와 각 서류의 원본 보관 기준이 무엇인가요
  shared_keywords(seed)=['증빙'] shared_keywords(peer)=['사업비', '정산', '증빙']
  bootstrap_titles=[4-4] 경기테크노파크 업무추진비 집행지침(2023.2.24.) / 구간 10; [2-12] 여비 규정(2023.12.21.) / 구간 12

## contract_review

- `finance_officer_contract_review_01_8a6dbfe4` [review_new] 계약 해지 시 위약금 규정에 대해 어떤 점을 반드시 검토해야 하나요
  categories=['rule', 'law'] note=위약금 관련 체크가 필요해 계약 리스크를 줄일 수 있습니다.
  seed_overlap=0.2038 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.2643 peer_target=finance_officer_contract_review_03_911af52f: 계약 변경 후 책임 분기와 관련된 사항을 어떻게 검토해야 하나요
  shared_keywords(seed)=['검토해야', '계약'] shared_keywords(peer)=['검토해야', '계약', '하나요']
  bootstrap_titles=지방자치단체를 당사자로 하는 계약에 관한 법률 / 구간 5; 근로기준법 / 구간 5
- `finance_officer_contract_review_02_1471a79b` [review_new] 대금 지급을 위한 서류 누락 시 어떤 절차를 따라야 하나요
  categories=['guide', 'rule'] note=서류 누락 문제를 사전에 방지하고 분쟁을 예방하기 위해 중요합니다.
  seed_overlap=0.0588 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.2000 peer_target=finance_officer_project_management_02_d641e979: 정산 기한이 다가왔을 때 미비된 사항이 있으면 어떤 절차를 통해 해결해야 하나요
  shared_keywords(seed)=['어떤'] shared_keywords(peer)=['어떤', '절차를', '하나요']
  bootstrap_titles=[3-10] 위원회 수당 등 지급 규칙(2025.6.19.) / 구간 20; [2-10] 재무회계 규정(2022.9.26.) / 구간 82
- `finance_officer_contract_review_03_911af52f` [review_new] 계약 변경 후 책임 분기와 관련된 사항을 어떻게 검토해야 하나요
  categories=['law', 'guide'] note=책임 분기를 명확히 하여 향후 분쟁을 예방하는 데 필요합니다.
  seed_overlap=0.3227 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.2643 peer_target=finance_officer_contract_review_01_8a6dbfe4: 계약 해지 시 위약금 규정에 대해 어떤 점을 반드시 검토해야 하나요
  shared_keywords(seed)=['검토해야', '계약', '변경'] shared_keywords(peer)=['검토해야', '계약', '하나요']
  bootstrap_titles=건설산업기본법 / 구간 5; 지방자치단체를 당사자로 하는 계약에 관한 법률 / 구간 5

## hr_admin

- `finance_officer_hr_admin_01_d577dec5` [review_new] 휴가 신청 시 필요한 서류와 그 제출 기한은 어떻게 되나요
  categories=['rule', 'guide'] note=서류 준비 및 기한 준수가 중요한 업무 프로세스입니다.
  seed_overlap=0.0500 seed_target=hr_promotion_years: 직급별 승진 소요년수를 표로 정리해줘
  peer_overlap=0.2222 peer_target=finance_officer_project_management_03_852bde30: 사업비 집행 후 결과보고를 위해 준비해야 할 서류와 그 제출 기한은 어떻게 되나요
  shared_keywords(seed)=[] shared_keywords(peer)=['기한은', '서류와']
  bootstrap_titles=[2-4] 인사 관리 규정(2025.10.24.) / 구간 199; [3-25] 공무직 근로자 관리규칙(2026.1.2.) / 구간 144
- `finance_officer_hr_admin_02_bbfb36fd` [review_new] 승진 신청에 필요한 평가 기준과 서류는 무엇인지 알려줄 수 있나요
  categories=['rule', 'guide'] note=승진 절차의 명확한 이해가 요구됩니다.
  seed_overlap=0.1611 seed_target=hr_promotion_years: 직급별 승진 소요년수를 표로 정리해줘
  peer_overlap=0.0909 peer_target=finance_officer_procurement_bid_02_790a52bc: 예정가격 산정 시 참고해야 할 법적 기준과 가이드라인은 무엇인가요
  shared_keywords(seed)=['승진'] shared_keywords(peer)=['기준과']
  bootstrap_titles=[3-5] 인사 관리 규칙(2026.1.23.) / 구간 114; [3-5] 인사 관리 규칙(2026.1.23.) / 구간 113
- `finance_officer_hr_admin_03_8b5d7c90` [review_new] 징계 절차에서 필요한 증거 자료와 그 보완 가능성은 어떤 것이 있나요
  categories=['rule', 'guide', 'law'] note=징계 관련 법적 요건을 충족하는 것이 중요합니다.
  seed_overlap=0.2038 seed_target=hr_discipline_notice: 징계 절차에서 사전 통지와 소명 기회가 필요한지 알려줘
  peer_overlap=0.0769 peer_target=finance_officer_procurement_bid_03_d21de556: 계약 체결 시 반드시 확인해야 할 계약서의 주요 항목은 어떤 것들이 있나요
  shared_keywords(seed)=['절차에서', '징계'] shared_keywords(peer)=['어떤']
  bootstrap_titles=[3-5] 인사 관리 규칙(2026.1.23.) / 구간 189; [3-18] 취업규칙(2026.1.1.) / 구간 192

## procurement_bid

- `finance_officer_procurement_bid_01_67913b0c` [review_new] 입찰을 진행하기 전에 검토해야 할 비교견적의 기준은 무엇인가요
  categories=['rule', 'guide'] note=정확한 비교견적 기준이 없으면 입찰이 부적합할 수 있다.
  seed_overlap=0.0909 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.0769 peer_target=finance_officer_contract_review_03_911af52f: 계약 변경 후 책임 분기와 관련된 사항을 어떻게 검토해야 하나요
  shared_keywords(seed)=['검토해야'] shared_keywords(peer)=['검토해야']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 301; [4-10] 편의시설 선정 지침(2024.07.02.) / 구간 8
- `finance_officer_procurement_bid_02_790a52bc` [review_new] 예정가격 산정 시 참고해야 할 법적 기준과 가이드라인은 무엇인가요
  categories=['law', 'guide'] note=정확한 예정가격 산정은 불필요한 비용 지출을 방지할 수 있다.
  seed_overlap=0.0500 seed_target=procurement_quote_rule: 구매 시 비교견적이나 입찰이 필요한 기준을 정리해줘
  peer_overlap=0.0909 peer_target=finance_officer_hr_admin_02_bbfb36fd: 승진 신청에 필요한 평가 기준과 서류는 무엇인지 알려줄 수 있나요
  shared_keywords(seed)=[] shared_keywords(peer)=['기준과']
  bootstrap_titles=국가를 당사자로 하는 계약에 관한 법률 / 구간 110; 국가를 당사자로 하는 계약에 관한 법률 / 구간 109
- `finance_officer_procurement_bid_03_d21de556` [review_new] 계약 체결 시 반드시 확인해야 할 계약서의 주요 항목은 어떤 것들이 있나요
  categories=['rule', 'guide'] note=계약서의 주요 항목을 놓치면 법적 문제가 발생할 수 있다.
  seed_overlap=0.0909 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.1538 peer_target=finance_officer_contract_review_01_8a6dbfe4: 계약 해지 시 위약금 규정에 대해 어떤 점을 반드시 검토해야 하나요
  shared_keywords(seed)=['계약'] shared_keywords(peer)=['계약', '어떤']
  bootstrap_titles=[3-25] 공무직 근로자 관리규칙(2026.1.2.) / 구간 615; [3-25] 공무직 근로자 관리규칙(2026.1.2.) / 구간 583

## project_management

- `finance_officer_project_management_01_7ddece88` [review_new] 사업비 정산 시 꼭 제출해야 하는 증빙 서류의 구체적인 종류와 각 서류의 원본 보관 기준이 무엇인가요
  categories=['rule', 'guide'] note=정확한 증빙 서류 제출로 감사 대응에 도움이 필요하기 때문.
  seed_overlap=0.1333 seed_target=corp_card_policy: 법인카드 사용 제한과 증빙 보관 기준을 알려줘
  peer_overlap=0.4000 peer_target=finance_officer_standard_01_7c6d867c: 정산 신청을 위한 증빙 서류의 종류와 각각의 원본 보관 기준은 어떻게 되나요
  shared_keywords(seed)=['보관', '증빙'] shared_keywords(peer)=['보관', '서류의', '원본', '정산', '종류와', '증빙']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 70; [2-10] 재무회계 규정(2022.9.26.) / 구간 69
- `finance_officer_project_management_02_d641e979` [review_new] 정산 기한이 다가왔을 때 미비된 사항이 있으면 어떤 절차를 통해 해결해야 하나요
  categories=['rule', 'guide', 'notice'] note=기한 준수를 통해 불이익을 피하기 위한 실무적인 질문.
  seed_overlap=0.0500 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.2000 peer_target=finance_officer_contract_review_02_1471a79b: 대금 지급을 위한 서류 누락 시 어떤 절차를 따라야 하나요
  shared_keywords(seed)=[] shared_keywords(peer)=['어떤', '절차를', '하나요']
  bootstrap_titles=[2-12] 여비 규정(2023.12.21.) / 구간 12; [2-10] 재무회계 규정(2022.9.26.) / 구간 276
- `finance_officer_project_management_03_852bde30` [review_new] 사업비 집행 후 결과보고를 위해 준비해야 할 서류와 그 제출 기한은 어떻게 되나요
  categories=['rule', 'guide'] note=제때 결과보고를 제출하여 사업의 진행 상황을 적절히 관리하기 위한 질문.
  seed_overlap=0.2167 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.2222 peer_target=finance_officer_hr_admin_01_d577dec5: 휴가 신청 시 필요한 서류와 그 제출 기한은 어떻게 되나요
  shared_keywords(seed)=['사업비', '집행'] shared_keywords(peer)=['기한은', '서류와']
  bootstrap_titles=[4-4] 경기테크노파크 업무추진비 집행지침(2023.2.24.) / 구간 10; [2-11] 사업관리 규정(2003.3.20.) / 구간 65

## standard

- `finance_officer_standard_01_7c6d867c` [review_edit] 정산 신청을 위한 증빙 서류의 종류와 각각의 원본 보관 기준은 어떻게 되나요
  categories=['rule', 'guide'] note=증빙 서류의 종류와 기준을 명확히 해야 지출 적정성을 확보할 수 있습니다.
  seed_overlap=0.1429 seed_target=corp_card_policy: 법인카드 사용 제한과 증빙 보관 기준을 알려줘
  peer_overlap=0.5385 peer_target=finance_officer_audit_response_01_027b1741: 법인카드 사용 시 필수적인 증빙 서류의 종류와 각각의 원본 보관 기준은 무엇인가요
  shared_keywords(seed)=['보관', '증빙'] shared_keywords(peer)=['각각의', '기준은', '보관', '서류의', '원본', '종류와', '증빙']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 70; [2-10] 재무회계 규정(2022.9.26.) / 구간 69
- `finance_officer_standard_02_3c353c23` [review_new] 정산 기한이 지나면 어떤 조치를 취해야 하며, 누락 시 발생할 수 있는 문제는 무엇인가요
  categories=['rule', 'guide'] note=정산 기한과 누락 시 조치를 알고 있어야 환수 위험을 사전에 피할 수 있습니다.
  seed_overlap=0.0500 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.1667 peer_target=finance_officer_project_management_02_d641e979: 정산 기한이 다가왔을 때 미비된 사항이 있으면 어떤 절차를 통해 해결해야 하나요
  shared_keywords(seed)=['어떤'] shared_keywords(peer)=['기한이', '어떤', '정산']
  bootstrap_titles=[2-12] 여비 규정(2023.12.21.) / 구간 12; [2-10] 재무회계 규정(2022.9.26.) / 구간 221
