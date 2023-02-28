from run import dp, bot, types
from keyboards import start_keyboards, contact_keyboards, cancel_keyboards, settings_keyboard
import sqlite3
from db.manager import is_authenticated, create_token, update_token, delete_user, get_user_language, set_language
from fetch import user_register, user_confirmation, is_confirmed, user_me, send_verif_code, send_message
import json
from aiogram.dispatcher.filters import Text
from run import State, StatesGroup, ClientStateGroup, MessageState, VerificationState
from aiogram.dispatcher.storage import FSMContext
from utils import send_message_local





@dp.message_handler(commands=['cancel'], state="*")
async def cancel_register(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state is None:
        return 

    
    async with state.proxy() as data:
        
        await send_message_local(message.from_user.id, text="Ro'yhatdan o'tish bekor qilindi! /start", lang=data['language'])

    await state.finish()



@dp.message_handler(lambda message: message.text, state=ClientStateGroup.language)
async def receiver_language(message: types.Message, state: FSMContext):
    
    async with state.proxy() as data:
        data['language'] = message.text
    
    await ClientStateGroup.next()

    await send_message_local(user_id=message.from_user.id,
    text="Telefon raqamingizni jo'nating. <b>Raqamni yuborish </b>  tugmasini bosing", lang=message.text, reply_markup=contact_keyboards(lang=message.text))


@dp.message_handler(lambda message: message.text != 'ru' or message.text != 'uz', state=ClientStateGroup.language)
async def incorrect_language(message: types.Message, state=FSMContext):
    await message.answer("Iltimos to'g'ri tilni tanlang. Пожалуйста введите коректный язык")
    

@dp.message_handler(lambda message: message.contact.phone_number, content_types=['contact'], state=ClientStateGroup.phone_number)
async def handle_contact(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        

        data['phone_number'] = message.contact.phone_number
        lang = data['language']

        await send_message_local(message.from_user.id, text="Ro'yxatdan o'tish uchun yangi parol kiriting  Va bu parol jalyuzi.com uchun xam ammal qiladi", lang=lang)

    await ClientStateGroup.next()



@dp.message_handler(lambda message: message.text, state=ClientStateGroup.password)
async def set_password(message: types.Message, state: FSMContext): 

    async with state.proxy() as data:
        data['password'] = message.text
        lang = data['language']
        phone_number = str(data['phone_number']).replace('+998', '')
        
        data = {
            "phone_number":  phone_number,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name if message.from_user.last_name is not None else 'Not',
            "telegram_id": message.from_user.id,
            "password": data['password'],
            "username": phone_number,
            "isTelegramBot": True
        }
        
        resp = user_register(data=data)

        if resp.get('ok'):
            await send_message_local(message.from_user.id, text=f"Ro'yhatdan muvaffiqiyatli o'tdingiz {message.from_user.first_name} 🤴", lang=lang, reply_markup=start_keyboards(lang))
            create_token(telegram_id=message.from_user.id, lang=lang, token=resp.get("token"))
            await state.finish()
        else:
            if resp.get('username'):
                return await bot.send_message(message.from_user.id, "Siz ro'yhatdan o'tgansiz")

            await bot.send_message(message.from_user.id, resp)
            




# @dp.message_handler(lambda message: message.text, state=ClientStateGroup.confirm_code)
# async def check_code(message: types.Message, state: FSMContext): 

#     async with state.proxy() as data:
#         data['confirm_code'] = message.text
#         lang = data['language']
#         phone_number = str(data['phone_number']).replace('+998', '')

#         obj = {
#             'phone_number': phone_number,
#             'password': data['password'],
#             'confirm': message.text
#         }

#         resp = user_confirmation(obj)

#         if resp.get('ok'):
#             update_token(message.from_user.id, resp.get('token'))

#             await state.finish()
#         else:
#             if resp.get('Error'):
#                 await send_message_local(message.from_user.id, "Noto'gri parol", lang=lang, reply_markup=cancel_keyboards)
#             else:
#                 await bot.send_message(message.from_user.id, resp, reply_markup=cancel_keyboards)


@dp.message_handler(commands=['verification'])
async def verification(message: types.Message, state=None):
    language = get_user_language(message.from_user.id)

    if is_confirmed(message.from_user.id):
        return await send_message_local(message.from_user.id, text="Sizning telefon raqamingiz tasdiqlangan!", lang=language)
    
    resp = send_verif_code(message.from_user.id)


    if resp.get('ok'):
        await VerificationState.confirm_code.set()
        return await send_message_local(message.from_user.id, text="Telefoningizga borgan kodni kiriting", lang=language)
    else:
        return await bot.send_message(message.from_user.id, resp)






@dp.message_handler(lambda message: message.text, state=VerificationState.confirm_code)
async def confirm_code_v(message: types.Message, state: FSMContext):
    language = get_user_language(message.from_user.id)
    
    async with state.proxy() as data:
        data['confirm_code'] = message.text
    
    data = {
        "confirm": message.text,
        "telegramId": message.from_user.id
    }

    resp = user_confirmation(data=data)

    if resp.get("ok"):
        
        update_token(message.from_user.id, resp.get('token'))
        
        await state.finish()

        return await send_message_local(message.from_user.id, text="Telefon nomer tasdiqlandi. /start", lang=language)
    else:
        return await bot.send_message(message.from_user.id, resp)





# Work on it 

# Settings




@dp.message_handler(Text(equals=["⚙️ Настройки", "⚙️ Sozlamalar"]))
async def settings_view(message: types.Message):
    language = get_user_language(message.from_user.id)
    await send_message_local(message.from_user.id, "⚙️ Sozlamalar", lang=language, reply_markup=settings_keyboard(language, message.from_user.id))




@dp.message_handler(Text(equals=["Изменить язык(ru)", "Tilni o'zgartirish(uz)"]))
async def set_lang(message: types.Message):
    language = get_user_language(message.from_user.id)

    if language == "ru":
        set_language(message.from_user.id, "uz")
    else:
        set_language(message.from_user.id, "ru")

    language = get_user_language(message.from_user.id)
    
    await settings_view(message)
    

# Chat
@dp.message_handler(Text(equals=["💬 Biz bilan Aloqa", "💬 Связаться с нами"]))
async def chat(message: types.Message, state=None):
    language = get_user_language(message.from_user.id)
    await bot.delete_message(message.from_user.id, message.message_id)

    await MessageState.message.set()

    await send_message_local(message.from_user.id, "Xabar yuboring", language)

@dp.message_handler(state=MessageState.message)
async def message_handle(message: types.Message, state=FSMContext):
    language = get_user_language(message.from_user.id)

    msg = f"telegramId: <code>{message.from_user.id}</code>,\nИмя: {message.from_user.first_name},\nusername: @{message.from_user.username},\nсообшения: {message.text}"

    await bot.send_message("-1001875684284", msg)

    await state.finish()

    await send_message_local(message.from_user.id, "Xabaringiz muvaffiqiyatli yuborildi. Tez orada administratorlar sizga javob berishadi 😊", language)
    