# coding: utf-8
from __future__ import unicode_literals
from little_fuctions import *


def handle_dialog(request, response, user_storage, database):
    from random import choice
    if not user_storage:
        user_storage = {"suggests": []}
    input_message = request.command.lower()
    if request.is_new_session or response.end_session:
        output_message = "Здравствуйте, Вас приветствует Ваш коммуникатор Адель." \
                         " Чтобы перейти к работе просто скажите мне свой логин и пароль через пробел."
        if response.end_session:
            user_storage = {'suggests': [x[2] for x in database.get_users(request.user_id)]
                            }
        return message_return(response, user_storage, output_message)

    if not database.get_users(request.user_id) or (not request.is_new_session and response.end_session):
        input_message=request.command.split(' ')
        database.add_user(request.user_id, input_message[0], input_message[1])
        output_message = "Добро пожаловать {}!".format(input_message[0])
        user_storage = {'suggests': [
            'Друзья', 'Группы', 'Помощь', 'Выход'
        ]}
        if not request.is_new_session and response.end_session:
            response.end_session = False
            response._response_dict['response']['end_session'] = response.end_session
        return message_return(response, user_storage, output_message)

    entry = database.get_individ(request.user_id)[1]
    print(entry)





    buttons, user_storage = get_suggests(user_storage)
    return message_error(response, user_storage, [
        "Я жду ответа!",
        "Не очень поняла ответ, но я надеюсь, что это была смешная шутка",
        "Я не настолько умная, как человеки, поэтому ответьте крайне линейно",
        "Вау... ничего не поняла"
    ])
