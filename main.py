# -*- coding: utf-8 -*-

import config
import telebot
import rest
import words

from telebot import types

bot = telebot.TeleBot(config.token)
api = rest.build_tele2_api()


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


@bot.message_handler(func=lambda x: False, content_types=["text"])
def default_test(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Хуи дрочены", url="https://ya.ru")
    url1 = types.InlineKeyboardButton(text="Пики точены", url="https://ya.ru")
    keyboard.row(url_button, url1)
    bot.send_message(message.chat.id, "Привет! Нажми на кнопку и перейди в поисковик.", reply_markup=keyboard)


def print_services(chat_id, services):
    def counter():
        counter.cnt += 1
        return counter.cnt
    counter.cnt = 0

    for service_chunk in chunks(services.body['data'], 2):
        msg = '\n\n'.join(map(lambda service: '*' + str(counter()) + '. ' + service['name'] +
                                              '*\n' + service['description'], service_chunk))
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for service in service_chunk:
            button = types.InlineKeyboardButton('Подробнее: ' + service['name'],
                                                callback_data="detailed_service@" + service['slug'])
            buttons.append(button)
        keyboard.add(*buttons)
        bot.send_message(chat_id, msg, reply_markup=keyboard, parse_mode='Markdown')


@bot.message_handler(func=lambda x: True, commands=['services'])
def get_service_list(message):
    services = api.services.get_available_services()
    if services.status_code != 200:
        bot.send_message(message.chat.id, words.REQUEST_FAILED)
    else:
        print_services(message.chat.id, services)


@bot.message_handler(commands=['help', 'start'])
def get_help(message):
    bot.send_message(message.chat.id, """Список команд:
/help - вывести справку
/services - получить список сервисов""")

if __name__ == '__main__':
    bot.polling(none_stop=True)
