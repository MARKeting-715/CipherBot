from __future__ import annotations

import secrets
import string

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from cipherbot.keyboards import gen_key_length_keyboard, gen_key_result_keyboard
from cipherbot.states import GenKeyState

router = Router(name="genkey")

ALPHABETS = {
    "letters": string.ascii_letters,
    "digits": string.digits,
    "mixed": string.ascii_letters + string.digits + "_-!@#$%^&*",
}


@router.callback_query(F.data.startswith("genkey:type:"))
async def choose_type(callback: CallbackQuery, state: FSMContext) -> None:
    key_type = callback.data.split(":", 2)[2]
    if key_type not in ALPHABETS:
        await callback.answer("Неизвестный тип ключа.", show_alert=True)
        return
    await state.update_data(key_type=key_type)
    await state.set_state(GenKeyState.choose_length)
    await callback.message.edit_text("🗝 Выберите длину ключа:", reply_markup=gen_key_length_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("genkey:length:"))
async def choose_length(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        length = int(callback.data.split(":", 2)[2])
    except ValueError:
        await callback.answer("Некорректная длина.", show_alert=True)
        return
    if length not in {8, 16, 32, 64}:
        await callback.answer("Доступны длины 8, 16, 32, 64.", show_alert=True)
        return
    await state.update_data(key_length=length)
    await _render_key(callback, state)


@router.callback_query(F.data == "genkey:again:last")
async def generate_again(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if not data.get("key_type") or not data.get("key_length"):
        await callback.answer("Сначала выберите тип и длину.", show_alert=True)
        return
    await _render_key(callback, state)


async def _render_key(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    key = generate_key(data["key_type"], int(data["key_length"]))
    await state.update_data(last_generated_key=key)
    await state.set_state(None)
    await callback.message.edit_text(f"🗝 Сгенерированный ключ\n\n{key}", reply_markup=gen_key_result_keyboard(), parse_mode=None)
    await callback.answer()


def generate_key(key_type: str, length: int) -> str:
    alphabet = ALPHABETS[key_type]
    return "".join(secrets.choice(alphabet) for _ in range(length))
