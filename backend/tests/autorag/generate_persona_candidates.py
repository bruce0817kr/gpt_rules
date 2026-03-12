from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI

from app.config import get_settings
from app.dependencies import get_catalog
from app.models.schemas import AnswerMode
from gold_dataset_utils import finalize_candidate_cases, load_json_cases

MODE_SPECS: dict[AnswerMode, dict[str, Any]] = {
    AnswerMode.STANDARD: {
        "count": 2,
        "focus": "규정 전반에서 직원이 자주 묻는 일반 실무 질문",
        "category_options": [["rule"], ["guide"], ["law"], ["notice"], ["rule", "guide"]],
    },
    AnswerMode.HR_ADMIN: {
        "count": 3,
        "focus": "복무, 휴가, 승진, 징계, 승인 절차 같은 인사 실무 질문",
        "category_options": [["rule", "guide"], ["rule", "law"], ["rule", "guide", "law"]],
    },
    AnswerMode.CONTRACT_REVIEW: {
        "count": 3,
        "focus": "계약 변경, 책임 분기, 위약, 서류 누락, 대금 지급 같은 계약 검토 질문",
        "category_options": [["rule", "guide"], ["rule", "guide", "law"], ["rule", "law"]],
    },
    AnswerMode.PROJECT_MANAGEMENT: {
        "count": 3,
        "focus": "사업비 집행, 결과보고, 정산, 승인 흐름, 일정 관리 질문",
        "category_options": [["rule", "guide"], ["rule", "notice"], ["rule", "guide", "notice"]],
    },
    AnswerMode.PROCUREMENT_BID: {
        "count": 3,
        "focus": "비교견적, 입찰, 계약 체결, 예정가격, 검수 질문",
        "category_options": [["rule", "guide", "law"], ["rule", "law"], ["rule", "guide"]],
    },
    AnswerMode.AUDIT_RESPONSE: {
        "count": 4,
        "focus": "증빙, 법인카드, 감사 대응, 환수 위험, 사후 보완 질문",
        "category_options": [["rule", "guide", "law"], ["rule", "guide", "notice"], ["rule", "law"]],
    },
}


def load_personas(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Persona file must contain a list: {path}")
    return payload


def select_persona(path: Path, persona_id: str) -> dict[str, Any]:
    for persona in load_personas(path):
        if str(persona.get("id")) == persona_id:
            return persona
    raise ValueError(f"Persona not found: {persona_id}")


def existing_questions(*paths: Path) -> list[str]:
    questions: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        for case in load_json_cases(path):
            question = str(case.get("question", case.get("query", ""))).strip()
            if question:
                questions.append(question)
    return questions


def document_hints(max_titles_per_category: int = 8) -> dict[str, list[str]]:
    catalog = get_catalog()
    grouped: dict[str, list[str]] = {}
    for record in catalog.list_documents():
        if record.status.value != "ready":
            continue
        grouped.setdefault(record.category.value, [])
        if record.title not in grouped[record.category.value]:
            grouped[record.category.value].append(record.title)

    return {
        category: titles[:max_titles_per_category]
        for category, titles in sorted(grouped.items())
    }


def build_messages(
    *,
    persona: dict[str, Any],
    mode: AnswerMode,
    count: int,
    hints: dict[str, list[str]],
    existing: list[str],
) -> list[dict[str, str]]:
    spec = MODE_SPECS[mode]
    hint_lines = "\n".join(
        f"- {category}: {', '.join(titles)}"
        for category, titles in hints.items()
        if titles
    )
    category_options = json.dumps(spec["category_options"], ensure_ascii=False)
    existing_lines = "\n".join(f"- {question}" for question in existing[-20:]) or "- 없음"
    persona_json = json.dumps(persona, ensure_ascii=False, indent=2)

    return [
        {
            "role": "system",
            "content": (
                "당신은 AutoRAG gold-set 확장을 위한 질문 생성 서브 에이전트다. "
                "반드시 한국어로, 실제 직원이 업무 중 묻는 것 같은 질문만 생성한다. "
                "답을 쓰지 말고 질문 후보만 JSON으로 반환한다."
            ),
        },
        {
            "role": "user",
            "content": (
                f"페르소나:\n{persona_json}\n\n"
                f"이번 생성 목표 answer_mode: {mode.value}\n"
                f"focus: {spec['focus']}\n"
                f"생성 개수: {count}\n"
                f"허용 categories 조합 예시: {category_options}\n\n"
                "문서 힌트:\n"
                f"{hint_lines}\n\n"
                "이미 있는 질문(중복 금지):\n"
                f"{existing_lines}\n\n"
                "출력 형식:\n"
                "{\n"
                '  "questions": [\n'
                "    {\n"
                '      "question": "실제 직원 질문",\n'
                f'      "answer_mode": "{mode.value}",\n'
                '      "categories": ["rule", "guide"],\n'
                '      "candidate_note": "왜 이 질문이 실무적으로 중요한지 한 줄"\n'
                "    }\n"
                "  ]\n"
                "}\n\n"
                "제약:\n"
                "- 질문은 실제 결재, 집행, 검토, 증빙, 승인 전에 묻는 형태여야 한다.\n"
                "- 너무 추상적이거나 홍보성/잡담성 질문은 금지한다.\n"
                "- 같은 의미의 질문을 변형해 중복 생성하지 않는다.\n"
                "- categories는 반드시 배열로 반환한다.\n"
                "- 질문 문장 안에 답을 넣지 않는다."
            ),
        },
    ]


def parse_candidate_payload(content: str) -> list[dict[str, Any]]:
    payload = json.loads(content)
    questions = payload.get("questions", [])
    if not isinstance(questions, list):
        raise ValueError("Generator payload must contain a questions list.")
    return questions


def generate_mode_candidates(
    client: OpenAI,
    *,
    model: str,
    persona: dict[str, Any],
    mode: AnswerMode,
    target_count: int,
    hints: dict[str, list[str]],
    existing: list[str],
) -> list[dict[str, Any]]:
    generated: list[dict[str, Any]] = []
    attempts = 0

    while len(generated) < target_count and attempts < 3:
        attempts += 1
        remaining = target_count - len(generated)
        completion = client.chat.completions.create(
            model=model,
            temperature=0.9,
            response_format={"type": "json_object"},
            messages=build_messages(
                persona=persona,
                mode=mode,
                count=remaining,
                hints=hints,
                existing=existing + [candidate["question"] for candidate in generated],
            ),
        )
        content = completion.choices[0].message.content or "{}"
        batch = parse_candidate_payload(content)
        normalized_batch = [
            {
                **candidate,
                "answer_mode": mode.value,
                "persona_id": persona["id"],
                "persona_label": persona["label"],
            }
            for candidate in batch
        ]
        finalized = finalize_candidate_cases(
            normalized_batch,
            existing_questions=existing + [candidate["question"] for candidate in generated],
        )
        generated.extend(finalized[:remaining])

    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate persona-based candidate questions for AutoRAG gold expansion.")
    parser.add_argument(
        "--persona-id",
        type=str,
        default="five_year_employee",
        help="Persona id from personas.json.",
    )
    parser.add_argument(
        "--personas-path",
        type=Path,
        default=Path(__file__).with_name("personas.json"),
        help="Path to the persona definition JSON file.",
    )
    parser.add_argument(
        "--seed-path",
        type=Path,
        default=Path(__file__).with_name("seed_questions.json"),
        help="Path to the existing seed question JSON file.",
    )
    parser.add_argument(
        "--count-scale",
        type=int,
        default=1,
        help="Multiplier applied to the default per-mode candidate counts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/app/data/autorag/candidates"),
        help="Directory where candidate question files will be written.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        help="Run id suffix used in output filenames.",
    )
    args = parser.parse_args()

    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required to generate persona candidates.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    persona = select_persona(args.personas_path, args.persona_id)
    hints = document_hints()
    current_questions = existing_questions(args.seed_path)
    client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

    generated_cases: list[dict[str, Any]] = []
    for mode, spec in MODE_SPECS.items():
        mode_count = max(1, int(spec["count"]) * max(1, args.count_scale))
        generated_cases.extend(
            generate_mode_candidates(
                client,
                model=settings.llm_model,
                persona=persona,
                mode=mode,
                target_count=mode_count,
                hints=hints,
                existing=current_questions + [case["question"] for case in generated_cases],
            )
        )

    payload = {
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "persona": persona,
        "cases": generated_cases,
    }

    output_path = args.output_dir / f"candidate_cases_{persona['id']}_{args.run_id}.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Generated candidates: {len(generated_cases)}")
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    main()
