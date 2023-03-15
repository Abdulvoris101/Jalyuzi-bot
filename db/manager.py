import sqlite3
import json

con = sqlite3.connect(".bot.db")

cur = con.cursor()


cur.execute("""CREATE TABLE IF NOT EXISTS TOKENS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINTEGER,
    token VARCHAR(500),
    language VARCHAR(50)
);""")


cur.execute("""CREATE TABLE IF NOT EXISTS CART (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINTEGER,
    product_id BIGINTEGER,
    product TEXT,
    square VARCHAR(200)
);""")


def is_authenticated(telegram_id, cur=cur):
    user = cur.execute(f"SELECT * FROM TOKENS WHERE telegram_id = {telegram_id}")

    if user.fetchone():
        return True
    
    return False



def create_token(telegram_id, lang, token="None", cur=cur):
    token = cur.execute(f"""
        INSERT INTO TOKENS (telegram_id, token, language)
        VALUES ({telegram_id}, '{token}', '{lang}');
    """)

    con.commit()


def get_token(telegram_id, cur=cur):
    token = cur.execute(f"""
        SELECT token FROM TOKENS WHERE telegram_id={telegram_id};
    """)
    con.commit()

    return token.fetchone()


def drop_all_cart(telegram_id, cur=cur):
    cur.execute(f"""
        DELETE FROM CART WHERE telegram_id={telegram_id};
    """)
    con.commit()
    
    return True

def update_token(telegram_id, token, cur=cur):
    cur.execute(f"UPDATE TOKENS SET token = '{token}' WHERE telegram_id = {telegram_id};")
    con.commit()


def get_user_language(telegram_id, cur=cur):
    language = cur.execute(f"""
        SELECT language FROM TOKENS WHERE telegram_id={telegram_id}
    """)
    language = language.fetchone()

    if language is not None:
        return language[0]

    return False


def delete_user(telegram_id, cur=cur):
    cur.execute(f"DELETE FROM TOKENS WHERE telegram_id = {telegram_id}")
    con.commit()

def is_product_incart(user_id, product_id):
    users = cur.execute(f"""
        SELECT telegram_id FROM CART WHERE product_id={int(product_id)}
    """)

    if len(users.fetchall()) >= 1:
        for user in users.fetchall():
            if user[0] == user_id:
                return True
            
            return False
    else:
        return False
    



def add_to_cart(user_id, product, square="1x1.5", cur=cur):
    product_id =  json.loads(product).get("id")

    status = is_product_incart(user_id, product_id)

    if status == False:
        cur.execute(f"""
            INSERT INTO CART (telegram_id, product_id, product, square)
            VALUES ({user_id}, {product_id}, '{product}', '{square}');
        """)

        con.commit()

        return True

    return False


def update_cart(user_id, product_id, square):

    status = cur.execute(f""" UPDATE CART SET square='{str(square)}' WHERE product_id={int(product_id)} AND telegram_id={int(user_id)};""")

    con.commit()

def get_cart_product(product_id):
    product = cur.execute(f"""
        SELECT square FROM CART WHERE product_id={product_id}
    """)

    return product.fetchone()


def get_cart_products(user_id):
    products = cur.execute(f"""
        SELECT product, square FROM CART WHERE telegram_id={user_id}
    """)


    return products.fetchall()


def set_language(telegram_id, lang):

    language = cur.execute(f"""
        UPDATE TOKENS SET language='{lang}' WHERE telegram_id = {telegram_id} 
    """)

    con.commit()
