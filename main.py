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


def query_type(query):
    return query.split('@')[0]

def parse_args(query):
    return query.split('@')[1:]


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
                                                callback_data='detailed_service@' + service['slug'])
            buttons.append(button)
        keyboard.add(*buttons)
        bot.send_message(chat_id, msg, reply_markup=keyboard, parse_mode='Markdown')


@bot.message_handler(commands=['services'])
def get_service_list(message):
    services = api.services.get_available_services()
    if services.status_code != 200:
        bot.send_message(message.chat.id, words.REQUEST_FAILED)
    else:
        print_services(message.chat.id, services)


def print_detailed_service(chat_id, service):
    msg = '*' + service['name'] + '*\n' + service['description'] + '\n' + words.ARCHIVE + ': ' +\
          words.yesno(service['archive']) + '\n' + words.CONN_FEE + ': ' + str(service['connectionFee']) + '\n' +\
          words.SUBSCR_FEE + ': ' + str(service['subscriptionFee'])
    kb = types.InlineKeyboardMarkup()
    to_site = types.InlineKeyboardButton(text='Подробнее на сайте', url=service['url'])
    add_service = types.InlineKeyboardButton(text='Подключить', callback_data='add_service@' + service['slug'])
    kb.add(to_site, add_service)
    bot.send_message(chat_id, msg, reply_markup=kb, parse_mode='Markdown')


@bot.callback_query_handler(lambda x: query_type(x.data) == 'detailed_service')
def callback_detailed_service(call):
    args = parse_args(call.data)
    service = api.services.get_info(args[0])
    if service.status_code != 200:
        bot.send_message(call.message.chat.id, words.REQUEST_FAILED)
    else:
        print_detailed_service(call.message.chat.id, service.body['data'])


@bot.message_handler(commands=['help', 'start'])
def get_help(message):
    bot.send_message(message.chat.id, """Список команд:
/help - вывести справку
/services - получить список сервисов""")

if __name__ == '__main__':
    bot.polling(none_stop=True)
