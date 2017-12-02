# -*- coding: utf-8 -*-

import config
import telebot
import rest
import words
import logging
from logging.handlers import RotatingFileHandler
import storage

from telebot import types

bot = telebot.TeleBot(config.token)
api = rest.build_tele2_api()

logFile = "activity.log"
logFormatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logHandler = RotatingFileHandler(logFile, mode='a', maxBytes=50*1024*1024,
                                 backupCount=5, encoding=None, delay=0)

logHandler.setFormatter(logFormatter)
logHandler.setLevel(logging.INFO)

appLog = logging.getLogger('root')
appLog.setLevel(logging.INFO)
appLog.addHandler(logHandler)

in_registration = {}


@bot.message_handler(func=lambda message: message.chat.id in in_registration.keys(), content_types=["text"])
def default_test(message):
    data = storage.Storage()
    if in_registration[message.chat.id][0] == 1:
        info = data.get_user_data(message.chat.id)
        if info is not None:
            for i in info:
                if message.text == i[1]:
                    in_registration.pop(message.text)
                    bot.send_message(message.chat.id, "Данный номер уже зарегестрирован на ваш аккаунт")
                    return

        in_registration[message.chat.id] = [2, [message.text]]
        bot.send_message(message.chat.id, "Введите токен")
    elif in_registration[message.chat.id][0] == 2:
        try:
            data.add_user_if_needed(message.chat.id, in_registration[message.chat.id][1][0], message.text)
        except Exception as e:
            appLog.warning(e, in_registration)
            bot.send_message(message.chat.id, "Произошла ошибка")
            return
        bot.send_message(message.chat.id, "Номер успешно добавлен")



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


@bot.message_handler(commands=['add'])
def add_number(message):
    in_registration[message.chat.id] = [1, []]
    bot.send_message(message.chat.id, "Введите ваш номер:")


if __name__ == '__main__':
    bot.polling(none_stop=True)