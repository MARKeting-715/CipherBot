from __future__ import annotations

import math
from collections import Counter


def analyze_text(text: str) -> dict[str, object]:
    freq = Counter(text)
    total = len(text)
    entropy = 0.0
    if total:
        entropy = -sum((count / total) * math.log2(count / total) for count in freq.values())

    repeats = repeated_sequences(text)
    return {
        "length": total,
        "unique_chars": len(freq),
        "frequency": freq.most_common(15),
        "entropy": entropy,
        "repeats": repeats,
    }


def repeated_sequences(text: str, min_len: int = 2, max_len: int = 5, limit: int = 10) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for size in range(min_len, max_len + 1):
        for index in range(0, max(0, len(text) - size + 1)):
            counter[text[index : index + size]] += 1

    return [(seq, count) for seq, count in counter.most_common(limit) if count > 1]


def format_analysis(text: str) -> str:
    data = analyze_text(text)
    frequency = "\n".join(f"`{_visible(char)}`: {count}" for char, count in data["frequency"]) or "нет данных"
    repeats = "\n".join(f"`{_visible(seq)}`: {count}" for seq, count in data["repeats"]) or "не найдены"
    return (
        "📊 Анализ текста\n\n"
        f"Символов: {data['length']}\n"
        f"Уникальных символов: {data['unique_chars']}\n"
        f"Энтропия: {data['entropy']:.3f}\n\n"
        f"Частота символов:\n{frequency}\n\n"
        f"Повторяющиеся последовательности:\n{repeats}"
    )


def _visible(value: str) -> str:
    return value.replace("\n", "\\n").replace("\t", "\\t") or "пусто"
