# Gold Review Summary goldbatch_20260312_1116_new_employee

- Candidate file: `/app/data/autorag/candidates/candidate_cases_new_employee_goldbatch_20260312_1116_new_employee.json`
- Review queue: `/app/data/autorag/review/review_queue_goldbatch_20260312_1116_new_employee.json`
- Total candidates: 18
- Suggested `review_new`: 18
- Suggested `review_edit`: 0
- Suggested `merge_or_skip`: 0

## Review Guide

- `review_new`: seed 질문과 겹침이 낮아 새 gold 후보로 우선 검토할 만한 질문
- `review_edit`: 일부 중복/표현 겹침이 있어 wording 조정 후 유지할 가능성이 높은 질문
- `merge_or_skip`: seed 또는 다른 후보와 매우 비슷해 통합 검토가 필요한 질문

## audit_response

- `new_employee_audit_response_01_ca0ed52b` [review_new] 법인카드 사용 후에 어떤 증빙 자료를 반드시 제출해야 하는지 확인해 주세요
  categories=['rule', 'guide'] note=증빙 자료가 부족하면 감사에서 문제가 될 수 있기 때문에 중요하다.
  seed_overlap=0.2808 seed_target=corp_card_policy: 법인카드 사용 제한과 증빙 보관 기준을 알려줘
  peer_overlap=0.1875 peer_target=new_employee_procurement_bid_03_25981457: 예정가격이 설정되기 전에 어떤 자료를 준비해야 하는지 체크리스트를 알려주세요
  shared_keywords(seed)=['법인카드', '사용', '증빙'] shared_keywords(peer)=['어떤', '자료를', '하는지']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 219; [2-10] 재무회계 규정(2022.9.26.) / 구간 362
- `new_employee_audit_response_02_13acecd7` [review_new] 감사 대응을 위해 지출 증빙 서류를 준비할 때 특히 주의해야 할 점이 무엇인지 알고 싶어요
  categories=['rule', 'guide'] note=지출 증빙이 부족하면 환수 위험이 커지므로 신중해야 한다.
  seed_overlap=0.2605 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.3278 peer_target=new_employee_audit_response_04_080bb0f9: 법인카드 사용 후 감사 대응을 위해 남겨야 할 기록과 서류 정리 방법에 대해 알고 싶어요
  shared_keywords(seed)=['감사', '대응을', '위해', '지출'] shared_keywords(peer)=['감사', '대응을', '싶어요', '알고', '위해']
  bootstrap_titles=[4-4] 경기테크노파크 업무추진비 집행지침(2023.2.24.) / 구간 10; [2-10] 재무회계 규정(2022.9.26.) / 구간 70
- `new_employee_audit_response_03_55f5a836` [review_new] 법인카드를 사용할 때 어떤 경우에 사후 보완 절차가 필요한지 알고 싶어요
  categories=['rule', 'guide'] note=사후 보완 절차를 미리 이해하지 않으면 절차에서 혼란이 생길 수 있다.
  seed_overlap=0.2167 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.2667 peer_target=new_employee_hr_admin_02_bd3a7cae: 복무규칙에 따라 결재 후 진행해야 할 승진 절차가 어떤 것인지 알고 싶어요
  shared_keywords(seed)=['보완', '어떤', '필요한지'] shared_keywords(peer)=['싶어요', '알고', '어떤', '절차가']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 219; [2-10] 재무회계 규정(2022.9.26.) / 구간 218
- `new_employee_audit_response_04_080bb0f9` [review_new] 법인카드 사용 후 감사 대응을 위해 남겨야 할 기록과 서류 정리 방법에 대해 알고 싶어요
  categories=['rule', 'guide'] note=기록과 서류 관리가 부실하면 감사 시 문제가 될 수 있다.
  seed_overlap=0.2079 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.3278 peer_target=new_employee_audit_response_02_13acecd7: 감사 대응을 위해 지출 증빙 서류를 준비할 때 특히 주의해야 할 점이 무엇인지 알고 싶어요
  shared_keywords(seed)=['감사', '대응을', '위해'] shared_keywords(peer)=['감사', '대응을', '싶어요', '알고', '위해']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 219; [2-10] 재무회계 규정(2022.9.26.) / 구간 362

## contract_review

- `new_employee_contract_review_01_79adb9de` [review_new] 계약 변경 시 서류 누락이 발생했을 때 어떤 절차를 따라야 하나요
  categories=['rule', 'guide'] note=서류 누락은 큰 문제를 일으킬 수 있어, 정확한 절차 확인이 필수적입니다.
  seed_overlap=0.2318 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.1833 peer_target=new_employee_contract_review_03_16f66fc0: 계약의 책임 분기 조항을 검토할 때 어떤 점에 특히 주의해야 하나요
  shared_keywords(seed)=['계약', '변경'] shared_keywords(peer)=['어떤', '하나요']
  bootstrap_titles=[3-23] 중소기업 E-비즈니스 정보화지원사업 운영규칙(2017.8.24.) / 구간 28; [2-10] 재무회계 규정(2022.9.26.) / 구간 306
- `new_employee_contract_review_02_421a6144` [review_new] 위약금 관련 조항은 어떤 상황에서 적용되는지 구체적으로 알고 싶어요
  categories=['rule', 'law'] note=위약금 조항을 이해하지 못하면 손해를 볼 수 있으므로 정확한 확인이 필요합니다.
  seed_overlap=0.0526 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.2000 peer_target=new_employee_hr_admin_02_bd3a7cae: 복무규칙에 따라 결재 후 진행해야 할 승진 절차가 어떤 것인지 알고 싶어요
  shared_keywords(seed)=['어떤'] shared_keywords(peer)=['싶어요', '알고', '어떤']
  bootstrap_titles=하도급거래 공정화에 관한 법률 / 구간 467; 근로기준법 / 구간 5
- `new_employee_contract_review_03_16f66fc0` [review_new] 계약의 책임 분기 조항을 검토할 때 어떤 점에 특히 주의해야 하나요
  categories=['rule', 'guide'] note=책임 분기 조항은 분쟁의 원인이 될 수 있어 중요하게 체크해야 합니다.
  seed_overlap=0.0500 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.1833 peer_target=new_employee_contract_review_01_79adb9de: 계약 변경 시 서류 누락이 발생했을 때 어떤 절차를 따라야 하나요
  shared_keywords(seed)=[] shared_keywords(peer)=['어떤', '하나요']
  bootstrap_titles=[4-1] 임직원 행동강령(2024.8.27.) / 구간 47; [2-13] 경영진 보수 및 직무청렴의무에 관한 규정(2025.12.24.) / 구간 34

## hr_admin

- `new_employee_hr_admin_01_3185cc97` [review_new] 휴가를 신청할 때 필요한 서류와 어떤 결재를 받아야 하는지 확인하고 싶어요
  categories=['rule', 'guide'] note=휴가 신청 전에 필수 서류를 확인하는 것이 중요함.
  seed_overlap=0.0526 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.1750 peer_target=new_employee_hr_admin_02_bd3a7cae: 복무규칙에 따라 결재 후 진행해야 할 승진 절차가 어떤 것인지 알고 싶어요
  shared_keywords(seed)=['어떤'] shared_keywords(peer)=['싶어요', '어떤']
  bootstrap_titles=[3-25] 공무직 근로자 관리규칙(2026.1.2.) / 구간 144; [3-18] 취업규칙(2026.1.1.) / 구간 26
- `new_employee_hr_admin_02_bd3a7cae` [review_new] 복무규칙에 따라 결재 후 진행해야 할 승진 절차가 어떤 것인지 알고 싶어요
  categories=['rule', 'guide'] note=승진 절차를 명확히 이해하고 준비하는 것이 중요함.
  seed_overlap=0.1333 seed_target=hr_promotion_years: 직급별 승진 소요년수를 표로 정리해줘
  peer_overlap=0.2667 peer_target=new_employee_audit_response_03_55f5a836: 법인카드를 사용할 때 어떤 경우에 사후 보완 절차가 필요한지 알고 싶어요
  shared_keywords(seed)=['승진'] shared_keywords(peer)=['싶어요', '알고', '어떤', '절차가']
  bootstrap_titles=[2-4] 인사 관리 규정(2025.10.24.) / 구간 104; [3-5] 인사 관리 규칙(2026.1.23.) / 구간 112
- `new_employee_hr_admin_03_08526c63` [review_new] 징계 절차에서 서면 통지를 어떻게 준비해야 하는지, 그 구체적인 절차가 궁금해요
  categories=['rule', 'guide'] note=징계와 관련된 서면 통지를 제대로 준비하는 것이 중요함.
  seed_overlap=0.1929 seed_target=hr_discipline_notice: 징계 절차에서 사전 통지와 소명 기회가 필요한지 알려줘
  peer_overlap=0.1250 peer_target=new_employee_project_management_02_70763784: 사업비 정산 절차에서 주의해야 할 항목과 결재 흐름이 어떻게 되는지 궁금해요
  shared_keywords(seed)=['절차에서', '징계'] shared_keywords(peer)=['궁금해요', '절차에서']
  bootstrap_titles=[3-5] 인사 관리 규칙(2026.1.23.) / 구간 164; [3-5] 인사 관리 규칙(2026.1.23.) / 구간 172

## procurement_bid

- `new_employee_procurement_bid_01_42ff9c44` [review_new] 비교견적을 받을 때 준비해야 할 서류와 절차는 무엇인지 자세히 알고 싶어요
  categories=['rule', 'guide'] note=비교견적은 비용 절감을 위해 필수적인 절차이기 때문에 정확한 준비가 중요합니다.
  seed_overlap=0.0500 seed_target=procurement_quote_rule: 구매 시 비교견적이나 입찰이 필요한 기준을 정리해줘
  peer_overlap=0.3846 peer_target=new_employee_project_management_01_a18100ca: 사업비 집행 후 결과보고를 위해 준비해야 할 서류와 순서를 자세히 알고 싶어요
  shared_keywords(seed)=[] shared_keywords(peer)=['서류와', '싶어요', '알고', '자세히', '준비해야']
  bootstrap_titles=[4-7] 전산자원관리 지침(2017.2.7.) / 구간 68; [3-30] 윤리경영 시행규칙(2021.05.27.) / 구간 70
- `new_employee_procurement_bid_02_5503ff44` [review_new] 입찰 공고 후 계약 체결까지 과정에서 확인해야 할 주요 사항이 무엇인지 알고 싶어요
  categories=['rule', 'law'] note=계약 체결 과정에서의 실수는 큰 문제를 발생시킬 수 있으므로 세심한 검토가 필요합니다.
  seed_overlap=0.0769 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.1929 peer_target=new_employee_procurement_bid_01_42ff9c44: 비교견적을 받을 때 준비해야 할 서류와 절차는 무엇인지 자세히 알고 싶어요
  shared_keywords(seed)=['계약'] shared_keywords(peer)=['싶어요', '알고']
  bootstrap_titles=지방자치단체를 당사자로 하는 계약에 관한 법률 / 구간 5; [2-10] 재무회계 규정(2022.9.26.) / 구간 341
- `new_employee_procurement_bid_03_25981457` [review_new] 예정가격이 설정되기 전에 어떤 자료를 준비해야 하는지 체크리스트를 알려주세요
  categories=['rule', 'guide'] note=예정가격 설정이 적절해야 이후의 모든 절차에 영향을 미치기 때문에 사전 준비가 중요합니다.
  seed_overlap=0.0667 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.1875 peer_target=new_employee_audit_response_01_ca0ed52b: 법인카드 사용 후에 어떤 증빙 자료를 반드시 제출해야 하는지 확인해 주세요
  shared_keywords(seed)=['전에'] shared_keywords(peer)=['어떤', '자료를', '하는지']
  bootstrap_titles=[3-1] 재무회계 규칙(2025.11.24.) / 구간 83; [3-1] 재무회계 규칙(2025.11.24.) / 구간 85

## project_management

- `new_employee_project_management_01_a18100ca` [review_new] 사업비 집행 후 결과보고를 위해 준비해야 할 서류와 순서를 자세히 알고 싶어요
  categories=['rule', 'guide'] note=결과보고는 사업비 집행의 필수 과정이기 때문에 정확한 준비가 필요합니다.
  seed_overlap=0.1833 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.3846 peer_target=new_employee_procurement_bid_01_42ff9c44: 비교견적을 받을 때 준비해야 할 서류와 절차는 무엇인지 자세히 알고 싶어요
  shared_keywords(seed)=['사업비', '집행'] shared_keywords(peer)=['서류와', '싶어요', '알고', '자세히', '준비해야']
  bootstrap_titles=[2-11] 사업관리 규정(2003.3.20.) / 구간 66; [2-11] 사업관리 규정(2003.3.20.) / 구간 65
- `new_employee_project_management_02_70763784` [review_new] 사업비 정산 절차에서 주의해야 할 항목과 결재 흐름이 어떻게 되는지 궁금해요
  categories=['rule', 'guide'] note=정산 오류를 방지하기 위해 정확한 절차 확인이 중요합니다.
  seed_overlap=0.1167 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.1250 peer_target=new_employee_hr_admin_03_08526c63: 징계 절차에서 서면 통지를 어떻게 준비해야 하는지, 그 구체적인 절차가 궁금해요
  shared_keywords(seed)=['사업비'] shared_keywords(peer)=['궁금해요', '절차에서']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 272; [2-10] 재무회계 규정(2022.9.26.) / 구간 264
- `new_employee_project_management_03_a22448e8` [review_new] 승인 받기 전에 사업비 사용 계획을 검토할 때 필요한 체크리스트가 있을까요
  categories=['rule', 'guide'] note=사전 검토는 승인 과정에서 실수를 줄이기 위한 필수 단계입니다.
  seed_overlap=0.3000 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.1125 peer_target=new_employee_project_management_02_70763784: 사업비 정산 절차에서 주의해야 할 항목과 결재 흐름이 어떻게 되는지 궁금해요
  shared_keywords(seed)=['사업비', '승인', '전에'] shared_keywords(peer)=['사업비']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 106; [2-11] 사업관리 규정(2003.3.20.) / 구간 46

## standard

- `new_employee_standard_01_e6ee01e1` [review_new] 휴가 신청 시 필요한 서류와 결재 절차를 정확히 알려줘
  categories=['rule', 'guide'] note=실무에서 휴가 처리에 실수가 없도록 준비하기 위해 중요하다.
  seed_overlap=0.0000 seed_target=hr_promotion_years: 직급별 승진 소요년수를 표로 정리해줘
  peer_overlap=0.0833 peer_target=new_employee_contract_review_01_79adb9de: 계약 변경 시 서류 누락이 발생했을 때 어떤 절차를 따라야 하나요
  shared_keywords(seed)=[] shared_keywords(peer)=['절차를']
  bootstrap_titles=[3-18] 취업규칙(2026.1.1.) / 구간 26; [3-25] 공무직 근로자 관리규칙(2026.1.2.) / 구간 144
- `new_employee_standard_02_1a43ea6c` [review_new] 계약 체결 시 확인해야 할 필수 항목과 증빙 자료는 무엇인지 궁금해
  categories=['rule', 'guide'] note=계약의 법적 효력을 확보하기 위한 준비가 필요하다.
  seed_overlap=0.0833 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.0769 peer_target=new_employee_contract_review_01_79adb9de: 계약 변경 시 서류 누락이 발생했을 때 어떤 절차를 따라야 하나요
  shared_keywords(seed)=['계약'] shared_keywords(peer)=['계약']
  bootstrap_titles=[3-23] 중소기업 E-비즈니스 정보화지원사업 운영규칙(2017.8.24.) / 구간 114; [3-1] 재무회계 규칙(2025.11.24.) / 구간 77
