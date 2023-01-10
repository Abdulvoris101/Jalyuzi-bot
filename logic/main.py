from aiogram import Bot, Dispatcher, executor, types
import os

from aiogram.types.web_app_info import WebAppInfo


from dotenv import load_dotenv


load_dotenv()

bot = Bot(token=os.environ.get('TOKEN_API'))
dp = Dispatcher(bot)
web_app = WebAppInfo(url="https://abdulvoris101.github.io/")

kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text='Rulloniy', web_app=web_app)]
    ],
)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text="Hello", reply_markup=kb)


if __name__ == '__main__':
    executor.start_polling(dp)

