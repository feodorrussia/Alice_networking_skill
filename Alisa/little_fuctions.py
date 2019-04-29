import requests
import random
import json

API_CODE = 'dict.1.1.20190331T101514Z.9cbf4535b1122019.dbd3fb8c0fded55cd45d1f44459bbfda21d8e82a'
BASIC_REQUEST = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?' \
                'key={API_CODE}&' \
                'lang=TRANS&' \
                'text=TEXTWORD'\
    .format(API_CODE=API_CODE)

ERRORS = {200: 'Запрос выполнен',
          401: 'Ключ API невалиден',
          402: 'Ключ API заблокирован',
          403: 'Превышено суточное ограничение на кол-во запросов',
          413: 'Превышен максимальный размер текста',
          501: 'Заданное направление перевода не поддерживается'}


def get_suggests(user_storage):
    if "suggests" in user_storage.keys():
        suggests = []
        for suggest in user_storage['suggests']:
            if type(suggest) != list:
                suggests.append({'title': suggest, 'hide': True})
            else:
                print(suggest)
                suggests.append({'title': suggest[0], "url": suggest[1], 'hide': False})
                print(suggests)
    else:
        suggests = []

    return suggests, user_storage


def message_error(response, user_storage, answer):
    message = random.choice(answer)
    response.set_text(message)
    response.set_tts(message + "Доступные команды: {}.".format(" ,".join(user_storage['suggests'])))
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(buttons)
    return response, user_storage


def read_answers_data(name: str) -> dict:
    return json.load(open(name + ".json", encoding="utf-8"))

def update_status_system(new: str, type: str = 'global_status'):
    f = json.load(open('data/status' + ".json", encoding="utf-8"))
    f[type] = new
    json.dump(f, open('data/status' + ".json", 'w', encoding="utf-8"))


def choice_wrd(last_char, used_words):
    if type(used_words) is not list:
        used_words = []
    user_word = random.choice(read_answers_data("data/words")[last_char])
    while user_word in used_words:
        user_word = random.choice(read_answers_data("data/words")[last_char])
    return user_word


# Ну вот эта функция всем функциям функция, ага. Замена постоянному формированию ответа, ага, экономит 4 строчки!!
def message_return(response, user_storage, message):  # ща будет магия
    response.set_text(message)
    response.set_tts(message)
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(buttons)
    return response, user_storage


def check_wrd(wrd):
    url_for_request = BASIC_REQUEST.replace('TRANS', "ru-ru").replace('TEXTWORD', wrd)
    response = requests.get(url_for_request).json()
    if 'code' in response.keys():
        return ERRORS[response['code']]
    else:
        dct = read_answers_data("data/words")
        return len(response['def']) > 0 or (wrd[0] in dct.keys() and wrd in dct[wrd[0][0]])
