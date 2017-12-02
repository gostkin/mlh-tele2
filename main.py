# -*- coding: utf-8 -*-

import config
import telebot
import rest
import words

bot = telebot.TeleBot(config.token)
api = rest.build_tele2_api()


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