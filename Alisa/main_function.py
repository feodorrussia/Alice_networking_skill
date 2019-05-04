# coding: utf-8
from __future__ import unicode_literals
from little_fuctions import *


def handle_dialog(request, response, user_storage, database):
    if not user_storage:
        user_storage = {"suggests": ['Помощь']}
    input_message = request.command.lower()

    if request.user_id not in database.get_session(all=True):
        database.add_session(request.user_id)

    if input_message in ['выйти', 'выход']:
        output_message = "Обращайтесь ещё!)"
        user_storage = {'suggests': ['Помощь', 'Войти']}
        database.update_status(database.get_session(request.user_id, 'user_name')[0], 0)
        database.update_status_system('out', request.user_id)
        database.update_status_system('login', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if len(request.command.split(' ')) == 2 and database.get_session(request.user_id, 'status_action')[0] == 'login':
        input_message = request.command.split(' ')
        if database.get_registration(input_message[0], input_message[1])[0]:
            if database.get_registration(input_message[0], input_message[1])[1]:
                new_message = database.get_new_message(input_message[0])
                if len(new_message) > 0:
                    output_message = "Добро пожаловать {}!\nУ Вас {} непрочитанных сообщений.".format(input_message[0], len(new_message))
                    user_storage = {'suggests': [
                        'Посмотреть сообщения', 'Друзья', 'Группы', 'Найти', 'Написать сообщение', 'Помощь', 'Выход'
                    ]}
                else:
                    output_message = "Добро пожаловать {}!\nУ Вас нет непрочитанных сообщений.".format(input_message[0])
                    user_storage = {'suggests': [
                        'Друзья', 'Группы', 'Найти', 'Написать сообщение', 'Помощь', 'Выход'
                    ]}
                database.update_status_system('in', request.user_id)
                database.update_status_system(input_message[0], request.user_id, 'user_name')
                database.update_status_system('working', request.user_id, 'status_action')
            else:
                output_message = "Упс! Похоже Вы неправильно ввели свои данные. Попробуйте ещё раз)"
        else:
            database.add_user(input_message[0], input_message[1])
            output_message = "Добро пожаловать {}!".format(input_message[0])
            user_storage = {'suggests': [
                'Друзья', 'Группы', 'Найти', 'Написать сообщение', 'Помощь', 'Выход'
            ]}
            database.update_status_system('in', request.user_id)
            database.update_status_system(input_message[0], request.user_id, 'user_name')
            database.update_status_system('working', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if request.is_new_session or input_message in ['войти', 'регистрация']:
        output_message = "Здравствуйте, Вас приветствует Ваш коммуникатор Адель." \
                         " Чтобы перейти к работе просто скажите мне свой логин и пароль через пробел."
        user_storage = {'suggests': ['Помощь']}
        database.update_status_system('out', request.user_id)
        database.update_status_system('login', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if input_message == 'помощь':
        database.update_status_system('help', request.user_id, 'status_action')
        output_message = "Привет! Я Адель, Ваш коммуникатор. Я помогу Вам отправить сообщение " \
                         "Вашему другу или разместить его в группе."
        user_storage = {'suggests': ['Мои возможности', 'Команды быстрого ввода', 'Главная']}
        database.update_status_system('working', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if input_message in ['главная', 'отбой, давай на главную']:
        output_message = "Прошу)"
        if database.get_session(request.user_id, 'global_status')[0] == 'out':
            database.update_status_system('out', request.user_id)
            user_storage = {'suggests': ['Помощь', 'Войти']}
        else:
            database.update_status_system('in', request.user_id)
            user_storage = {'suggests': ['Друзья', 'Группы', 'Найти', 'Написать сообщение', 'Помощь', 'Выход']}
        database.update_status_system('working', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if input_message in ['друзья', 'вернись в друзья'] and database.get_session(request.user_id, 'global_status')[0] == 'in':
        friendship = database.get_friendship(database.get_session(request.user_id, 'user_name')[0])
        if friendship[0]:
            output_message = "Ваши друзья:\n" + '\n'.join([x[1]+f'{" (в сети)" if database.get_user(x[1])[1][0][2] == 1 else " (не в сети)"}' for x in friendship[1]])
            user_storage = {'suggests': ['Написать сообщение', 'Найти', 'Главная']}
        else:
            output_message = "Похоже у Вас нет друзей.(\nНо вы их всегда можете найти)"
            user_storage = {'suggests': ['Найти', 'Главная']}
        database.update_status_system('working', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if input_message in ['найти', 'найди'] and database.get_session(request.user_id, 'global_status')[0] == 'in':
        output_message = "Хорошо.\nПоскажите, Вам найти друга или группу?"
        user_storage = {'suggests': ['Человека', 'Группу', 'Главная']}
        database.update_status_system('searching', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if database.get_session(request.user_id, 'status_action')[0] == 'searching' and input_message in [
        'человека','друга'] or database.get_session(request.user_id, 'status_action')[0] == 'working' and input_message in [
        'найди человека','найди друга']:
        output_message = "Хорошо.\nСкажите мне его имя его учётной записи(логин в системе)"
        user_storage = {'suggests': ['Главная', 'Отмена']}
        database.update_status_system('searching_user', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if database.get_session(request.user_id, 'status_action')[0] == 'searching_user' and input_message != 'отмена':
        if request.command == database.get_session(request.user_id, 'user_name')[0]:
            output_message = "Ха-ха, очень хорошая шутка!\nА теперь давайте серьёзно."
            return message_return(response, user_storage, output_message)
        friend = database.get_user(request.command)
        if friend[0]:
            output_message = f"Ура!\nЯ нашла Вашего друга!\nХотите добавить его в друзья?\n({friend[1][0][0]}{' (в сети)' if friend[1][0][2] == 1 else ' (не в сети)'})"
            user_storage = {'suggests': ['Да', 'Нет']}
            database.update_status_system('adding_friendship', request.user_id, 'status_action')
            database.update_status_system(friend[1][0][0], request.user_id, 'recipient_name')
        else:
            output_message = "Простите, мне не удалось найти пользователя по Вашему запросу("
            user_storage = {
                'suggests': ['Попробовать ещё раз', 'Отбой, давай на главную', 'Вернись в друзья']}
            database.update_status_system('searching_error', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if database.get_session(request.user_id, 'status_action')[0] == 'adding_friendship':
        if input_message == 'да':
            result = database.add_friendship(str(database.get_session(request.user_id, 'user_name')[0]),
                                             str(database.get_session(request.user_id, 'recipient_name')[0]))
            if result:
                output_message = f'''Отлично! Теперь у Вас в друзьях есть {database.get_session(request.user_id, 'recipient_name')[0]}\nХотите написать ему?'''
                user_storage = {'suggests': ['Да', 'Нет']}
                database.update_status_system('end_adding', request.user_id, 'status_action')
            else:
                output_message = f'''У меня для Вас хорошая новость-{
                database.get_session(request.user_id, 'recipient_name')[0]} уже есть у Вас в друзьях!Хотите написать ему?'''
                user_storage = {'suggests': ['Да', 'Нет']}
                database.update_status_system('end_adding', request.user_id, 'status_action')
        else:
            output_message = 'Хорошо, рада была помочь Вам!'
            user_storage = {'suggests': ['Друзья', 'Группы', 'Помощь', 'Главная']}
            database.update_status_system('end_adding', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if database.get_session(request.user_id, 'status_action')[0] == 'end_adding':
        if input_message == 'да':
            output_message = 'Я готова, пишите сообщение!'
            user_storage = {
                'suggests': ['Отмена', 'Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
            database.update_status_system('sending_letter', request.user_id, 'status_action')
        else:
            output_message = 'Хорошо, рада была помочь Вам!'
            user_storage = {'suggests': ['Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
            database.update_status_system('working', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if database.get_session(request.user_id, 'status_action')[0] == 'sending_letter' and input_message != 'отмена':
        database.add_message(database.get_session(request.user_id, 'user_name')[0], request.command,
                             database.get_session(request.user_id, 'recipient_name')[0])
        output_message = 'Ваше сообщение отправлено! Перейти к диалогу?'
        user_storage = {
            'suggests': ['Да', 'Нет']}
        database.update_status_system('dialog?', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if database.get_session(request.user_id, 'status_action')[0] == 'dialog?':
        if input_message=='да':
            output_message = 'Хорошо, теперь Вы можете сразу видеть полученные сообщения и незамедлительно на них отвечать'
            user_storage = {'suggests': ['Распечатать историю диалога','Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
            database.update_status_system('chatting', request.user_id, 'status_action')
        else:
            output_message = 'Хорошо, рада была помочь Вам!'
            user_storage = {'suggests': ['Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
            database.update_status_system('working', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if input_message == 'написать сообщение' and database.get_session(request.user_id, 'status_action')[0] == 'working':
        output_message = 'Хорошо, скажите кому мне написать сообщение'
        user_storage = {'suggests': ['Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
        database.update_status_system('connect_recipient', request.user_id, 'status_action')
        return message_return(response, user_storage, output_message)

    if database.get_session(request.user_id, 'status_action')[0] == 'connect_recipient' and input_message != 'отмена':
        output_message = 'Я готова, пишите сообщение!'
        user_storage = {'suggests': ['Отмена', 'Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
        database.update_status_system('sending_letter', request.user_id, 'status_action')
        database.update_status_system(request.command, request.user_id, 'recipient_name')
        return message_return(response, user_storage, output_message)

    if 'напиши' in input_message and len(request.command.split(' ')) == 2 and database.get_session(request.user_id, 'status_action')[0] == 'working':
        output_message = 'Я готова, пишите сообщение!'
        user_storage = {'suggests': ['Отмена', 'Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
        database.update_status_system('sending_letter', request.user_id, 'status_action')
        database.update_status_system(request.command.split(' ')[1], request.user_id, 'recipient_name')
        return message_return(response, user_storage, output_message)

    if database.get_session(request.user_id, 'status_action')[0] == 'chatting' and input_message == 'распечатать историю диалога':
        user = database.get_session(request.user_id, 'user_name')[0]
        recipient = database.get_session(request.user_id, 'recipient_name')[0]
        print(user, recipient)
        dialog = database.get_dialog(user, recipient)
        print('    dialog:!!!   ', dialog)
        output_message = ''
        if dialog[0]:
            for message in dialog[1]:
                if message[0] == user:
                    output_message += 'Вы: ' + message[1] + '\n'
                else:
                    output_message += message[0] + ': ' + message[1] + '\n'
        else:
            output_message = 'Упс, что-то пошло не так)'
        user_storage = {'suggests': ['Распечатать историю диалога', 'Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
        return message_return(response, user_storage, output_message)

    buttons, user_storage = get_suggests(user_storage)
    return message_error(response, user_storage,
                         ['Конфуз;) Я ещё в разработке', 'Ой, сейчас исправлю)'
                          ])
