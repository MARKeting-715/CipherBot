from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from cipherbot.analyzer import format_analysis
from cipherbot.constants import MAX_TEXT_LENGTH
from cipherbot.exporter import export_analysis_txt, timestamped_name
from cipherbot.keyboards import analyze_result_keyboard
from cipherbot.states import AnalyzeState

router = Router(name="analyze")


@router.message(AnalyzeState.wait_text)
async def wait_text(message: Message, state: FSMContext) -> None:
    text = message.text or ""
    if not text or len(text) > MAX_TEXT_LENGTH:
        await message.answer(f"Текст должен быть непустым и не длиннее {MAX_TEXT_LENGTH} символов.")
        return
    result = format_analysis(text)
    await state.update_data(last_analysis=result)
    await state.set_state(None)
    await message.answer(result, reply_markup=analyze_result_keyboard(), parse_mode=None)


@router.callback_query(F.data == "analyze:export:last")
async def export_last(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    analysis = data.get("last_analysis")
    if not analysis:
        await callback.answer("Нет анализа для экспорта.", show_alert=True)
        return
    file = BufferedInputFile(export_analysis_txt(analysis), filename=timestamped_name("analysis", "txt"))
    await callback.message.answer_document(file)
    await callback.answer("Файл подготовлен.")
