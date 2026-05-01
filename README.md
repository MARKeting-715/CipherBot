# CipherBot

Telegram-бот для шифрования, дешифрования, определения шифра, анализа текста, генерации ключей, истории операций и экспорта данных.

## Возможности

- Inline-меню после `/start`
- Шифрование и дешифрование: Caesar, Vigenere, XOR, Base64, Morse, PolyCitrus
- Автоопределение: Caesar, Base64, Morse, XOR
- Анализ текста: длина, уникальные символы, частоты, энтропия, повторы
- Генератор ключей: буквенный, числовой, смешанный
- SQLite-история с пагинацией, открытием, удалением и очисткой
- Экспорт истории в TXT/JSON и экспорт анализа в TXT
- FSM-сценарии на aiogram 3

## Быстрый старт

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `BOT_TOKEN` в `.env`, затем запустите:

```bash
python -m cipherbot.main
```

## PolyCitrus

PolyCitrus работает с Unicode scalar values, поэтому поддерживает разные языки, смешанный текст и эмодзи.

Формула шифрования:

```text
E_i = (U_i + K_i + i * S) mod M
```

Формула расшифровки:

```text
U_i = (E_i - K_i - i * S) mod M
```

Где `S = 7`, `M` исключает surrogate-диапазон Unicode.

## Тесты

```bash
pytest
```
