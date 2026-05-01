from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from cipherbot.db import Database
from cipherbot.keyboards import (
    algorithm_keyboard,
    export_format_keyboard,
    gen_key_type_keyboard,
    main_menu_keyboard,
    profile_keyboard,
)

router = Router(name="common")


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    db.upsert_user(message.from_user.id, message.from_user.username if message.from_user else None)
    await message.answer(_home_text(), reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "menu:open:home")
async def open_home(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    if not await _private_callback(callback):
        return
    await state.clear()
    db.upsert_user(callback.from_user.id, callback.from_user.username)
    await callback.message.edit_text(_home_text(), reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:open:encrypt")
async def open_encrypt(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _private_callback(callback):
        return
    await state.clear()
    await callback.message.edit_text("🔐 Выберите алгоритм для шифрования:", reply_markup=algorithm_keyboard("encrypt"))
    await callback.answer()


@router.callback_query(F.data == "menu:open:decrypt")
async def open_decrypt(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _private_callback(callback):
        return
    await state.clear()
    await callback.message.edit_text("🔓 Выберите алгоритм для расшифровки:", reply_markup=algorithm_keyboard("decrypt"))
    await callback.answer()


@router.callback_query(F.data == "menu:open:detect")
async def open_detect(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _private_callback(callback):
        return
    from cipherbot.states import DetectState

    await state.clear()
    await state.set_state(DetectState.wait_text)
    await callback.message.edit_text("🔍 Отправьте текст для определения шифра.")
    await callback.answer()


@router.callback_query(F.data == "menu:open:analyze")
async def open_analyze(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _private_callback(callback):
        return
    from cipherbot.states import AnalyzeState

    await state.clear()
    await state.set_state(AnalyzeState.wait_text)
    await callback.message.edit_text("📊 Отправьте текст для анализа.")
    await callback.answer()


@router.callback_query(F.data == "menu:open:genkey")
async def open_genkey(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _private_callback(callback):
        return
    from cipherbot.states import GenKeyState

    await state.clear()
    await state.set_state(GenKeyState.choose_type)
    await callback.message.edit_text("🗝 Выберите тип ключа:", reply_markup=gen_key_type_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:open:history")
async def open_history(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    if not await _private_callback(callback):
        return
    from cipherbot.routers.history import render_history

    await state.clear()
    await render_history(callback, db=db, page=0)


@router.callback_query(F.data == "menu:open:export")
async def open_export(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _private_callback(callback):
        return
    await state.clear()
    await callback.message.edit_text("📁 Выберите формат экспорта истории:", reply_markup=export_format_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:open:profile")
async def open_profile(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    if not await _private_callback(callback):
        return
    await state.clear()
    user = db.upsert_user(callback.from_user.id, callback.from_user.username)
    favorite = db.favorite_algorithm(callback.from_user.id)
    username = f"@{user.username}" if user.username else "не указан"
    text = (
        "👤 Профиль\n\n"
        f"ID: `{user.telegram_id}`\n"
        f"Username: {username}\n"
        f"Дата регистрации: {user.created_at}\n"
        f"Количество операций: {user.operations_count}\n"
        f"Любимый алгоритм: {favorite}"
    )
    await callback.message.edit_text(text, reply_markup=profile_keyboard(), parse_mode=None)
    await callback.answer()


async def _private_callback(callback: CallbackQuery) -> bool:
    if callback.message and callback.message.chat.type != "private":
        await callback.answer("Откройте бота в личном чате.", show_alert=True)
        return False
    return True


def _home_text() -> str:
    return (
        "CipherBot\n\n"
        "Выберите действие через inline-меню. Команды нужны только для входа через /start."
    )
