from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from cipherbot.constants import MAX_TEXT_LENGTH
from cipherbot.detector import detect_cipher, format_detection
from cipherbot.keyboards import detect_result_keyboard
from cipherbot.states import DetectState

router = Router(name="detect")


@router.message(DetectState.wait_text)
async def wait_text(message: Message, state: FSMContext) -> None:
    text = message.text or ""
    if not text or len(text) > MAX_TEXT_LENGTH:
        await message.answer(f"Текст должен быть непустым и не длиннее {MAX_TEXT_LENGTH} символов.")
        return
    result = detect_cipher(text)
    await state.update_data(last_detect_text=text, last_detect_algorithm=result.algorithm)
    await state.set_state(None)
    await message.answer(format_detection(result), reply_markup=detect_result_keyboard(result.algorithm))
