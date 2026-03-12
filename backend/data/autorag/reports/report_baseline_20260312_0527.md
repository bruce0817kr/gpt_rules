# Ralph Loop Report baseline_20260312_0527

- Generated at (UTC): 2026-03-11T20:27:28.189859+00:00
- Retrieval F1 with reranker: 0.9712
- Retrieval F1 without reranker: 0.5452
- Generation BLEU: 39.0314
- Generation ROUGE: 0.4327

## Interpretation

- `BAAI/bge-reranker-v2-m3` materially improves retrieval quality over vector-only ranking.
- Current priority is improving low-ROUGE generation cases while preserving retrieval gains.

## Weakest Generation Cases

- `audit_missing_evidence` 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘.
  mode=audit_response categories=['rule' 'guide' 'law'] rouge=0.1905 bleu=18.7745
- `contract_risk_review` 계약 변경 시 반드시 검토해야 할 조항과 위험 포인트를 알려줘.
  mode=contract_review categories=['rule' 'guide' 'law'] rouge=0.2286 bleu=15.9835
- `project_expense_flow` 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘.
  mode=project_management categories=['rule' 'guide' 'notice'] rouge=0.4167 bleu=54.8531

## Weakest Retrieval Cases

- `procurement_quote_rule` 구매 시 비교견적이나 입찰이 필요한 기준을 정리해줘.
  reranker_on_f1=0.7692 reranker_off_f1=0.6364
- `hr_promotion_years` 직급별 승진 소요년수를 표로 정리해줘.
  reranker_on_f1=1.0000 reranker_off_f1=0.5000
- `hr_leave_process` 연차휴가 사용 절차와 승인 흐름을 알려줘.
  reranker_on_f1=1.0000 reranker_off_f1=0.0000

## Biggest Reranker Gains

- `hr_leave_process` 연차휴가 사용 절차와 승인 흐름을 알려줘.
  reranker_on_f1=1.0000 reranker_off_f1=0.0000
- `project_expense_flow` 사업비 집행 전에 확인해야 할 승인 절차와 결과보고 항목을 알려줘.
  reranker_on_f1=1.0000 reranker_off_f1=0.4000
- `audit_missing_evidence` 감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘.
  reranker_on_f1=1.0000 reranker_off_f1=0.4000

## Next Actions

- Tune prompt structure for the weakest generation cases.
- Expand the reviewed seed set beyond the current bootstrap 8 questions.
- Keep `BAAI/bge-reranker-v2-m3` as the default reranker because retrieval quality is substantially higher with it enabled.
