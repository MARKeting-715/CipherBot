from __future__ import annotations

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery

from cipherbot.db import Database
from cipherbot.exporter import export_history_txt, export_json, timestamped_name

router = Router(name="export")


@router.callback_query(F.data.startswith("export:format:"))
async def export_history(callback: CallbackQuery, db: Database) -> None:
    fmt = callback.data.split(":", 2)[2]
    rows = db.export_history(callback.from_user.id)
    if fmt == "json":
        file = BufferedInputFile(export_json(rows), filename=timestamped_name("history", "json"))
    elif fmt == "txt":
        file = BufferedInputFile(export_history_txt(rows), filename=timestamped_name("history", "txt"))
    else:
        await callback.answer("Неизвестный формат.", show_alert=True)
        return
    await callback.message.answer_document(file)
    await callback.answer("Файл экспорта подготовлен.")
