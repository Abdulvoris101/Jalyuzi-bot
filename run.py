from aiogram import Bot, Dispatcher, executor, types
import os
import sqlite3
from dotenv import load_dotenv
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()


load_dotenv()

bot = Bot(token=os.environ.get('TOKEN_API'), parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)


class ClientStateGroup(StatesGroup):
    language = State()
    phone_number = State()
    password = State()
    confirm_code = State()

class ProductEditState(StatesGroup):
    product_id = State()
    square = State()

class AddressStateGroup(StatesGroup):
    city = State()
    district = State()
    house = State()

class UpdateUserState(StatesGroup):
    first_name = State()
    last_name = State()

class VerificationState(StatesGroup):
    confirm_code = State()

class MessageState(StatesGroup):
    message = State()


if __name__ == '__main__':
    from auth.handlers import dp
    from core.handlers import dp


    executor.start_polling(dp, skip_updates=True)

