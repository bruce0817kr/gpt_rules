# Paraphrase Regression Report paraphrase_gold5y_20260312_1108

- Review queue: `/app/data/autorag/review/review_queue_gold5y_20260312_0917.json`
- Total rows: 18
- ok: 3
- needs_review: 9
- high_risk: 6

## By Mode

- `audit_response` ok=1 needs_review=3 high_risk=0
- `contract_review` ok=0 needs_review=1 high_risk=2
- `hr_admin` ok=0 needs_review=0 high_risk=3
- `procurement_bid` ok=1 needs_review=2 high_risk=0
- `project_management` ok=1 needs_review=2 high_risk=0
- `standard` ok=0 needs_review=1 high_risk=1

## High Risk Cases

- `five_year_employee_contract_review_03_d92271d8` [contract_review] 대금 지급을 위한 증빙이 누락될 경우 어떤 절차를 따라야 하나요
  status=high_risk template=- confidence=low similarity=0.1293 retrieval_f1=1.0000
  citation_panel_clean=False citations=5 referenced=0
  expected_ids=['cae8e105770b432c9cba14d3f73e7915::구간 70', '8654bda6ea7a4b49ad8eb28b4692cbe6::구간 20', 'cae8e105770b432c9cba14d3f73e7915::구간 56', 'cae8e105770b432c9cba14d3f73e7915::구간 82']
  current_ids=['cae8e105770b432c9cba14d3f73e7915::구간 70', '8654bda6ea7a4b49ad8eb28b4692cbe6::구간 20', 'cae8e105770b432c9cba14d3f73e7915::구간 56', 'cae8e105770b432c9cba14d3f73e7915::구간 82']
- `five_year_employee_hr_admin_02_08666670` [hr_admin] 승진 권고를 위한 추천서 작성 시 어떤 기준과 양식을 따라야 하나요
  status=high_risk template=- confidence=low similarity=0.3474 retrieval_f1=0.8571
  citation_panel_clean=True citations=6 referenced=6
  expected_ids=['99f005f4ecc74f57bcb4476f081b4c19::구간 314', '43309a76ff174026a8c9b330a7485f53::구간 114', '43309a76ff174026a8c9b330a7485f53::구간 368', '43309a76ff174026a8c9b330a7485f53::구간 143']
  current_ids=['43309a76ff174026a8c9b330a7485f53::구간 114', '43309a76ff174026a8c9b330a7485f53::구간 113', '1c722f2453a646aea4a6477d99eb573f::구간 105', '1c722f2453a646aea4a6477d99eb573f::구간 104']
- `five_year_employee_hr_admin_03_5ae23cad` [hr_admin] 근무 태도 징계 시 참고해야 할 규정과 절차는 무엇인지 확인할 수 있을까요
  status=high_risk template=- confidence=low similarity=0.3741 retrieval_f1=0.7500
  citation_panel_clean=True citations=3 referenced=3
  expected_ids=['99f005f4ecc74f57bcb4476f081b4c19::구간 252', '1c722f2453a646aea4a6477d99eb573f::구간 328', '99f005f4ecc74f57bcb4476f081b4c19::구간 250', '1c722f2453a646aea4a6477d99eb573f::구간 326']
  current_ids=['1c722f2453a646aea4a6477d99eb573f::구간 328', '1c722f2453a646aea4a6477d99eb573f::구간 326', '99f005f4ecc74f57bcb4476f081b4c19::구간 252']
- `five_year_employee_standard_02_0ba0dcce` [standard] 사업비 집행 시 원가 계산 및 증빙 서류는 어떤 기준을 따라야 하나요
  status=high_risk template=- confidence=low similarity=0.4038 retrieval_f1=0.7500
  citation_panel_clean=True citations=3 referenced=3
  expected_ids=['ac1edc218c3347b5859d4c56e94a067b::구간 10', 'cae8e105770b432c9cba14d3f73e7915::구간 70', 'cae8e105770b432c9cba14d3f73e7915::구간 86', 'ac1edc218c3347b5859d4c56e94a067b::구간 45']
  current_ids=['ac1edc218c3347b5859d4c56e94a067b::구간 10', 'cae8e105770b432c9cba14d3f73e7915::구간 70', 'cae8e105770b432c9cba14d3f73e7915::구간 56']
- `five_year_employee_hr_admin_01_e64bb61e` [hr_admin] 휴가 중 업무 대행자는 어떻게 지정하고, 이 과정에서 필요한 결재는 무엇인가요
  status=high_risk template=- confidence=low similarity=0.5152 retrieval_f1=0.3333
  citation_panel_clean=True citations=1 referenced=1
  expected_ids=['ced48a974f5e44d0a680e04c382738d2::구간 38', 'b4045a7626c844bc87f7b7d50fb10845::구간 9', '1c722f2453a646aea4a6477d99eb573f::구간 252', '99f005f4ecc74f57bcb4476f081b4c19::구간 178']
  current_ids=['ced48a974f5e44d0a680e04c382738d2::구간 38']
- `five_year_employee_contract_review_01_11017db6` [contract_review] 계약서에 명시된 위약금 조항의 적용 범위와 절차는 어떻게 되나요
  status=high_risk template=- confidence=low similarity=0.6381 retrieval_f1=0.8000
  citation_panel_clean=False citations=5 referenced=0
  expected_ids=['58e04bfa5fbb4be5b6551535863ae98a::구간 4', 'cae8e105770b432c9cba14d3f73e7915::구간 354', '99f005f4ecc74f57bcb4476f081b4c19::구간 609', '99f005f4ecc74f57bcb4476f081b4c19::구간 543']
  current_ids=['58e04bfa5fbb4be5b6551535863ae98a::구간 4', 'cae8e105770b432c9cba14d3f73e7915::구간 354', '99f005f4ecc74f57bcb4476f081b4c19::구간 543', '99f005f4ecc74f57bcb4476f081b4c19::구간 609']

## Needs Review Cases

- `five_year_employee_audit_response_01_7469eb85` [audit_response] 법인카드 사용 후 증빙 서류는 어떤 형식으로 제출해야 하며, 누락 시 어떤 위험이 있을까요
  status=needs_review template=corp_card_policy confidence=low similarity=0.5057 retrieval_f1=0.6667
  citation_panel_clean=True citations=4 referenced=4
  expected_ids=['cae8e105770b432c9cba14d3f73e7915::구간 362', '877ad38b63324f48953489f933e61ca2::구간 12', 'cae8e105770b432c9cba14d3f73e7915::구간 219', 'ac1edc218c3347b5859d4c56e94a067b::구간 45']
  current_ids=['cae8e105770b432c9cba14d3f73e7915::구간 219', 'cae8e105770b432c9cba14d3f73e7915::구간 363', '877ad38b63324f48953489f933e61ca2::구간 12', 'cae8e105770b432c9cba14d3f73e7915::구간 70']
- `five_year_employee_audit_response_04_a01c72d3` [audit_response] 환수 위험을 피하기 위해 지원금 지출 시 어떤 증빙을 확보해야 하나요
  status=needs_review template=- confidence=low similarity=0.5104 retrieval_f1=0.8889
  citation_panel_clean=True citations=4 referenced=4
  expected_ids=['ac1edc218c3347b5859d4c56e94a067b::구간 10', 'cae8e105770b432c9cba14d3f73e7915::구간 82', 'ac1edc218c3347b5859d4c56e94a067b::구간 45', 'cae8e105770b432c9cba14d3f73e7915::구간 56']
  current_ids=['ac1edc218c3347b5859d4c56e94a067b::구간 10', 'cae8e105770b432c9cba14d3f73e7915::구간 56', 'ac1edc218c3347b5859d4c56e94a067b::구간 45', 'cae8e105770b432c9cba14d3f73e7915::구간 76']
- `five_year_employee_audit_response_03_7113aa6a` [audit_response] 사업비 정산 시 필수로 제출해야 하는 증빙 서류 목록은 무엇인지 확인할 수 있을까요
  status=needs_review template=- confidence=low similarity=0.5898 retrieval_f1=0.7692
  citation_panel_clean=True citations=5 referenced=5
  expected_ids=['877ad38b63324f48953489f933e61ca2::구간 12', 'ac1edc218c3347b5859d4c56e94a067b::구간 10', 'cae8e105770b432c9cba14d3f73e7915::구간 69', 'cae8e105770b432c9cba14d3f73e7915::구간 56']
  current_ids=['877ad38b63324f48953489f933e61ca2::구간 12', 'ac1edc218c3347b5859d4c56e94a067b::구간 10', 'cae8e105770b432c9cba14d3f73e7915::구간 69', 'cae8e105770b432c9cba14d3f73e7915::구간 70']
- `five_year_employee_procurement_bid_02_41864b68` [procurement_bid] 예정가격 설정 기준에 따라 가격 책정 시 유의해야 할 사항은 무엇인가요
  status=needs_review template=- confidence=medium similarity=0.6108 retrieval_f1=0.5714
  citation_panel_clean=True citations=2 referenced=2
  expected_ids=['9b9b2217b7194bec83573133ab40291c::구간 110', '9b9b2217b7194bec83573133ab40291c::구간 109', 'f6f2c8b2e0df4d65a382daafa6e41560::구간 264', 'f6f2c8b2e0df4d65a382daafa6e41560::구간 85']
  current_ids=['9b9b2217b7194bec83573133ab40291c::구간 110', '9b9b2217b7194bec83573133ab40291c::구간 109']
- `five_year_employee_standard_01_2f2855b6` [standard] 교육훈련 규칙에 따라 직원 교육 계획 수립 시 반드시 포함해야 할 항목은 무엇인가요
  status=needs_review template=- confidence=low similarity=0.6444 retrieval_f1=0.8889
  citation_panel_clean=True citations=4 referenced=4
  expected_ids=['99f005f4ecc74f57bcb4476f081b4c19::구간 270', 'dcccf0db3cf44121a69a2dea53ac0003::구간 8', 'dcccf0db3cf44121a69a2dea53ac0003::구간 30', 'dcccf0db3cf44121a69a2dea53ac0003::구간 14']
  current_ids=['99f005f4ecc74f57bcb4476f081b4c19::구간 270', 'dcccf0db3cf44121a69a2dea53ac0003::구간 8', 'dcccf0db3cf44121a69a2dea53ac0003::구간 14', 'dcccf0db3cf44121a69a2dea53ac0003::구간 6']
- `five_year_employee_project_management_02_73f9ae43` [project_management] 결과보고 시 포함해야 할 주요 항목과 제출 기한은 어떻게 되나요
  status=needs_review template=- confidence=low similarity=0.6621 retrieval_f1=0.7500
  citation_panel_clean=True citations=3 referenced=3
  expected_ids=['214a173629da433d8b4d97fba5032780::구간 64', '43309a76ff174026a8c9b330a7485f53::구간 422', 'cae8e105770b432c9cba14d3f73e7915::구간 273', '3aa3e8b396504bbda35e8b958a163f4a::구간 94']
  current_ids=['214a173629da433d8b4d97fba5032780::구간 64', '43309a76ff174026a8c9b330a7485f53::구간 422', '43309a76ff174026a8c9b330a7485f53::구간 421']
- `five_year_employee_project_management_03_1e783e09` [project_management] 정산 과정에서 보완해야 할 서류나 절차가 있다면 어떤 것들이 있나요
  status=needs_review template=- confidence=low similarity=0.8230 retrieval_f1=0.5714
  citation_panel_clean=True citations=2 referenced=2
  expected_ids=['877ad38b63324f48953489f933e61ca2::구간 12', 'cae8e105770b432c9cba14d3f73e7915::구간 271', 'cae8e105770b432c9cba14d3f73e7915::구간 277', 'cae8e105770b432c9cba14d3f73e7915::구간 71']
  current_ids=['877ad38b63324f48953489f933e61ca2::구간 12', 'cae8e105770b432c9cba14d3f73e7915::구간 71']
- `five_year_employee_procurement_bid_01_e0e33251` [procurement_bid] 입찰에 필요한 비교견적 제출 시 요구되는 서류 목록은 무엇인가요
  status=needs_review template=procurement_quote_rule confidence=low similarity=0.9908 retrieval_f1=0.7692
  citation_panel_clean=True citations=5 referenced=5
  expected_ids=['3aa3e8b396504bbda35e8b958a163f4a::구간 73', 'cae8e105770b432c9cba14d3f73e7915::구간 56', '8e169ef54945417a9cf4799722f7f0c4::구간 68', 'a116034c047b4c3fb897903f9598593d::구간 14']
  current_ids=['3aa3e8b396504bbda35e8b958a163f4a::구간 73', 'cae8e105770b432c9cba14d3f73e7915::구간 341', 'cae8e105770b432c9cba14d3f73e7915::구간 56', 'a116034c047b4c3fb897903f9598593d::구간 14']
- `five_year_employee_contract_review_02_80f5ca27` [contract_review] 계약 변경 사항을 승인받기 위해 반드시 첨부해야 하는 서류는 무엇인가요
  status=needs_review template=contract_change_review confidence=low similarity=1.0000 retrieval_f1=0.5714
  citation_panel_clean=True citations=2 referenced=2
  expected_ids=['00d855d4747048dda6da29b95e300646::구간 28', '1141dfe95b47437fb09b5a88aace0e28::구간 20', '00d855d4747048dda6da29b95e300646::구간 29', 'cae8e105770b432c9cba14d3f73e7915::구간 79']
  current_ids=['00d855d4747048dda6da29b95e300646::구간 28', '1141dfe95b47437fb09b5a88aace0e28::구간 20']

## Citation Panel Issues

- `five_year_employee_contract_review_01_11017db6` [contract_review] citations=5 referenced=0 query=계약서에 명시된 위약금 조항의 적용 범위와 절차는 어떻게 되나요
- `five_year_employee_contract_review_03_d92271d8` [contract_review] citations=5 referenced=0 query=대금 지급을 위한 증빙이 누락될 경우 어떤 절차를 따라야 하나요
