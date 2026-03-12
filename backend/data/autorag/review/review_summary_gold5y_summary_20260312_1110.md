# Gold Review Summary gold5y_summary_20260312_1110

- Candidate file: `/app/data/autorag/candidates/candidate_cases_five_year_employee_gold5y_20260312_0917.json`
- Review queue: `/app/data/autorag/review/review_queue_gold5y_20260312_0917.json`
- Total candidates: 18
- Suggested `review_new`: 17
- Suggested `review_edit`: 1
- Suggested `merge_or_skip`: 0

## Review Guide

- `review_new`: seed 질문과 겹침이 낮아 새 gold 후보로 우선 검토할 만한 질문
- `review_edit`: 일부 중복/표현 겹침이 있어 wording 조정 후 유지할 가능성이 높은 질문
- `merge_or_skip`: seed 또는 다른 후보와 매우 비슷해 통합 검토가 필요한 질문

## audit_response

- `five_year_employee_audit_response_01_7469eb85` [review_new] 법인카드 사용 후 증빙 서류는 어떤 형식으로 제출해야 하며, 누락 시 어떤 위험이 있을까요
  categories=['rule', 'guide'] note=증빙 서류 제출 방식과 누락 시 위험을 사전에 확인하는 것이 중요합니다.
  seed_overlap=0.2808 seed_target=corp_card_policy: 법인카드 사용 제한과 증빙 보관 기준을 알려줘
  peer_overlap=0.1875 peer_target=five_year_employee_standard_02_0ba0dcce: 사업비 집행 시 원가 계산 및 증빙 서류는 어떤 기준을 따라야 하나요
  shared_keywords(seed)=['법인카드', '사용', '증빙'] shared_keywords(peer)=['서류는', '어떤', '증빙']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 362; [2-12] 여비 규정(2023.12.21.) / 구간 12
- `five_year_employee_audit_response_02_b2c13cf2` [review_new] 감사 시 지출 증빙이 부족한 경우에는 어떤 절차를 통해 보완해야 하나요
  categories=['rule', 'guide'] note=부족한 증빙에 대한 보완 절차를 이해하는 것은 감사 대응에 필수적입니다.
  seed_overlap=0.2853 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.2667 peer_target=five_year_employee_contract_review_03_d92271d8: 대금 지급을 위한 증빙이 누락될 경우 어떤 절차를 따라야 하나요
  shared_keywords(seed)=['감사', '어떤', '증빙이', '지출'] shared_keywords(peer)=['어떤', '절차를', '증빙이', '하나요']
  bootstrap_titles=[4-4] 경기테크노파크 업무추진비 집행지침(2023.2.24.) / 구간 10; [2-10] 재무회계 규정(2022.9.26.) / 구간 82
- `five_year_employee_audit_response_03_7113aa6a` [review_new] 사업비 정산 시 필수로 제출해야 하는 증빙 서류 목록은 무엇인지 확인할 수 있을까요
  categories=['rule', 'guide'] note=정산 시 필요한 서류 목록을 사전에 확인하여 위험을 줄이는 것이 중요합니다.
  seed_overlap=0.1269 seed_target=corp_card_policy: 법인카드 사용 제한과 증빙 보관 기준을 알려줘
  peer_overlap=0.3333 peer_target=five_year_employee_project_management_01_3710ec10: 사업비 집행 전 반드시 확인해야 할 증빙 서류 목록은 무엇인가요
  shared_keywords(seed)=['증빙'] shared_keywords(peer)=['목록은', '사업비', '증빙']
  bootstrap_titles=[2-12] 여비 규정(2023.12.21.) / 구간 12; [4-4] 경기테크노파크 업무추진비 집행지침(2023.2.24.) / 구간 10
- `five_year_employee_audit_response_04_a01c72d3` [review_new] 환수 위험을 피하기 위해 지원금 지출 시 어떤 증빙을 확보해야 하나요
  categories=['rule', 'guide'] note=지원금 지출에 대해 요구되는 증빙을 명확히 아는 것이 필수적입니다.
  seed_overlap=0.2167 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.2265 peer_target=five_year_employee_audit_response_02_b2c13cf2: 감사 시 지출 증빙이 부족한 경우에는 어떤 절차를 통해 보완해야 하나요
  shared_keywords(seed)=['어떤', '위해', '지출'] shared_keywords(peer)=['어떤', '지출', '하나요']
  bootstrap_titles=[4-4] 경기테크노파크 업무추진비 집행지침(2023.2.24.) / 구간 10; [2-10] 재무회계 규정(2022.9.26.) / 구간 82

## contract_review

- `five_year_employee_contract_review_01_11017db6` [review_new] 계약서에 명시된 위약금 조항의 적용 범위와 절차는 어떻게 되나요
  categories=['rule', 'guide'] note=위약금 조항은 계약 이행에 중요한 영향을 미치므로 사전에 명확히 할 필요가 있다.
  seed_overlap=0.0500 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.0769 peer_target=five_year_employee_hr_admin_03_5ae23cad: 근무 태도 징계 시 참고해야 할 규정과 절차는 무엇인지 확인할 수 있을까요
  shared_keywords(seed)=[] shared_keywords(peer)=['절차는']
  bootstrap_titles=[3-2] 위임전결 규칙(2025.11.24.) / 구간 4; [2-10] 재무회계 규정(2022.9.26.) / 구간 354
- `five_year_employee_contract_review_02_80f5ca27` [review_new] 계약 변경 사항을 승인받기 위해 반드시 첨부해야 하는 서류는 무엇인가요
  categories=['rule', 'guide'] note=서류 누락으로 인해 계약 변경이 지체되지 않도록 확인해야 한다.
  seed_overlap=0.2167 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.0667 peer_target=five_year_employee_procurement_bid_03_fe5f284e: 계약 체결 전 검토해야 할 주요 조항과 해당 조항의 위험 요소는 무엇인가요
  shared_keywords(seed)=['계약', '변경'] shared_keywords(peer)=['계약']
  bootstrap_titles=[3-23] 중소기업 E-비즈니스 정보화지원사업 운영규칙(2017.8.24.) / 구간 28; [3-12] 경기테크노파크 시설관리규칙 / 구간 20
- `five_year_employee_contract_review_03_d92271d8` [review_new] 대금 지급을 위한 증빙이 누락될 경우 어떤 절차를 따라야 하나요
  categories=['rule', 'guide'] note=증빙 서류 누락은 대금 지급에 직접적인 영향을 미치므로 사전 확인이 중요하다.
  seed_overlap=0.1111 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.2667 peer_target=five_year_employee_audit_response_02_b2c13cf2: 감사 시 지출 증빙이 부족한 경우에는 어떤 절차를 통해 보완해야 하나요
  shared_keywords(seed)=['어떤', '증빙이'] shared_keywords(peer)=['어떤', '절차를', '증빙이', '하나요']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 70; [3-10] 위원회 수당 등 지급 규칙(2025.6.19.) / 구간 20

## hr_admin

- `five_year_employee_hr_admin_01_e64bb61e` [review_new] 휴가 중 업무 대행자는 어떻게 지정하고, 이 과정에서 필요한 결재는 무엇인가요
  categories=['rule', 'guide'] note=대행자 지정 시의 결재 누락 방지를 위해 중요하다.
  seed_overlap=0.0500 seed_target=hr_promotion_years: 직급별 승진 소요년수를 표로 정리해줘
  peer_overlap=0.0833 peer_target=five_year_employee_project_management_03_1e783e09: 정산 과정에서 보완해야 할 서류나 절차가 있다면 어떤 것들이 있나요
  shared_keywords(seed)=[] shared_keywords(peer)=['과정에서']
  bootstrap_titles=[2-8] 문서 관리 규정(2025.12.24.) / 구간 38; [3-13] 직제 규칙(2026.1.20.) / 구간 9
- `five_year_employee_hr_admin_02_08666670` [review_new] 승진 권고를 위한 추천서 작성 시 어떤 기준과 양식을 따라야 하나요
  categories=['rule'] note=승진 절차에서의 문서적 오류를 피하기 위함이다.
  seed_overlap=0.1333 seed_target=hr_promotion_years: 직급별 승진 소요년수를 표로 정리해줘
  peer_overlap=0.2000 peer_target=five_year_employee_contract_review_03_d92271d8: 대금 지급을 위한 증빙이 누락될 경우 어떤 절차를 따라야 하나요
  shared_keywords(seed)=['승진'] shared_keywords(peer)=['어떤', '위한', '하나요']
  bootstrap_titles=[3-25] 공무직 근로자 관리규칙(2026.1.2.) / 구간 314; [3-5] 인사 관리 규칙(2026.1.23.) / 구간 114
- `five_year_employee_hr_admin_03_5ae23cad` [review_new] 근무 태도 징계 시 참고해야 할 규정과 절차는 무엇인지 확인할 수 있을까요
  categories=['rule', 'law'] note=징계 절차의 법적 준수 여부를 확인하기 위해 필요하다.
  seed_overlap=0.1269 seed_target=hr_discipline_notice: 징계 절차에서 사전 통지와 소명 기회가 필요한지 알려줘
  peer_overlap=0.0769 peer_target=five_year_employee_contract_review_01_11017db6: 계약서에 명시된 위약금 조항의 적용 범위와 절차는 어떻게 되나요
  shared_keywords(seed)=['징계'] shared_keywords(peer)=['절차는']
  bootstrap_titles=[3-25] 공무직 근로자 관리규칙(2026.1.2.) / 구간 252; [2-4] 인사 관리 규정(2025.10.24.) / 구간 328

## procurement_bid

- `five_year_employee_procurement_bid_01_e0e33251` [review_new] 입찰에 필요한 비교견적 제출 시 요구되는 서류 목록은 무엇인가요
  categories=['rule', 'guide'] note=명확한 서류 목록 확인을 통해 입찰 과정의 투명성을 확보할 수 있다.
  seed_overlap=0.0500 seed_target=procurement_quote_rule: 구매 시 비교견적이나 입찰이 필요한 기준을 정리해줘
  peer_overlap=0.1429 peer_target=five_year_employee_project_management_01_3710ec10: 사업비 집행 전 반드시 확인해야 할 증빙 서류 목록은 무엇인가요
  shared_keywords(seed)=[] shared_keywords(peer)=['목록은']
  bootstrap_titles=[2-3] 감사 규정(2021.09.28.) / 구간 73; [2-10] 재무회계 규정(2022.9.26.) / 구간 56
- `five_year_employee_procurement_bid_02_41864b68` [review_new] 예정가격 설정 기준에 따라 가격 책정 시 유의해야 할 사항은 무엇인가요
  categories=['rule', 'law'] note=예정가격 설정에 따른 법적 요구 사항을 확인하여 위반을 방지할 수 있다.
  seed_overlap=0.0500 seed_target=procurement_quote_rule: 구매 시 비교견적이나 입찰이 필요한 기준을 정리해줘
  peer_overlap=0.0500 peer_target=five_year_employee_procurement_bid_01_e0e33251: 입찰에 필요한 비교견적 제출 시 요구되는 서류 목록은 무엇인가요
  shared_keywords(seed)=[] shared_keywords(peer)=[]
  bootstrap_titles=국가를 당사자로 하는 계약에 관한 법률 / 구간 110; 국가를 당사자로 하는 계약에 관한 법률 / 구간 109
- `five_year_employee_procurement_bid_03_fe5f284e` [review_edit] 계약 체결 전 검토해야 할 주요 조항과 해당 조항의 위험 요소는 무엇인가요
  categories=['rule', 'guide'] note=계약 위험 요소를 사전에 파악하여 문제 발생을 예방할 수 있다.
  seed_overlap=0.4000 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.0714 peer_target=five_year_employee_contract_review_01_11017db6: 계약서에 명시된 위약금 조항의 적용 범위와 절차는 어떻게 되나요
  shared_keywords(seed)=['검토해야', '계약', '위험', '조항과'] shared_keywords(peer)=['조항의']
  bootstrap_titles=[2-13] 경영진 보수 및 직무청렴의무에 관한 규정(2025.12.24.) / 구간 56; [3-1] 재무회계 규칙(2025.11.24.) / 구간 76

## project_management

- `five_year_employee_project_management_01_3710ec10` [review_new] 사업비 집행 전 반드시 확인해야 할 증빙 서류 목록은 무엇인가요
  categories=['rule', 'guide'] note=정확한 증빙 없이 사업비를 집행할 경우 문제가 발생할 수 있기 때문입니다.
  seed_overlap=0.2722 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.3333 peer_target=five_year_employee_audit_response_03_7113aa6a: 사업비 정산 시 필수로 제출해야 하는 증빙 서류 목록은 무엇인지 확인할 수 있을까요
  shared_keywords(seed)=['사업비', '집행'] shared_keywords(peer)=['목록은', '사업비', '증빙']
  bootstrap_titles=[4-4] 경기테크노파크 업무추진비 집행지침(2023.2.24.) / 구간 10; [2-10] 재무회계 규정(2022.9.26.) / 구간 69
- `five_year_employee_project_management_02_73f9ae43` [review_new] 결과보고 시 포함해야 할 주요 항목과 제출 기한은 어떻게 되나요
  categories=['rule', 'guide'] note=결과보고가 누락되면 프로젝트 평가에 부정적인 영향을 미칠 수 있습니다.
  seed_overlap=0.1500 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.0909 peer_target=five_year_employee_standard_01_2f2855b6: 교육훈련 규칙에 따라 직원 교육 계획 수립 시 반드시 포함해야 할 항목은 무엇인가요
  shared_keywords(seed)=['결과보고'] shared_keywords(peer)=['포함해야']
  bootstrap_titles=[2-11] 사업관리 규정(2003.3.20.) / 구간 64; [3-5] 인사 관리 규칙(2026.1.23.) / 구간 422
- `five_year_employee_project_management_03_1e783e09` [review_new] 정산 과정에서 보완해야 할 서류나 절차가 있다면 어떤 것들이 있나요
  categories=['rule', 'notice'] note=정산 시 서류가 부족하면 재정적 문제로 이어질 수 있기 때문에 미리 확인이 필요합니다.
  seed_overlap=0.0588 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.1333 peer_target=five_year_employee_audit_response_02_b2c13cf2: 감사 시 지출 증빙이 부족한 경우에는 어떤 절차를 통해 보완해야 하나요
  shared_keywords(seed)=['어떤'] shared_keywords(peer)=['보완해야', '어떤']
  bootstrap_titles=[2-12] 여비 규정(2023.12.21.) / 구간 12; [2-10] 재무회계 규정(2022.9.26.) / 구간 271

## standard

- `five_year_employee_standard_01_2f2855b6` [review_new] 교육훈련 규칙에 따라 직원 교육 계획 수립 시 반드시 포함해야 할 항목은 무엇인가요
  categories=['rule', 'guide'] note=교육비 집행 및 결과 보고를 위해 필요한 사전 준비 사항이다.
  seed_overlap=0.0000 seed_target=hr_promotion_years: 직급별 승진 소요년수를 표로 정리해줘
  peer_overlap=0.0909 peer_target=five_year_employee_project_management_02_73f9ae43: 결과보고 시 포함해야 할 주요 항목과 제출 기한은 어떻게 되나요
  shared_keywords(seed)=[] shared_keywords(peer)=['포함해야']
  bootstrap_titles=[3-25] 공무직 근로자 관리규칙(2026.1.2.) / 구간 270; [3-9] 교육훈련 규칙(2024.4.30) / 구간 8
- `five_year_employee_standard_02_0ba0dcce` [review_new] 사업비 집행 시 원가 계산 및 증빙 서류는 어떤 기준을 따라야 하나요
  categories=['rule', 'guide'] note=정확한 사업비 집행과 감사 대응을 위해 중요한 문서 요구 사항이다.
  seed_overlap=0.1538 seed_target=corp_card_policy: 법인카드 사용 제한과 증빙 보관 기준을 알려줘
  peer_overlap=0.3000 peer_target=five_year_employee_project_management_01_3710ec10: 사업비 집행 전 반드시 확인해야 할 증빙 서류 목록은 무엇인가요
  shared_keywords(seed)=['기준을', '증빙'] shared_keywords(peer)=['사업비', '증빙', '집행']
  bootstrap_titles=[4-4] 경기테크노파크 업무추진비 집행지침(2023.2.24.) / 구간 10; [2-10] 재무회계 규정(2022.9.26.) / 구간 70
