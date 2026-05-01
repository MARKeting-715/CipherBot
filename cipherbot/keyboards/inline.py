from __future__ import annotations

from math import ceil

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from cipherbot.constants import ALGORITHMS
from cipherbot.db import HistoryRecord


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔐 Зашифровать", callback_data="menu:open:encrypt")
    builder.button(text="🔓 Расшифровать", callback_data="menu:open:decrypt")
    builder.button(text="🔍 Определить шифр", callback_data="menu:open:detect")
    builder.button(text="📊 Анализ текста", callback_data="menu:open:analyze")
    builder.button(text="🗝 Генератор ключей", callback_data="menu:open:genkey")
    builder.button(text="📜 История", callback_data="menu:open:history")
    builder.button(text="📁 Экспорт", callback_data="menu:open:export")
    builder.button(text="👤 Профиль", callback_data="menu:open:profile")
    builder.adjust(2)
    return builder.as_markup()


def algorithm_keyboard(section: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for value, title in ALGORITHMS.items():
        builder.button(text=title, callback_data=f"{section}:select:{value}")
    builder.button(text="⬅️ Назад", callback_data="menu:open:home")
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()


def operation_result_keyboard(section: str) -> InlineKeyboardMarkup:
    reverse = "decrypt" if section == "encrypt" else "encrypt"
    reverse_text = "🔁 Расшифровать обратно" if section == "encrypt" else "🔁 Зашифровать обратно"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=reverse_text, callback_data=f"{reverse}:repeat:last")],
            [InlineKeyboardButton(text="💾 Сохранить в историю", callback_data=f"{section}:save:last")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:open:home")],
        ]
    )


def back_home_keyboard(back_to: str = "home") -> InlineKeyboardMarkup:
    callback = "menu:open:home" if back_to == "home" else f"menu:open:{back_to}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=callback)],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:open:home")],
        ]
    )


def detect_result_keyboard(algorithm: str) -> InlineKeyboardMarkup:
    callback = f"decrypt:select:{algorithm}" if algorithm != "unknown" else "menu:open:decrypt"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔓 Попробовать расшифровать", callback_data=callback)],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="menu:open:home")],
        ]
    )


def analyze_result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📁 Экспорт анализа", callback_data="analyze:export:last")],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="menu:open:home")],
        ]
    )


def gen_key_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Буквенный", callback_data="genkey:type:letters")
    builder.button(text="Числовой", callback_data="genkey:type:digits")
    builder.button(text="Смешанный", callback_data="genkey:type:mixed")
    builder.button(text="⬅️ Назад", callback_data="menu:open:home")
    builder.adjust(1)
    return builder.as_markup()


def gen_key_length_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for length in (8, 16, 32, 64):
        builder.button(text=str(length), callback_data=f"genkey:length:{length}")
    builder.button(text="⬅️ Назад", callback_data="menu:open:genkey")
    builder.adjust(4, 1)
    return builder.as_markup()


def gen_key_result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Сгенерировать снова", callback_data="genkey:again:last")],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="menu:open:home")],
        ]
    )


def history_keyboard(records: list[HistoryRecord], page: int, total: int, page_size: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for record in records:
        builder.button(
            text=f"📂 #{record.id} {record.operation_type}/{record.algorithm}",
            callback_data=f"history:open:{record.id}",
        )

    pages = max(1, ceil(total / page_size))
    prev_page = max(0, page - 1)
    next_page = min(pages - 1, page + 1)
    builder.row(
        InlineKeyboardButton(text="⬅️", callback_data=f"history:page:{prev_page}"),
        InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="history:noop:page"),
        InlineKeyboardButton(text="➡️", callback_data=f"history:page:{next_page}"),
    )
    builder.row(InlineKeyboardButton(text="🗑 Очистить историю", callback_data="history:clear:all"))
    builder.row(InlineKeyboardButton(text="🏠 Меню", callback_data="menu:open:home"))
    return builder.as_markup()


def history_record_keyboard(record_id: int, page: int = 0) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"history:delete:{record_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"history:page:{page}")],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="menu:open:home")],
        ]
    )


def export_format_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="TXT", callback_data="export:format:txt"),
                InlineKeyboardButton(text="JSON", callback_data="export:format:json"),
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu:open:home")],
        ]
    )


def profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📜 История", callback_data="menu:open:history")],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="menu:open:home")],
        ]
    )
