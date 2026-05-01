from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from cipherbot.db import Database, HistoryRecord
from cipherbot.keyboards.inline import history_keyboard, history_record_keyboard

router = Router(name="history")
PAGE_SIZE = 5


@router.callback_query(F.data.startswith("history:page:"))
async def page(callback: CallbackQuery, db: Database) -> None:
    page_num = int(callback.data.split(":", 2)[2])
    await render_history(callback, db, page_num)


@router.callback_query(F.data.startswith("history:open:"))
async def open_record(callback: CallbackQuery, db: Database) -> None:
    record_id = int(callback.data.split(":", 2)[2])
    record = db.get_history_record(callback.from_user.id, record_id)
    if record is None:
        await callback.answer("Запись не найдена.", show_alert=True)
        return
    await callback.message.edit_text(_record_text(record), reply_markup=history_record_keyboard(record.id), parse_mode=None)
    await callback.answer()


@router.callback_query(F.data.startswith("history:delete:"))
async def delete_record(callback: CallbackQuery, db: Database) -> None:
    record_id = int(callback.data.split(":", 2)[2])
    deleted = db.delete_history_record(callback.from_user.id, record_id)
    await callback.answer("Запись удалена." if deleted else "Запись не найдена.")
    await render_history(callback, db, 0)


@router.callback_query(F.data == "history:clear:all")
async def clear(callback: CallbackQuery, db: Database) -> None:
    count = db.clear_history(callback.from_user.id)
    await callback.answer(f"Удалено записей: {count}.")
    await render_history(callback, db, 0)


@router.callback_query(F.data == "history:noop:page")
async def noop(callback: CallbackQuery) -> None:
    await callback.answer()


async def render_history(callback: CallbackQuery, db: Database, page: int) -> None:
    records, total = db.list_history(callback.from_user.id, page, PAGE_SIZE)
    text = "📜 История операций\n\n"
    if not records:
        text += "История пуста."
    else:
        text += "\n".join(_history_line(record) for record in records)
    await callback.message.edit_text(text, reply_markup=history_keyboard(records, page, total, PAGE_SIZE))
    await callback.answer()


def _history_line(record: HistoryRecord) -> str:
    return f"#{record.id} | {record.operation_type} | {record.algorithm} | {record.created_at}"


def _record_text(record: HistoryRecord) -> str:
    return (
        f"📂 Запись #{record.id}\n\n"
        f"Тип: {record.operation_type}\n"
        f"Алгоритм: {record.algorithm}\n"
        f"Время: {record.created_at}\n\n"
        f"Вход:\n{_trim(record.input_text)}\n\n"
        f"Результат:\n{_trim(record.output_text)}"
    )


def _trim(text: str, limit: int = 1200) -> str:
    return text if len(text) <= limit else text[:limit] + "\n..."
