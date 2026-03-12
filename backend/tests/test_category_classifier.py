from app.models.schemas import DocumentCategory
from app.services.category_classifier import DocumentCategoryClassifier
from app.services.document_parser import ParsedSection


def test_category_classifier_detects_foundation() -> None:
    classifier = DocumentCategoryClassifier()

    category = classifier.classify(
        title="[1-1] 정관(2025.04.14.)",
        filename="[1-1] 정관.md",
        tags=[],
        sections=[ParsedSection(text="재단의 목적과 조직에 관한 사항", location="구간 1")],
    )

    assert category == DocumentCategory.FOUNDATION


def test_category_classifier_detects_guide() -> None:
    classifier = DocumentCategoryClassifier()

    category = classifier.classify(
        title="업무추진비 집행지침",
        filename="guide.md",
        tags=[],
        sections=[ParsedSection(text="이 지침은 업무추진비 집행 절차를 정한다.", location="구간 1")],
    )

    assert category == DocumentCategory.GUIDE


def test_category_classifier_detects_rule() -> None:
    classifier = DocumentCategoryClassifier()

    category = classifier.classify(
        title="재무회계 규정",
        filename="rule.md",
        tags=[],
        sections=[ParsedSection(text="예산과 회계 처리에 관한 규정", location="구간 1")],
    )

    assert category == DocumentCategory.RULE
