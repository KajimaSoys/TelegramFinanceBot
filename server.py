"""Сервер Telegram бота, запускаемый непосредственно"""
import logging

#import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import exceptions
import expenses
import general
import incomes
import re
from categories import Categories
from server_utils import States



logging.basicConfig(level=logging.DEBUG)

API_TOKEN = '1798389140:AAFAIr3PJv4sTLrkFGgjEs9h06yNnquZD_s'#os.getenv("TELEGRAM_API_TOKEN")

#Подключение к прокси серверу
#PROXY_URL = os.getenv("TELEGRAM_PROXY_URL")
#PROXY_AUTH = aiohttp.BasicAuth(
#    login=os.getenv("TELEGRAM_PROXY_LOGIN"),
#    password=os.getenv("TELEGRAM_PROXY_PASSWORD"))
#Для восможности пользования лишь одним юзером
#ACCESS_ID = os.getenv("TELEGRAM_ACCESS_ID")

bot = Bot(token=API_TOKEN)#, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
#глобальная переменная для определения текущего состояния(Доход/Расход)
value = 0

@dp.message_handler(commands=['start', 'help', 'back'], state='*')
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    global value
    value = 0
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.START_STATE[0])
    await message.answer(
        "Бот для учёта финансов\n\n"
        "Добавить расход: /consumption\n"
        "Добавить доход: /gain\n"
        "Сегодняшняя статистика: /today\n"
        "За текущий месяц: /month\n"
        "Последние внесённые расходы: /expenses\n"
        "Последние внесённые доходы: /incomes\n"
        "Конверитровать валюту: /convert\n"
        )


@dp.message_handler(commands=['convert'], state=States.START_STATE)
async def convert_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.CONVERT_STATE[0])
    await message.answer("Введите сумму с указанием валюты [доллар/ов, рубль/ей/я, лари, тенге]")

@dp.message_handler(state=States.CONVERT_STATE)
async def convert(message: types.Message):
    currency = {
        'RUB_GEL': 0.045,
        'RUB_USD': 0.016,
        'RUB_KZT': 7.65,
        'GEL_USD': 0.37,
        'GEL_KZT': 170.63,
        'USD_KZT': 464.94,
    }

    possible_curr = ['рубль', 'рублей', 'рубля', 'доллар', 'долларов', 'тенге', 'лари', 'gel', 'rub', 'kzt', 'usd']

    input_curr = ''.join(filter(str.islower, message.text))
    input_value = float(re
                        .findall(r'\d*\.\d+|\d*\,\d+|\d+', message.text)[0]
                        .replace(',', '.'))
    print(input_value)

    if input_curr in possible_curr:
        if ('лари' or 'gel') in message.text:
            rub = input_value / currency['RUB_GEL']
            gel = input_value
            usd = input_value * currency['GEL_USD']
            kzt = input_value * currency['GEL_KZT']
        elif ('доллар' or 'usd') in message.text:
            rub = input_value / currency['RUB_USD']
            gel = input_value / currency['GEL_USD']
            usd = input_value
            kzt = input_value * currency['USD_KZT']
        elif ('рубл' or 'rub') in message.text:
            rub = input_value
            gel = input_value * currency['RUB_GEL']
            usd = input_value * currency['RUB_USD']
            kzt = input_value * currency['RUB_KZT']
        elif ('тенге' or 'kzt') in message.text:
            rub = input_value / currency['RUB_KZT']
            gel = input_value / currency['GEL_KZT']
            usd = input_value / currency['USD_KZT']
            kzt = input_value
        await message.reply(text=f"'{message.text}' по курсу равны:\n\n{rub:.2f} RUB\n{gel:.2f} GEL\n{usd:.2f} USD\n{kzt:.2f} KZT\n\nГлавное меню: /back", reply=False)
    else:
        await message.reply(text='Валюта не распознана, попробуй снова!\n\nГлавное меню: /back', reply=False)



@dp.message_handler(lambda message: message.text.startswith('/del'), state=States.START_STATE)
async def del_expense(message: types.Message):
    """Удаляет одну запись о расходе или доходе по их идентификатору"""
    if value == 1:
        row_id = int(message.text[4:])
        incomes.delete_income(row_id)
        answer_message = ("Позиция удалена\n\n"
                          "Просмотр последних доходов: /incomes\n"
                          "Главное меню: /back"
                          )
        await message.answer(answer_message)
    elif value == 2:
        row_id = int(message.text[4:])
        expenses.delete_expense(row_id)
        answer_message = ("Позиция удалена\n\n"
                          "Просмотр последних расходов: /expenses\n"
                          "Главное меню: /back"
                          )
        await message.answer(answer_message)
    else:
        answer_message = ("Я не понимаю удалять доход или расход :c\n\n"
                          "Просмотр последних доходов: /incomes\n"
                          "Просмотр последних расходов: /expenses\n"
                          "Главное меню: /back"
                          )
        await message.answer(answer_message)



@dp.message_handler(commands=['categories'], state=States.START_STATE)
async def categories_list(message: types.Message):
    """Отправляет список категорий расходов или доходов"""
    if not value == 0:
        categories = Categories().get_all_categories(value)
        answer_message = ("Категории:\n\n* " +\
                ("\n* ".join([(c.name).encode('cp1251').decode('utf-8')+' ('+", ".join(c.aliases).encode('cp1251').decode('utf-8')+')' for c in categories]))+"\n\nГлавное меню: /back")
    else:
        answer_message = ("Я не понимаю, какие категории вы хотите увидеть\n\n"
                          "Главное меню: /back")
    await message.answer(answer_message)


@dp.message_handler(commands=['today'], state=States.START_STATE)
async def today_statistics(message: types.Message):
    """Отправляет сегодняшнюю статистику"""
    answer_message = general.get_today_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['month'], state=States.START_STATE)
async def month_statistics(message: types.Message):
    """Отправляет статистику текущего месяца"""
    answer_message = general.get_month_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['expenses'], state=States.START_STATE)
async def list_expenses(message: types.Message):
    """Отправляет последние несколько записей о расходах"""
    last_expenses = expenses.last()
    global value
    value = 2
    if not last_expenses:
        await message.answer("Расходы ещё не заведены\n\n"+"Добавить расход: /consumption\n"+"Категории трат: /categories\n"+"Главное меню: /back")
        return
    last_expenses_rows = [
        f"{expense.amount} руб. на {expense.category_exp_name.encode('cp1251').decode('utf-8')} — нажми "
        f"/del{expense.id} для удаления"
        for expense in last_expenses]
    answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* "\
            .join(last_expenses_rows)+"\n\nДобавить расход: /consumption\n"+"Категории трат: /categories\n"+"Главное меню: /back"
    await message.answer(answer_message)


@dp.message_handler(commands=['incomes'], state=States.START_STATE)
async def list_incomes(message: types.Message):
    """Отправляет последние несколько записей о доходах"""
    last_incomes = incomes.last()
    global value
    value = 1
    if not last_incomes:
        await message.answer("Доходы ещё не заведены\n\n"+"Добавить доход: /gain\n"+"Категории трат: /categories\n"+"Главное меню: /back")
        return
    last_incomes_rows = [
        f"{income.amount} руб. на {income.category_inc_name.encode('cp1251').decode('utf-8')} — нажми "
        f"/del{income.id} для удаления"
        for income in last_incomes]
    answer_message = "Последние сохранённые доходы:\n\n* " + "\n\n* "\
            .join(last_incomes_rows)+"\n\nДобавить доход: /gain\n"+"Категории трат: /categories\n"+"Главное меню: /back"
    await message.answer(answer_message)


@dp.message_handler(commands=['gain'], state=States.START_STATE)
async def month_statistics(message: types.Message):
    """Добавляет новый доход"""
    global value
    value = 1
    answer_message = ("Введите доход. Например, '15000 зарплата' или '300 перевод'\n\n"
                      "Категории доходов: /categories\n"
                      "Главное меню: /back")
    await message.answer(answer_message)

@dp.message_handler(commands=['consumption'], state=States.START_STATE)
async def month_statistics(message: types.Message):
    """Добавляет новый расход"""
    global value
    value = 2
    answer_message = ("Введите расход. Например, '250 такси' или '100 перевод'\n\n"
                      "Категории расходов: /categories\n"
                      "Главное меню: /back")
    await message.answer(answer_message)

@dp.message_handler(state=States.START_STATE)
async def add_expense(message: types.Message):
    """Добавляет новый расход или доход в зависимости от значения value"""
    if value == 1:
        try:
            income = incomes.add_income(message.text)
        except exceptions.NotCorrectMessage as e:
            await message.answer(str(e))
            return
        answer_message = (
            f"Добавлены доходы {income.amount} руб на {income.category_inc_name.encode('cp1251').decode('utf-8')}.\n\n"
            f"{general.get_today_statistics()}")
    elif value == 2:
        try:
            expense = expenses.add_expense(message.text)
        except exceptions.NotCorrectMessage as e:
            await message.answer(str(e))
            return
        answer_message = (
            f"Добавлены траты {expense.amount} руб на {expense.category_exp_name.encode('cp1251').decode('utf-8')}.\n\n"
            f"{general.get_today_statistics()}")
    else:
        answer_message = ("Я не понимаю доход это или расход :c\n\n"
                          "Добавить расход: /consumption\n"
                          "Добавить доход: /gain\n"
                          "Главное меню: /back"
                          )
    await message.answer(answer_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
