from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from cipherbot.config import load_config
from cipherbot.db import Database
from cipherbot.middlewares import PrivateCallbackMiddleware
from cipherbot.routers import routers


async def main() -> None:
    config = load_config()
    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    db = Database(config.database_path)
    db.init()

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    dp["db"] = db
    dp.callback_query.middleware(PrivateCallbackMiddleware())
    for router in routers:
        dp.include_router(router)

    logging.getLogger(__name__).info("CipherBot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
