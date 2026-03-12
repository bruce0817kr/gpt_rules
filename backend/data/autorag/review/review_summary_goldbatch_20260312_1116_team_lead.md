# Gold Review Summary goldbatch_20260312_1116_team_lead

- Candidate file: `/app/data/autorag/candidates/candidate_cases_team_lead_goldbatch_20260312_1116_team_lead.json`
- Review queue: `/app/data/autorag/review/review_queue_goldbatch_20260312_1116_team_lead.json`
- Total candidates: 18
- Suggested `review_new`: 18
- Suggested `review_edit`: 0
- Suggested `merge_or_skip`: 0

## Review Guide

- `review_new`: seed 질문과 겹침이 낮아 새 gold 후보로 우선 검토할 만한 질문
- `review_edit`: 일부 중복/표현 겹침이 있어 wording 조정 후 유지할 가능성이 높은 질문
- `merge_or_skip`: seed 또는 다른 후보와 매우 비슷해 통합 검토가 필요한 질문

## audit_response

- `team_lead_audit_response_01_961aa331` [review_new] 증빙 서류가 부족할 경우 감사에서 어떤 문제와 리스크가 발생할 수 있는지 알고 싶습니다
  categories=['rule', 'guide'] note=증빙 부족 시 감사 대응 방안을 명확히 할 필요가 있습니다.
  seed_overlap=0.1452 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.1864 peer_target=team_lead_audit_response_03_8e2e9acb: 감사에서 환수 위험을 줄이기 위해 사후 보완으로 어떤 절차와 문서가 필요할지 확인하고 싶습니다
  shared_keywords(seed)=['부족할', '어떤'] shared_keywords(peer)=['감사에서', '싶습니다', '어떤']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 70; [2-3] 감사 규정(2021.09.28.) / 구간 114
- `team_lead_audit_response_02_bc26f79b` [review_new] 법인카드 사용 내역 중 일부가 누락된 경우 어떤 보완 조치를 취해야 하며, 이에 대한 책임은 어떻게 나누어지나요
  categories=['rule', 'guide'] note=법인카드 사용에 따른 책임 소재를 분명히 하는 것이 중요합니다.
  seed_overlap=0.1553 seed_target=corp_card_policy: 법인카드 사용 제한과 증빙 보관 기준을 알려줘
  peer_overlap=0.1300 peer_target=team_lead_audit_response_01_961aa331: 증빙 서류가 부족할 경우 감사에서 어떤 문제와 리스크가 발생할 수 있는지 알고 싶습니다
  shared_keywords(seed)=['법인카드', '사용'] shared_keywords(peer)=['경우', '어떤']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 362; [2-10] 재무회계 규정(2022.9.26.) / 구간 219
- `team_lead_audit_response_03_8e2e9acb` [review_new] 감사에서 환수 위험을 줄이기 위해 사후 보완으로 어떤 절차와 문서가 필요할지 확인하고 싶습니다
  categories=['rule', 'guide'] note=환수 위험을 미연에 방지하기 위한 절차를 이해하는 것이 필수적입니다.
  seed_overlap=0.1409 seed_target=audit_missing_evidence: 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘
  peer_overlap=0.1864 peer_target=team_lead_audit_response_01_961aa331: 증빙 서류가 부족할 경우 감사에서 어떤 문제와 리스크가 발생할 수 있는지 알고 싶습니다
  shared_keywords(seed)=['어떤', '위해'] shared_keywords(peer)=['감사에서', '싶습니다', '어떤']
  bootstrap_titles=[2-3] 감사 규정(2021.09.28.) / 구간 135; [2-3] 감사 규정(2021.09.28.) / 구간 33
- `team_lead_audit_response_04_ec9b261d` [review_new] 사업비 정산 후 사후 보완이 필요할 경우, 이를 위한 승인 절차와 책임자가 누구인지 알고 싶습니다
  categories=['rule', 'guide'] note=정산 관련 절차와 책임자를 확인하여 체계적인 대응이 가능합니다.
  seed_overlap=0.1667 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.2778 peer_target=team_lead_standard_01_4a765575: 사업비 집행을 위한 세부 승인 절차와 책임자는 누구인지 확인할 수 있을까요
  shared_keywords(seed)=['사업비', '승인', '절차와'] shared_keywords(peer)=['누구인지', '사업비', '승인', '위한', '절차와']
  bootstrap_titles=[3-1] 재무회계 규칙(2025.11.24.) / 구간 27; [2-10] 재무회계 규정(2022.9.26.) / 구간 281

## contract_review

- `team_lead_contract_review_01_c880b846` [review_new] 계약 변경 시 책임 분기와 위약 조항에 대한 명확한 기준을 알고 싶습니다
  categories=['rule', 'guide'] note=이 질문은 계약 변경에 따른 리스크를 사전에 파악하기 위해 중요합니다.
  seed_overlap=0.1833 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.2353 peer_target=team_lead_standard_02_b036285e: 계약 검토 중에 발생할 수 있는 리스크와 예외 조항에 대해 알고 싶습니다
  shared_keywords(seed)=['계약', '변경'] shared_keywords(peer)=['계약', '싶습니다', '알고', '조항에']
  bootstrap_titles=[3-23] 중소기업 E-비즈니스 정보화지원사업 운영규칙(2017.8.24.) / 구간 29; [3-23] 중소기업 E-비즈니스 정보화지원사업 운영규칙(2017.8.24.) / 구간 28
- `team_lead_contract_review_02_cee5c814` [review_new] 서류 누락 시 대금 지급에 어떤 영향이 있는지와 이를 방지하기 위한 준수 사항은 무엇인지 확인할 수 있을까요
  categories=['rule', 'law'] note=서류 누락의 리스크를 미리 인지하고 대처하자는 취지의 질문입니다.
  seed_overlap=0.0500 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.1053 peer_target=team_lead_standard_01_4a765575: 사업비 집행을 위한 세부 승인 절차와 책임자는 누구인지 확인할 수 있을까요
  shared_keywords(seed)=[] shared_keywords(peer)=['위한', '확인할']
  bootstrap_titles=[2-8] 문서 관리 규정(2025.12.24.) / 구간 44
- `team_lead_contract_review_03_e3e898f5` [review_new] 계약 검토 시 유의해야 할 예외 조항과 그에 따른 책임 소재는 어떻게 되는지 설명해 주세요
  categories=['guide', 'law'] note=예외 조항을 명확히 해두어 리스크를 줄이는 것이 필요합니다.
  seed_overlap=0.1750 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.1667 peer_target=team_lead_procurement_bid_02_14446d9a: 계약 체결 후 검수 과정에서 발생할 수 있는 리스크와 그에 따른 책임은 어떻게 되나요
  shared_keywords(seed)=['계약', '조항과'] shared_keywords(peer)=['계약', '그에', '따른']
  bootstrap_titles=지방자치단체를 당사자로 하는 계약에 관한 법률 / 구간 5

## hr_admin

- `team_lead_hr_admin_01_d65bed73` [review_new] 휴가 대체 승인 시, 어떤 절차를 통해 승인되며, 누구에게 보고해야 하나요
  categories=['rule', 'guide'] note=휴가 대체 승인 절차를 이해하는 것은 업무 연속성을 유지하는 데 중요합니다.
  seed_overlap=0.1214 seed_target=hr_leave_process: 연차휴가 사용 절차와 승인 흐름을 알려줘
  peer_overlap=0.1611 peer_target=team_lead_hr_admin_02_7c3226bf: 직원 징계 시, 법적 요건과 내부 지침에 따라 어떤 절차를 따라야 하는지 확인할 수 있나요
  shared_keywords(seed)=['승인'] shared_keywords(peer)=['어떤', '절차를']
  bootstrap_titles=[2-4] 인사 관리 규정(2025.10.24.) / 구간 199; [3-25] 공무직 근로자 관리규칙(2026.1.2.) / 구간 144
- `team_lead_hr_admin_02_7c3226bf` [review_new] 직원 징계 시, 법적 요건과 내부 지침에 따라 어떤 절차를 따라야 하는지 확인할 수 있나요
  categories=['rule', 'law'] note=징계 절차의 법적 요건을 아는 것은 리스크 관리에 중요합니다.
  seed_overlap=0.1125 seed_target=hr_discipline_notice: 징계 절차에서 사전 통지와 소명 기회가 필요한지 알려줘
  peer_overlap=0.1611 peer_target=team_lead_hr_admin_01_d65bed73: 휴가 대체 승인 시, 어떤 절차를 통해 승인되며, 누구에게 보고해야 하나요
  shared_keywords(seed)=['징계'] shared_keywords(peer)=['어떤', '절차를']
  bootstrap_titles=[3-5] 인사 관리 규칙(2026.1.23.) / 구간 172; [3-25] 공무직 근로자 관리규칙(2026.1.2.) / 구간 252
- `team_lead_hr_admin_03_630e37ec` [review_new] 승진 심사에서 누가 최종 결정을 내리며, 그 과정에서 어떤 리스크 요소를 고려해야 하나요
  categories=['rule', 'guide'] note=승진 심사의 결정 구조를 파악하여 공정성을 확보하는 것이 필요합니다.
  seed_overlap=0.1167 seed_target=hr_promotion_years: 직급별 승진 소요년수를 표로 정리해줘
  peer_overlap=0.1500 peer_target=team_lead_hr_admin_01_d65bed73: 휴가 대체 승인 시, 어떤 절차를 통해 승인되며, 누구에게 보고해야 하나요
  shared_keywords(seed)=['승진'] shared_keywords(peer)=['어떤', '하나요']
  bootstrap_titles=[2-4] 인사 관리 규정(2025.10.24.) / 구간 105; [2-4] 인사 관리 규정(2025.10.24.) / 구간 104

## procurement_bid

- `team_lead_procurement_bid_01_cb6d024a` [review_new] 입찰 절차에서 필요한 비교견적 제출 기준과 누가 검토하는지 알고 싶습니다
  categories=['rule', 'guide'] note=비교견적 제출 기준을 명확히 하고 검토자의 책임을 확인하기 위해 중요합니다.
  seed_overlap=0.0714 seed_target=hr_discipline_notice: 징계 절차에서 사전 통지와 소명 기회가 필요한지 알려줘
  peer_overlap=0.1250 peer_target=team_lead_standard_02_b036285e: 계약 검토 중에 발생할 수 있는 리스크와 예외 조항에 대해 알고 싶습니다
  shared_keywords(seed)=['절차에서'] shared_keywords(peer)=['싶습니다', '알고']
  bootstrap_titles=[2-10] 재무회계 규정(2022.9.26.) / 구간 301; [2-10] 재무회계 규정(2022.9.26.) / 구간 341
- `team_lead_procurement_bid_02_14446d9a` [review_new] 계약 체결 후 검수 과정에서 발생할 수 있는 리스크와 그에 따른 책임은 어떻게 되나요
  categories=['rule', 'law'] note=검수에서의 리스크와 책임을 확인하여 사전 예방 조치를 마련하기 위해 필요합니다.
  seed_overlap=0.0714 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.1875 peer_target=team_lead_standard_02_b036285e: 계약 검토 중에 발생할 수 있는 리스크와 예외 조항에 대해 알고 싶습니다
  shared_keywords(seed)=['계약'] shared_keywords(peer)=['계약', '리스크와', '발생할']
  bootstrap_titles=국가를 당사자로 하는 계약에 관한 법률 / 구간 150; 국가를 당사자로 하는 계약에 관한 법률 / 구간 156
- `team_lead_procurement_bid_03_a03c7410` [review_new] 예정가격 결정 시 어떤 규정을 따르며, 그에 대한 검토 책임자는 누구인지 궁금합니다
  categories=['rule', 'guide'] note=예정가격 결정 기준과 검토 책임자를 명확히 하여 계약과정을 방지하는 데 중요한 질문입니다.
  seed_overlap=0.0500 seed_target=procurement_quote_rule: 구매 시 비교견적이나 입찰이 필요한 기준을 정리해줘
  peer_overlap=0.1111 peer_target=team_lead_standard_01_4a765575: 사업비 집행을 위한 세부 승인 절차와 책임자는 누구인지 확인할 수 있을까요
  shared_keywords(seed)=[] shared_keywords(peer)=['누구인지', '책임자는']
  bootstrap_titles=[3-1] 재무회계 규칙(2025.11.24.) / 구간 85; [3-1] 재무회계 규칙(2025.11.24.) / 구간 264

## project_management

- `team_lead_project_management_01_1afb2788` [review_new] 사업비 집행 후 결과보고 시 누가 최종 승인권자인지와 보고 주기는 어떻게 되는지 확인할 수 있을까요
  categories=['rule', 'guide'] note=결과보고와 관련된 승인 프로세스를 명확히 하려는 목적입니다.
  seed_overlap=0.2643 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.1452 peer_target=team_lead_project_management_03_10c6581b: 사업비 집행 일정을 계획할 때 고려해야 할 승인 절차와 그것이 프로젝트에 미치는 영향을 알고 싶습니다
  shared_keywords(seed)=['결과보고', '사업비', '집행'] shared_keywords(peer)=['사업비', '집행']
  bootstrap_titles=[2-11] 사업관리 규정(2003.3.20.) / 구간 64; [3-1] 재무회계 규칙(2025.11.24.) / 구간 103
- `team_lead_project_management_02_4a3fafe5` [review_new] 사업비 정산 시 필요한 증빙 서류와, 누락 시 발생할 수 있는 리스크는 무엇인지 알아야 할까요
  categories=['rule', 'notice'] note=정산 과정에서의 증빙 중요성을 강조하기 위한 질문입니다.
  seed_overlap=0.1167 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.1056 peer_target=team_lead_project_management_01_1afb2788: 사업비 집행 후 결과보고 시 누가 최종 승인권자인지와 보고 주기는 어떻게 되는지 확인할 수 있을까요
  shared_keywords(seed)=['사업비'] shared_keywords(peer)=['사업비']
  bootstrap_titles=[2-12] 여비 규정(2023.12.21.) / 구간 12; [2-10] 재무회계 규정(2022.9.26.) / 구간 70
- `team_lead_project_management_03_10c6581b` [review_new] 사업비 집행 일정을 계획할 때 고려해야 할 승인 절차와 그것이 프로젝트에 미치는 영향을 알고 싶습니다
  categories=['rule', 'guide'] note=일정 관리에서 승인 절차의 중요성을 인식하기 위한 질문입니다.
  seed_overlap=0.3000 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.2273 peer_target=team_lead_audit_response_04_ec9b261d: 사업비 정산 후 사후 보완이 필요할 경우, 이를 위한 승인 절차와 책임자가 누구인지 알고 싶습니다
  shared_keywords(seed)=['사업비', '승인', '절차와', '집행'] shared_keywords(peer)=['사업비', '승인', '싶습니다', '알고', '절차와']
  bootstrap_titles=[2-11] 사업관리 규정(2003.3.20.) / 구간 57; [2-10] 재무회계 규정(2022.9.26.) / 구간 106

## standard

- `team_lead_standard_01_4a765575` [review_new] 사업비 집행을 위한 세부 승인 절차와 책임자는 누구인지 확인할 수 있을까요
  categories=['rule', 'guide'] note=정확한 승인 절차와 책임 소재 파악이 필수적이므로
  seed_overlap=0.2308 seed_target=project_expense_flow: 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘
  peer_overlap=0.2778 peer_target=team_lead_audit_response_04_ec9b261d: 사업비 정산 후 사후 보완이 필요할 경우, 이를 위한 승인 절차와 책임자가 누구인지 알고 싶습니다
  shared_keywords(seed)=['사업비', '승인', '절차와'] shared_keywords(peer)=['누구인지', '사업비', '승인', '위한', '절차와']
  bootstrap_titles=[2-11] 사업관리 규정(2003.3.20.) / 구간 13; [2-11] 사업관리 규정(2003.3.20.) / 구간 55
- `team_lead_standard_02_b036285e` [review_new] 계약 검토 중에 발생할 수 있는 리스크와 예외 조항에 대해 알고 싶습니다
  categories=['rule', 'guide'] note=리스크 관리와 예외 사항 확인이 계약의 안전성을 높이기 때문
  seed_overlap=0.0667 seed_target=contract_risk_review: 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘
  peer_overlap=0.2353 peer_target=team_lead_contract_review_01_c880b846: 계약 변경 시 책임 분기와 위약 조항에 대한 명확한 기준을 알고 싶습니다
  shared_keywords(seed)=['계약'] shared_keywords(peer)=['계약', '싶습니다', '알고', '조항에']
  bootstrap_titles=[3-1] 재무회계 규칙(2025.11.24.) / 구간 87; [2-10] 재무회계 규정(2022.9.26.) / 구간 355
