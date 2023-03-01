import requests
import json
from db.manager import get_token

baseUrl = 'https://jalyuzi.com'

headers = {
    'Content-Type': 'application/json',
    'User-Agent': "Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36",
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}


def user_me(telegram_id):
    r = requests.get(f"{baseUrl}/api/users/?telegram_id={telegram_id}")
    return r.json()

def update_user(telegram_id, data):
    token = get_token(telegram_id)

    headers['Authorization'] = f"Token {token[0]}"

    r = requests.put(f"{baseUrl}/api/users/me/", headers=headers, data=data)

    return r

def send_message(telegram_id, msg):
    user = user_me(telegram_id)

    token = get_token(telegram_id)

    headers['Authorization'] = f"Token {token[0]}"

    data = {
        "name": user.get("first_name"),
        "phone_number": user.get("username"),
        "email": "123@gmail.com",
        "message": msg,
    }

    r = requests.post(f"{baseUrl}/api/contact/", headers=headers, data=json.dumps(data))
    
    return r.json()


def create_address(telegram_id, data):
    token = get_token(telegram_id)

    headers['Authorization'] = f"Token {token[0]}"

    r = requests.post(f"{baseUrl}/api/orders/address/", headers=headers, data=data)

    return r.json()

def get_address(telegram_id):
    token = get_token(telegram_id)
    headers['Authorization'] = f"Token {token[0]}"

    r = requests.get(f"{baseUrl}/api/orders/address/", headers=headers)

    if len(r.json()) >= 1:
        return r.json()
    
    return False

def create_order(telegram_id, data):
    token = get_token(telegram_id)

    headers['Authorization'] = f"Token {token[0]}"

    data = requests.post(f"{baseUrl}/api/orders/", headers=headers, data=data)

    return data

def send_verif_code(telegram_id):
    data = {
        'telegram_id': telegram_id
    }
    data = json.dumps(data)

    r = requests.post(f"{baseUrl}/api/users/send_verification/", headers=headers, data=data)


    return r.json()



def user_register(data):
    r = requests.post(baseUrl + '/api/users/', headers=headers, data=json.dumps(data))

    return r.json()


def user_confirmation(data):
    r = requests.post(baseUrl + '/api/users/verification/', headers=headers, data=json.dumps(data))

    return r.json()

def is_confirmed(telegram_id):
    user = requests.get(baseUrl + '/api/users/?telegram_id=' + str(telegram_id))
    user = user.json()
    return user.get('first_confirm')

def get_categories():
    categories = json.loads(requests.get(f'{baseUrl}/api/categories/').text)

    return categories

def get_category(category_id):
    if category_id is not None:
        category = json.loads(requests.get(f'{baseUrl}/api/category/{category_id}').text)
        return category

    return "Нет"


def get_color(color_id):
    if color_id is not None:
        color = json.loads(requests.get(f'{baseUrl}/api/filter/color/{color_id}').text)
        return color
    
    return "Нет"

def get_category_products(category_id, page):
    products = json.loads(requests.get(f"{baseUrl}/api/products/?category={category_id}&page_size=10&page={page}").text)

    if products.get("detail") == "Неправильная страница":
        return False

    return products

def get_product_from_list(category_id, page, index):
    products = requests.get(f"{baseUrl}/api/products/?category={category_id}&page={page}&page_size=10")
    product = products.json().get("results")[index - 1]
    

    return product


def get_product(slug):
    product = json.loads(requests.get(f"{baseUrl}/api/product/{slug}").text)

    if product.get("detail") == "Неправильная страница":
        return None

    return product

