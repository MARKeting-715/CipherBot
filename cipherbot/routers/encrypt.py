from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from cipherbot.ciphers import CipherError, decrypt_text, encrypt_text
from cipherbot.constants import ALGORITHMS, KEY_REQUIRED, MAX_TEXT_LENGTH
from cipherbot.db import Database
from cipherbot.keyboards import operation_result_keyboard
from cipherbot.states import EncryptState

router = Router(name="encrypt")
log = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("encrypt:select:"))
async def select_cipher(callback: CallbackQuery, state: FSMContext) -> None:
    algorithm = callback.data.split(":", 2)[2]
    if algorithm == "last":
        data = await state.get_data()
        algorithm = data.get("last_detect_algorithm", "base64")
    if algorithm not in ALGORITHMS:
        await callback.answer("Неизвестный алгоритм.", show_alert=True)
        return

    await state.update_data(operation="encrypt", algorithm=algorithm)
    await state.set_state(EncryptState.wait_text)
    await callback.message.edit_text(f"🔐 {ALGORITHMS[algorithm]}\n\nОтправьте текст для шифрования.")
    await callback.answer()


@router.message(EncryptState.wait_text)
async def wait_text(message: Message, state: FSMContext) -> None:
    text = message.text or ""
    if not _valid_text(text):
        await message.answer(f"Текст должен быть непустым и не длиннее {MAX_TEXT_LENGTH} символов.")
        return

    data = await state.get_data()
    algorithm = data["algorithm"]
    await state.update_data(input_text=text)
    if algorithm in KEY_REQUIRED:
        await state.set_state(EncryptState.wait_key)
        await message.answer(_key_prompt(algorithm))
        return

    await _finish(message, state, algorithm, text, None)


@router.message(EncryptState.wait_key)
async def wait_key(message: Message, state: FSMContext) -> None:
    key = message.text or ""
    if not key:
        await message.answer("Ключ не может быть пустым.")
        return
    data = await state.get_data()
    await _finish(message, state, data["algorithm"], data["input_text"], key)


@router.callback_query(F.data == "encrypt:save:last")
async def save_last(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    data = await state.get_data()
    if data.get("last_operation") != "encrypt" or data.get("last_saved"):
        await callback.answer("Нет нового результата для сохранения.", show_alert=True)
        return

    db.add_history(
        callback.from_user.id,
        "encrypt",
        data["last_algorithm"],
        data["last_input"],
        data["last_output"],
    )
    await state.update_data(last_saved=True)
    await callback.answer("Сохранено в историю.")


@router.callback_query(F.data == "encrypt:repeat:last")
async def encrypt_back(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get("last_operation") != "decrypt":
        await callback.answer("Нет результата для обратного действия.", show_alert=True)
        return
    try:
        output = encrypt_text(data["last_algorithm"], data["last_output"], data.get("last_key"))
    except CipherError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    await state.update_data(
        last_operation="encrypt",
        last_input=data["last_output"],
        last_output=output,
        last_saved=False,
    )
    await callback.message.edit_text(_result_text("encrypt", data["last_algorithm"], output), reply_markup=operation_result_keyboard("encrypt"))
    await callback.answer()


async def _finish(message: Message, state: FSMContext, algorithm: str, text: str, key: str | None) -> None:
    try:
        result = encrypt_text(algorithm, text, key)
    except CipherError as exc:
        await message.answer(str(exc))
        return
    except Exception:
        log.exception("Encryption failed")
        await message.answer("Ошибка при шифровании.")
        return

    await state.update_data(
        last_operation="encrypt",
        last_algorithm=algorithm,
        last_input=text,
        last_output=result,
        last_key=key,
        last_saved=False,
    )
    await state.set_state(None)
    await message.answer(_result_text("encrypt", algorithm, result), reply_markup=operation_result_keyboard("encrypt"))


def _result_text(operation: str, algorithm: str, result: str) -> str:
    title = "🔐 Результат шифрования" if operation == "encrypt" else "🔓 Результат расшифровки"
    shown = _trim_for_telegram(result)
    return f"{title}\n\nАлгоритм: {ALGORITHMS[algorithm]}\n\n{shown}"


def _key_prompt(algorithm: str) -> str:
    if algorithm == "caesar":
        return "Введите числовой ключ Caesar."
    return "Введите ключ."


def _valid_text(text: str) -> bool:
    return bool(text) and len(text) <= MAX_TEXT_LENGTH


def _trim_for_telegram(text: str, limit: int = 3400) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n... результат сокращён для отображения. Полная версия сохраняется в историю."
