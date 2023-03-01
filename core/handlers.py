from run import dp, bot, types, State, UpdateUserState, ClientStateGroup, ProductEditState, AddressStateGroup
from keyboards import start_keyboards, language_keyboards, category_keyboards, products_keyboard, add_cart_keyboards, basket_keyboard
from db.manager import is_authenticated, get_user_language, add_to_cart, get_cart_products, update_cart, get_cart_product, drop_all_cart, set_language
from fetch import is_confirmed, get_categories, get_category_products, get_category, get_product_from_list, baseUrl, get_color, get_product, user_me, get_address, create_order, create_address, update_user
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.storage import FSMContext
from utils import send_message_local, translate_text
import json
import math
import time
from decimal import Decimal
import re

# Commands /start and /basket

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message, state=None):   
    language = get_user_language(message.from_user.id)
    me = user_me(telegram_id=message.from_user.id)


    if is_authenticated(message.from_user.id) == True and me.get("detail") is None:
        return await send_message_local(message.from_user.id, text=f"Assalomu aleykum <b>{message.from_user.first_name}</b> 😊\n\nNima buyurtma qilamiz ?", lang=language, reply_markup=start_keyboards(lang=language))
    
    # elif is_authenticated(message.from_user.id) and me.get("detail") is None:
    #     await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

    #     return await send_message_local(message.from_user.id, "Siz telefon raqamingizni tasdiqlamadingiz! Tasdiqlash uchun  /verification komandasini ni yuboring", lang=language)

    await ClientStateGroup.language.set()

    await bot.send_message(chat_id=message.from_user.id, text=f"""
        Assalomu Alaykum! Bizning botdan foydalanish uchun ro'yxatdan o'ting\n\nЗдравствуйте! Чтобы пользоваться нашим ботом вам необходимо пройти регистрацию.
    """)

    await bot.send_message(chat_id=message.from_user.id, text=f"""
        Tilingizni tanlang\n\nВыберите ваш язык
    """, reply_markup=language_keyboards)




@dp.message_handler(commands=['basket'])
async def basket(message: types.Message):
    products = get_cart_products(message.from_user.id)
    text = ""
    overall_price = 0

    for index, product in enumerate(products):
        square = product[1]
        product = json.loads(product[0])
        lang = get_user_language(message.from_user.id)



        name = product.get("name")
        product_id = product.get("id")
        price = product.get("price_sum")
        slug = product.get("slug")
        blackout = product.get("blackout")
        square_ = re.findall(r"[-+]?(?:\d*\.*\d+)", square)
        w = float(square_[0])
        h = float(square_[1])
        

        all_square = w * h
        all_price = float(price) * all_square
        overall_price = overall_price + all_price
        
        
        url = f"{baseUrl}/product/{slug}"
        

        text += f"<b>{index + 1}</b>. <b>{name}</b> - {blackout} <a href='{url}'>️𝖚𝖗𝖑</a> \nОбш кв: {square}\n\n"

    overall_price = str(int(overall_price))

    showPrice = f"{overall_price[slice(-9, -6)]} {overall_price[slice(-6, -3)]} {overall_price[-3:]}"
    
    text += f"Общ.цена: {showPrice} сум"


    await bot.send_message(message.from_user.id, text, reply_markup=basket_keyboard(len(products)))



@dp.message_handler(commands=['address'])
async def address(message: types.Message, state=None):
    if is_authenticated(message.from_user.id):
        language = get_user_language(message.from_user.id)
        address = get_address(message.from_user.id)

        if address == False:
            await AddressStateGroup.city.set()
            await send_message_local(message.from_user.id, "Shaharni kiriting:", language)
        else:
            await send_message_local(message.from_user.id, "Siz allaqachon address  kiritgansiz.", language)
    else:
        await send_message_local(message.from_user.id, "Siz Ro'yhatdan o'tmaagansiz yoki Telefon nomeringizni tasdiqlamagansiz.", language)




# Functions



def products_text(category, current_page, user_id):
    products = get_category_products(category_id=category.get('id'), page=int(current_page))
    language = get_user_language(user_id)
    
    if products != False:
        page_size = products.get("page_size") 
        total = products.get("total") 
        

        if int(total) > int(page_size):
            all_page = int(total) / int(page_size)
            all_page = math.ceil(all_page)
        else:
            all_page = 1

        text = f'{translate_text("Sahifa", language)} {current_page}/{int(all_page)}\n\n'

        for index, product in enumerate(products.get('results')):
            name = product.get('name')
            weight = product.get('weight')
            price_sum = product.get('price_sum')
            slug = product.get('slug')

            text += f'<b>{index + 1}</b>. {name}-{weight} <b>{price_sum}</b> сум.\nhttps://jalyuzi.com/product/{slug} \n\n'
        
        return text
    
    return False

# Address

@dp.message_handler(state=AddressStateGroup.city)
async def city_handler(message: types.Message, state=FSMContext):
    language = get_user_language(message.from_user.id)

    async with state.proxy() as data:
        data['city'] = message.text
    
    await AddressStateGroup.next()
    await send_message_local(message.from_user.id, "Tumani kiriting: ", language)


@dp.message_handler(state=AddressStateGroup.district)
async def district_handler(message: types.Message, state=FSMContext):
    language = get_user_language(message.from_user.id)

    async with state.proxy() as data:
        data['district'] = message.text

    await AddressStateGroup.next()


    await send_message_local(message.from_user.id, "Mahala va Uyni kiriting: ", language)



@dp.message_handler(state=AddressStateGroup.house)
async def house_handler(message: types.Message, state=FSMContext):
    language = get_user_language(message.from_user.id)

    async with state.proxy() as data:
        data['house'] = message.text

        data_obj = {
            "city": data['city'],
            "state": data['district'],
            "address": data['house'],
        }

        dt = create_address(message.from_user.id, json.dumps(data_obj))

    await state.finish()
    await send_message_local(message.from_user.id, "Address muvaffaqiyatli kiritilindi.", language)


# Message handlers - 

@dp.message_handler(Text(equals=["🛍 Sotib olish", "🛍 Покупка"], ignore_case=True))
async def to_shop(message: types.Message):
    language = get_user_language(message.from_user.id)


    await send_message_local(message.from_user.id, "Kategoriyalar", lang=language, reply_markup=category_keyboards(lang=language))



@dp.message_handler(Text(equals=["⬅️ Назад", "⬅️ Orqaga"], ignore_case=True))
async def to_start(message: types.Message):
    await send_welcome(message)



@dp.message_handler()
async def handle_message(message: types.Message, state=None):
    language  = get_user_language(message.from_user.id)
    user = user_me(message.from_user.id)

    for category in get_categories():

        if message.text == category.get('name'):
            category_id = category.get("id")

            per_page = len(get_category_products(category_id=category_id, page=1).get('results'))

            text = products_text(category=category, current_page=1, user_id=message.from_user.id)
            
            await bot.send_message(message.from_user.id, text=text, reply_markup=products_keyboard(per_page=per_page, category_id=category_id, current=1))

    if message.text == f"Изменение имени({user.get('first_name')})" or message.text == f"Ismni o'zgartirish({user.get('first_name')})":
        
        await UpdateUserState.first_name.set()
        await send_message_local(message.from_user.id, "Yangi ism kiriting: ", language)

    elif message.text == f"Смена фамилии({user.get('last_name')})" or message.text == f"Familiyani o'zgartirish({user.get('last_name')})":
        await UpdateUserState.last_name.set()
        await send_message_local(message.from_user.id, "Yangi familiya kiriting: ", language)





@dp.message_handler(state=UpdateUserState.first_name)
async def first_name(message: types.Message, state=FSMContext):
    lang = get_user_language(message.from_user.id)
    user = user_me(message.from_user.id)

    async with state.proxy() as data:
        data['first_name'] = message.text
        data['last_name'] = "message.text"


    data = {
        "first_name": message.text,
        "last_name": str(user.get("last_name"))
    }


    resp = update_user(message.from_user.id, json.dumps(data))
    resp = json.loads(resp.text)

    if resp.get("ok"):
        await state.finish()

        await send_message_local(message.from_user.id, "Ism o'zgardi", lang)
        await send_welcome(message)

    else:
        await send_message_local(message.from_user.id, resp, lang)




@dp.message_handler(state=UpdateUserState.last_name)
async def last_name(message: types.Message, state=FSMContext):
    lang = get_user_language(message.from_user.id)
    user = user_me(message.from_user.id)

    data = {
        "first_name": user.get("first_name"),
        "last_name": message.text 
    }


    resp = update_user(message.from_user.id, json.dumps(data))
    resp = json.loads(resp.text)

    if resp.get("ok"):
        await state.finish()
        await send_message_local(message.from_user.id, "Familiya o'zgardi", lang)
        await send_welcome(message)

    else:
        await send_message_local(message.from_user.id, resp, lang)




# Callback query - handler

@dp.callback_query_handler()
async def change_message(callback: types.CallbackQuery, state=None):

    
    cat_id = str(callback.data)[9:]
    basket_id = str(callback.data)[7:]


    current = re.findall(r'\d+', callback.data)

    if len(current) > 0:
        current = current[-1]


    # Buy products

    if callback.data == "basket_reset":
        drop_all_cart(callback.from_user.id)
        language = get_user_language(callback.from_user.id)

        await send_message_local(callback.from_user.id, "Korzinka tozalandi.", language)

        

    elif callback.data == "basket_buy":
        
        products = get_cart_products(callback.from_user.id)
        text = ""
        overall_price = 0
        order_products = []
        
        address = get_address(callback.from_user.id)
        lang = get_user_language(callback.from_user.id)
        detail  = address.get("detail")

        if detail is None and len(address) >= 1:
            len_of_product = len(products)

            for index, product in enumerate(products):
                square = product[1]
                product = json.loads(product[0])


                name = product.get("name")
                product_id = product.get("id")
                price = product.get("price_sum")
                slug = product.get("slug")
                blackout = product.get("blackout")
                square_ = re.findall(r"[-+]?(?:\d*\.*\d+)", square)
                w = float(square_[0])
                h = float(square_[1])
                

                all_square = w * h
                all_price = float(price) * all_square

                overall_price = overall_price + all_price


                # order_products.append({
                #     "product": product_id,
                #     "product_price": price,
                #     "overall_price": int(overall_price),
                #     "size": square,
                #     "type_id": "None",
                #     "status": "pending",
                #     "address": address[0].get("id"),
                #     "amount": 1
                # })


            # data = create_order(telegram_id=callback.from_user.id, data=json.dumps(order_products))
            # drop_all_cart(callback.from_user.id)
            # if len_of_product >= 1:

            #     await bot.send_message(callback.from_user.id, translate_text(f"Sizning buyurtmangiz qabul qilindi.\nTez orada administratorlar siz bilan bo'glanishadi ", lang))

        else:
            await bot.send_message(callback.from_user.id, translate_text(f"Siz address kiritmagan ekansiz!", lang)  + "\n/address")


    # Basket handler 

    elif str(callback.data) == f"basket_{basket_id}":
        language = get_user_language(callback.from_user.id)

        products = get_cart_products(callback.from_user.id)
        product = json.loads(products[int(basket_id) - 1][0])
        product_id = product.get("id")
        product_name = product.get("name")

        await ProductEditState.square.set()


        async with state.proxy() as data:
            data['product_id'] = product_id

        await bot.send_message(callback.from_user.id, translate_text(f"{product_name} Tovarning kengligini va balandligini metr o'lcho'vida yuboring.\nShunaqangi tartibda yuboring:\n", language) + "2x3")

    # Next and back handler

    for index, category in enumerate(get_categories()):
        category_id = category.get("id")


        if callback.data == f"next_{category.get('id')}_{current}":
            
            category_id = category.get("id")

            next_i = int(current) + 1
            current = str(next_i)
            
            category_products = get_category_products(category_id=category_id, page=next_i)    

            if category_products != False:
                await bot.delete_message(callback.from_user.id, callback.message.message_id)
                per_page = len(category_products.get('results'))
            else:
                per_page = 1

            text = products_text(category=category, current_page=str(next_i), user_id=callback.from_user.id)

            if text != False:
                return await bot.send_message(callback.from_user.id, text=text, reply_markup=products_keyboard(per_page=per_page, category_id=category_id, current=str(next_i)))
            return await callback.answer("Not found")

        elif callback.data == f"back_{category.get('id')}_{current}":
            if int(current) > 1:
                category_id = category.get("id")
                back_i = int(current) - 1
                current = str(back_i)
                
                category_products = get_category_products(category_id=category_id, page=back_i)

                if category_products != False:
                    await bot.delete_message(callback.from_user.id, callback.message.message_id)
                    per_page = len(category_products.get('results'))
                else:
                    per_page = 1
                
                text = products_text(category=category, current_page=str(back_i), user_id=callback.from_user.id)

                if text != False:
                    return await bot.send_message(callback.from_user.id, text=text, reply_markup=products_keyboard(per_page=per_page, category_id=category_id, current=str(back_i)))
                
                return await callback.answer("Not found")

    # Get product handler

    for let in range(1, 13):
        page_current = callback.data[7:8]

        if str(callback.data) == f"page_{let}_{page_current}_{cat_id}":

            
            language = get_user_language(callback.from_user.id)

            product = get_product_from_list(category_id=cat_id, page=page_current, index=let)
            photo_product = baseUrl + product.get("image")
            # photo_product = "http://www.jalyuzi.uz/image/cache/catalog/photos/item/tkanVer/diamond-03212-228x228.jpg"
            name = product.get("name")
            weight = product.get("weight")
            color_id = product.get("color")

            if len(color_id) >= 1:
                color_id = product.get("color")[0]
                color = get_color(color_id).get("name")
            else:
                color = "Нет"
            
            open_site = translate_text("Saytda ko'rish", language)
            product_slug = product.get("slug")

            url = f'<a href="{baseUrl}/product/{product.get("slug")}"><b>{open_site} 🌐</b></a>' 
            category_name = get_category(cat_id).get("name")
            price = product.get("price_sum")

            text = f"<b>{translate_text('Tovar nomi', language)}</b>: {name},\n<b>{translate_text('Lenta kengligi', language)}</b>: {weight},\n<b>{translate_text('Kategoriya', language)}</b>: {category_name},\n<b>{translate_text('Rang', language)}</b>: {color}<b>\n{translate_text('narxi', language)}</b>: {price} сум\n\n{url}"      


            await bot.send_photo(chat_id=callback.from_user.id, photo=str(photo_product), caption=text, reply_markup=add_cart_keyboards(lang=language, product_slug=product_slug))

    # Add to cart handler

    if str(callback.data)[:7] == 'product':
        language = get_user_language(callback.from_user.id)

        slug = str(callback.data)[8:]
        product = get_product(slug)

        if product is not None:
            if is_authenticated(callback.from_user.id):
                status = add_to_cart(callback.from_user.id, json.dumps(product))
                
                if status:
                    return await bot.send_message(callback.from_user.id, str(translate_text("Mahsulot savatga muvaffaqiyatli qo‘shildi", language)) + ' ✅\n/basket')
                else:
                    msg = await bot.send_message(callback.from_user.id, str(translate_text("Mahsulot korzinkaga qoshilib bo'lingan", language)) + ' ❌\n/basket')
                    time.sleep(2)
                    await bot.delete_message(callback.from_user.id, msg.message_id)

# State 

@dp.message_handler(state=ProductEditState.square)
async def square_handle(message:types.Message, state=FSMContext):
    first_letter = str(message.text)[:1]
    last_letter = str(message.text)[-1]
    language = get_user_language(message.from_user.id)

    if first_letter.isdigit() and last_letter.isdigit():
        async with state.proxy() as data:
            data['square'] = message.text
            product_id = data['product_id']

            update_cart(message.from_user.id, product_id, message.text)
            await state.finish()
            return await bot.send_message(message.from_user.id, translate_text("Ummumiy kv muvafiqiyatli o'zgardi ✅", language) + '\n/basket')

        
    else:
        return await send_message_local(message.from_user.id, "Iltimos tepada misol qilib keltirilgandaka kiritin!", language)


