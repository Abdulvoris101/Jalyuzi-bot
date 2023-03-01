from run import types
from aiogram.types.web_app_info import WebAppInfo
from fetch import get_categories, get_category_products, get_token, user_me
from utils import translate_text
import math


def settings_keyboard(lang, user_id):
    user = user_me(user_id)
    
    settings_keyboard_ = types.ReplyKeyboardMarkup([
        [
            types.KeyboardButton(translate_text(f"Tilni o'zgartirish", lang) + f"({lang})"),
            types.KeyboardButton(translate_text("Ismni o'zgartirish", lang) + f"({user.get('first_name')})")
        ],
        [
            types.KeyboardButton(translate_text("Familiyani o'zgartirish", lang)  + f"({user.get('last_name')})")
        ]
    ], resize_keyboard=True, one_time_keyboard=True
    )

    settings_keyboard_.add(translate_text("⬅️ Orqaga", lang))

    return settings_keyboard_
    

def basket_keyboard(length):
    if length == 0:
        basket_keyboard_ = types.InlineKeyboardMarkup(row_width=1)
    elif length <= 10:
        basket_keyboard_ = types.InlineKeyboardMarkup(row_width=math.ceil(length / 2))
    else:
        basket_keyboard_ = types.InlineKeyboardMarkup(row_width=5)


    for i in range(length):
        basket_keyboard_.insert(types.InlineKeyboardButton(f"{i + 1}", callback_data=f"basket_{i + 1}"))
    
    basket_keyboard_.add(types.InlineKeyboardButton(f"🛍 Покупать", callback_data=f"basket_buy"))
    basket_keyboard_.add(types.InlineKeyboardButton(f"❌ Удалить все", callback_data=f"basket_reset"))

    return basket_keyboard_


def products_keyboard(per_page, category_id, current):
    product_keyboard_ = types.InlineKeyboardMarkup(row_width=5)
    
    for i in range(per_page):
        product_keyboard_.insert(types.InlineKeyboardButton(i + 1, callback_data=f"page_{i + 1}_{current}_{category_id}"))
    
    product_keyboard_.row(types.InlineKeyboardButton("⬅️", callback_data=f"back_{category_id}_{current}"), types.InlineKeyboardButton("➡️", callback_data=f"next_{category_id}_{current}"))

    return product_keyboard_

    

def category_keyboards(lang):
    categories = get_categories()

    categories.append({
        'name': f'⬅️ {translate_text("Orqaga", lang=lang)}'
    })
        
    category_keyboards = types.ReplyKeyboardMarkup([
        [types.KeyboardButton(category.get('name'))] for category in categories
    ], resize_keyboard=True, one_time_keyboard=True)

    return category_keyboards


language_keyboards = types.ReplyKeyboardMarkup([
    [
        types.KeyboardButton("uz"),
        types.KeyboardButton("ru")
    ]

],resize_keyboard=True)


def add_cart_keyboards(lang, product_slug):
    cart_keyboards = types.InlineKeyboardMarkup(row_width=1)
    cart_keyboards.insert(types.InlineKeyboardButton(f"🛒 {translate_text(text='Korzinkaga qoshish', lang=lang)}", callback_data=f"product_{product_slug}"))
    
    return cart_keyboards

def start_keyboards(lang):
    
    start_keyboards = types.ReplyKeyboardMarkup([
        [
            types.KeyboardButton(f'🛍 {translate_text(text="Sotib olish", lang=lang)} ')
        ],
        [

            types.KeyboardButton(f'💬 {translate_text(text="Biz bilan Aloqa", lang=lang)}'),
            types.KeyboardButton(f'⚙️ {translate_text(text="Sozlamalar", lang=lang)}'),
        ],
        [
                    types.KeyboardButton(f'⚡️ {translate_text(text="Ijtimoiy tarmoqlar", lang=lang)}'),

        ]

    ],resize_keyboard=True, one_time_keyboard=True)

    return start_keyboards


def contact_keyboards(lang):
    text = "Raqamni yuborish"
    contact_keyboards = types.ReplyKeyboardMarkup([
        [
            types.KeyboardButton(text=translate_text(text, lang), request_contact=True)
        ]
    ], resize_keyboard=True, one_time_keyboard=True)

    return contact_keyboards

cancel_keyboards = types.ReplyKeyboardMarkup(resize_keyboard=True).add("/cancel")

