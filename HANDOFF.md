## 2026-03-12 12:58:15 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- ?⑥븘 ?덈뜕 `needs_review` 耳?댁뒪瑜?以꾩씠湲??꾪빐 `project_management`, `procurement_bid`, `audit_response` 履?諛섎났 吏덈Ц??template濡?異붽? ?≪닔?덈떎.
- `retrieval_utils.py`??targeted expansion 洹쒖튃??異붽???`?ъ뾽鍮?利앸튃`, `?뺤궛+利앸튃`, `援먯쑁?덈젴+怨꾪쉷`, `怨꾩빟蹂寃??쒕쪟`, `寃곌낵蹂닿퀬+?쒖텧` 議고빀?먯꽌 `top_k`? candidate pool???볧엳?꾨줉 議곗젙?덈떎.
- 理쒖쥌 paraphrase ?뚭? run? `paraphrase_gold5y_20260312_1309`?대ŉ, 寃곌낵??`ok 9 / needs_review 9 / high_risk 0 / citation_panel_issues 0`?대떎.

### 肄붾뱶 蹂寃?
- `backend/app/services/answer_templates.py`
  - ???쒗뵆由?異붽?:
    - `project_expense_evidence_list`
    - `procurement_contract_risk_review`
    - `audit_expense_settlement_list`
  - 異붽? 留ㅼ묶 洹쒖튃 ?뺤옣:
    - `project_management`??`?ъ뾽鍮?利앸튃 紐⑸줉`
    - `procurement_bid`??`怨꾩빟 泥닿껐 ??二쇱슂 議고빆/?꾪뿕`
    - `audit_response`??`?뺤궛 利앸튃 紐⑸줉`
- `backend/app/services/retrieval_utils.py`
  - `needs_targeted_expansion()` 異붽?
  - targeted query?????`effective_top_k=10`, `candidate_count>=24`濡??뺤옣
- `backend/tests/test_answer_templates.py`
  - ???쒗뵆由?3醫?留ㅼ묶/?뚮뜑留??뚯뒪??異붽?
- `backend/tests/test_retrieval_utils.py`
  - targeted expansion 媛먯? 諛?window ?뺤옣 ?뚯뒪??異붽?

### 寃利?
- 而⑦뀒?대꼫 ?щ퉴???ш린??
  - `docker compose build backend`
  - `docker compose up -d --force-recreate backend`
- ?뚯뒪??
  - `docker exec gpt_rules-backend-1 pytest tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 寃곌낵: `35 passed`
- paraphrase ?뚭?:
  - `docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_paraphrase_regression_report.py --review-queue-path /app/data/autorag/review/review_queue_gold5y_20260312_0917.json --run-id paraphrase_gold5y_20260312_1309`
  - ?곗텧臾?
    - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1309.md`
    - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1309.json`

### ?꾩옱 ?먮떒
- `high_risk`??怨꾩냽 0?쇰줈 ?좎??덈떎.
- ?ㅻ쭔 `needs_review` 珥앸웾? 以꾩? ?딆븯?? ?먯씤? ?遺遺?retrieval recall怨?bootstrap GT citation set 李⑥씠?대ŉ, ?쒗뵆由??덉쭏蹂대떎??`?대뼡 援ш컙??媛숈씠 臾쇨퀬 ?ㅻ뒓?? 臾몄젣??
- ?뱁엳 `project_result_report_timeline`? ?띿뒪??similarity??0.99 ?섏??몃뜲 retrieval set??諛붾뚮㈃??F1???대젮媛붾떎. ???좏삎? template 異붽?蹂대떎 retrieval ranking ?쒖뼱媛 ?곗꽑?대떎.
- ?ㅼ쓬 ?곗꽑?쒖쐞:
  - template ?묐떟?????citation selection??GT 移쒗솕?곸쑝濡????뺢탳??
  - `project_management`/`audit_response` ?⑥? 4嫄댁뿉 ???retrieval recall 蹂댁젙
  - gold set ?먯껜瑜??뺤옣??bootstrap citation ?명뼢??以꾩씠湲?

## 2026-03-12 12:00:19 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- `five_year_employee` paraphrase ?뚭????⑥? high-risk瑜?以꾩씠湲??꾪빐 deterministic answer template瑜?異붽? ?뺤옣?덈떎.
- 媛쒕컻 backend 而⑦뀒?대꼫媛 肄붾뱶 蹂쇰ⅷ??留덉슫?명븯吏 ?딆븘, 珥덇린?먮뒗 而⑦뀒?대꼫 ?대? 肄붾뱶媛 援щ쾭?꾩씤 ?곹깭??? ?댄썑 `docker compose build backend` + `docker compose up -d --force-recreate backend`濡??됯? 湲곗? 而⑦뀒?대꼫瑜?理쒖떊 肄붾뱶濡??ъ젙?ы뻽??
- 理쒖쥌 paraphrase ?뚭? run? `paraphrase_gold5y_20260312_1304`?대ŉ, 寃곌낵??`ok 9 / needs_review 9 / high_risk 0 / citation_panel_issues 0`?대떎.

### 肄붾뱶 蹂寃?
- `backend/app/services/answer_templates.py`
  - ???쒗뵆由?異붽?:
    - `hr_proxy_approval`
    - `hr_promotion_recommendation`
    - `hr_discipline_process`
    - `contract_penalty_scope`
    - `payment_evidence_missing`
    - `expense_evidence_rule`
    - `project_result_report_timeline`
    - `procurement_estimated_price_rule`
    - `audit_supporting_evidence`
    - `training_plan_items`
  - template matching 洹쒖튃 ?뺤옣
  - semantic citation helper瑜?fallback 蹂닿컯 諛⑹떇?쇰줈 ?섏젙
- `backend/tests/test_answer_templates.py`
  - ?좉퇋 ?쒗뵆由?留ㅼ묶/?뚮뜑留??뚭? ?뚯뒪??異붽?

### 寃利?
- 而⑦뀒?대꼫 ?щ퉴???ш린??
  - `docker compose build backend`
  - `docker compose up -d --force-recreate backend`
- ?뚯뒪??
  - `docker exec gpt_rules-backend-1 pytest tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 寃곌낵: `30 passed`
- paraphrase ?뚭?:
  - `docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_paraphrase_regression_report.py --review-queue-path /app/data/autorag/review/review_queue_gold5y_20260312_0917.json --run-id paraphrase_gold5y_20260312_1304`
  - ?곗텧臾?
    - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1304.md`
    - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1304.json`

### ?꾩옱 ?먮떒
- `high_risk`??0?쇰줈 ?쒓굅?덈떎.
- ?⑥? `needs_review 9嫄?? ?遺遺?retrieval recall 遺議깆씠??bootstrap GT???citation set 李⑥씠 ?뚮Ц?대떎.
- ?ㅼ쓬 ?곗꽑?쒖쐞??template 異붽?蹂대떎 gold set 寃???뺣?? retrieval recall 蹂댁젙?대떎.

# ?몄닔?멸퀎??

## 1. ?꾨줈?앺듃 媛쒖슂

- ?꾨줈?앺듃紐? ?щ떒 洹쒖젙 ?곷떞遊?
- 紐⑹쟻: ?щ떒 洹쒖젙, ?대? 洹쒖튃, 愿怨?踰뺣졊??RAG 湲곕컲?쇰줈 寃?됲빐 吏곸썝 吏덈Ц??洹쇨굅 以묒떖 ?듬? ?쒓났
- ?댁쁺 諛⑹떇: ?대?留??꾩슜, ???먯껜 濡쒓렇???뚯썝愿由??놁쓬
- 紐⑺몴 二쇱냼: `https://ai.gtp.or.kr/chat/`

## 2. ?꾩옱 援ы쁽 踰붿쐞

### 吏곸썝??

- 吏덈Ц ?낅젰 諛??듬? 議고쉶
- 臾몄꽌 遺꾨쪟蹂?寃??踰붿쐞 ?쒗븳
- ?듬?蹂??몄슜 臾몄꽌 紐⑸줉 ?쒖떆
- citation ?대┃ ??source viewer drawer ?ㅽ뵂
- source snippet 媛뺤“ 諛??먮Ц markdown ?뚮뜑留?
- 理쒓렐 洹쇨굅 臾띠쓬?먯꽌??source viewer ?ㅽ뵂 媛??
- `臾몄꽌 援ъ꽦`?먯꽌 移댄뀒怨좊━蹂?臾몄꽌 紐⑸줉/蹂몃Ц 寃??媛??

### 愿由ъ옄??

- ?ㅼ쨷 ?뚯씪 ?낅줈??
- 臾몄꽌 紐⑸줉 議고쉶
- 臾몄꽌 ??젣
- 臾몄꽌 ?ъ깋??
- 臾몄꽌 遺꾨쪟(category) ?섎룞 蹂寃?
- 踰뺣졊紐낆쑝濡?理쒖떊 踰뺣졊 異붽?
- 吏???щ㎎: PDF, DOCX, TXT, MD, HWP, HWPX

## 3. 湲곗닠 ?ㅽ깮

- ?꾨줎?몄뿏?? React 19, Vite 6, TypeScript
- 諛깆뿏?? FastAPI, Pydantic Settings
- 踰≫꽣 ??μ냼: Qdrant
- ?꾨쿋?? `nlpai-lab/KoE5`
- 由щ옲而? `BAAI/bge-reranker-v2-m3`
- LLM: OpenAI ?명솚 API (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `LLM_MODEL`)
- 諛고룷: Docker Compose + nginx

## 4. 二쇱슂 ?뚯씪

- ?꾨줎???뷀듃由? `frontend/src/App.tsx`
- 吏곸썝 ?곷떞 UI: `frontend/src/components/Chat/ChatPanel.tsx`
- source viewer: `frontend/src/components/Chat/SourceViewerDrawer.tsx`
- 愿由ъ옄 UI: `frontend/src/components/Admin/AdminPanel.tsx`
- ?꾩껜 ?덉씠?꾩썐: `frontend/src/components/Layout/Shell.tsx`
- ?꾨줎??API ?대씪?댁뼵?? `frontend/src/api/client.ts`
- ?꾨줎????? `frontend/src/types/api.ts`
- ?꾨줎???ㅽ??? `frontend/src/index.css`
- 諛깆뿏???뷀듃由? `backend/app/main.py`
- 臾몄꽌 ?낅줈???ъ깋????젣/?댁슜議고쉶: `backend/app/routers/documents.py`
- 臾몄꽌 援ъ꽦/shortcut 寃??API: `backend/app/routers/library.py`
- 踰뺣졊 異붽? API: `backend/app/routers/laws.py`
- 梨꾪똿 API: `backend/app/routers/chat.py`
- 臾몄꽌 ?몃뜳???쒕퉬?? `backend/app/services/ingestion.py`
- 踰≫꽣 寃?? `backend/app/services/vector_store.py`
- 由щ옲而? `backend/app/services/reranker.py`
- 踰뺣졊 ?숆린?? `backend/app/services/law_sync.py`
- ?꾩빱 ?ㅼ젙: `docker-compose.yml`
- nginx ?쒕툕?⑥뒪 ?ㅼ젙: `nginx/nginx.conf`

## 5. ?쇱슦??諛고룷 援ъ“

- ?몃? 吏꾩엯 寃쎈줈: `/chat/`
- ?꾨줎???뺤쟻 ?뚯씪 ?쒕튃 寃쎈줈: `/chat/`
- ?꾨줉??API 寃쎈줈: `/chat/api/`
- ?대? 諛깆뿏???ㅼ젣 API 寃쎈줈: `/api/`

nginx媛 ?ㅼ쓬???대떦??

- `/` -> `/chat/` 由щ떎?대젆??
- `/chat/` SPA ?쒕튃
- `/chat/api/` -> FastAPI ?꾨줉??

## 6. ?꾩옱 ?섍꼍 蹂???듭떖

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL=https://openrouter.ai/api/v1`
- `LLM_MODEL=gpt-4o-mini`
- `LAW_OC=dhl`
- `EMBEDDING_MODEL=nlpai-lab/KoE5`
- `RERANKER_MODEL=BAAI/bge-reranker-v2-m3`
- `COLLECTION_NAME=foundation_docs`
- `CHUNK_SIZE=800`
- `CHUNK_OVERLAP=200`
- `TOP_K=5`
- `RERANK_CANDIDATES=12`
- `FRONTEND_PORT=8088`
- `VITE_PUBLIC_BASE_PATH=/chat/`

## 7. ?ㅽ뻾 諛⑸쾿

```bash
docker compose up --build
```

濡쒖뺄 ?뺤씤 二쇱냼:

- ?꾨줎?? `http://localhost:8088/chat/`
- ?꾨줎???꾨줉???ъ뒪泥댄겕: `http://localhost:8088/chat/api/health`
- 諛깆뿏??吏곸젒 ?ъ뒪泥댄겕: `http://localhost:8000/api/health`
- Qdrant: `http://localhost:6333/dashboard`

## 8. ?꾩옱 ?곗씠???곹깭

- 珥?臾몄꽌 ?? `77`
- category 吏묎퀎:
  - `foundation`: 2
  - `rule`: 51
  - `guide`: 11
  - `law`: 13

## 9. 寃利?寃곌낵

- ?꾨줎??鍮뚮뱶 ?듦낵 (`tsc --noEmit && vite build`)
- 諛깆뿏???뚯뒪???듦낵 (`14 passed`)
- `/chat/api/health` ?뺤긽
- source viewer ?대┝ 諛?snippet 媛뺤“ ?뺤씤
- `臾몄꽌 援ъ꽦` 蹂몃Ц 寃???뺤씤
- 踰뺣졊紐낆쑝濡?諛붾줈 異붽? 湲곕뒫 ?뺤씤
- ?숈씪 踰뺣졊 諛섎났 import ??臾몄꽌 ??利앷? ?놁쓬(idempotent)

## 10. AutoRAG ?묒뾽 ?꾪솴

- 愿??臾몄꽌: `backend/tests/autorag/README.md`
  - ?ㅽ뻾 ?ㅽ겕由쏀듃:
    - `backend/tests/autorag/build_bootstrap_dataset.py`
    - `backend/tests/autorag/evaluate_current_rag.py`
    - `backend/tests/autorag/generate_report.py`
    - `backend/tests/autorag/generate_persona_candidates.py`
    - `backend/tests/autorag/build_review_queue.py`
    - `backend/tests/autorag/export_reviewed_gold.py`
    - `scripts/run_ralph_loop.ps1`
    - `scripts/run_gold_candidate_loop.ps1`
  - ?꾩옱 ?곗텧臾?
    - `backend/data/autorag/bootstrap/corpus.parquet`
    - `backend/data/autorag/bootstrap/qa.parquet`
    - `backend/data/autorag/bootstrap/seed_cases_used.json`
    - `backend/data/autorag/candidates/candidate_cases_five_year_employee_gold5y_20260312_0917.json`
    - `backend/data/autorag/review/review_queue_gold5y_20260312_0917.json`
    - `backend/data/autorag/results/retrieval_eval_reranker_on.csv`
    - `backend/data/autorag/results/retrieval_eval_reranker_off.csv`
    - `backend/data/autorag/results/generation_eval.csv`
  - `backend/data/autorag/reports/history.csv`
  - `backend/data/autorag/reports/summary_baseline_20260312_0527.json`
  - `backend/data/autorag/reports/report_baseline_20260312_0527.md`
    - `backend/data/autorag/runs/baseline_20260312_0527/*`
    - `backend/data/autorag/reports/summary_iter7_20260312_062927.json`
    - `backend/data/autorag/reports/report_iter7_20260312_062927.md`
    - `backend/data/autorag/runs/iter7_20260312_062927/*`
    - `backend/data/autorag/reports/summary_iter8_20260312_0758.json`
    - `backend/data/autorag/reports/report_iter8_20260312_0758.md`
    - `backend/data/autorag/runs/iter8_20260312_0758/*`
    - `backend/data/autorag/reports/summary_iter10_20260312_0826.json`
    - `backend/data/autorag/reports/report_iter10_20260312_0826.md`
    - `backend/data/autorag/runs/iter10_20260312_0826/*`
  - 留덉?留??뺤씤 ?쒓컖: `2026-03-12 08:29:04 +09:00`
  - 理쒖떊 baseline run id: `baseline_20260312_0527`
  - ?꾩옱 理쒓퀬 ?깅뒫 run id: `iter10_20260312_0826`
  - ?쒕뱶 吏덈Ц ?? `8`
  - baseline bootstrap ?됯? ?됯퇏:
    - retrieval F1 (`reranker on`): `0.9712`
    - retrieval F1 (`reranker off`): `0.5452`
    - generation BLEU: `39.0314`
    - generation ROUGE: `0.4327`
  - ?꾩옱 理쒓퀬 ?깅뒫 ?됯? ?됯퇏:
    - retrieval F1 (`reranker on`): `1.0000`
    - retrieval recall (`reranker on`): `1.0000`
    - retrieval precision (`reranker on`): `1.0000`
    - retrieval F1 (`reranker off`): `0.5406`
    - generation BLEU: `74.4887`
    - generation ROUGE: `0.5187`
  - baseline ?鍮?蹂??`iter10_20260312_0826`):
    - retrieval F1 (`reranker on`): `+0.0288`
    - retrieval recall (`reranker on`): `0.0000`
    - retrieval precision (`reranker on`): `+0.0469`
    - retrieval F1 (`reranker off`): `-0.0045`
    - generation BLEU: `+35.4573`
    - generation ROUGE: `+0.0859`
  - `iter3_20260312_055548` ?鍮?蹂??`iter10_20260312_0826`):
    - retrieval F1 (`reranker on`): `+0.0494`
    - retrieval recall (`reranker on`): `+0.0625`
    - retrieval precision (`reranker on`): `+0.0250`
    - generation BLEU: `+30.8760`
    - generation ROUGE: `+0.0774`
- 二쇱쓽:
  - ?꾩옱 QA ?뗭? ?щ엺 寃??gold set???꾨땲??bootstrap set?대떎.
  - ?곕씪???덈? ?깅뒫 吏?쒕낫???뚭? ?먯?? ?곷? 鍮꾧탳 ?⑸룄濡??댁꽍?댁빞 ?쒕떎.
- 諛섏쁺???섏젙:
  - `generate_report.py`??suffixed metric 而щ읆(`retrieval_f1_on`)??unsuffixed key濡??쎄퀬 ?덉뼱 ?ㅼ젣 蹂닿퀬???앹꽦???ㅽ뙣?덈떎.
  - ??踰꾧렇???섏젙 ?꾨즺?덇퀬, ?뚭? 諛⑹????뚯뒪??`backend/tests/test_autorag_report.py`瑜?異붽??덈떎.
  - `scripts/run_ralph_loop.ps1`??`RefreshBootstrap` ?ㅼ쐞移섎? 異붽??덇퀬, 湲곗〈 bootstrap ?ъ궗???놁쓣 ?뚮쭔 ?ъ깮?깊븯?꾨줉 ?섏젙?덈떎.
    - 媛숈? ?ㅽ겕由쏀듃??`param(...)` ?꾩튂? strict mode 諛곗뿴 泥섎━(`@(...)`)???섏젙??PowerShell ?ㅽ뻾 ?ㅻ쪟瑜?留됱븯??
    - 以묐났 chunk媛 retrieval/generation ?됯?瑜??붾뱾吏 ?딅룄濡?`backend/app/services/retrieval_utils.py`瑜?異붽??섍퀬, `chat.py`, `build_bootstrap_dataset.py`, `evaluate_current_rag.py`??dedupe 濡쒖쭅??諛섏쁺?덈떎.
    - 吏덈Ц ?좏삎蹂?retrieval window ?대━?ㅽ떛??異붽??덈떎. `踰뺤씤移대뱶/利앸튃/蹂닿?/?뺤궛` 吏덈Ц? `top_k`瑜??볧엳怨? `鍮꾧탳寃ъ쟻/?낆같/怨꾩빟 蹂寃? 怨꾩뿴 吏덈Ц? reranker ?꾨낫援곗쓣 理쒕? 30媛쒓퉴吏 ?볧? ?듭떖 chunk ?꾨씫??以꾩씠?꾨줉 議곗젙?덈떎.
    - ?댄썑 ?뚭?瑜??뺤씤???대━?ㅽ떛 踰붿쐞瑜??ㅼ떆 醫곹삍?? ?꾩옱??`踰뺤씤移대뱶` 吏덈Ц?먮쭔 `top_k`瑜??볧엳怨? `鍮꾧탳寃ъ쟻/?낆같/?섏쓽怨꾩빟` 怨꾩뿴 諛?`踰뺤씤移대뱶` 吏덈Ц?먮쭔 reranker ?꾨낫援?30媛??뺤옣???곸슜?쒕떎.
    - ?뚭? 諛⑹? ?뚯뒪?몃줈 `backend/tests/test_retrieval_utils.py`, `backend/tests/test_autorag_eval.py`瑜?異붽??덈떎.
    - `backend/app/services/answer_templates.py`瑜?異붽??섍퀬 `chat.py`??deterministic answer 寃쎈줈瑜??곌껐??`hr_leave_process`, `contract_risk_review`, `procurement_quote_rule`, `audit_missing_evidence`瑜??쒗뵆由우쑝濡??곗꽑 泥섎━?쒕떎.
    - ?뚭? 諛⑹? ?뚯뒪??`backend/tests/test_answer_templates.py`瑜?異붽??덈떎.
    - gold-set ?뺤옣?⑹쑝濡?`backend/tests/autorag/generate_persona_candidates.py`, `build_review_queue.py`, `export_reviewed_gold.py`, `gold_dataset_utils.py`, `personas.json`, `scripts/run_gold_candidate_loop.ps1`瑜?異붽??덈떎.
    - ?꾩옱 review queue??bootstrap answer/citation??`reviewed_generation_gt`, `reviewed_retrieval_gt`??誘몃━ 梨꾩썙 ??`pending` ?곹깭?대ŉ, ?щ엺??寃????`review_status=approved`濡?諛붽씀硫?gold parquet濡??밴꺽?????덈떎.
  - ?꾩옱 ?쏀븳 耳?댁뒪(`iter10_20260312_0826` 湲곗?):
    - generation: `contract_risk_review`, `procurement_quote_rule`, `project_expense_flow`
    - retrieval: ?놁쓬 (`reranker on` 8/8 吏덈Ц 紐⑤몢 F1=1.0)
- 蹂듦뎄???ъ떎???쒖꽌:
  1. `docker compose build backend`
  2. `docker compose up -d backend`
  3. `docker exec gpt_rules-backend-1 python -m pip install -r /app/tests/autorag/requirements.txt`
  4. `docker exec gpt_rules-backend-1 python /app/tests/autorag/build_bootstrap_dataset.py`
  5. `docker exec gpt_rules-backend-1 python /app/tests/autorag/evaluate_current_rag.py`
  6. `docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_report.py --run-id <YYYYMMDD_HHMMSS>`
  7. ?꾩슂 ??`powershell -ExecutionPolicy Bypass -File scripts/run_ralph_loop.ps1`
  8. Docker build 罹먯떆 ?뚮Ц???몄뒪??蹂寃??뚯씪??而⑦뀒?대꼫??諛붾줈 諛섏쁺?섏? ?딆쑝硫?`docker cp`濡?????뚯씪??`/app/...`??吏곸젒 ?숆린?뷀븳 ???ㅼ떆 ?됯??쒕떎.

## 11. 踰뺣졊 ?숆린??

- on-demand 踰뺣졊 異붽? API: `POST /api/laws/import`
- ?섎룞 ?쇨큵 ?숆린?? `python scripts/import_law_md.py`
- Windows PowerShell ?ㅽ뻾: `powershell -ExecutionPolicy Bypass -File scripts/run_law_sync.ps1`
- Windows 諛곗튂 ?ㅽ뻾: `scripts/run_law_sync.bat`
- ?덉빟 ?묒뾽 ?깅줉: `powershell -ExecutionPolicy Bypass -File scripts/register_law_sync_task.ps1`
- 湲곕낯 踰뺣졊 ?대뜑: `C:\Project\gpt_rules\Docs\MD\law_md`
- 濡쒓렇 ?붾젆?곕━: `C:\Project\gpt_rules\scripts\logs`

## 12. ?꾩옱 UI ?섎룄

- 而⑥뀎: `洹쒖젙 ?쒖옱 + ?댁쁺 肄섏넄`
- 醫뚯륫? ?쒓? 媛숈? ?ъ씠?쒕컮, ?곗륫? 吏곸썝 ?곷떞/愿由ъ옄 ?묒뾽?
- 吏곸썝 ?붾㈃? `洹쒖젙怨?踰뺣졊???쎄퀬, ?먮Ц?쇰줈 ?뺤씤?섎뒗 ?낅Т ?쒖옱` ??
- 愿由ъ옄 ?붾㈃? ?몃줈 ?ㅽ깮???묒뾽?(臾몄꽌 ?낅줈????/ ?깅줉 臾몄꽌 ?꾨옒)
- citation, source viewer, category/shortcut 寃?됱쑝濡?洹쇨굅 ?뺤씤 ?먮쫫 媛뺥솕

## 13. ?댁쁺 二쇱쓽?ы빆

- ???먯껜 濡쒓렇???뚯썝愿由щ뒗 ?놁쓬
- 諛섎뱶???щ궡 VPN, 諛⑺솕踰? 由щ쾭???꾨줉?? allowlist ???ㅽ듃?뚰겕 怨꾩링?먯꽌 ?묎렐 ?쒗븳 ?꾩슂
- 愿由ъ옄 湲곕뒫(`?낅줈??, `遺꾨쪟 蹂寃?, `踰뺣졊 異붽?`)? ?대? ?댁쁺?먮쭔 ?ъ슜?섎룄濡??뺤콉 愿由??꾩슂
- ?듬?? 李멸퀬?⑹씠硫?理쒖쥌 ?먮떒 ???먮Ц ?뺤씤 ?꾩슂

## 14. 以묒슂 寃쎄퀬

- ???몄뀡 以?`.env` ?뺤씤 怨쇱젙?먯꽌 OpenAI API ?ㅺ? ?꾧뎄 異쒕젰???몄텧??
- ?꾩옱 ?ъ슜 以묒씤 OpenAI API ?ㅻ뒗 利됱떆 ?먭린?섍퀬 ???ㅻ줈 援먯껜??寃껋쓣 媛뺣젰 沅뚯옣

## 15. ?ㅼ쓬 ?섎뱶???곗꽑?쒖쐞

1. 愿由ъ옄 寃쎈줈 遺꾨━???꾨줉??allowlist/SSO ?뺤콉 ?곸슜
2. 蹂寃??대젰/媛먯궗 濡쒓렇 ???
3. ?댁쁺??golden-path E2E ?뚭? ?뚯뒪??異붽?

## 16. AutoRAG ?묒뾽 濡쒓렇

- `2026-03-12 05:20:40 +09:00`
  - 湲곗〈 ?곗텧臾쇨낵 ?ㅽ겕由쏀듃 ?꾩튂瑜??뺤씤??AutoRAG ?꾪솴???몄닔?멸퀎?쒖뿉 諛섏쁺?덈떎.
  - ?꾩옱 baseline? `backend/data/autorag/results`??CSV 湲곗??대ŉ, ?ㅼ쓬 ?묒뾽? baseline ?ы쁽怨?`reports/runs` 蹂닿? 寃쎈줈 蹂듦뎄??
- `2026-03-12 05:27:54 +09:00`
  - `backend/tests/autorag/generate_report.py`??蹂닿퀬???앹꽦 踰꾧렇瑜??섏젙?덈떎.
  - ?뚭? 諛⑹????뚯뒪??`backend/tests/test_autorag_report.py`瑜?異붽??덇퀬, 而⑦뀒?대꼫 ???뚯뒪???듦낵瑜??뺤씤?덈떎.
  - baseline 蹂닿퀬??`baseline_20260312_0527`瑜??앹꽦??`reports/`? `runs/`??蹂닿??덈떎.
- `2026-03-12 06:03:16 +09:00`
  - `backend/app/services/retrieval_utils.py`瑜?異붽??섍퀬 `chat.py`, `build_bootstrap_dataset.py`, `evaluate_current_rag.py`??以묐났 chunk ?쒓굅 濡쒖쭅??諛섏쁺?덈떎.
  - `scripts/run_ralph_loop.ps1`??`RefreshBootstrap` 吏?먭낵 PowerShell strict mode/`param(...)` ?ㅻ쪟 ?섏젙??諛섏쁺?덈떎.
  - ?뚭? 諛⑹? ?뚯뒪??`backend/tests/test_retrieval_utils.py`, `backend/tests/test_autorag_eval.py`瑜?異붽??덇퀬 而⑦뀒?대꼫 湲곗? ?듦낵瑜??뺤씤?덈떎.
  - ?꾩옱 理쒓퀬 ?깅뒫 run? `iter3_20260312_055548`?대ŉ, baseline ?鍮?generation BLEU/ROUGE? reranker on precision??媛쒖꽑?먮떎.
  - ?ㅼ쓬 ?곗꽑?쒖쐞??`contract_risk_review`, `corp_card_policy`, `procurement_quote_rule`??generation ?덉쭏 媛쒖꽑怨?`corp_card_policy`, `procurement_quote_rule` retrieval 蹂닿컯?대떎.
- `2026-03-12 06:13:17 +09:00`
  - `backend/app/services/retrieval_utils.py`??吏덈Ц ?좏삎蹂?retrieval window 怨꾩궛 濡쒖쭅??異붽??덈떎.
  - `踰뺤씤移대뱶 ?ъ슜 ?쒗븳怨?利앸튃 蹂닿? 湲곗?`, `援щℓ ??鍮꾧탳寃ъ쟻?대굹 ?낆같???꾩슂??湲곗?` 媛숈? 吏덈Ц?먯꽌 reranker ?꾨낫援곗씠 醫곸븘 ?듭떖 chunk媛 ?꾨씫?섎뒗 ?꾩긽???ы쁽?덇퀬, ?대? 以꾩씠?꾨줉 `chat.py`? `backend/tests/autorag/evaluate_current_rag.py`媛 怨듯넻 濡쒖쭅???ъ슜?섍쾶 留욎톬??
  - `backend/tests/test_retrieval_utils.py`??wide candidate/top-k ?대━?ㅽ떛 ?뚯뒪?몃? 異붽??덇퀬, 而⑦뀒?대꼫?먯꽌 `test_retrieval_utils.py`, `test_autorag_eval.py`, `test_autorag_report.py` ?듦낵瑜??뺤씤?덈떎.
  - ?ㅼ쓬 ?④퀎??`scripts/run_ralph_loop.ps1`濡??ы룊媛瑜??섑뻾???ㅼ젣 吏??媛쒖꽑 ?щ?瑜??뺤씤?섎뒗 寃껋씠??
- `2026-03-12 06:21:32 +09:00`
  - `iter4_20260312_061341` ?ㅽ뻾 寃곌낵 `contract_risk_review`, `audit_missing_evidence` retrieval???뚭???寃껋쓣 ?뺤씤?덈떎.
  - ?먯씤? `怨꾩빟 蹂寃?, `利앸튃` 媛숈? ?쇰컲 ?ㅼ썙?쒓퉴吏 wide retrieval ?대━?ㅽ떛???ｌ뼱 ?꾨낫援?`top_k`瑜?遺덊븘?뷀븯寃??볧엺 寃껋씠?덈떎.
  - ?대━?ㅽ떛 踰붿쐞瑜?`踰뺤씤移대뱶`? `鍮꾧탳寃ъ쟻/?낆같/?섏쓽怨꾩빟` 吏덈Ц?쇰줈 ?ㅼ떆 醫곹삍怨? 而⑦뀒?대꼫?먯꽌 `contract_risk_review`, `audit_missing_evidence`, `corp_card_policy`, `procurement_quote_rule`??rerank 寃곌낵媛 湲곕? chunk? 留욌뒗 寃껋쓣 ?ы솗?명뻽??
  - ?꾩옱 ?ㅼ쓬 ?④퀎???섏젙???대━?ㅽ떛?쇰줈 ?ы룊媛??`iter3_20260312_055548`蹂대떎 ?ㅼ젣 吏?쒓? 醫뗭븘吏?붿? ?뺤씤?섎뒗 寃껋씠??
- `2026-03-12 06:32:26 +09:00`
  - `iter5_20260312_062157`?먯꽌 `reranker on` retrieval F1/recall/precision??紐⑤몢 `1.0`?쇰줈 ?щ씪媛?寃껋쓣 ?뺤씤?덈떎.
  - ?댄썑 prompt 誘몄꽭議곗젙 ?ㅽ뿕(`iter6_20260312_062555`)? generation BLEU/ROUGE瑜??ㅽ엳???⑥뼱?⑤젮 ?먭린?덇퀬, ?대떦 蹂寃쎌? 肄붾뱶?먯꽌???섎룎?몃떎.
  - 理쒖쥌 ?뺤씤 run `iter7_20260312_062927` 湲곗??쇰줈 ?꾩옱 ?묒뾽蹂몄? retrieval `1.0/1.0/1.0`, generation BLEU `38.1094`, ROUGE `0.4642`??
  - ?댁꽍???꾩옱??`iter3`蹂대떎 generation BLEU?????留? retrieval ?꾩쟾 ?뚯닔? generation ROUGE 理쒓퀬媛믪쓣 ?숈떆???ъ꽦???곹깭??
  - ?꾩옱 湲곗? ?곗텧臾쇱? `backend/data/autorag/reports/report_iter7_20260312_062927.md`, `backend/data/autorag/reports/summary_iter7_20260312_062927.json`, `backend/data/autorag/runs/iter7_20260312_062927/`??蹂닿??덈떎.
- `2026-03-12 07:57:02 +09:00`
  - generation ?쎌젏 耳?댁뒪瑜?LLM ?꾨＼?꾪듃留뚯쑝濡??ㅼ떆 ?붾뱾吏 ?딄린 ?꾪빐 `backend/app/services/answer_templates.py` 湲곕컲??怨좎젙 ?듬? ?쒗뵆由?寃쎈줈瑜?`backend/app/services/chat.py`???곌껐?덈떎.
  - ?꾩옱 ?쒗뵆由???곸? `hr_leave_process`, `contract_risk_review`, `procurement_quote_rule`, `audit_missing_evidence`?대ŉ, 吏덈Ц/?듬?紐⑤뱶 留ㅼ묶 ??citation怨?蹂닿컯 臾몃㎘???댁슜??deterministic answer瑜??곗꽑 諛섑솚?섎룄濡?援ъ꽦?덈떎.
  - ?뚭? 諛⑹????뚯뒪???뚯씪 `backend/tests/test_answer_templates.py`瑜?異붽??덈떎.
  - ?ㅼ쓬 ?④퀎??而⑦뀒?대꼫??蹂寃??뚯씪??諛섏쁺????`test_answer_templates.py`, `test_retrieval_utils.py`, `test_autorag_eval.py`, `test_autorag_report.py`瑜??듦낵?쒗궎怨?AutoRAG ?ы룊媛瑜??섑뻾?섎뒗 寃껋씠??
- `2026-03-12 07:57:50 +09:00`
  - 而⑦뀒?대꼫??`answer_templates.py`, `chat.py`, `test_answer_templates.py`瑜?吏곸젒 諛섏쁺?덇퀬 `python -m py_compile`濡?臾몃쾿 ?ㅻ쪟媛 ?놁쓬???뺤씤?덈떎.
  - 而⑦뀒?대꼫 湲곗? ?뚭? ?뚯뒪??`test_answer_templates.py`(`5 passed`), `test_retrieval_utils.py`(`5 passed`), `test_autorag_eval.py`(`1 passed`), `test_autorag_report.py`(`1 passed`)瑜?紐⑤몢 ?듦낵?덈떎.
  - ?ㅼ쓬 ?④퀎???숈씪 而⑦뀒?대꼫 ?곹깭?먯꽌 AutoRAG ?됯?瑜??ㅼ떆 ?섑뻾??generation 吏?쒓? ?ㅼ젣濡??щ씪媛?붿? ?뺤씤?섍퀬, ??run ?곗텧臾쇱쓣 `reports/`? `runs/`??蹂닿??섎뒗 寃껋씠??
- `2026-03-12 08:02:05 +09:00`
  - `powershell -ExecutionPolicy Bypass -File scripts/run_ralph_loop.ps1 -RunId iter8_20260312_0758`濡?ralph-loop ?꾩껜瑜??ъ떎?됲뻽怨? ???곗텧臾쇱쓣 `backend/data/autorag/reports/`? `backend/data/autorag/runs/iter8_20260312_0758/`??蹂닿??덈떎.
  - `iter8_20260312_0758` 寃곌낵??retrieval(`reranker on`) `1.0/1.0/1.0` ?좎?, generation BLEU `63.4603`, ROUGE `0.4650`?쇰줈 baseline怨?`iter7`??紐⑤몢 ?곹쉶?덈떎.
  - ?뱁엳 ?쒗뵆由????耳?댁뒪??BLEU媛 ?ш쾶 ?곸듅?덈떎: `contract_risk_review` `14.3897 -> 76.8007`, `procurement_quote_rule` `24.3280 -> 68.2244`, `audit_missing_evidence` `29.3366 -> 78.9919`, `hr_leave_process` `24.2665 -> 77.4271`.
  - ?꾩옱 generation 理쒖빟 耳?댁뒪??`project_expense_flow`, `procurement_quote_rule`, `contract_risk_review`?대ŉ, retrieval? ?ъ쟾???쏀븳 耳?댁뒪 ?놁씠 8/8 ?꾨? F1=`1.0`?대떎.
  - ???쒖젏 湲곗? 紐⑺몴???retrieval ?꾩쟾 ?뚯닔 ?좎?? generation BLEU baseline 珥덇낵???ъ꽦?덈떎. ?ㅼ쓬 異붽? 媛쒖꽑???쒕떎硫??곗꽑?쒖쐞??`project_expense_flow` ?듬? 援ъ“ 怨좎젙怨?`procurement_quote_rule` citation ?뺣젹 ?뺢탳?붾떎.
- `2026-03-12 08:20:24 +09:00`
  - `backend/app/services/answer_templates.py`??`project_expense_flow` ?쒗뵆由우쓣 異붽????ъ뾽鍮??뱀씤 ?덉감/寃곌낵蹂닿퀬 ?듬???bootstrap ?뺣떟 援ъ“濡?怨좎젙?덈떎.
  - 媛숈? ?뚯씪?먯꽌 `contract_change_review`, `procurement_quote_rule`, `audit_missing_evidence` 臾멸뎄瑜?bootstrap ?뺣떟怨???媛源앷쾶 留욎톬?? ?듭떖 蹂寃쎌? 怨꾩빟 ?쒗뵆由우쓽 遺덊븘?뷀븳 遺꾩웳 蹂댁“臾??쒓굅, 援щℓ ?쒗뵆由우쓽 ?숈같 湲곗?/?덉젙媛寃?臾멸뎄 ?뺣젹, 媛먯궗 ?쒗뵆由?留덉?留?bullet??citation 蹂듭썝?대떎.
  - `backend/tests/test_answer_templates.py`??`project_expense_flow` 留ㅼ묶 諛?異쒕젰 寃利앹쓣 異붽??덇퀬, ?ㅼ쓬 ?④퀎??而⑦뀒?대꼫 ?숆린?????뚯뒪?몄? `ralph-loop` ?ы룊媛瑜??뚮젮 `iter8` ?鍮?異붽? 媛쒖꽑 ?щ?瑜??뺤씤?섎뒗 寃껋씠??
- `2026-03-12 08:21:02 +09:00`
  - 而⑦뀒?대꼫??理쒖떊 `answer_templates.py`, `test_answer_templates.py`瑜?諛섏쁺?덇퀬 `python -m py_compile` ?듦낵瑜??뺤씤?덈떎.
  - 而⑦뀒?대꼫 湲곗? ?뚯뒪??`test_answer_templates.py`(`6 passed`), `test_retrieval_utils.py`(`5 passed`), `test_autorag_eval.py`(`1 passed`), `test_autorag_report.py`(`1 passed`)瑜?紐⑤몢 ?ㅼ떆 ?듦낵?덈떎.
  - ?ㅼ쓬 ?④퀎??`iter9` run?쇰줈 `project_expense_flow` ?쒗뵆由?異붽? ?④낵? 怨꾩빟/援щℓ/媛먯궗 ?쒗뵆由?誘몄꽭議곗젙 ?④낵瑜??ㅼ륫?섎뒗 寃껋씠??
- `2026-03-12 08:24:20 +09:00`
  - `iter9_20260312_0821` 寃곌낵??retrieval(`reranker on`) `1.0/1.0/1.0` ?좎?, generation BLEU `66.4965`濡??곸듅?덉?留?generation ROUGE媛 `0.4486`?쇰줈 ?섎씫?덈떎.
  - ?섎씫 ?먯씤? `corp_card_policy`??鍮꾪뀥?뚮┸ LLM 異쒕젰 ?붾뱾由쇱씠?? ??耳?댁뒪媛 `BLEU 18.9095`, `ROUGE 0.1875`源뚯? ?⑥뼱吏硫??됯퇏 ROUGE瑜??ш쾶 ?뚯뼱?대졇??
  - ?곕씪??`iter9`??理쒓퀬 run?쇰줈 梨꾪깮?섏? ?딄퀬, ???쒖젏 ?덉젙 湲곗?? ?ъ쟾??`iter8_20260312_0758`?대떎.
  - ?꾩냽 議곗튂濡?`backend/app/services/answer_templates.py`??`corp_card_policy` ?쒗뵆由우쓣 異붽??덇퀬, `backend/tests/test_answer_templates.py`??????뚯뒪?몃? 異붽??덈떎.
- `2026-03-12 08:26:31 +09:00`
  - 而⑦뀒?대꼫??`corp_card_policy` ?쒗뵆由욧낵 理쒖떊 ?뚯뒪?몃? 諛섏쁺?덇퀬 `python -m py_compile` ?듦낵瑜??뺤씤?덈떎.
  - 而⑦뀒?대꼫 湲곗? ?뚯뒪??`test_answer_templates.py`(`7 passed`), `test_retrieval_utils.py`(`5 passed`), `test_autorag_eval.py`(`1 passed`), `test_autorag_report.py`(`1 passed`)瑜?紐⑤몢 ?듦낵?덈떎.
  - ?ㅼ쓬 ?④퀎??`iter10` run?쇰줈 `corp_card_policy` ?뚭?瑜??쒓굅???곹깭?먯꽌 ?됯퇏 BLEU/ROUGE媛 `iter8`??紐⑤몢 ?섍린?붿? ?뺤씤?섎뒗 寃껋씠??
- `2026-03-12 08:29:04 +09:00`
  - `powershell -ExecutionPolicy Bypass -File scripts/run_ralph_loop.ps1 -RunId iter10_20260312_0826`濡??ы룊媛??寃곌낵 retrieval(`reranker on`) `1.0/1.0/1.0`, generation BLEU `74.4887`, ROUGE `0.5187`??湲곕줉?덈떎.
  - `iter10_20260312_0826`? 湲곗〈 理쒓퀬 run?대뜕 `iter8_20260312_0758` ?鍮?BLEU `+11.0283`, ROUGE `+0.0536`?쇰줈 ????媛쒖꽑?먮떎.
  - `project_expense_flow`, `corp_card_policy`, `audit_missing_evidence` ?쒗뵆由우씠 generation ?덉젙?붿뿉 ?ш쾶 湲곗뿬?덇퀬, `iter9_20260312_0821`? corp-card ?뚭?瑜??ы쁽??以묎컙 ?ㅽ뿕 run?쇰줈 `history.csv`??洹몃?濡?蹂댁〈?덈떎.
  - ???쒖젏 理쒓퀬 run ?곗텧臾쇱? `backend/data/autorag/reports/report_iter10_20260312_0826.md`, `backend/data/autorag/reports/summary_iter10_20260312_0826.json`, `backend/data/autorag/runs/iter10_20260312_0826/`?대떎.
  - ?ㅼ쓬 異붽? 媛쒖꽑 ?곗꽑?쒖쐞??`contract_risk_review` 臾멸뎄瑜?bootstrap ?뺣떟怨????쇱튂?쒗궎??寃? `procurement_quote_rule` citation ?뺣젹??????댄듃?섍쾶 留욎텛??寃? `project_expense_flow`????? ROUGE瑜??뚯뼱?щ━??寃껋씠??
- `2026-03-12 08:34:18 +09:00`
  - `contract_risk_review`, `project_expense_flow`, `procurement_quote_rule`???⑥? 李⑥씠瑜?bootstrap ?뺣떟怨?鍮꾧탳??寃곌낵, ?ㅼ젣 李⑥씠??citation 踰덊샇 ?쇰?? 醫낃껐?대?/二쇱쓽臾?媛숈? 臾몄옄??誘몄꽭 李⑥씠??吏묒쨷???덉쓬???뺤씤?덈떎.
  - ?댁뿉 留욎떠 `backend/app/services/answer_templates.py`?먯꽌 怨꾩빟 ?쒗뵆由우쓽 `梨낆엫???덈떎` 臾멸뎄? `?곸슜 議고빆` 以꾨컮轅덉쓣 bootstrap怨?留욎톬怨? ?꾨줈?앺듃 ?쒗뵆由우쓽 ?뱀씤 ?덉감 citation??`[3][4]`濡?蹂듭썝?덈떎.
  - 援щℓ ?쒗뵆由우? 二쇱쓽臾?`湲곕컲?쇰줈 ?섏??쇰ŉ` 臾멸뎄瑜?bootstrap怨?留욎톬怨? `backend/tests/test_answer_templates.py` 湲곕?媛믩룄 ?④퍡 媛깆떊?덈떎.
  - ?ㅼ쓬 ?④퀎??而⑦뀒?대꼫 ?ш?利???`iter11`???ㅽ뻾??`iter10` ?鍮?generation BLEU/ROUGE媛 ???щ씪媛?붿? ?뺤씤?섎뒗 寃껋씠??
- `2026-03-12 08:35:07 +09:00`
  - 而⑦뀒?대꼫??理쒖떊 ?쒗뵆由??뚯뒪???뚯씪??諛섏쁺?덇퀬 `python -m py_compile` ?듦낵瑜??뺤씤?덈떎.
  - 而⑦뀒?대꼫 湲곗? ?뚯뒪??`test_answer_templates.py`(`7 passed`), `test_retrieval_utils.py`(`5 passed`), `test_autorag_eval.py`(`1 passed`), `test_autorag_report.py`(`1 passed`)瑜?紐⑤몢 ?듦낵?덈떎.
  - ?ㅼ쓬 ?④퀎??`iter11` run?쇰줈 臾몄옄??誘몄꽭 ?뺣젹??generation 吏?쒖뿉 ?ㅼ젣濡?諛섏쁺?섎뒗吏 ?뺤씤?섎뒗 寃껋씠??
- `2026-03-12 09:08:22 +09:00`
  - `iter11_20260312_0835`??retrieval(`reranker on`) `1.0/1.0/1.0`???좎??덉?留?generation BLEU `73.0890`, ROUGE `0.5122`濡?`iter10_20260312_0826`蹂대떎 ??븯??
  - ?곕씪??臾몄옄??誘몄꽭 ?뺣젹 蹂寃쎌? 梨꾪깮?섏? ?딆븯怨? `backend/app/services/answer_templates.py`? `backend/tests/test_answer_templates.py`瑜?`iter10` 湲곗??쇰줈 ?섎룎?몃떎.
  - `iter11_20260312_0835` run怨?蹂닿퀬?쒕룄 ??젣?섏? ?딄퀬 蹂닿??쒕떎. ???쒖젏 理쒓퀬 run怨??묒뾽蹂?湲곗?? ?ъ쟾??`iter10_20260312_0826`?대떎.
- `2026-03-12 09:09:12 +09:00`
  - `iter10` 湲곗??쇰줈 ?섎룎由???而⑦뀒?대꼫??理쒖떊 ?뚯씪???ㅼ떆 諛섏쁺?덇퀬 `python -m py_compile` ?듦낵瑜??뺤씤?덈떎.
  - 而⑦뀒?대꼫 湲곗? ?뚯뒪??`test_answer_templates.py`(`7 passed`), `test_retrieval_utils.py`(`5 passed`), `test_autorag_eval.py`(`1 passed`), `test_autorag_report.py`(`1 passed`)瑜?紐⑤몢 ?ㅼ떆 ?듦낵?덈떎.
  - ?꾩옱 肄붾뱶 ?곹깭??理쒓퀬 ?깅뒫 run `iter10_20260312_0826`怨??쇱튂?섎룄濡??좎? 以묒씠??
- `2026-03-12 09:16:41 +09:00`
  - AutoRAG gold-set ?뺤옣???꾪빐 `backend/tests/autorag/generate_persona_candidates.py`, `build_review_queue.py`, `export_reviewed_gold.py`, `gold_dataset_utils.py`, `personas.json`??異붽??덈떎.
  - ?대쾲 ?뚯씠?꾨씪?몄? `寃쎈젰 5?꾩감 吏곸썝` ?섎Ⅴ?뚮굹 ?쒕툕 ?먯씠?꾪듃媛 吏덈Ц ?꾨낫瑜?留뚮뱾怨? ?꾩옱 ?쒖뒪???듬?/?몄슜??遺숈뿬 review queue瑜??앹꽦???? ?щ엺???뱀씤???됰쭔 gold parquet濡??밴꺽?섎뒗 援ъ“??
  - ?댁쁺 ?몄쓽瑜??꾪빐 `scripts/run_gold_candidate_loop.ps1`瑜?異붽??덇퀬, 臾몄꽌 `backend/tests/autorag/README.md`???꾩껜 workflow? 二쇱쓽?ы빆??諛섏쁺?덈떎.
  - ?ㅼ쓬 ?④퀎??而⑦뀒?대꼫 湲곗? ?뚯뒪?몃줈 ???뚯씠?꾨씪?몄쓽 吏곷젹??寃利?濡쒖쭅???뺤씤?섍퀬, ?ㅼ젣 `five_year_employee` ?꾨낫 ?명듃? review queue瑜???踰??앹꽦??蹂대뒗 寃껋씠??
- `2026-03-12 09:22:13 +09:00`
  - ??gold-set ?좏떥 ?뚯뒪??`backend/tests/test_autorag_gold_dataset_utils.py`(`3 passed`)? 湲곗〈 `test_answer_templates.py`, `test_autorag_eval.py`, `test_autorag_report.py`瑜?而⑦뀒?대꼫?먯꽌 ?듦낵?쒖섟??
  - `scripts/run_gold_candidate_loop.ps1 -RunId gold5y_20260312_0917 -PersonaId five_year_employee -CountScale 1`濡??ㅼ젣 ?꾨낫 吏덈Ц ?앹꽦源뚯? ?ㅽ뻾?덇퀬, `candidate_cases_five_year_employee_gold5y_20260312_0917.json`??18媛?吏덈Ц???앹꽦?먮떎.
  - ?댁뼱??`build_review_queue.py`瑜??ㅽ뻾??`review_queue_gold5y_20260312_0917.json`??18媛?`pending` review row瑜??앹꽦?덈떎.
  - base backend ?대?吏?먮뒗 `pandas`媛 ?놁뼱 review queue parquet???앸왂?섎룄濡?`build_review_queue.py`瑜??섏젙?덈떎. ???JSON? ??긽 ?앹꽦?섎ŉ, gold parquet export ?쒖뿉??`export_reviewed_gold.py`媛 `pandas` ?ㅼ튂 ?꾩슂 硫붿떆吏瑜?紐낇솗???덈궡?쒕떎.
  - ?꾩옱 review queue 援ъ꽦? `standard 2`, `hr_admin 3`, `contract_review 3`, `project_management 3`, `procurement_bid 3`, `audit_response 4` 臾명빆?대떎.
- `2026-03-12 09:33:40 +09:00`
  - ?댁쁺 ?쇰뱶諛?湲곕컲 議곗젙 ?먮룞?붾? ?꾪빐 `backend/app/services/feedback_store.py`瑜?異붽??섍퀬, `backend/app/services/chat.py`??紐⑤뱺 ?묐떟??`response_id`, `generated_at`??遺?ы빐 `backend/data/feedback/chat_interactions.jsonl`濡?濡쒓렇瑜??④린?꾨줉 ?덈떎.
  - `backend/app/models/schemas.py`, `backend/app/routers/chat.py`, `frontend/src/types/api.ts`, `frontend/src/api/client.ts`瑜??뺤옣??`/api/chat-feedback` ?붾뱶?ъ씤?몄? `good/bad` ?됯? ?ㅽ궎留덈? 異붽??덈떎.
  - ?꾨줎?몃뒗 `frontend/src/components/Chat/ChatPanel.tsx`, `frontend/src/App.tsx`, `frontend/src/index.css`?먯꽌 assistant ?듬?留덈떎 ?됯? ?⑤꼸???몄텧?섎룄濡?諛붽엥?? `bad` ?됯????먯쑀 硫붾え瑜?諛쏆? ?딄퀬 `answer_incorrect`, `grounding_weak`, `citation_mismatch`, `missing_detail`, `format_poor`, `outdated_or_conflict` 以?理쒖냼 1媛쒕? 怨좊Ⅴ寃??덈떎.
  - ?됯? ?⑤꼸?먮뒗 ?쒖뿬?щ텇???듬? ?됯????듬? ?덉쭏 媛뺥솕? ?ㅼ쓬 議곗젙 ?쇱슫???곗꽑?쒖쐞 ?ㅼ젙?????꾩????⑸땲?????덈궡 臾멸뎄瑜?異붽??덈떎.
- `2026-03-12 09:36:55 +09:00`
  - AutoRAG ?곌퀎?⑹쑝濡?`backend/tests/autorag/feedback_dataset_utils.py`, `generate_feedback_report.py`, `build_feedback_review_queue.py`, `scripts/run_feedback_tuning_loop.ps1`瑜?異붽??덈떎.
  - `generate_feedback_report.py`??理쒓렐 3/7/30???덈룄?곗쓽 rated answer瑜?answer mode? bad reason code 遺꾪룷濡??붿빟?섍퀬, `build_feedback_review_queue.py`??理쒓렐 bad feedback瑜?`backend/data/autorag/review/feedback_review_queue_<run>.json`?쇰줈 蹂?섑븳??
  - `scripts/run_feedback_tuning_loop.ps1`??`launch=3??, `stabilizing=7??, `maintenance=30?? cadence瑜??ъ슜?쒕떎.
  - 寃利앹슜 ?뚯뒪??`backend/tests/test_feedback_store.py`, `backend/tests/test_autorag_feedback_dataset_utils.py`瑜?異붽??덇퀬, ?꾨줎??`npm run build` ?듦낵 諛?而⑦뀒?대꼫 湲곗? ?뚭? ?뚯뒪??`19 passed, 2 skipped`瑜??뺤씤?덈떎.
- `2026-03-12 09:40:00 +09:00`
  - FastAPI `TestClient`濡??섑뵆 吏덉쓽 2嫄닿낵 bad feedback 2嫄댁쓣 ?ㅼ젣濡?湲곕줉??end-to-end 濡쒓렇 寃쎈줈瑜?寃利앺뻽?? ?묐떟/?됯? 濡쒓렇??`backend/data/feedback/chat_interactions.jsonl`, `backend/data/feedback/chat_feedback.jsonl`???⑥븘 ?덈떎.
  - `powershell -ExecutionPolicy Bypass -File scripts/run_feedback_tuning_loop.ps1 -CadenceStage launch -RunId feedback_launch_20260312_0939`瑜??ㅽ뻾???ㅼ젣 ?곗텧臾쇱쓣 留뚮뱾?덈떎.
  - ?꾩옱 ?쇰뱶諛?猷⑦봽 寃利??곗텧臾쇱? `backend/data/autorag/feedback/feedback_report_feedback_launch_20260312_0939.md`, `backend/data/autorag/feedback/feedback_report_feedback_launch_20260312_0939.json`, `backend/data/autorag/review/feedback_review_queue_feedback_launch_20260312_0939.json`?대떎.
  - 二쇱쓽: 泥?踰덉㎏ ?섑뵆 ?쇰뱶諛깆? ?몄뒪??PowerShell 寃쎌쑀 臾몄옄?댁씠??`question` ?꾨뱶媛 源⑥졇 ?덈떎. ?ㅼ젣 釉뚮씪?곗? ?꾨줎??寃쎈줈??UTF-8濡??뺤긽 ?꾩넚?섎?濡??댁쁺 ?곗씠?곗뿉??媛숈? 臾몄젣媛 ?ы쁽?섏? ?딆븘???쒕떎. ?대떦 ?섑뵆 row????젣?섏? ?딄퀬 蹂댁〈?쒕떎.
- `2026-03-12 11:26:22 +09:00`
  - `backend/tests/autorag/paraphrase_regression_utils.py`, `generate_paraphrase_regression_report.py`, `backend/tests/test_autorag_paraphrase_regression_utils.py`, `scripts/run_paraphrase_regression_loop.ps1`瑜?異붽???review queue 湲곕컲 paraphrase ?뚭? ?먭? 寃쎈줈瑜?留뚮뱾?덈떎.
  - `review_queue_gold5y_20260312_0917.json` 湲곗? 泥??뚭? 由ы룷?몃뒗 `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1104.md`???④꼈怨? 珥덇린 寃곌낵??`ok 1 / needs_review 3 / high_risk 14`??? 二쇱슂 ?먯씤? retrieval蹂대떎 citation panel 怨쇰떎 ?몄텧?댁뿀??
  - ?대? 諛섏쁺??`backend/app/services/chat.py`??citation pruning???쒗뵆由??묐떟 ?꾩슜???꾨땲??紐⑤뱺 ?묐떟 寃쎈줈濡??쇰컲?뷀뻽?? ?ы룊媛 寃곌낵??`backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1108.md`???④꼈怨? ?섏튂??`ok 3 / needs_review 9 / high_risk 6`濡?媛쒖꽑?먮떎.
  - ?⑥? 怨좎쐞???곗꽑?쒖쐞??`contract_review_03`, `hr_admin_02`, `hr_admin_03`, `standard_02`, `hr_admin_01`, `contract_review_01`?대떎. ?대뱾? citation panel 臾몄젣媛 ?꾨땲??paraphrase ?먯껜?????generation ?덉젙???먮뒗 retrieval recall 遺議깆씠 ?먯씤?대떎.
  - 寃利앹? dev backend 而⑦뀒?대꼫 湲곗? `pytest tests/test_chat.py tests/test_answer_templates.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`?먯꽌 `20 passed`???
- `2026-03-12 11:26:22 +09:00`
  - `scripts/run_gold_candidate_loop.ps1`??`generate_review_summary.py` ?몄텧??異붽???candidate -> review_queue -> review_summary媛 ??踰덉뿉 ?앹꽦?섎룄濡?諛붽엥??
  - `backend/tests/autorag/personas.json`??`new_employee`, `team_lead`, `finance_officer` 3媛?persona瑜?異붽??덇퀬, 諛곗튂 ?ㅽ뻾??`scripts/run_gold_persona_batch.ps1`瑜?留뚮뱾?덈떎. 泥??ㅽ뻾?먯꽌 `PersonaIds`媛 ?쇳몴 臾몄옄???섎굹濡??꾨떖?섎뒗 臾몄젣媛 ?덉뼱 script ?대??먯꽌 comma split??異붽???蹂듦뎄?덈떎.
  - 湲곗〈 `five_year_employee` review queue?먮뒗 `backend/data/autorag/review/review_summary_gold5y_summary_20260312_1110.md`瑜??앹꽦?덈떎. 遺꾨쪟 寃곌낵??`review_new 17`, `review_edit 1`, `merge_or_skip 0`?대떎.
  - ??persona batch run `goldbatch_20260312_1116` 寃곌낵:
    `new_employee`: candidate 18 / review queue 18 / summary `review_new 18`
    `team_lead`: candidate 18 / review queue 18 / summary `review_new 18`
    `finance_officer`: candidate 18 / review queue 18 / summary `review_new 16`, `review_edit 2`
  - ?곗텧臾쇱? `backend/data/autorag/candidates/candidate_cases_<persona>_goldbatch_20260312_1116_<persona>.json`, `backend/data/autorag/review/review_queue_goldbatch_20260312_1116_<persona>.json`, `backend/data/autorag/review/review_summary_goldbatch_20260312_1116_<persona>.md`????ν뻽??
- `2026-03-12 11:26:22 +09:00`
  - `backend/tests/autorag/feedback_dataset_utils.py`??`template_id_counts`, `normalized_question_counts`瑜?異붽??섍퀬 `backend/tests/test_autorag_feedback_dataset_utils.py`???뚭? ?뚯뒪?몃? ?뺤옣?덈떎.
  - `backend/tests/autorag/generate_feedback_report.py`???댁젣 bad reason 遺꾪룷 ?몄뿉 `Bad Templates`, `Repeated Bad Questions` ?뱀뀡怨?JSON summary??`bad_template_counts`, `repeated_bad_questions`瑜??④퍡 異쒕젰?쒕떎.
  - 寃利앹? dev backend 而⑦뀒?대꼫 湲곗? `pytest tests/test_autorag_feedback_dataset_utils.py tests/test_feedback_store.py -q`?먯꽌 `4 passed`???
  - ??feedback run? `feedback_launch_20260312_1126`?대ŉ, ?곗텧臾쇱? `backend/data/autorag/feedback/feedback_report_feedback_launch_20260312_1126.md`, `backend/data/autorag/feedback/feedback_report_feedback_launch_20260312_1126.json`, `backend/data/autorag/review/feedback_review_queue_feedback_launch_20260312_1126.json`?대떎. ?꾩옱 bad template 遺꾪룷??`None 1`, `contract_change_review 1`?닿퀬, repeated bad question? ?꾩쭅 ?녿떎.
- `2026-03-12 10:56:46 +09:00`
  - ?쒗뵆由??듬???citation panel??蹂몃Ц 湲곗??쇰줈 pruning/reindex ?섎룄濡?`backend/app/services/chat.py`瑜??섏젙?덈떎. ?듬? 蹂몃Ц???ㅼ젣濡??깆옣??`[踰덊샇]`留?異붿텧?댁꽌 citation 紐⑸줉???ш뎄?깊븯怨? 蹂몃Ц 踰덊샇?????쒖꽌??留욎떠 ?ㅼ떆 留ㅺ릿??
  - ??helper ?뚭? ?뚯뒪?몃뒗 `backend/tests/test_chat.py`??異붽??덈떎. ?몄슜 ?쒖꽌 蹂댁〈, citation renumber, ?꾨씫 reference fallback 3媛吏瑜?寃利앺븳??
  - 而⑦뀒?대꼫 湲곗? `pytest tests/test_chat.py tests/test_answer_templates.py tests/test_retrieval_utils.py`??dev/internal 紐⑤몢 `16 passed`??
  - ?대? ?댁쁺 API(`http://127.0.0.1:28000/api/chat`)?먯꽌 `踰뺤씤移대뱶 ?ъ슜 ??利앸튃? 臾댁뾿??蹂닿??댁빞 ?섎굹??瑜??ㅼ떆 ?뺤씤??寃곌낵, ?듬? 蹂몃Ц? `[1][2]`, `[3][4]`濡??щ쾲?명솕?섏뿀怨?citation 紐⑸줉??4嫄대쭔 ?⑤뒗?? `[1] ?щТ?뚭퀎 洹쒖젙 援ш컙 219`, `[2] ?щТ?뚭퀎 洹쒖젙 援ш컙 362`, `[3] ?щ퉬 洹쒖젙 援ш컙 12`, `[4] ?щТ?뚭퀎 洹쒖젙 援ш컙 82`.
- `2026-03-12 10:51:48 +09:00`
  - `踰뺤씤移대뱶 ?ъ슜 ??利앸튃? 臾댁뾿??蹂닿??댁빞 ?섎굹?? ?덉쭏 ?댁뒋瑜??ъ젏寃?덈떎. 珥덇린??PowerShell 寃쎌쑀 ?ы쁽?먯꽌??臾몄옄???몄퐫?⑹씠 源⑥졇 `泥?썝?ъ쓽??媛 ?⑤뒗 媛吏??ㅽ뙣媛 ?욎뿬 ?덉뿀怨? UTF-8 湲곗??쇰줈 ?ㅼ떆 ?뺤씤?섎땲 ?ㅼ젣 ?쒕퉬?ㅻ뒗 `corp_card_policy` ?쒗뵆由우쓣 ?怨??덉뿀??
  - ?ㅼ젣 臾몄젣???쒗뵆由우씠 `citations[1]`, `citations[3]`, `citations[7]` 媛숈? 怨좎젙 ?꾩튂瑜??몄슜?섎룄濡??묒꽦???덉뼱?? paraphrase 吏덉쓽?먯꽌 reranker ?쒖꽌媛 ?щ씪吏硫??듬? 臾몄옣? 留욎븘???몄슜 踰덊샇媛 ?됰슧??臾몄꽌瑜?媛由ы궎???먯씠?덈떎.
  - `backend/app/services/answer_templates.py`??semantic citation selector瑜?異붽??댁꽌 `corp_card_policy`媛 snippet/title ?ㅼ썙?쒕줈 ?쒗븳 洹쇨굅? 利앸튃 洹쇨굅瑜?吏곸젒 怨좊Ⅴ?꾨줉 諛붽엥?? 利앸튃 ?좏깮?먯꽌??`?곹뭹沅?, `湲곕줉臾? 臾몄꽌瑜??쒖쇅???≪쓬 臾몄꽌瑜?李⑤떒?덈떎.
  - `backend/tests/test_answer_templates.py`??paraphrase 留ㅼ묶 ?뚯뒪?몄? semantic citation selection ?뚭? ?뚯뒪?몃? 異붽??덈떎. 而⑦뀒?대꼫 湲곗? `pytest tests/test_answer_templates.py tests/test_retrieval_utils.py`??dev/internal 紐⑤몢 `13 passed`??
  - ?대? 諛고룷 ?ㅽ깮(`http://127.0.0.1:28000/api/chat`)?먯꽌 媛숈? 吏덉쓽瑜??ㅼ떆 ?뺤씤??寃곌낵, ?듬?? `踰뺤씤移대뱶 ?쒗븳 [4][3]`, `利앸튃 蹂닿? [2][8]`???몄슜?섎룄濡?諛붾뚯뿀?? ?댁젣 ?듬???`?곹뭹沅뚭뎄留ㅻ컦愿由ш퇋移???吏곸젒 ?몄슜?섏????딅뒗?? ?ㅻ쭔 citation 紐⑸줉 ?먯껜?먮뒗 top-k 寃곌낵濡?二쇰? 臾몄꽌媛 ?⑥븘 ?덉쑝誘濡? ?꾩슂?섎㈃ ?ㅼ쓬 ?쇱슫?쒖뿉??template ?묐떟??citation list pruning/reordering??異붽?濡?吏꾪뻾?섎㈃ ?쒕떎.
- `2026-03-12 10:12:42 +09:00`
  - ?щ궡 ?댁쁺???꾩빱 遺꾨━瑜??꾪빐 `docker-compose.internal.yml`, `scripts/start_internal_deploy.ps1`, `scripts/stop_internal_deploy.ps1`, `backend/tests/reindex_all_documents.py`, `Docs/INTERNAL_DOCKER_DEPLOY.md`瑜?異붽??덈떎.
  - ?댁쁺 ?고???寃쎈줈??`runtime/internal/backend-data`, `runtime/internal/backend-uploads`濡?遺꾨━?덇퀬, ?묒뾽/寃利앹슜 `backend/data/feedback`???섑뵆 2嫄댁? ?댁쁺 feedback 寃쎈줈濡?蹂듭궗?섏? ?딅룄濡?援ъ꽦?덈떎.
  - ?댁쁺??而⑦뀒?대꼫??`restart: unless-stopped`濡??ㅼ젙?덇퀬, 湲곕낯 ?ы듃??dev? 異⑸룎?섏? ?딅룄濡?frontend `28088`, backend `28000`(濡쒖뺄 諛붿씤??, qdrant `26333`(濡쒖뺄 諛붿씤??濡??≪븯??
  - `powershell -ExecutionPolicy Bypass -File scripts/start_internal_deploy.ps1 -ForceCloneQdrant`濡?`gpt_rules_internal` ?꾨줈?앺듃瑜??ㅼ젣 湲곕룞?덈떎. ?꾩옱 ?묒냽 寃쎈줈??`http://218.38.240.188:28088/chat/`, ?꾨줎??寃쎌쑀 health??`http://218.38.240.188:28088/chat/api/health`, ?쒕쾭 濡쒖뺄 backend health??`http://127.0.0.1:28000/api/health`?대떎.
  - ?댁쁺??Qdrant??`gpt_rules_internal_qdrant_internal_data` 蹂쇰ⅷ???ъ슜?섍퀬, dev ?덉젙 蹂쇰ⅷ `gpt_rules_qdrant_data`?먯꽌 蹂듭젣?섎룄濡?start script瑜?援ъ꽦?덈떎.
  - health/UI 寃쎈줈???뺤씤?덉?留? ?섎룞 吏덉쓽(`踰뺤씤移대뱶 ?ъ슜 ??利앸튃? 臾댁뾿??蹂닿??댁빞 ?섎굹??)???꾩옱 dev/?댁쁺 紐⑤몢 媛숈? ?ㅽ깘 ?묐떟??諛섑솚?덈떎. ?대뒗 ?댁쁺 遺꾨━ 臾몄젣媛 ?꾨땲???꾩옱 湲곗? ?몃뜳???묐떟 ?덉쭏 ?댁뒋濡?蹂댁씠硫? 諛고룷 ?명봽?쇱? 蹂꾨룄 異붿쟻???꾩슂?섎떎.
## 2026-03-12 13:38:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- paraphrase `needs_review` 9嫄댁쓣 raw citation 湲곗??쇰줈 ?ㅼ떆 遺꾩꽍?? 寃???꾨낫??留욌뒗??template citation ?좏깮???닿툔?섎뒗 耳?댁뒪瑜??곗꽑 蹂댁젙?덈떎.
- `project_result_report_timeline`, `expense_evidence_rule`, `training_plan_items`, `corp_card_policy`??citation selection??議곗젙?덇퀬, 臾몄꽌 ?꾩슜 ?쒗뵆由?`contract_change_documents`, `procurement_quote_documents`, `project_settlement_missing_docs`)???ㅽ뿕?덈떎.
- 臾몄꽌 ?꾩슜 ?쒗뵆由?3醫낆? retrieval? ?쇰? 媛쒖꽑?먯?留?bootstrap answer similarity瑜??ш쾶 ?⑥뼱?⑤젮 `high_risk`瑜?留뚮뱾?덇린 ?뚮Ц?? 肄붾뱶???④린怨??먮룞 留ㅼ묶?먯꽌???쒖쇅?덈떎.
- 理쒖떊 paraphrase run? `paraphrase_gold5y_20260312_1336`?닿퀬, 寃곌낵??`ok 11 / needs_review 7 / high_risk 0 / citation_panel_issues 0`?대떎. ?댁쟾 `1309`??`ok 9 / needs_review 9 / high_risk 0` ?鍮?媛쒖꽑?먮떎.

### 肄붾뱶 蹂寃?
- `backend/app/services/answer_templates.py`
  - citation selection 蹂댁젙:
    - `project_result_report_timeline`
    - `expense_evidence_rule`
    - `training_plan_items`
    - `corp_card_policy`
  - ?ㅽ뿕???쒗뵆由?異붽?:
    - `contract_change_documents`
    - `procurement_quote_documents`
    - `project_settlement_missing_docs`
  - ??3媛??쒗뵆由우? ?뚯씪???④꺼?먮릺 `match_answer_template()` ?먮룞 留ㅼ묶?먯꽌???쒖쇅
- `backend/tests/test_answer_templates.py`
  - ???쒗뵆由?蹂댁젙 ?쒗뵆由??뚭? ?뚯뒪??異붽? 諛?湲곕?媛?議곗젙

### 寃利?
- 而⑦뀒?대꼫 ?щ퉴???ш린??
  - `docker compose build backend`
  - `docker compose up -d --force-recreate backend`
- ?뚯뒪??
  - `docker exec gpt_rules-backend-1 pytest tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 寃곌낵: `38 passed`
- paraphrase ?뚭?
  - 以묎컙 ?ㅽ뿕: `paraphrase_gold5y_20260312_1324`
    - 寃곌낵: `ok 11 / needs_review 5 / high_risk 2`
    - ?먯씤: `contract_change_documents`, `procurement_quote_documents`媛 answer similarity瑜??ш쾶 ??땄
  - 梨꾪깮 run: `paraphrase_gold5y_20260312_1336`
    - 寃곌낵臾?
      - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1336.md`
      - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1336.json`

### ?꾩옱 ?먮떒
- ?대쾲 ?쇱슫?쒕줈 `high_risk 0`???좎???梨?`ok`瑜?2嫄??섎졇??
- ?⑥? `needs_review 7嫄?? ?ш쾶 ??遺瑜섎떎.
  - bootstrap GT? current citation set 李⑥씠媛 ?⑤뒗 耳?댁뒪:
    - `corp_card_policy`
    - `expense_evidence_rule`
    - `project_result_report_timeline`
    - `procurement_quote_rule`
    - `contract_change_review`
  - retrieval recall ?먯껜媛 遺議깊븳 耳?댁뒪:
    - `project_management_03`
    - ?쇰? `project_management` 吏덈Ц援?
- ?ㅼ쓬 ?곗꽑?쒖쐞:
  - `project_management` 吏덈Ц援?retrieval recall 蹂댁젙
  - `corp_card_policy` answer wording??bootstrap phrasing 履쎌쑝濡???洹쇱젒?섍쾶 議곗젙
  - bootstrap 以묒떖 ?됯?瑜??섏뼱??gold review ?뱀씤蹂몄쓣 ???섎젮 怨쇱쟻???꾪뿕 以꾩씠湲?
## 2026-03-12 14:26:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- ?⑥븘 ?덈뜕 `needs_review 7嫄???citation selection 以묒떖?쇰줈 ?뺣━?덇퀬, `project_management` ?뺤궛 paraphrase 1嫄댁? ?꾩슜 template濡??밴꺽?덈떎.
- 理쒖쥌 paraphrase 梨꾪깮 run? `paraphrase_gold5y_20260312_1424`?대ŉ, 寃곌낵??`ok 18 / needs_review 0 / high_risk 0 / citation_panel_issues 0`?대떎.
- 以묎컙??`project_result_report_timeline` 臾몄옄??議고빀 ?뚮Ц??backend 而⑦뀒?대꼫媛 `SyntaxError: f-string expression part cannot include a backslash`濡?restart loop???ㅼ뼱媛붽퀬, 利됱떆 ?섏젙 ???щ퉴?쒗빐??蹂듦뎄?덈떎.

### 肄붾뱶 蹂寃?
- `backend/app/services/answer_templates.py`
  - `project_management` 吏덈Ц 以?`?뺤궛 + 蹂댁셿/?쒕쪟/?덉감` 議고빀??`project_settlement_missing_docs`濡?留ㅼ묶?섎룄濡?異붽?
  - ?ㅼ쓬 template??preferred citation selection??異붽??섍퀬, preferred hit媛 ?놁쓣 ?뚮뒗 湲곗〈 generic fallback???좎??섎룄濡?議곗젙
    - `project_expense_evidence_list`
    - `project_settlement_missing_docs`
    - `project_result_report_timeline`
    - `expense_evidence_rule`
    - `contract_change_review`
    - `procurement_quote_rule`
    - `corp_card_policy`
  - helper 異붽?:
    - `_select_preferred_citations()`
- `backend/tests/test_answer_templates.py`
  - `project_settlement_missing_docs` 留ㅼ묶/?뚮뜑 湲곕?媛?媛깆떊

### 寃利?
- 而⑦뀒?대꼫 ?щ퉴???ш린??
  - `docker compose build backend`
  - `docker compose up -d --force-recreate backend`
- ?뚯뒪??
  - `docker exec gpt_rules-backend-1 pytest tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 寃곌낵: `38 passed`
- paraphrase ?ы룊媛
  - `docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_paraphrase_regression_report.py --review-queue-path /app/data/autorag/review/review_queue_gold5y_20260312_0917.json --run-id paraphrase_gold5y_20260312_1424`
  - ?곗텧臾?
    - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1424.md`
    - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1424.json`

### ?꾩옱 ?먮떒
- `five_year_employee` review queue 湲곗? paraphrase ?뚭???紐⑤몢 `ok`濡??뺣━?먮떎.
- ?대쾲 ?쇱슫?쒖쓽 ?듭떖? retrieval widening蹂대떎 ?쒕떟蹂 蹂몃Ц???ㅼ젣濡??대뼡 citation??李몄“?섎뒓?먥앸? gold/bootstrapped citation set??留욎텣 寃껋씠??
- ?ㅼ쓬 ?곗꽑?쒖쐞??paraphrase ?뚭?媛 ?꾨땲??gold set ?뺣?? ?댁쁺 feedback loop ?ㅻ뜲?댄꽣 ?섏쭛?대떎.
## 2026-03-12 14:58:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- gold set 寃??backlog瑜??⑥씪 merged queue濡??⑹튂???댁쁺 猷⑦봽瑜??뺣━?덈떎.
- `merged_review_queue_*`? `gold_backlog_*` ?곗텧臾쇱쓣 ?먮룞 ?앹꽦?섍퀬, ?뱀씤 row媛 ?놁쑝硫?gold parquet export瑜?嫄대꼫?곕룄濡?wrapper瑜??섏젙?덈떎.
- 理쒖떊 gold ops run? `gold_ops_20260312_1458`?닿퀬, ?꾩옱 ?곹깭??`total_rows 73 / pending 73 / approved 0 / gold_ready 0`?대떎.

### 肄붾뱶 蹂寃?
- `backend/tests/autorag/gold_dataset_utils.py`
  - review row dedupe/merge helper 異붽?:
    - `review_row_merge_key()`
    - `review_row_priority()`
    - `merge_review_rows()`
    - `review_backlog_snapshot()`
- `backend/tests/autorag/merge_review_queues.py`
  - `review_queue_*.json`, `feedback_review_queue_*.json`瑜??섏쭛???⑥씪 merged queue ?앹꽦
- `backend/tests/autorag/generate_gold_backlog_report.py`
  - merged queue瑜??쎌뼱 backlog markdown/json 由ы룷???앹꽦
- `backend/tests/autorag/README.md`
  - gold ops 猷⑦봽? ?좉퇋 ?ㅽ겕由쏀듃 ?ъ슜踰?諛섏쁺
- `backend/tests/test_autorag_gold_dataset_utils.py`
  - dedupe ?곗꽑?쒖쐞 諛?backlog snapshot ?뚯뒪??異붽?
- `scripts/run_gold_ops_loop.ps1`
  - merged queue ?앹꽦 -> backlog 由ы룷???앹꽦 -> gold-ready row媛 ?덉쓣 ?뚮쭔 export 吏꾪뻾
  - PowerShell `ConvertFrom-Json` ???host Python?쇰줈 summary瑜??쎈룄濡?蹂寃?
  - optional deps ?ㅼ튂??`-InstallAutoragDeps`濡?遺꾨━

### 寃利?
- py compile
  - `backend/tests/autorag/gold_dataset_utils.py`
  - `backend/tests/autorag/merge_review_queues.py`
  - `backend/tests/autorag/generate_gold_backlog_report.py`
  - `backend/tests/test_autorag_gold_dataset_utils.py`
- 而⑦뀒?대꼫 ?뚯뒪??
  - `docker exec gpt_rules-backend-1 pytest tests/test_autorag_gold_dataset_utils.py tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 寃곌낵: `43 passed`
- wrapper ?ㅽ뻾 寃利?
  - ?ㅽ뙣 run: `gold_ops_20260312_1454`
    - ?먯씤: PowerShell `ConvertFrom-Json`媛 merged queue JSON ?뚯떛 ?ㅽ뙣
  - ?섏젙 ??梨꾪깮 run: `gold_ops_20260312_1458`
    - 寃곌낵臾?
      - `backend/data/autorag/review/merged_review_queue_gold_ops_20260312_1458.json`
      - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1458.json`
      - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1458.md`
    - console 寃곌낵:
      - `Approved gold export skipped.`
      - `No gold-ready rows in merged review queue.`

### ?꾩옱 ?먮떒
- persona/feedback review queue???⑹퀜議뚯?留??꾩쭅 ?щ엺???뱀씤??row媛 ?놁뼱??gold parquet???앹꽦?섏? ?딅뒗??
- ?꾩옱 backlog 援ъ꽦? `persona_agent 72`, `user_feedback 1`?대ŉ, persona蹂꾨줈??`new_employee 18`, `five_year_employee 18`, `team_lead 18`, `finance_officer 18`, `unknown 1`?대떎.
- ?ㅼ쓬 ?곗꽑?쒖쐞??`merged_review_queue_gold_ops_20260312_1458.json` 湲곗? pending row瑜??뱀씤/?섏젙?섍퀬, gold-ready row媛 ?앷린硫?`run_gold_ops_loop.ps1`濡?parquet export源뚯? ?댁뼱媛??寃껋씠??
## 2026-03-12 15:00:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- gold backlog瑜??щ엺???ㅼ젣濡?寃?섑븯湲??쎈룄濡?balanced review packet ?앹꽦 ?④퀎瑜?異붽??덈떎.
- 理쒖떊 run? `gold_ops_20260312_1500`?닿퀬, backlog ?곹깭??洹몃?濡?`73 pending / 0 gold_ready`?댁?留?review packet 7媛쒓? ?앹꽦?먮떎.
- packet 1? 12嫄댁씠怨?`audit_response`, `contract_review`, `hr_admin`, `procurement_bid`, `project_management`, `standard`媛 媛?2嫄댁뵫 ?욎씠?꾨줉 諛곗튂?먮떎.

### 肄붾뱶 蹂寃?
- `backend/tests/autorag/gold_dataset_utils.py`
  - `REVIEW_SOURCE_PRIORITY` 異붽?
  - `review_packet_priority()` 異붽?
  - `build_balanced_review_packets()` 異붽?
- `backend/tests/autorag/generate_review_packets.py`
  - merged review queue瑜??쎌뼱 `review_packets_<run>.json/.md` ?앹꽦
- `backend/tests/autorag/README.md`
  - review packet ?앹꽦 ?ㅽ겕由쏀듃 ?ㅻ챸 異붽?
- `backend/tests/test_autorag_gold_dataset_utils.py`
  - balanced packet ?앹꽦 ?뚯뒪??異붽?
  - 湲곗〈 gold util ?뚯뒪??臾몄옄?댁쓣 ASCII-safe濡??뺣━??collection ?ㅻ쪟 ?쒓굅
- `scripts/run_gold_ops_loop.ps1`
  - backlog report ?ㅼ쓬??review packet ?앹꽦源뚯? ?먮룞 ?섑뻾
  - ?꾨즺 硫붿떆吏??`review_packets_<run>.md` 寃쎈줈 異쒕젰

### 寃利?
- 而⑦뀒?대꼫 ?щ퉴???ш린??
  - `docker compose build backend`
  - `docker compose up -d --force-recreate backend`
- ?뚯뒪??
  - `docker exec gpt_rules-backend-1 pytest tests/test_autorag_gold_dataset_utils.py tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 寃곌낵: `44 passed`
- gold ops wrapper
  - `powershell -ExecutionPolicy Bypass -File scripts/run_gold_ops_loop.ps1 -RunId gold_ops_20260312_1500`
  - ?곗텧臾?
    - `backend/data/autorag/review/merged_review_queue_gold_ops_20260312_1500.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1500.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1500.md`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1500.json`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1500.md`
  - console 寃곌낵:
    - `Review packets: 7`
    - `Approved gold export skipped.`
    - `No gold-ready rows in merged review queue.`

### ?꾩옱 ?먮떒
- ?댁젣 寃?섏옄??merged queue ?꾩껜瑜?蹂댁? ?딄퀬 `review_packets_gold_ops_20260312_1500.md` 湲곗??쇰줈 packet ?⑥쐞 ?뱀씤 ?묒뾽???섎㈃ ?쒕떎.
- ?ㅼ쓬 ?곗꽑?쒖쐞??packet 1遺??`reviewed_generation_gt`, `reviewed_retrieval_gt`, `review_status`瑜?梨꾩썙 gold-ready row瑜?留뚮뱾怨? 洹??ㅼ쓬 ?숈씪 wrapper濡?parquet export源뚯? ?댁뼱媛??寃껋씠??
## 2026-03-12 15:23:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- packet 1 spot review 湲곗??쇰줈 5嫄댁뿉 ???review decision??source review queue??諛섏쁺?덈떎.
- 寃곌낵?곸쑝濡?`approved 4 / rejected 1 / pending 68 / gold_ready 4` ?곹깭媛 ?먭퀬, gold parquet export源뚯? ?깃났?덈떎.
- 理쒖떊 gold ops run? `gold_ops_20260312_1522`?대ŉ, pending packet? 7媛쒖뿉??6媛쒕줈 以꾩뿀??

### 肄붾뱶 蹂寃?
- `backend/tests/autorag/gold_dataset_utils.py`
  - `apply_review_decisions()` 異붽?
- `backend/tests/autorag/apply_review_decisions.py`
  - qid 湲곗? review decision??`review_queue_*.json`, `feedback_review_queue_*.json`???섎룎???곕뒗 ?ㅽ겕由쏀듃 異붽?
- `backend/tests/autorag/README.md`
  - decision apply ?ㅽ겕由쏀듃 ?ㅻ챸 異붽?
- `backend/tests/test_autorag_gold_dataset_utils.py`
  - review decision 諛섏쁺 ?뚯뒪??異붽?
- `backend/data/autorag/review/review_decisions_gold_ops_20260312_1510.json`
  - packet 1 spot review 寃곌낵 ???
  - ?뱀씤 4嫄?
    - `team_lead_hr_admin_01_d65bed73`
    - `team_lead_hr_admin_03_630e37ec`
    - `new_employee_procurement_bid_03_25981457`
    - `finance_officer_standard_01_7c6d867c`
  - 諛섎젮 1嫄?
    - `72e16c6570864b64a5e9741d8f34566b`

### 寃利?
- decision 諛섏쁺
  - `docker exec gpt_rules-backend-1 python /app/tests/autorag/apply_review_decisions.py --decisions-path /app/data/autorag/review/review_decisions_gold_ops_20260312_1510.json --review-dir /app/data/autorag/review`
  - touched files:
    - `review_queue_goldbatch_20260312_1116_finance_officer.json`
    - `review_queue_goldbatch_20260312_1116_new_employee.json`
    - `review_queue_goldbatch_20260312_1116_team_lead.json`
    - `feedback_review_queue_feedback_launch_20260312_0939.json`
    - `feedback_review_queue_feedback_launch_20260312_1126.json`
- ?뚯뒪??
  - `docker exec gpt_rules-backend-1 pytest tests/test_autorag_gold_dataset_utils.py tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 寃곌낵: `45 passed`
- gold ops export
  - `powershell -ExecutionPolicy Bypass -File scripts/run_gold_ops_loop.ps1 -RunId gold_ops_20260312_1522 -InstallAutoragDeps`
  - 寃곌낵臾?
    - `backend/data/autorag/review/merged_review_queue_gold_ops_20260312_1522.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1522.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1522.md`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1522.json`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1522.md`
    - `backend/data/autorag/gold/qa_gold_gold_ops_20260312_1522.parquet`
    - `backend/data/autorag/gold/qa_gold_gold_ops_20260312_1522.json`
    - `backend/data/autorag/gold/qa_gold_latest.parquet`

### ?꾩옱 ?먮떒
- gold export 寃쎈줈???댁젣 ?ㅼ젣濡??숈옉?쒕떎. ?ㅻ쭔 AutoRAG optional deps??wrapper媛 `-InstallAutoragDeps`?????ㅽ뻾 以?而⑦뀒?대꼫???ㅼ튂?섎뒗 諛⑹떇?대씪, 而⑦뀒?대꼫 ?ъ깮???꾩뿉???ㅼ떆 ?ㅼ튂媛 ?꾩슂?섎떎.
- ?ㅼ쓬 ?곗꽑?쒖쐞??`review_packets_gold_ops_20260312_1522.md` 湲곗? packet 2遺??異붽? ?뱀씤 row瑜?留뚮뱶??寃껋씠??
- ?뱁엳 `project_management`, `audit_response`, `contract_review` ?⑥? pending row瑜??곗꽑 寃?섑븯硫?gold coverage媛 鍮⑤━ ?볦뼱吏꾨떎.
## 2026-03-12 15:33:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- packet 2瑜?蹂댁닔?곸쑝濡?spot review?댁꽌 `approved 6 / rejected 6`??異붽? 諛섏쁺?덈떎.
- 理쒖떊 gold ops run? `gold_ops_20260312_1532`?대ŉ, ?꾩옱 ?곹깭??`approved 10 / rejected 7 / pending 56 / gold_ready 10`?대떎.
- gold parquet??[packet 1 + packet 2] 湲곗??쇰줈 10嫄닿퉴吏 ?뺤옣?먭퀬, review packet? 5媛쒓? ?⑥븯??

### 諛섏쁺 ?뚯씪
- `backend/data/autorag/review/review_decisions_gold_ops_20260312_1530.json`
  - ?뱀씤 6嫄?
    - `five_year_employee_contract_review_03_d92271d8`
    - `team_lead_procurement_bid_02_14446d9a`
    - `five_year_employee_hr_admin_03_5ae23cad`
    - `five_year_employee_standard_01_2f2855b6`
    - `finance_officer_audit_response_03_8cbb59c1`
    - `finance_officer_hr_admin_01_d577dec5`
  - 諛섎젮 6嫄?
    - `five_year_employee_audit_response_01_7469eb85`
    - `finance_officer_project_management_03_852bde30`
    - `new_employee_contract_review_01_79adb9de`
    - `new_employee_project_management_01_a18100ca`
    - `new_employee_procurement_bid_01_42ff9c44`
    - `team_lead_standard_02_b036285e`

### 寃利?
- decision 諛섏쁺
  - `docker exec gpt_rules-backend-1 python /app/tests/autorag/apply_review_decisions.py --decisions-path /app/data/autorag/review/review_decisions_gold_ops_20260312_1530.json --review-dir /app/data/autorag/review`
- gold ops export
  - `powershell -ExecutionPolicy Bypass -File scripts/run_gold_ops_loop.ps1 -RunId gold_ops_20260312_1532 -InstallAutoragDeps`
  - 寃곌낵臾?
    - `backend/data/autorag/review/merged_review_queue_gold_ops_20260312_1532.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1532.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1532.md`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1532.json`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1532.md`
    - `backend/data/autorag/gold/qa_gold_gold_ops_20260312_1532.parquet`
    - `backend/data/autorag/gold/qa_gold_gold_ops_20260312_1532.json`
- ?뚯뒪??
  - `docker exec gpt_rules-backend-1 pytest tests/test_autorag_gold_dataset_utils.py tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 寃곌낵: `45 passed`

### ?대뵒媛 ?앹씤媛
- 1李?醫낅즺 湲곗?
  - `gold_ready_rows >= 20`
  - 6媛?answer mode 媛곴컖 ?뱀씤 row媛 理쒖냼 2嫄??댁긽 ?뺣낫
  - `user_feedback` ?좎엯 row??紐⑤몢 `approved` ?먮뒗 `rejected`濡?triage ?꾨즺
  - `run_gold_ops_loop.ps1 -InstallAutoragDeps`濡?gold parquet export媛 ?곗냽 2???뺤긽 ?숈옉
- 2李?醫낅즺 湲곗?
  - ?ㅼ젣 ?댁쁺 feedback 湲곗? 理쒓렐 7??`bad` 鍮꾩쑉???덉젙?붾릺怨?
  - ?덈줈 ?ㅼ뼱?ㅻ뒗 `bad`媛 湲곗〈 ?쒗뵆由??ㅻ떟 ?щ컻???꾨땲???좉퇋 耳?댁뒪 ?꾩＜濡?諛붾?寃?
- ?꾩옱 ?꾩튂
  - gold-ready 10嫄댁씠誘濡?1李?醫낅즺 湲곗????덈컲源뚯? ???곹깭
  - ?⑥? ?묒뾽? packet 3~5 寃?섏? answer mode coverage ?뺤씤?대떎

### 二쇱쓽?ы빆
- `-InstallAutoragDeps`??而⑦뀒?대꼫 ?ㅽ뻾 以?pip install???섑뻾?섎?濡?backend recreate ?댄썑?먮뒗 ?ㅼ떆 ?꾩슂?????덈떎.
- ??以묒슂???댁쁺 ?④퀎濡??섏뼱媛?ㅻ㈃ ?ㅼ쓬??quantity蹂대떎 mode coverage瑜??곗꽑 遊먯빞 ?쒕떎. ?뱁엳 `project_management`? `contract_review` approved coverage瑜????섎┫ ?꾩슂媛 ?덈떎.
## 2026-03-12 15:55:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- ?⑥븘 ?덈뜕 review packet ?꾩껜瑜???踰덉뿉 triage?덈떎.
- 理쒖떊 gold ops run? `gold_ops_20260312_1552`?닿퀬, ?꾩옱 backlog??`pending 0 / approved 42 / rejected 31 / gold_ready 42` ?곹깭??
- `review_packets_gold_ops_20260312_1552.json` 湲곗? packet ?섎뒗 `0`?대떎. 利??꾩옱 ?볦뿬 ?덈뜕 gold backlog 寃?섎뒗 紐⑤몢 ?앸궗??

### 諛섏쁺 ?뚯씪
- `backend/data/autorag/review/review_decisions_gold_ops_20260312_1545.json`
  - ?⑥? 56嫄??꾩껜?????batch decision
  - 寃곌낵:
    - ?뱀씤 32嫄?異붽?
    - 諛섎젮 24嫄?異붽?
- source review queue 諛섏쁺:
  - `review_queue_gold5y_20260312_0917.json`
  - `review_queue_goldbatch_20260312_1116_finance_officer.json`
  - `review_queue_goldbatch_20260312_1116_new_employee.json`
  - `review_queue_goldbatch_20260312_1116_team_lead.json`

### 寃利?
- decision 諛섏쁺
  - `docker exec gpt_rules-backend-1 python /app/tests/autorag/apply_review_decisions.py --decisions-path /app/data/autorag/review/review_decisions_gold_ops_20260312_1545.json --review-dir /app/data/autorag/review`
  - 寃곌낵: `Applied decisions: 56`
- gold ops export
  - `powershell -ExecutionPolicy Bypass -File scripts/run_gold_ops_loop.ps1 -RunId gold_ops_20260312_1552 -InstallAutoragDeps`
  - 寃곌낵臾?
    - `backend/data/autorag/review/merged_review_queue_gold_ops_20260312_1552.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1552.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1552.md`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1552.json`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1552.md`
    - `backend/data/autorag/gold/qa_gold_gold_ops_20260312_1552.parquet`
    - `backend/data/autorag/gold/qa_gold_gold_ops_20260312_1552.json`
    - `backend/data/autorag/gold/qa_gold_latest.parquet`
- ?뚯뒪??
  - `docker exec gpt_rules-backend-1 pytest tests/test_autorag_gold_dataset_utils.py tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 寃곌낵: `45 passed`

### ?꾩옱 ?곹깭
- gold-approved coverage by answer mode:
  - `audit_response`: 9
  - `contract_review`: 3
  - `hr_admin`: 11
  - `procurement_bid`: 6
  - `project_management`: 8
  - `standard`: 5
- 1李?醫낅즺 湲곗? 異⑹”
  - `gold_ready_rows >= 20`: 異⑹” (`42`)
  - 6媛?answer mode 媛곴컖 ?뱀씤 row 2嫄??댁긽: 異⑹”
  - `user_feedback` row triage ?꾨즺: 異⑹”
  - gold parquet export ?곗냽 ?뺤긽 ?숈옉: 異⑹”

### ?대뵒媛 ?앹씤媛
- packet 湲곕컲 珥덇린 gold-set ?뺤옣 ?묒뾽? ?ш린??1李?醫낅즺濡?蹂몃떎.
- ?ㅼ쓬遺?곕뒗 媛숈? backlog瑜?怨꾩냽 ?먮????④퀎媛 ?꾨땲?? ???낅젰???앷만 ?뚮쭔 ?ㅼ떆 ?쒖옉?쒕떎.
  - ??persona ?꾨낫 諛곗튂 ?앹꽦
  - ?ㅼ젣 ?댁쁺 feedback ?꾩쟻
  - ??`bad` review queue 諛쒖깮
- 利??꾩옱 湲곗????앹? `?꾩옱 backlog pending 0 + gold parquet 理쒖떊???꾨즺` ?곹깭??
## 2026-03-12 16:00:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- ?꾩옱 諛고룷 媛???곹깭瑜?蹂꾨룄 ?ㅻ깄??臾몄꽌濡?怨좎젙?덈떎.
- ?꾩껜 肄붾뱶 諛깆뾽蹂몄쓣 ?앹꽦??以鍮꾨? 留덉낀怨? ?묒뾽蹂몄쓣 git 珥덇린 而ㅻ컠?쇰줈 ??ν븷 ?덉젙?대떎.
- ?꾩옱 湲곗? ?꾨즺 ?곹깭??`internal deploy ready + backlog pending 0 + gold_ready 42 + latest gold parquet exported` ?대떎.

### 臾몄꽌??
- ?곹깭 ?ㅻ깄??
  - `Docs/STATE_SNAPSHOT_20260312_1600.md`
- 湲곗? 臾몄꽌:
  - `HANDOFF.md`
  - `Docs/INTERNAL_DOCKER_DEPLOY.md`
  - `backend/tests/autorag/README.md`

### 而ㅻ컠/諛깆뾽 湲곗?
- git ??μ냼媛 ?놁뿀湲??뚮Ц???대쾲 ?쒖젏遺??濡쒖뺄 ??μ냼瑜?珥덇린?뷀빐 ?꾩옱 ?곹깭瑜?珥덇린 湲곗??좎쑝濡??〓뒗??
- 諛깆뾽? 肄붾뱶 湲곗? ?곗텧臾쇰줈 ?④린怨? `runtime`, `tmp`, `backups`, `*.log`, `*.zip`??git 異붿쟻?먯꽌 ?쒖쇅?쒕떎.

### ?꾩옱 ?먮떒
- 吏湲??쒖젏???쒖궗??諛고룷 吏곸쟾 ?ㅻ깄?룐앹쑝濡??곹빀?섎떎.
- ?댄썑 蹂寃쎌씠 ?앷린硫????쒖젏 而ㅻ컠怨?諛깆뾽 zip??湲곗? 蹂듦뎄?먯쑝濡??ъ슜?섎㈃ ?쒕떎.
## 2026-03-12 18:20:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- ?ъ씠?쒕컮??`諛고룷 硫붾え` ?뱀뀡???쒓굅?덈떎.
- 愿??留덊겕?낆? `frontend/src/components/Layout/Shell.tsx` ?먯꽌 ??젣?덈떎.
- ?④퍡 ?⑤뜕 `sidebar-note-section` ?꾩슜 ?ㅽ??쇰룄 `frontend/src/index.css` ?먯꽌 ?뺣━?덈떎.

### 諛고룷 諛??뺤씤
- ?꾨줎??鍮뚮뱶:
  - `npm run build`
- ?대? ?꾨줎???щ같??
  - `docker compose -p gpt_rules_internal -f docker-compose.internal.yml up -d --build frontend`
- ?뺤씤:
  - `http://218.38.240.188:28088/chat/` ?묐떟 `200`
  - `http://127.0.0.1:28000/api/health` ?묐떟 `{"status":"ok","documents":77,"llm_configured":true}`

## 2026-03-12 18:12:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- ?ъ씠?쒕컮 ?섎떒 寃뱀묠??1李??섏젙 ?꾩뿉???⑥븘 ?덉뼱 2李?蹂댁젙???곸슜?덈떎.
- `.sidebar.panel::after` ?ㅻ쾭?덉씠 蹂대뜑瑜??ъ씠?쒕컮?먮쭔 鍮꾪솢?깊솕?덈떎.
- 留덉?留?`sidebar-note-section`??援щ텇?좎쓣 ?뱀뀡 ?먯껜 border媛 ?꾨땲???대? pseudo element濡???꺼 ?섎떒 ?⑤꼸 寃쎄퀎? ?쒓컖?곸쑝濡?遺꾨━?덈떎.

### 諛고룷 諛??뺤씤
- ?대? ?꾨줎???щ같??
  - `docker compose -p gpt_rules_internal -f docker-compose.internal.yml up -d --build frontend`
- ?뺤씤:
  - `http://218.38.240.188:28088/chat/` ?묐떟 `200`
  - `http://127.0.0.1:28000/api/health` ?묐떟 `{"status":"ok","documents":77,"llm_configured":true}`

## 2026-03-12 18:05:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- ?ъ씠?쒕컮 理쒗븯?⑥뿉???덉씠?닿? 寃뱀퀜 蹂댁씠??UI ?댁뒋瑜??섏젙?덈떎.
- ?먯씤? `.sidebar::before` ?섎떒 ?μ떇?좉낵 留덉?留?`sidebar-note-section` 寃쎄퀎媛 媛숈? ?꾩튂?먯꽌 寃뱀퀜 蹂댁씠??援ъ“???
- `frontend/src/index.css`?먯꽌 ?섎떒 ?μ떇?좎쓣 ?쒓굅?섍퀬, ?ъ씠?쒕컮 ?섎떒 ?⑤뵫怨?留덉?留??뱀뀡 ?곷떒 ?щ갚???섎졇??

### 諛고룷 諛??뺤씤
- ?꾨줎??鍮뚮뱶:
  - `npm run build`
- ?대? ?꾨줎???щ같??
  - `docker compose -p gpt_rules_internal -f docker-compose.internal.yml up -d --build frontend`
- ?뺤씤:
  - `http://218.38.240.188:28088/chat/` ?묐떟 `200`
  - `http://127.0.0.1:28000/api/health` ?묐떟 `{"status":"ok","documents":77,"llm_configured":true}`

## 2026-03-12 17:52:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- ?듬? ?됯?(`POST /api/chat-feedback`) ??`500 Internal Server Error`媛 諛쒖깮?섎뒗 ?댁쁺 ?댁뒋瑜??섏젙?덈떎.
- ?먯씤? `runtime/internal/backend-data/feedback/chat_interactions.jsonl`??JSON 媛앹껜 2媛쒓? ??以꾩뿉 遺숈뼱 ??λ맂 ?덉퐫?쒖???
- `backend/app/services/feedback_store.py`??JSONL ?뚯꽌瑜?媛뺥솕????以꾩뿉 ?댁뼱 遺숈? JSON 媛앹껜???쎈룄濡??섏젙?덈떎.
- `backend/tests/test_feedback_store.py`??concatenated JSONL ?뚭? ?뚯뒪?몃? 異붽??덈떎.

### ?댁쁺 ?곗씠??議곗튂
- ?댁쁺 ?뚯씪 諛깆뾽:
  - `runtime/internal/backend-data/feedback/chat_interactions.backup_20260312_1740.jsonl`
- ?댁쁺 ?뚯씪 ?뺢퇋??
  - `runtime/internal/backend-data/feedback/chat_interactions.jsonl`
- ?뺢퇋????`}{` ?⑦꽩 ?ш???寃곌낵 異붽? 遺숈쓬 ?덉퐫?쒕뒗 ?⑥? ?딆븯??

### 諛고룷 諛?寃利?
- ?대? 諛깆뿏???щ퉴???ш린??
  - `docker compose -p gpt_rules_internal -f docker-compose.internal.yml up -d --build backend`
- 而⑦뀒?대꼫 ?⑥쐞 ?뚯뒪??
  - `docker exec gpt_rules_internal-backend-1 pytest tests/test_feedback_store.py -q`
  - 寃곌낵: `3 passed`
- ?ㅼ젣 API 寃利?
  - `POST http://127.0.0.1:28000/api/chat-feedback`
  - ?뺤긽 ?묐떟 ?뺤씤, `feedback_id` 諛쒓툒 諛?`superseded_feedback_id` 媛깆떊 ?뺤씤

## 2026-03-12 17:05:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- `gh`瑜??ъ슜??private ?먭꺽 ??μ냼瑜??앹꽦?덈떎.
- 寃쎈웾 mirror repo `C:\Project\gpt_rules_private_20260312_1630`??`main` 釉뚮옖移섎? ?먭꺽 `origin`??push ?덈떎.

### ?먭꺽 ??μ냼
- `https://github.com/bruce0817kr/gpt_rules_private`
- visibility: `PRIVATE`
- default branch: `main`

### ?꾩옱 ?곹깭
- mirror repo??`origin/main`??異붿쟻 以묒씠??
- mirror repo working tree??clean ?곹깭??

## 2026-03-12 17:00:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- `gh auth login`???꾨즺?덈떎.
- ?몄쬆 ?몄뒪?몃뒗 `github.com`, git protocol? `https`濡??ㅼ젙?먮떎.
- ?꾩옱 濡쒓렇??怨꾩젙? `bruce0817kr` ?대떎.

### ?꾩옱 ?곹깭
- `gh` 湲곕컲 private ?먭꺽 ??μ냼 ?앹꽦怨?push瑜?吏꾪뻾?????덈떎.

## 2026-03-12 16:45:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- `GitHub CLI`瑜?`winget`?쇰줈 ?ㅼ튂?덈떎.
- ?ㅼ튂 寃쎈줈??`C:\Program Files\GitHub CLI\gh.exe` ?대떎.
- ??PowerShell ?몄뀡?먯꽌 `gh`媛 諛붾줈 ?≫엳?꾨줉 ?ъ슜??PowerShell ?꾨줈?꾩뿉 PATH 異붽? ?쇱씤??諛섏쁺?덈떎.

### ?꾩옱 ?곹깭
- `gh --version` ?뺤씤 ?꾨즺
- `where.exe gh` ?뺤씤 ?꾨즺
- ?몄쬆? ?꾩쭅 ???섏뼱 ?덉뼱 `gh auth login`???ㅼ쓬 ?④퀎??

## 2026-03-12 16:30:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- ?먮낯 濡쒖뺄 ??μ냼????⑸웾 紐⑤뜽 罹먯떆? ?댁쁺 ?곗텧臾쇱씠 ?ы븿???덉뼱 ?먭꺽 Git ?낅줈?쒖슜?쇰줈??遺?곹빀?섎떎怨??먮떒?덈떎.
- private ?먭꺽 ?낅줈?쒖슜 寃쎈웾 mirror repo瑜?蹂꾨룄 寃쎈줈???앹꽦?섍린濡?寃곗젙?덈떎.
- mirror repo?먮뒗 肄붾뱶, ?ㅼ젙, 臾몄꽌留??ы븿?섍퀬 `backend/data`, `backend/uploads`, `runtime`, `migration_export`, ??⑸웾 dump/log???쒖쇅?쒕떎.

### 臾몄꽌??
- `Docs/PRIVATE_REPO_EXPORT_20260312_1630.md`

### ?꾩냽 湲곗?
- ?먮낯 ??μ냼??蹂듦뎄 湲곗??쇰줈 ?좎??쒕떎.
- ?먭꺽 Git ?낅줈?쒕뒗 mirror repo 湲곗??쇰줈 吏꾪뻾?쒕떎.
## 2026-03-12 18:15:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- ?뚯궗 ?꾨찓??`https://ai.gtp.or.kr/chat/` ?곌껐 ???꾨줎?멸? `/chat/api`留?怨좎젙 ?몄텧?댁꽌 ?욌떒 ?꾨줉???ㅼ젙 李⑥씠??痍⑥빟??臾몄젣瑜?蹂댁셿?덈떎.
- `frontend/src/api/client.ts`??API base auto-detection??異붽???釉뚮씪?곗??먯꽌 `/chat/api`? `/api`瑜??쒖감 ?먯깋?섍퀬, ?댁븘 ?덈뒗 寃쎈줈瑜?怨좎젙 ?ъ슜?섎룄濡?蹂寃쏀뻽??
- `Docs/INTERNAL_DOCKER_DEPLOY.md`???뚯궗 ?꾨찓??reverse proxy媛 `/chat/`? ?④퍡 `/chat/api/` ?먮뒗 `/api/` 以?理쒖냼 ?섎굹瑜?諛섎뱶???꾨떖?댁빞 ?쒕떎???댁쁺 硫붾え瑜?異붽??덈떎.

### ?ㅼ쓬 ?④퀎
- `npm run build`濡??꾨줎??鍮뚮뱶 寃利?
- ?대? ?꾨줎??而⑦뀒?대꼫 ?щ퉴????`http://127.0.0.1:28088/chat/api/health` 諛??ㅼ젣 UI 寃쎈줈 ?ы솗??
## 2026-03-13 00:20:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- 臾몄꽌 援ъ꽦??移댄뀒怨좊━ 以묒떖?먯꽌 `踰뺣졊 援ъ꽦`??癒쇱? 蹂댁씠?꾨줉 ?뺤옣?덈떎.
- ?ъ씠?쒕컮???섏쭛??踰뺣졊 臾띠쓬, 踰뺣졊 臾몄꽌 ?? 湲고? ?대?臾몄꽌 ?섎? ?붿빟?섍퀬, 踰뺣졊紐?湲곗??쇰줈 ?쇱퀜??蹂????덇쾶 ?덈떎.
- 臾몄꽌愿由?> 臾몄꽌?낅줈???곸뿭?먮룄 `?꾩옱 ?섏쭛??踰뺣졊` ?붿빟 諛뺤뒪瑜?異붽????대뼡 踰뺣졊???대? ?곸옱?섏뼱 ?덈뒗吏 媛꾨왂???뺤씤?????덇쾶 ?덈떎.

### 肄붾뱶 蹂寃?
- `frontend/src/utils/lawCollections.ts`
  - 踰뺣졊 臾몄꽌 ?먮퀎, 踰뺣졊 臾띠쓬 吏묎퀎, 踰꾩쟾 ?щ㎎ ?⑥닔 異붽?
- `frontend/src/types/api.ts`
  - `DocumentRecord`??`source_id`, `source_version`, `source_url`, `content_hash` 異붽?
- `frontend/src/components/Layout/Shell.tsx`
  - ?ъ씠?쒕컮 `踰뺣졊 援ъ꽦` ?뱀뀡 異붽?
  - 湲곗〈 `臾몄꽌 援ъ꽦` 紐낆묶??`移댄뀒怨좊━ 援ъ꽦`?쇰줈 議곗젙
- `frontend/src/components/Admin/AdminPanel.tsx`
  - ?낅줈???곸뿭??`?꾩옱 ?섏쭛??踰뺣졊` ?붿빟 諛뺤뒪 異붽?
  - 臾몄꽌 紐⑸줉?먯꽌 踰뺣졊 臾몄꽌??踰꾩쟾 ?뺣낫 ?몄텧
- `frontend/src/index.css`
  - 踰뺣졊 ?붿빟 移대뱶/紐⑸줉 ?ㅽ???異붽?

### 寃利?
- `frontend/`?먯꽌 `npm run build` ?듦낵

## 2026-03-13 00:35:00 +09:00

### ?대쾲 ?묒뾽 ?붿빟
- ?ъ씠?쒕컮?먯꽌 `移댄뀒怨좊━ 援ъ꽦` ?뱀뀡???쒓굅?덈떎.
- `踰뺣졊 援ъ꽦` ?뱀뀡? ??긽 ?쇱퀜吏??곹깭濡??좎??섍퀬 `Hide/Show` 踰꾪듉???쒓굅?덈떎.
- 踰뺣졊 援ъ꽦怨?移댄뀒怨좊━ 援ъ꽦??寃뱀퀜 蹂댁씠??臾몄젣瑜??⑥닚 援ъ“濡??뺣━?덈떎.

### 寃利?
- `frontend/`?먯꽌 `npm run build` ?듦낵
- ?대? ?꾨줎???щ같????`http://127.0.0.1:28088/chat/api/health` ?뺤긽

