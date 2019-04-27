# coding: utf-8
from __future__ import unicode_literals
from little_fuctions import *


def handle_dialog(request, response, user_storage, database):
    from random import choice
    if not user_storage:
        user_storage = {"suggests": []}
    input_message = request.command.lower()
    if request.is_new_session:
        if not database.get_entry(request.user_id):
            output_message = "Привет-привет. Не хочешь ли ты сыграть в слова? Если да, то просто назови своё имя!"
        else:
            output_message = "И снова здравствуй! Продолжим игру??"
            user_storage = {'suggests': [
                "Продолжить",
                "Начать сначала"
            ]}
        return message_return(response, user_storage, output_message)

    if "помощь" in input_message or "что ты умеешь" in input_message:
        output_message = "В этой игре тебе просто-напросто нужно говорить слово, начинающиеся с той же буквы, " \
                         "что заканчивается предыдущее. Статистика отгаданных слов сохраняется, при начале новой игры" \
                         " счет в данный момент обнуляется, а максимальный остается. Что ж, сыграем?"
        user_storage = {'suggests': [
            "Продолжить",
            "Начать сначала"
        ]}
        return message_return(response, user_storage, output_message)

    if input_message in ['не хочется', 'в следующий раз', 'выход', "не хочу", 'выйти', 'стоп']:
        output_message = "Окей, напиши мне что-нибудь, если захочешь снова поиграть)"
        response.end_session = True
        return message_return(response, user_storage, output_message)

    if not database.get_entry(request.user_id):
        database.add_user(request.user_id, input_message)
        output_message = "Что ж, я тебя запомню. Начнем?"
        user_storage = {'suggests': [
            "Давай"
        ]}
        return message_return(response, user_storage, output_message)

    if "таблица лидеров" in input_message or "лидеры" in input_message or "рейтинг" in input_message:
        leaders = database.make_leaderboard()
        output_message = "Имеющиеся на данный момент лидеры:\n{}\n" \
            .format(",\n".join(["{}. {}, счет - {}".format(i[0], i[1].capitalize(), i[2]) for i in leaders]))
        current_user_stats = database.get_entry(request.user_id)[0]
        current_user_stats = (current_user_stats[1], current_user_stats[4], current_user_stats[3])
        if not any([True if current_user_stats[:2] == lead[1:] else False for lead in leaders]):
            output_message += '==========\n{}, сейчас: {}, максимально: {}' \
                .format(current_user_stats[1], current_user_stats[3], current_user_stats[4])
        output_message += "\nПродолжим игру или начнем сначала?"

        user_storage = {'suggests': [
            "Продолжить",
            "Начать сначала"
        ]}

        return message_return(response, user_storage, output_message)

    entry = database.get_entry(request.user_id)[0]
    if "продолжить" in input_message or "давай" in input_message or "сначала" in input_message or (
            "хочу" in input_message and "не" in input_message) and not entry[2]:
        chosen_word = choice_wrd(entry[2] if entry[2] else choice("айцукенгшщзхфывапролджэячсмитбю"),
                                 database.get_words(request.user_id))
        if "сначала" in input_message:
            database.update(request.user_id, chosen_word[-1] if chosen_word[-1] not in "ьъ" else chosen_word[-2],
                            current_score=0, max_score=entry[3] if entry[3] > entry[4] else entry[4])
        else:
            database.update(request.user_id, chosen_word[-1] if chosen_word[-1] not in "ьъ" else chosen_word[-2],
                            current_score=entry[3], max_score=entry[3] if entry[3] > entry[4] else entry[4])
        output_message = "Только запомни, учитываться будет только первое слово. Что ж, начнём! Внимание, слово " \
                         "- {}.".format(chosen_word)
        user_storage = {'suggests': []}
        return message_return(response, user_storage, output_message)

    elif entry and entry[2]:
        user_word = input_message.split()
        if user_word[0][0].lower() == entry[2]:
            if check_wrd(user_word[0]):
                used_words = database.get_words(request.user_id)
                if user_word[0] not in used_words:
                    used_words.append(user_word[0])
                    chosen_word = choice_wrd(user_word[0][-1] if user_word[0][-1] not in "ьъ" else user_word[0][-2],
                                             used_words)
                    output_message = "Правильно! Следующее слово - {}.".format(chosen_word)
                    database.update(request.user_id,
                                    chosen_word[-1] if chosen_word[-1] not in "ьъ" else chosen_word[-2],
                                    current_score=entry[3] + 1, max_score=entry[3] if entry[3] > entry[4] else entry[4])
                    database.add_word(request.user_id, user_word[0])
                else:
                    output_message = "Неправильно, это слово уже использовалось!"
            else:
                output_message = "Неправильно, " \
                                 "ты это слово выдумал, что ли? " \
                                 "Если нет, то скорее всего его просто нет в моем словаре, " \
                                 "лучше подбери другой вариант."
        else:
            output_message = "Неправильно! Слово начинается не с той буквы, напоминаю, должна быть буква {}." \
                .format(entry[2])
        return message_return(response, user_storage, output_message)

    buttons, user_storage = get_suggests(user_storage)
    return message_error(response, user_storage, [
        "Я жду ответа!",
        "Не очень понял ответ, но я надеюсь, что это была смешная шутка",
        "Я не настолько умный, как человеки, поэтому ответьте крайне линейно",
        "Вау... ничего не понял"
    ])
