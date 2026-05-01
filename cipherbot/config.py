from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    database_path: Path
    log_level: str = "INFO"


def load_config() -> Config:
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is required. Copy .env.example to .env and set the token.")

    return Config(
        bot_token=token,
        database_path=Path(os.getenv("DATABASE_PATH", "cipherbot.sqlite3")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
