from app.models.schemas import DocumentCategory
from app.services.document_parser import ParsedSection


class DocumentCategoryClassifier:
    def classify(
        self,
        title: str,
        filename: str,
        tags: list[str],
        sections: list[ParsedSection],
    ) -> DocumentCategory:
        title_lower = title.lower()
        filename_lower = filename.lower()
        corpus = "\n".join([title, filename, " ".join(tags)]).lower()

        if title_lower.startswith("[1-") or "정관" in title_lower:
            return DocumentCategory.FOUNDATION

        if title_lower.startswith("[4-"):
            return DocumentCategory.GUIDE

        if title_lower.startswith("[2-") or title_lower.startswith("[3-"):
            return DocumentCategory.RULE

        law_keywords = (
            "법률",
            "법령",
            "시행령",
            "시행규칙",
            "근로기준법",
            "개인정보보호법",
            "민법",
            "상법",
        )
        if any(keyword in corpus for keyword in law_keywords):
            return DocumentCategory.LAW

        guide_keywords = ("지침", "요령", "매뉴얼", "편람", "운영지침", "가이드")
        if any(keyword in title_lower for keyword in guide_keywords) or any(
            keyword in filename_lower for keyword in guide_keywords
        ):
            return DocumentCategory.GUIDE

        notice_keywords = ("공지", "공고", "알림", "안내문", "게시")
        if any(keyword in title_lower for keyword in notice_keywords):
            return DocumentCategory.NOTICE

        rule_keywords = ("규정", "규칙", "강령")
        if any(keyword in title_lower for keyword in rule_keywords):
            return DocumentCategory.RULE

        return DocumentCategory.OTHER
