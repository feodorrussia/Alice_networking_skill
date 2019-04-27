# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с логами.
import logging

# Импортируем модуль для работы с API Алисы
from alice_sdk import AliceRequest, AliceResponse

# Импортируем модуль с логикой игры
from main_function import *

# Импортируем модуль работы с базами данных


# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request

# Импортируем базу данных
import database_module

# Инициализируем "приложение" для самого веб-сервиса
app = Flask(__name__)

# Хранилище данных о сессиях.
session_storage = {}

logging.basicConfig(level=logging.DEBUG)


@app.route("/life_simulation/ping")
def ping():
    return "pong"


# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])
def main():
    # Функция получает тело запроса и возвращает ответ.
    alice_request = AliceRequest(request.json)
    logging.info('Request: {}'.format(alice_request))
    database = database_module.DatabaseManager()
    alice_response = AliceResponse(alice_request)

    user_id = alice_request.user_id
    print(user_id)
    print(session_storage.get(user_id))
    print(len(session_storage))
    alice_response, session_storage[user_id] = handle_dialog(
        alice_request, alice_response, session_storage.get(user_id), database
    )

    logging.info('Response: {}'.format(alice_response))
    print()

    return alice_response.dumps()


# Просто будем проверять, работает ли наш сервис
@app.route('/')
def ping_get():
    return "Hello, Alice!)"


if __name__ == '__main__':
    app.run()
