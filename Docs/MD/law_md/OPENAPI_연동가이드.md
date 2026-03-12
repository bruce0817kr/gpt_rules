# 국가법령정보 OpenAPI 연동 안내문 (프로젝트 적용용)

## 1) 목적
본 문서는 프로젝트에서 국가법령정보 OpenAPI를 사용해 **최신 법령 본문을 자동 수집/갱신**하기 위한 최소 구현 가이드를 제공합니다.

- 대상 API: `https://www.law.go.kr/DRF/lawService.do`
- 주요 target
  - `target=law`: 법령 목록/검색
  - `target=eflaw`: 현행법령(시행일) 본문 조회

---

## 2) 인증/접근
- 파라미터 `OC` 필수
- 현재 환경 사용값: `dhl`
- 운영 반영 시 권장:
  - 코드 하드코딩 금지
  - `.env` 또는 OS 환경변수로 관리
  - 로그 출력 시 인증값 마스킹

예)
```bash
LAW_OC=dhl
```

---

## 3) 권장 수집 플로우
1. 법령명 기준으로 법령 페이지(`https://www.law.go.kr/법령/{법령명}`) 조회
2. 페이지 내 `lsiSeq(MST)`와 `efYd` 추출
3. OpenAPI 본문 호출
   - `target=eflaw&MST={lsiSeq}&efYd={efYd}&type=JSON`
4. JSON 원본 저장 + Markdown 변환 저장
5. 리포트(CSV)로 성공/실패 추적

---

## 4) API 호출 예시
### 4-1) 목록 조회
```text
https://www.law.go.kr/DRF/lawService.do?OC=dhl&target=law&type=JSON&query=근로기준법
```

### 4-2) 본문 조회(시행일 기준)
```text
https://www.law.go.kr/DRF/lawService.do?OC=dhl&target=eflaw&type=JSON&MST=265959&efYd=20251023
```

---

## 5) 프로젝트 구조 권장안
```text
law_md/
  ├─ *.json                 # 법령 원본
  ├─ *.md                   # 변환 산출물
  ├─ law_collection_report.csv
  └─ OPENAPI_연동가이드.md
```

---

## 6) 운영 체크리스트
- [ ] 법령명 리스트(인사노무/계약/공사) 유지관리
- [ ] 실패 재시도(네트워크/일시 오류) 2~3회
- [ ] 변경 감지(해시/개정일) 시에만 MD 재생성
- [ ] 일일 또는 주간 배치 스케줄링
- [ ] 결과 리포트 자동 생성(CSV)

---

## 7) 보안/컴플라이언스
- OpenAPI 결과는 원문 보존(JSON) + 가공본(MD) 분리 저장
- 법령 원문은 출처 URL 및 수집시각을 파일 헤더에 기록
- 대외 배포 시 최신성 검증(시행일/개정일) 재확인

---

## 8) 이번 작업 산출물
- 저장 경로: `C:\Project\gpt_rules\Docs\hwpx\law_md`
- 생성 파일:
  - 법령별 `*.json`, `*.md`
  - `law_collection_report.csv`
  - 본 가이드 문서
