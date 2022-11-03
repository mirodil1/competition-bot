from aiogram.dispatcher.filters.state import StatesGroup, State

class Message(StatesGroup):
    message = State()