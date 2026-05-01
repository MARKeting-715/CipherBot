from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject


class PrivateCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, CallbackQuery) and event.message and event.message.chat.type != "private":
            await event.answer("Откройте бота в личном чате.", show_alert=True)
            return None
        return await handler(event, data)
