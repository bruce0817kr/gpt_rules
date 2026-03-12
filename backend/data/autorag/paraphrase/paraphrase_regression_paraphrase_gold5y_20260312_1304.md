# Paraphrase Regression Report paraphrase_gold5y_20260312_1304

- Review queue: `/app/data/autorag/review/review_queue_gold5y_20260312_0917.json`
- Total rows: 18
- ok: 9
- needs_review: 9
- high_risk: 0

## By Mode

- `audit_response` ok=2 needs_review=2 high_risk=0
- `contract_review` ok=2 needs_review=1 high_risk=0
- `hr_admin` ok=3 needs_review=0 high_risk=0
- `procurement_bid` ok=1 needs_review=2 high_risk=0
- `project_management` ok=0 needs_review=3 high_risk=0
- `standard` ok=1 needs_review=1 high_risk=0

## High Risk Cases

- none

## Needs Review Cases

- `five_year_employee_audit_response_01_7469eb85` [audit_response] 법인카드 사용 후 증빙 서류는 어떤 형식으로 제출해야 하며, 누락 시 어떤 위험이 있을까요
  status=needs_review template=corp_card_policy confidence=low similarity=0.5057 retrieval_f1=0.6667
  citation_panel_clean=True citations=4 referenced=4
  expected_ids=['cae8e105770b432c9cba14d3f73e7915::구간 362', '877ad38b63324f48953489f933e61ca2::구간 12', 'cae8e105770b432c9cba14d3f73e7915::구간 219', 'ac1edc218c3347b5859d4c56e94a067b::구간 45']
  current_ids=['cae8e105770b432c9cba14d3f73e7915::구간 219', 'cae8e105770b432c9cba14d3f73e7915::구간 363', '877ad38b63324f48953489f933e61ca2::구간 12', 'cae8e105770b432c9cba14d3f73e7915::구간 70']
- `five_year_employee_project_management_03_1e783e09` [project_management] 정산 과정에서 보완해야 할 서류나 절차가 있다면 어떤 것들이 있나요
  status=needs_review template=- confidence=low similarity=0.5182 retrieval_f1=0.5714
  citation_panel_clean=True citations=2 referenced=2
  expected_ids=['877ad38b63324f48953489f933e61ca2::구간 12', 'cae8e105770b432c9cba14d3f73e7915::구간 271', 'cae8e105770b432c9cba14d3f73e7915::구간 277', 'cae8e105770b432c9cba14d3f73e7915::구간 71']
  current_ids=['877ad38b63324f48953489f933e61ca2::구간 12', 'cae8e105770b432c9cba14d3f73e7915::구간 71']
- `five_year_employee_procurement_bid_03_fe5f284e` [procurement_bid] 계약 체결 전 검토해야 할 주요 조항과 해당 조항의 위험 요소는 무엇인가요
  status=needs_review template=- confidence=low similarity=0.5210 retrieval_f1=0.8889
  citation_panel_clean=True citations=4 referenced=4
  expected_ids=['7dc540f5efd6451c903a515e960ffc23::구간 56', 'f6f2c8b2e0df4d65a382daafa6e41560::구간 76', '99f005f4ecc74f57bcb4476f081b4c19::구간 576', '99f005f4ecc74f57bcb4476f081b4c19::구간 445']
  current_ids=['7dc540f5efd6451c903a515e960ffc23::구간 56', 'f6f2c8b2e0df4d65a382daafa6e41560::구간 76', '99f005f4ecc74f57bcb4476f081b4c19::구간 576', '99f005f4ecc74f57bcb4476f081b4c19::구간 445']
- `five_year_employee_audit_response_03_7113aa6a` [audit_response] 사업비 정산 시 필수로 제출해야 하는 증빙 서류 목록은 무엇인지 확인할 수 있을까요
  status=needs_review template=- confidence=low similarity=0.5995 retrieval_f1=0.7692
  citation_panel_clean=True citations=5 referenced=5
  expected_ids=['877ad38b63324f48953489f933e61ca2::구간 12', 'ac1edc218c3347b5859d4c56e94a067b::구간 10', 'cae8e105770b432c9cba14d3f73e7915::구간 69', 'cae8e105770b432c9cba14d3f73e7915::구간 56']
  current_ids=['877ad38b63324f48953489f933e61ca2::구간 12', 'ac1edc218c3347b5859d4c56e94a067b::구간 10', 'cae8e105770b432c9cba14d3f73e7915::구간 69', 'cae8e105770b432c9cba14d3f73e7915::구간 70']
- `five_year_employee_project_management_01_3710ec10` [project_management] 사업비 집행 전 반드시 확인해야 할 증빙 서류 목록은 무엇인가요
  status=needs_review template=- confidence=low similarity=0.6567 retrieval_f1=0.5455
  citation_panel_clean=True citations=3 referenced=3
  expected_ids=['ac1edc218c3347b5859d4c56e94a067b::구간 10', 'cae8e105770b432c9cba14d3f73e7915::구간 69', '1141dfe95b47437fb09b5a88aace0e28::구간 26', 'ac1edc218c3347b5859d4c56e94a067b::구간 45']
  current_ids=['ac1edc218c3347b5859d4c56e94a067b::구간 10', 'cae8e105770b432c9cba14d3f73e7915::구간 69', 'cae8e105770b432c9cba14d3f73e7915::구간 70']
- `five_year_employee_procurement_bid_01_e0e33251` [procurement_bid] 입찰에 필요한 비교견적 제출 시 요구되는 서류 목록은 무엇인가요
  status=needs_review template=procurement_quote_rule confidence=low similarity=0.9908 retrieval_f1=0.7692
  citation_panel_clean=True citations=5 referenced=5
  expected_ids=['3aa3e8b396504bbda35e8b958a163f4a::구간 73', 'cae8e105770b432c9cba14d3f73e7915::구간 56', '8e169ef54945417a9cf4799722f7f0c4::구간 68', 'a116034c047b4c3fb897903f9598593d::구간 14']
  current_ids=['3aa3e8b396504bbda35e8b958a163f4a::구간 73', 'cae8e105770b432c9cba14d3f73e7915::구간 341', 'cae8e105770b432c9cba14d3f73e7915::구간 56', 'a116034c047b4c3fb897903f9598593d::구간 14']
- `five_year_employee_project_management_02_73f9ae43` [project_management] 결과보고 시 포함해야 할 주요 항목과 제출 기한은 어떻게 되나요
  status=needs_review template=project_result_report_timeline confidence=low similarity=0.9949 retrieval_f1=0.7500
  citation_panel_clean=True citations=3 referenced=3
  expected_ids=['214a173629da433d8b4d97fba5032780::구간 64', '43309a76ff174026a8c9b330a7485f53::구간 422', 'cae8e105770b432c9cba14d3f73e7915::구간 273', '3aa3e8b396504bbda35e8b958a163f4a::구간 94']
  current_ids=['214a173629da433d8b4d97fba5032780::구간 64', '43309a76ff174026a8c9b330a7485f53::구간 422', 'cae8e105770b432c9cba14d3f73e7915::구간 273']
- `five_year_employee_standard_01_2f2855b6` [standard] 교육훈련 규칙에 따라 직원 교육 계획 수립 시 반드시 포함해야 할 항목은 무엇인가요
  status=needs_review template=training_plan_items confidence=low similarity=1.0000 retrieval_f1=0.5714
  citation_panel_clean=True citations=2 referenced=2
  expected_ids=['99f005f4ecc74f57bcb4476f081b4c19::구간 270', 'dcccf0db3cf44121a69a2dea53ac0003::구간 8', 'dcccf0db3cf44121a69a2dea53ac0003::구간 30', 'dcccf0db3cf44121a69a2dea53ac0003::구간 14']
  current_ids=['99f005f4ecc74f57bcb4476f081b4c19::구간 270', 'dcccf0db3cf44121a69a2dea53ac0003::구간 8']
- `five_year_employee_contract_review_02_80f5ca27` [contract_review] 계약 변경 사항을 승인받기 위해 반드시 첨부해야 하는 서류는 무엇인가요
  status=needs_review template=contract_change_review confidence=low similarity=1.0000 retrieval_f1=0.5714
  citation_panel_clean=True citations=2 referenced=2
  expected_ids=['00d855d4747048dda6da29b95e300646::구간 28', '1141dfe95b47437fb09b5a88aace0e28::구간 20', '00d855d4747048dda6da29b95e300646::구간 29', 'cae8e105770b432c9cba14d3f73e7915::구간 79']
  current_ids=['00d855d4747048dda6da29b95e300646::구간 28', '1141dfe95b47437fb09b5a88aace0e28::구간 20']

## Citation Panel Issues

- none
