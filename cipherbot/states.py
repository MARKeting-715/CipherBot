from aiogram.fsm.state import State, StatesGroup


class EncryptState(StatesGroup):
    choose_cipher = State()
    wait_text = State()
    wait_key = State()


class DecryptState(StatesGroup):
    choose_cipher = State()
    wait_text = State()
    wait_key = State()


class DetectState(StatesGroup):
    wait_text = State()


class AnalyzeState(StatesGroup):
    wait_text = State()


class GenKeyState(StatesGroup):
    choose_type = State()
    choose_length = State()
