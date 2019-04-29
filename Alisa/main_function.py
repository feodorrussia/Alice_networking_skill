# coding: utf-8
from __future__ import unicode_literals
from little_fuctions import *


def handle_dialog(request, response, user_storage, database):
    if not user_storage:
        user_storage = {"suggests": ['Помощь']}
    input_message = request.command.lower()

    if input_message in ['выйти', 'выход']:
        output_message = "Обращайтесь ещё!)"
        user_storage = {'suggests': ['Помощь', 'Войти']}
        database.uppdate_status(0, request.user_id)
        update_status_system('out')
        return message_return(response, user_storage, output_message)

    if len(request.command.split(' ')) == 2 and read_answers_data("data/status")[
        'global_status'] == 'out':
        input_message = request.command.split(' ')
        if database.get_individ(input_message[0], input_message[1])[0]:
            if database.get_individ(request.user_id, input_message[0], input_message[1])[1]:
                output_message = "Добро пожаловать {}!".format(input_message[0])
                user_storage = {'suggests': [
                    'Друзья', 'Группы', 'Помощь', 'Выход'
                ]}
                update_status_system('in')
            else:
                output_message = "Упс! Похоже Вы неправильно ввели свои данные. Попробуйте ещё раз)"
            return message_return(response, user_storage, output_message)
        else:
            database.add_user(request.user_id, input_message[0], input_message[1])
            output_message = "Добро пожаловать {}!".format(input_message[0])
            user_storage = {'suggests': [
                'Друзья', 'Группы', 'Помощь', 'Выход'
            ]}
            update_status_system('in')
            return message_return(response, user_storage, output_message)

    if request.is_new_session or input_message in ['войти', 'регистрация']:
        output_message = "Здравствуйте, Вас приветствует Ваш коммуникатор Адель." \
                         " Чтобы перейти к работе просто скажите мне свой логин и пароль через пробел."
        user_storage = {'suggests': ['Помощь']}
        update_status_system('out')
        return message_return(response, user_storage, output_message)

    if input_message == 'помощь':
        update_status_system('help')
        output_message = "Привет! Я Адель, Ваш коммуникатор. Я помогу Вам отправить сообщение " \
                         "Вашему другу или разместить его в группе."
        user_storage = {'suggests': ['Мои возможности', 'Команды быстрого ввода', 'Главная']}
        return message_return(response, user_storage, output_message)

    if input_message == 'главная':
        output_message = "Прошу)"
        update_status_system('in')
        if read_answers_data("data/status")['global_status'] == 'out':
            user_storage = {'suggests': ['Помощь', 'Войти']}
        else:
            user_storage = {'suggests': ['Друзья', 'Группы', 'Помощь', 'Выход']}
        return message_return(response, user_storage, output_message)

    buttons, user_storage = get_suggests(user_storage)
    return message_error(response, user_storage,
                         ['Конфуз;) Я ещё в разработке', 'Ой, сейчас исправлю)'
                          ])
