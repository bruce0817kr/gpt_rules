from app.models.schemas import LibraryShortcutScope, DocumentRecord


class ShortcutScopeMatcher:
    KEYWORDS: dict[LibraryShortcutScope, tuple[str, ...]] = {
        LibraryShortcutScope.HR: (
            "인사",
            "보수",
            "복무",
            "휴가",
            "교육훈련",
            "공무직",
            "노사",
            "성희롱",
            "성폭력",
            "인권",
            "명예퇴직",
            "숙소",
        ),
        LibraryShortcutScope.FINANCE: (
            "재무",
            "회계",
            "예산",
            "정산",
            "업무추진비",
            "임금",
            "법인카드",
            "상품권",
            "마일리지",
            "여비",
            "수당",
            "지출",
            "결산",
        ),
        LibraryShortcutScope.GENERAL_AFFAIRS: (
            "총무",
            "시설",
            "차량",
            "전산",
            "홈페이지",
            "문서 관리",
            "기록물",
            "정보공개",
            "공인",
            "영상정보처리기기",
            "데이터 센터",
            "편의시설",
        ),
        LibraryShortcutScope.GENERAL_ADMIN: (
            "이사회",
            "위원회",
            "직제",
            "위임전결",
            "운영위원회",
            "청원심의회",
            "규정관리",
            "행동강령",
            "적극행정",
            "감사",
            "원장추천위원회",
            "사업관리",
        ),
        LibraryShortcutScope.LEGAL: (
            "법률",
            "시행령",
            "시행규칙",
            "근로기준법",
            "산업안전보건법",
            "하도급",
            "공정화",
            "중대재해",
            "계약에 관한 법률",
            "건축법",
            "진흥법",
        ),
    }

    def matches(self, scope: LibraryShortcutScope, record: DocumentRecord) -> bool:
        title_corpus = f"{record.title}\n{record.filename}".lower()
        if scope == LibraryShortcutScope.LEGAL:
            return record.category == record.category.LAW or any(
                keyword.lower() in title_corpus for keyword in self.KEYWORDS[scope]
            )
        if scope == LibraryShortcutScope.GENERAL_ADMIN:
            return self._general_admin_match(title_corpus)
        return any(keyword.lower() in title_corpus for keyword in self.KEYWORDS[scope])

    def _general_admin_match(self, title_corpus: str) -> bool:
        other_scopes = [
            LibraryShortcutScope.HR,
            LibraryShortcutScope.FINANCE,
            LibraryShortcutScope.GENERAL_AFFAIRS,
            LibraryShortcutScope.LEGAL,
        ]
        if any(
            keyword.lower() in title_corpus
            for scope in other_scopes
            for keyword in self.KEYWORDS[scope]
        ):
            return False
        return any(keyword.lower() in title_corpus for keyword in self.KEYWORDS[LibraryShortcutScope.GENERAL_ADMIN]) or True
