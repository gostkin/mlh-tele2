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

def print_service(chat_id, service):
    message = '*' + service['name'] + '*\n' + service['description']
    bot.send_message(chat_id, message, parse_mode='Markdown')

@bot.message_handler(commands=['getServices'])
def get_service_list(message):
    services = api.services.get_available_services()
    if services.status_code != 200:
        bot.send_message(message.chat.id, words.REQUEST_FAILED)
    else:
        for service in services.body['data']:
            print_service(message.chat.id, service)


if __name__ == '__main__':
    bot.polling(none_stop=True)