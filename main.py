# -*- coding: utf-8 -*-

import config
import telebot
import rest
import words

from telebot import types

bot = telebot.TeleBot(config.token)
api = rest.build_tele2_api()


@bot.message_handler(content_types=["text"])
def default_test(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Хуи дрочены", url="https://ya.ru")
    url1 = types.InlineKeyboardButton(text="Пики точены", url="https://ya.ru")
    keyboard.row(url_button, url1)
    bot.send_message(message.chat.id, "Привет! Нажми на кнопку и перейди в поисковик.", reply_markup=keyboard)

#@bot.message_handler(content_types=['text'])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, message.text)
    print(message)


def print_services(chat_id, services):
    ret = ""
    iter = 1
    for service in services.body['data']:
        ret += '*' + str(iter) + '. ' + service['name'] + '*\n' + service['description'] + '\n\n'
        iter += 1

    bot.send_message(chat_id, ret, parse_mode='Markdown')


@bot.message_handler(commands=['get_services'])
def get_service_list(message):
    services = api.services.get_available_services()
    if services.status_code != 200:
        bot.send_message(message.chat.id, words.REQUEST_FAILED)
    else:
        print_services(message.chat.id, services)


if __name__ == '__main__':
    bot.polling(none_stop=True)