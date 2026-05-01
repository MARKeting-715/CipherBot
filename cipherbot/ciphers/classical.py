from __future__ import annotations

import base64
import binascii

UNICODE_MOD = 0x110000 - 0x800
POLYCITRUS_SHIFT = 7


class CipherError(ValueError):
    pass


MORSE_TABLE = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    ".": ".-.-.-",
    ",": "--..--",
    "?": "..--..",
    "!": "-.-.--",
    ":": "---...",
    ";": "-.-.-.",
    "'": ".----.",
    '"': ".-..-.",
    "-": "-....-",
    "/": "-..-.",
    "(": "-.--.",
    ")": "-.--.-",
    "@": ".--.-.",
    "=": "-...-",
    "+": ".-.-.",
}
REVERSE_MORSE = {value: key for key, value in MORSE_TABLE.items()}


def encrypt_text(algorithm: str, text: str, key: str | None = None) -> str:
    match algorithm:
        case "caesar":
            return caesar(text, _int_key(key), decrypt=False)
        case "vigenere":
            return vigenere(text, _required_key(key), decrypt=False)
        case "xor":
            return xor_cipher(text, _required_key(key), decrypt=False)
        case "base64":
            return base64.b64encode(text.encode("utf-8")).decode("ascii")
        case "morse":
            return morse_encrypt(text)
        case "polycitrus":
            return polycitrus(text, _required_key(key), decrypt=False)
        case _:
            raise CipherError("Неизвестный алгоритм.")


def decrypt_text(algorithm: str, text: str, key: str | None = None) -> str:
    match algorithm:
        case "caesar":
            return caesar(text, _int_key(key), decrypt=True)
        case "vigenere":
            return vigenere(text, _required_key(key), decrypt=True)
        case "xor":
            return xor_cipher(text, _required_key(key), decrypt=True)
        case "base64":
            try:
                return base64.b64decode(text.encode("ascii"), validate=True).decode("utf-8")
            except (binascii.Error, UnicodeDecodeError):
                raise CipherError("Некорректный Base64-текст.") from None
        case "morse":
            return morse_decrypt(text)
        case "polycitrus":
            return polycitrus(text, _required_key(key), decrypt=True)
        case _:
            raise CipherError("Неизвестный алгоритм.")


def caesar(text: str, shift: int, decrypt: bool = False) -> str:
    shift = -shift if decrypt else shift
    out: list[str] = []
    for char in text:
        if "a" <= char <= "z":
            out.append(chr((ord(char) - ord("a") + shift) % 26 + ord("a")))
        elif "A" <= char <= "Z":
            out.append(chr((ord(char) - ord("A") + shift) % 26 + ord("A")))
        elif "а" <= char <= "я":
            out.append(chr((ord(char) - ord("а") + shift) % 32 + ord("а")))
        elif "А" <= char <= "Я":
            out.append(chr((ord(char) - ord("А") + shift) % 32 + ord("А")))
        elif char == "ё":
            out.append(char)
        elif char == "Ё":
            out.append(char)
        else:
            out.append(char)
    return "".join(out)


def vigenere(text: str, key: str, decrypt: bool = False) -> str:
    shifts = [ord(ch) for ch in key]
    out: list[str] = []
    key_index = 0
    for char in text:
        if char.isalpha():
            shift = shifts[key_index % len(shifts)] % 26
            if decrypt:
                shift = -shift
            out.append(_shift_letter(char, shift))
            key_index += 1
        else:
            out.append(char)
    return "".join(out)


def xor_cipher(text: str, key: str, decrypt: bool = False) -> str:
    key_bytes = key.encode("utf-8")
    if decrypt:
        if not _looks_hex(text):
            raise CipherError("Для расшифровки XOR нужен hex-текст.")
        try:
            raw = bytes.fromhex(text)
            decoded = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(raw))
            return decoded.decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            raise CipherError("Некорректный XOR/hex-текст или ключ.") from None

    source = text.encode("utf-8")
    encrypted = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(source))
    return encrypted.hex()


def morse_encrypt(text: str) -> str:
    words: list[str] = []
    for word in text.upper().split(" "):
        encoded_chars = [MORSE_TABLE.get(char, char) for char in word]
        words.append(" ".join(encoded_chars))
    return " / ".join(words)


def morse_decrypt(text: str) -> str:
    words: list[str] = []
    for word in text.strip().split(" / "):
        chars = [REVERSE_MORSE.get(token, token) for token in word.split()]
        words.append("".join(chars))
    return " ".join(words)


def polycitrus(text: str, key: str, decrypt: bool = False, shift: int = POLYCITRUS_SHIFT) -> str:
    out: list[str] = []
    key_points = [_to_scalar_index(ord(ch)) for ch in key]
    for index, char in enumerate(text):
        value = _to_scalar_index(ord(char))
        key_value = key_points[index % len(key_points)]
        if decrypt:
            code_point = (value - key_value - index * shift) % UNICODE_MOD
        else:
            code_point = (value + key_value + index * shift) % UNICODE_MOD
        out.append(chr(_from_scalar_index(code_point)))
    return "".join(out)


def _to_scalar_index(code_point: int) -> int:
    if 0xD800 <= code_point <= 0xDFFF:
        raise CipherError("Surrogate Unicode-коды не поддерживаются.")
    if code_point > 0xDFFF:
        return code_point - 0x800
    return code_point


def _from_scalar_index(index: int) -> int:
    if index >= 0xD800:
        return index + 0x800
    return index


def _shift_letter(char: str, shift: int) -> str:
    if "a" <= char <= "z":
        start = ord("a")
        return chr((ord(char) - start + shift) % 26 + start)
    if "A" <= char <= "Z":
        start = ord("A")
        return chr((ord(char) - start + shift) % 26 + start)
    if "а" <= char <= "я":
        start = ord("а")
        return chr((ord(char) - start + shift) % 32 + start)
    if "А" <= char <= "Я":
        start = ord("А")
        return chr((ord(char) - start + shift) % 32 + start)
    return char


def _required_key(key: str | None) -> str:
    if not key:
        raise CipherError("Для выбранного алгоритма нужен ключ.")
    return key


def _int_key(key: str | None) -> int:
    if not key:
        raise CipherError("Для Caesar нужен числовой ключ.")
    try:
        return int(key)
    except ValueError:
        raise CipherError("Ключ Caesar должен быть целым числом.") from None


def _looks_hex(text: str) -> bool:
    stripped = text.strip()
    return len(stripped) >= 2 and len(stripped) % 2 == 0 and all(ch in "0123456789abcdefABCDEF" for ch in stripped)
