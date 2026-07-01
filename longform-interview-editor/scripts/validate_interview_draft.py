#!/usr/bin/env python3
"""Run lightweight structural checks on a Markdown Q&A interview draft."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


HEADING_RE = re.compile(r"^##\s+(?:(\d+)[｜|]\s*)?(.+?)\s*$", re.MULTILINE)
ANSWER_RE = re.compile(
    r"\*\*(?:嘉宾|[^*\n：]{1,20})：\*\*\s*\n+(.+?)(?=\n\*\*[^*\n：]{1,20}：|\n##\s|\Z)",
    re.DOTALL,
)


def compact_length(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft", type=Path)
    parser.add_argument("--min-answer", type=int, default=150)
    parser.add_argument("--max-answer", type=int, default=500)
    args = parser.parse_args()

    text = args.draft.read_text(encoding="utf-8")
    warnings: list[str] = []

    headings = HEADING_RE.findall(text)
    numbers = [int(number) for number, _ in headings if number]
    if numbers:
        expected = list(range(numbers[0], numbers[0] + len(numbers)))
        if numbers != expected:
            warnings.append(f"chapter numbering is discontinuous: {numbers}")

    titles = [title.strip() for _, title in headings]
    duplicates = sorted({title for title in titles if titles.count(title) > 1})
    if duplicates:
        warnings.append(f"duplicate chapter titles: {duplicates}")

    if re.search(r"^##\s+\d+\|", text, re.MULTILINE):
        warnings.append("mixed separator detected: use ｜ consistently")

    answers = ANSWER_RE.findall(text)
    for index, answer in enumerate(answers, 1):
        length = compact_length(answer)
        if length < args.min_answer or length > args.max_answer:
            warnings.append(
                f"answer {index} length {length} is outside "
                f"{args.min_answer}-{args.max_answer}"
            )

    if not answers:
        warnings.append("no bold speaker-labelled answers detected")

    if warnings:
        print("WARN")
        for warning in warnings:
            print(f"- {warning}")
        return 1

    print(f"OK: {len(headings)} chapters, {len(answers)} answers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
