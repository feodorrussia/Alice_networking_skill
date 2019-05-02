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
        database.update_status(0, request.user_id)
        update_status_system('out')
        return message_return(response, user_storage, output_message)

    if len(request.command.split(' ')) == 2 and read_answers_data("data/status")[
        'global_status'] == 'out':
        input_message = request.command.split(' ')
        if database.get_registration(input_message[0], input_message[1])[0]:
            if database.get_registration(input_message[0], input_message[1])[1]:
                output_message = "Добро пожаловать {}!".format(input_message[0])
                user_storage = {'suggests': [
                    'Друзья', 'Группы', 'Найти', 'Помощь', 'Выход'
                ]}
                update_status_system('in')
                update_status_system(input_message[0], 'user_name')
                update_status_system('working', 'status_action')
            else:
                output_message = "Упс! Похоже Вы неправильно ввели свои данные. Попробуйте ещё раз)"
            return message_return(response, user_storage, output_message)
        else:
            database.add_user(input_message[0], input_message[1])
            output_message = "Добро пожаловать {}!".format(input_message[0])
            user_storage = {'suggests': [
                'Друзья', 'Группы', 'Найти', 'Помощь', 'Выход'
            ]}
            update_status_system('in')
            update_status_system(input_message[0], 'user_name')
            update_status_system('working', 'status_action')
            return message_return(response, user_storage, output_message)

    if request.is_new_session or input_message in ['войти', 'регистрация']:
        output_message = "Здравствуйте, Вас приветствует Ваш коммуникатор Адель." \
                         " Чтобы перейти к работе просто скажите мне свой логин и пароль через пробел."
        user_storage = {'suggests': ['Помощь']}
        update_status_system('out')
        update_status_system('login', 'status_action')
        return message_return(response, user_storage, output_message)

    if input_message == 'помощь':
        update_status_system('help')
        output_message = "Привет! Я Адель, Ваш коммуникатор. Я помогу Вам отправить сообщение " \
                         "Вашему другу или разместить его в группе."
        user_storage = {'suggests': ['Мои возможности', 'Команды быстрого ввода', 'Главная']}
        update_status_system('working', 'status_action')
        return message_return(response, user_storage, output_message)

    if input_message in ['главная', 'отбой, давай на главную']:
        output_message = "Прошу)"
        update_status_system('in')
        if read_answers_data("data/status")['global_status'] == 'out':
            user_storage = {'suggests': ['Помощь', 'Войти']}
        else:
            user_storage = {'suggests': ['Друзья', 'Группы', 'Найти', 'Помощь', 'Выход']}
        update_status_system('working', 'status_action')
        return message_return(response, user_storage, output_message)

    if input_message in ['друзья', 'вернись в друзья'] and read_answers_data("data/status")[
        'global_status'] == 'in':
        friendship = database.get_friendship(read_answers_data("data/status")['user_name'])
        if friendship[0]:
            output_message = "Ваши друзья:\n" + '\n'.join([x[0] for x in friendship[1][0]])
            user_storage = {'suggests': ['Написать сообщение', 'Найти', 'Главная']}
        else:
            output_message = "Похоже у Вас нет друзей.(\nНо вы их всегда можете найти)"
            user_storage = {'suggests': ['Найти', 'Главная']}
        update_status_system('working', 'status_action')
        return message_return(response, user_storage, output_message)

    if input_message in ['найти', 'найди'] and read_answers_data("data/status")[
        'global_status'] == 'in':
        output_message = "Хорошо.\nПоскажите, Вам найти друга или группу?"
        user_storage = {'suggests': ['Человека', 'Группу', 'Главная']}
        update_status_system('searching', 'status_action')
        return message_return(response, user_storage, output_message)

    if read_answers_data("data/status")['status_action'] == 'searching' and input_message in [
        'человека', 'найди человека', 'друга', 'найди друга']:
        output_message = "Хорошо.\nСкажите мне его имя его учётной записи(логин в системе)"
        user_storage = {'suggests': ['Главная', 'Отмена']}
        update_status_system('searching_user', 'status_action')
        return message_return(response, user_storage, output_message)

    if read_answers_data("data/status")[
        'status_action'] == 'searching_user' and input_message != 'отмена':
        if request.command == read_answers_data("data/status")['user_name']:
            output_message = "Ха-ха, очень хорошая шутка!\nА теперь давайте серьёзно."
            return message_return(response, user_storage, output_message)
        friend = database.get_user(request.command)
        if friend[0]:
            output_message = f"Ура!\nЯ нашла Вашего друга!\nХотите добавить его в друзья?\n({friend[1][0][0]}{' (в сети)' if friend[1][0][2] == 1 else ' (не в сети)'})"
            user_storage = {'suggests': ['Да', 'Нет']}
            update_status_system('adding_friendship', 'status_action')
            update_status_system(friend[1][0][0], 'recipient_name')
        else:
            output_message = "Простите, мне не удалось найти пользователя по Вашему запросу("
            user_storage = {
                'suggests': ['Попробовать ещё раз', 'Отбой, давай на главную', 'Вернись в друзья']}
            update_status_system('searching_error', 'status_action')
        return message_return(response, user_storage, output_message)

    if read_answers_data("data/status")['status_action'] == 'adding_friendship':
        if input_message == 'да':
            result = database.add_friendship(str(read_answers_data("data/status")['user_name']),
                                             str(read_answers_data("data/status")[
                                                     'recipient_name']))
            if result:
                output_message = f'''Отлично! Теперь у Вас в друзьях есть {
                read_answers_data("data/status")['recipient_name']}\nХотите написать ему?'''
                user_storage = {'suggests': ['Да', 'Нет', 'Главная']}
                update_status_system('end_adding', 'status_action')
            else:
                output_message = f'''У меня для Вас хорошая новость-{
                read_answers_data("data/status")[
                    'recipient_name']} уже есть у Вас в друзьях!Хотите написать ему?'''
                user_storage = {'suggests': ['Да', 'Нет', 'Главная']}
                update_status_system('end_adding', 'status_action')
        else:
            output_message = 'Хорошо, рада была помочь Вам!'
            user_storage = {'suggests': ['Друзья', 'Группы', 'Помощь', 'Главная']}
            update_status_system('end_adding', 'status_action')
        return message_return(response, user_storage, output_message)

    if read_answers_data("data/status")['status_action'] == 'end_adding':
        if input_message == 'да':
            output_message = 'Я готова, пишите сообщение!'
            user_storage = {
                'suggests': ['Отмена', 'Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
            update_status_system('sending_letter', 'status_action')
        else:
            output_message = 'Хорошо, рада была помочь Вам!'
            user_storage = {'suggests': ['Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
            update_status_system('working', 'status_action')
        return message_return(response, user_storage, output_message)

    if read_answers_data("data/status")[
        'status_action'] == 'sending_letter' and input_message != 'отмена':
        database.add_message(read_answers_data("data/status")['user_name'], request.command,
                             read_answers_data("data/status")['recipient_name'])
        output_message = 'Ваше сообщение отправлено! Перейти к диалогу?'
        user_storage = {
            'suggests': ['Да', 'Нет']}
        update_status_system('dialog?', 'status_action')
        return message_return(response, user_storage, output_message)

    if read_answers_data("data/status")['status_action'] == 'dialog?':
        if input_message=='да':
            output_message = 'Хорошо, теперь Вы можете сразу видеть полученные сообщения и незамедлительно на них отвечать'
            user_storage = {'suggests': ['Распечатать историю диалога','Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
            update_status_system('chatting', 'status_action')
        else:
            output_message = 'Хорошо, рада была помочь Вам!'
            user_storage = {'suggests': ['Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
            update_status_system('working', 'status_action')
        return message_return(response, user_storage, output_message)

    if input_message == 'написать сообщение' and read_answers_data("data/status")[
        'status_action'] == 'working':
        output_message = 'Хорошо, скажите кому мне написать сообщение'
        user_storage = {'suggests': ['Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
        update_status_system('connect_recipient', 'status_action')
        return message_return(response, user_storage, output_message)

    if read_answers_data("data/status")[
        'status_action'] == 'connect_recipient' and input_message != 'отмена':
        output_message = 'Я готова, пишите сообщение!'
        user_storage = {'suggests': ['Отмена', 'Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
        update_status_system('sending_letter', 'status_action')
        return message_return(response, user_storage, output_message)

    if read_answers_data("data/status")[
        'status_action'] == 'chatting' and input_message == 'распечатать историю сообщений':
        user = read_answers_data("data/status")['user_name']
        recipient = read_answers_data("data/status")['recipient_name']
        dialog = database.get_dialog(user, request.command, recipient)
        print('    dialog:!!!   ', dialog)
        output_message = ''
        if dialog[0]:
            for message in dialog[1][0]:
                if message[0] == user:
                    output_message += 'Вы: ' + message[1]
                else:
                    output_message += message[0] + ': ' + message[1]
        else:
            output_message='Упс, что-то пошло не так)'
        user_storage = {'suggests': ['Друзья', 'Группы', 'Найти', 'Помощь', 'Главная']}
        return message_return(response, user_storage, output_message)

    buttons, user_storage = get_suggests(user_storage)
    return message_error(response, user_storage,
                         ['Конфуз;) Я ещё в разработке', 'Ой, сейчас исправлю)'
                          ])
