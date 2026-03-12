from app.models.schemas import DocumentDomain
from app.services.document_parser import ParsedSection


class DocumentDomainClassifier:
    KEYWORDS: dict[DocumentDomain, tuple[str, ...]] = {
        DocumentDomain.HR: (
            "인사",
            "채용",
            "근태",
            "복무",
            "휴가",
            "평가",
            "승진",
            "징계",
            "직원",
            "급여",
            "교육훈련",
            "성희롱",
            "성폭력",
            "성평등",
            "취업",
            "노사",
            "명예퇴직",
            "공무직",
        ),
        DocumentDomain.FINANCE: (
            "재무",
            "회계",
            "예산",
            "정산",
            "지출",
            "수입",
            "결산",
            "세무",
            "영수증",
            "법인카드",
            "자금",
            "재원",
            "업무추진비",
            "여비",
            "수당",
            "보수",
            "임금",
            "마일리지",
        ),
        DocumentDomain.GENERAL_AFFAIRS: (
            "총무",
            "비품",
            "자산",
            "시설",
            "차량",
            "사무실",
            "보안",
            "우편",
            "인장",
            "용역관리",
            "전산",
            "홈페이지",
            "인터넷",
            "시설관리",
            "기록물",
            "영상정보처리기기",
        ),
        DocumentDomain.GENERAL_ADMIN: (
            "행정",
            "공문",
            "결재",
            "시행",
            "보고",
            "위원회",
            "지침",
            "출장",
            "행정지원",
            "문서관리",
            "기안",
        ),
        DocumentDomain.LEGAL: (
            "법무",
            "법률",
            "법령",
            "계약",
            "준법",
            "소송",
            "개인정보",
            "규제",
            "협약",
            "감사",
            "부패",
            "고발",
            "이해충돌",
            "윤리",
            "행동강령",
        ),
        DocumentDomain.PROCUREMENT: (
            "조달",
            "구매",
            "입찰",
            "발주",
            "업체",
            "제안서",
            "계약체결",
            "물품",
            "상품권",
        ),
        DocumentDomain.RESEARCH: (
            "연구",
            "과제",
            "연구비",
            "학술",
            "성과",
            "실험",
            "과학기술",
            "연구윤리",
            "사업관리",
            "정보화지원사업",
        ),
    }

    def classify(self, title: str, filename: str, tags: list[str], sections: list[ParsedSection]) -> DocumentDomain:
        title_corpus = "\n".join([title, filename, " ".join(tags)]).lower()
        body_corpus = "\n".join(section.text for section in sections[:8]).lower()
        best_domain = DocumentDomain.OTHER
        best_score = 0
        for domain, keywords in self.KEYWORDS.items():
            score = sum(title_corpus.count(keyword.lower()) * 3 for keyword in keywords)
            score += sum(body_corpus.count(keyword.lower()) for keyword in keywords)
            if score > best_score:
                best_domain = domain
                best_score = score
        return best_domain if best_score > 0 else DocumentDomain.GENERAL_ADMIN
