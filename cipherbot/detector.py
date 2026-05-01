from __future__ import annotations

import base64
import binascii
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionResult:
    algorithm: str
    confidence: int
    reason: str


BASE64_RE = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
MORSE_RE = re.compile(r"^[.\-/\s]+$")
HEX_RE = re.compile(r"^[0-9a-fA-F]+$")


def detect_cipher(text: str) -> DetectionResult:
    candidates = [
        _score_base64(text),
        _score_morse(text),
        _score_xor(text),
        _score_caesar(text),
    ]
    return max(candidates, key=lambda item: item.confidence)


def _score_base64(text: str) -> DetectionResult:
    stripped = text.strip()
    if len(stripped) < 8 or len(stripped) % 4 != 0 or not BASE64_RE.fullmatch(stripped):
        return DetectionResult("unknown", 5, "структура не похожа на Base64")
    try:
        decoded = base64.b64decode(stripped, validate=True)
    except binascii.Error:
        return DetectionResult("unknown", 10, "Base64 не проходит валидацию")
    printable = sum(32 <= byte <= 126 or byte in (9, 10, 13) for byte in decoded)
    confidence = 65 + int(30 * printable / max(1, len(decoded)))
    return DetectionResult("base64", min(confidence, 95), "валидная Base64-структура")


def _score_morse(text: str) -> DetectionResult:
    stripped = text.strip()
    if len(stripped) < 3 or not MORSE_RE.fullmatch(stripped):
        return DetectionResult("unknown", 5, "символы не похожи на азбуку Морзе")
    dot_dash = sum(ch in ".-" for ch in stripped)
    confidence = 55 + int(40 * dot_dash / max(1, len(stripped)))
    return DetectionResult("morse", min(confidence, 92), "используются точки, тире и разделители")


def _score_xor(text: str) -> DetectionResult:
    stripped = text.strip()
    if len(stripped) < 8 or len(stripped) % 2 != 0 or not HEX_RE.fullmatch(stripped):
        return DetectionResult("unknown", 5, "не hex-строка")
    return DetectionResult("xor", 70, "XOR-результат в боте хранится как hex")


def _score_caesar(text: str) -> DetectionResult:
    letters = [ch for ch in text if ch.isalpha()]
    if len(letters) < 8:
        return DetectionResult("unknown", 5, "мало букв для частотного анализа")
    vowels = sum(ch.lower() in "aeiouаеёиоуыэюя" for ch in letters)
    ratio = vowels / len(letters)
    confidence = 45 if 0.2 <= ratio <= 0.55 else 25
    return DetectionResult("caesar", confidence, "текст состоит из букв и подходит для Caesar-проверки")


def format_detection(result: DetectionResult) -> str:
    name = result.algorithm if result.algorithm != "unknown" else "не определён"
    return (
        "🔍 Результат определения\n\n"
        f"Вероятный шифр: {name}\n"
        f"Уверенность: {result.confidence}%\n"
        f"Основание: {result.reason}"
    )
