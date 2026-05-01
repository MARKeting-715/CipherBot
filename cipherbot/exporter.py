from __future__ import annotations

import json
from datetime import datetime
from typing import Any


def export_json(data: Any) -> bytes:
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


def export_history_txt(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        return "История пуста.\n".encode("utf-8")

    chunks: list[str] = []
    for row in rows:
        chunks.append(
            "\n".join(
                [
                    f"ID: {row['id']}",
                    f"Тип: {row['operation_type']}",
                    f"Алгоритм: {row['algorithm']}",
                    f"Время: {row['created_at']}",
                    f"Вход: {row['input_text']}",
                    f"Результат: {row['output_text']}",
                ]
            )
        )
    return ("\n\n---\n\n".join(chunks) + "\n").encode("utf-8")


def export_analysis_txt(text: str) -> bytes:
    return (text + "\n").encode("utf-8")


def timestamped_name(prefix: str, extension: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}.{extension}"
