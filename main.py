# -*- coding: utf-8 -*-

import config
import telebot
import rest
import words
import logging
from logging.handlers import RotatingFileHandler
import storage
from simple_rest_client.exceptions import *
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
                    in_registration.pop(message.chat.id)
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
        in_registration.pop(message.chat.id)
        bot.send_message(message.chat.id, "Номер успешно добавлен")
    data.close()


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


def print_tariffs(chat_id, tariffs):
    def counter():
        counter.cnt += 1
        return counter.cnt
    counter.cnt = 0

    for tariff_chunk in chunks(tariffs.body['data'], 2):
        msg = '\n\n'.join(map(lambda service: '*' + str(counter()) + '. ' + service['name'] +
                                              '*\n', tariff_chunk))
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for tariff in tariff_chunk:
            button = types.InlineKeyboardButton('Подробнее: ' + tariff['name'],
                                                callback_data='detailed_tariff@' + tariff['slug'])
            buttons.append(button)
        keyboard.add(*buttons)
        bot.send_message(chat_id, msg, reply_markup=keyboard, parse_mode='Markdown')


@bot.message_handler(commands=['services'])
def get_service_list(message):
    try:
        services = api.services.get_available_services()
        print_services(message.chat.id, services)
    except Exception as e:
        appLog.warning(e)
        bot.send_message(message.chat.id, words.REQUEST_FAILED)


@bot.message_handler(commands=['tariffs'])
def get_service_list(message):
    try:
        tariffs = api.tariffs.get_available_tariffs()
        print_tariffs(message.chat.id, tariffs)
    except Exception as e:
        appLog.warning(e)
        bot.send_message(message.chat.id, words.REQUEST_FAILED)


@bot.message_handler(commands=['add'])
def add_number(message):
    in_registration[message.chat.id] = [1, []]
    bot.send_message(message.chat.id, "Введите ваш номер:")


def print_detailed_tariff(chat_id, tariff):
    msg = '*Тариф \"' + tariff['name'] + '\"*\n' + '\n' + words.ARCHIVE + ': ' + \
          words.yesno(tariff['archive']) + '\n' + \
          words.SUBSCR_FEE + ': ' + str(tariff['subscriptionFee'])
    kb = types.InlineKeyboardMarkup()
    to_site = types.InlineKeyboardButton(text='Подробнее на сайте', url=tariff['url'])
    add_service = types.InlineKeyboardButton(text='Подключить', callback_data='set_tariff@' + tariff['slug'])
    kb.add(to_site, add_service)
    bot.send_message(chat_id, msg, reply_markup=kb, parse_mode='Markdown')


def print_detailed_service(chat_id, service):
    msg = '*Сервис \"' + service['name'] + '"*\n' + service['description'] + '\n' + words.ARCHIVE + ': ' +\
          words.yesno(service['archive']) + '\n' + words.CONN_FEE + ': ' + str(service['connectionFee']) + '\n' +\
          words.SUBSCR_FEE + ': ' + str(service['subscriptionFee'])
    kb = types.InlineKeyboardMarkup()
    to_site = types.InlineKeyboardButton(text='Подробнее на сайте', url=service['url'])
    add_service = types.InlineKeyboardButton(text='Подключить', callback_data='add_service@' + service['slug'])
    kb.add(to_site, add_service)
    bot.send_message(chat_id, msg, reply_markup=kb, parse_mode='Markdown')


def phone_selector(chat_id, callback):
    data = storage.Storage()
    phones = data.get_user_data(chat_id)
    kb = types.InlineKeyboardMarkup(row_width=1)
    for phone in phones:
        btn = types.InlineKeyboardButton(text=phone[1], callback_data=callback + '@' + phone[1] + '@' + phone[2])
        kb.add(btn)
    bot.send_message(chat_id, 'Выберите телефон:', reply_markup=kb)
    data.close()


def add_service_to_phone(chat_id, service_id, phone, token):
    try:
        api.subscribers.add_service(phone, token, service_id)
        bot.send_message(chat_id, 'Сервис успешно подключён!')
    except Exception as e:
        bot.send_message(chat_id, str(e))


@bot.callback_query_handler(lambda x: query_type(x.data) == 'add_service_to_phone')
def callback_add_service_to_phone(call):
    args = parse_args(call.data)
    add_service_to_phone(call.message.chat.id, *args)


@bot.callback_query_handler(lambda x: query_type(x.data) == 'add_service')
def callback_add_service(call):
    args = parse_args(call.data)
    data = storage.Storage()
    phones = data.get_user_data(call.message.chat.id)
    if phones is None or len(phones) == 0:
        bot.send_message(call.message.chat.id, 'Ни одного телефона не подключено. Вы можете добавить телефон командой '
                                               '/add')
    elif len(phones) > 1:
        phone_selector(call.message.chat.id, 'add_service_to_phone@' + args[0])
    else:
        add_service_to_phone(call.message.chat.id, args[0], phones[0][1], phones[0][2])
    data.close()


@bot.callback_query_handler(lambda x: query_type(x.data) == 'detailed_service')
def callback_detailed_service(call):
    args = parse_args(call.data)

    try:
        service = api.services.get_info(args[0])
        print_detailed_service(call.message.chat.id, service.body['data'])
    except Exception as e:
        appLog.warning(e)
        bot.send_message(call.message.chat.id, words.REQUEST_FAILED)


@bot.callback_query_handler(lambda x: query_type(x.data) == 'detailed_tariff')
def callback_detailed_tariff(call):
    args = parse_args(call.data)

    try:
        tariff = api.tariffs.get_info(args[0])
        print_detailed_tariff(call.message.chat.id, tariff.body['data'])
    except Exception as e:
        appLog.warning(e)
        bot.send_message(call.message.chat.id, words.REQUEST_FAILED)


@bot.message_handler(commands=['help', 'start'])
def get_help(message):
    bot.send_message(message.chat.id, """Список команд:
/help - вывести справку
/services - получить список сервисов""")


@bot.message_handler(commands=['numbers'])
def get_numbers(message):
    data = storage.Storage()
    try:
        numbers = data.get_user_data(message.chat.id)
        if not numbers:
            bot.send_message(message.chat.id, "У вас нет зарегестрированных номеров")
        else:
            print_numbers(message.chat.id, numbers)
    except Exception as e:
        appLog.warning(e)
        bot.send_message(message.chat.id, words.REQUEST_FAILED)


def print_numbers(chat_id, numbers):
    def counter():
        counter.cnt += 1
        return counter.cnt
    counter.cnt = 0

    for number in chunks(numbers, 1):
        print(number)
        msg = '*Ваши номера*:\n'+'\n'.join(map(lambda service: '*' + str(counter()) + '. ' + service[1] +
                                              '*\n', number))
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        for n in number:
            button = types.InlineKeyboardButton('Подробнее: ' + n[1],
                                                callback_data='detailed_number@' + n[1])
            buttons.append(button)
        keyboard.add(*buttons)
        bot.send_message(chat_id, msg, reply_markup=keyboard, parse_mode='Markdown')


def print_detailed_number(chat_id, number):
    msg = '*Номер* : ' + number['msisdn'] + '\n' + \
          "*Фамилия*: " + number['lastName'] + '\n' + \
          "*Имя*: " + number['firstName'] + '\n' + \
          "*Отчество*: " + number['middleName'] + '\n' + \
          "*E-mail*: " + number['email'] + '\n'
    kb = types.InlineKeyboardMarkup()
    actions = types.InlineKeyboardButton(text='Действия с номером', callback_data='add_service@' + number['msisdn'])
    kb.add(actions)
    bot.send_message(chat_id, msg, reply_markup=kb, parse_mode='Markdown')


@bot.callback_query_handler(lambda x: query_type(x.data) == 'detailed_number')
def callback_detailed_number(call):
    args = parse_args(call.data)
    try:
        user = api.subscribers.get_user_info(args[0])
        print_detailed_number(call.message.chat.id, user.body['data'])
    except Exception as e:
        appLog.warning(e)
        bot.send_message(call.message.chat.id, words.REQUEST_FAILED)


if __name__ == '__main__':
    bot.polling(none_stop=True)

