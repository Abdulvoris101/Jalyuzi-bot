from deep_translator import GoogleTranslator
from auth.handlers import bot, types


def send_message_local(user_id, text, lang, reply_markup=None, bot=bot):
    translate= GoogleTranslator(source='uz', target='ru').translate(text)

    if reply_markup is not None:
        return bot.send_message(user_id, translate if lang == 'ru' else text, reply_markup=reply_markup)
    
    return bot.send_message(user_id, translate if lang == 'ru' else text)
    
    

def translate_text(text, lang):
    if lang == 'ru':
        translate = GoogleTranslator(source='uz', target='ru').translate(text)
        return translate
    
    return text