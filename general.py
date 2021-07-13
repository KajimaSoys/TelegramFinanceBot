import datetime
import re
from typing import List, NamedTuple, Optional

import pytz

import db
import exceptions

class Message(NamedTuple):
    """Структура распаршенного сообщения о новом доходе или расходе"""
    amount: int
    category_text: str

def _parse_message(raw_message: str) -> Message:
    """Парсит текст пришедшего сообщения"""
    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessage(
            "Не могу понять сообщение. Напишите сообщение в формате, "
            "например:\n1500 метро")

    amount = regexp_result.group(1).replace(" ", "")
    category_text = regexp_result.group(2).strip().lower()
    return Message(amount=amount, category_text=category_text)

def get_today_statistics() -> str:
    """Возвращает строкой статистику расходов за сегодня"""
    #достаем расходы за день
    cursor = db.get_cursor()
    cursor.execute("select sum(amount)"
                   "from expense where date(created)=date('now', 'localtime')")
    result = cursor.fetchone()
    if not result[0]:
        expence_return = ("Сегодня ещё нет расходов\n\n")
    else:
        all_today_expenses = result[0]
        cursor.execute("select sum(amount) "
                       "from expense where date(created)=date('now', 'localtime') "
                       "and category_exp_codename in (select codename "
                       "from category_exp where is_base_expense=true)")
        result = cursor.fetchone()
        base_today_expenses = result[0] if result[0] else 0
        cursor = db.get_cursor()
        expence_return = (f"Расходы сегодня:\n"
                          f"всего — {all_today_expenses} руб.\n"
                          f"базовые — {base_today_expenses} руб. из {_get_budget_limit()} руб.\n\n")
    #достаем доходы за день
    cursor.execute("select sum(amount)"
                   "from income where date(created)=date('now', 'localtime')")
    result = cursor.fetchone()
    if not result[0]:
        income_return = ("Сегодня ещё нет доходов\n\n")
    else:
        all_today_incomes = result[0]
        income_return = (f"Доходы сегодня:\n"
                         f"всего - {all_today_incomes}руб. \n\n")
    return (expence_return + income_return +
            "Статистика за месяц: /month\n"
            "Главное меню: /back\n")

def get_month_statistics() -> str:
    """Возвращает строкой статистику расходов за текущий месяц"""
    #достаем расходы за месяц
    now = _get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created) >= '{first_day_of_month}'")
    result = cursor.fetchone()
    if not result[0]:
        expence_return = "В этом месяце ещё нет расходов\n\n"
        exp = 0
    else:
        all_today_expenses = result[0]
        cursor.execute(f"select sum(amount) "
                       f"from expense where date(created) >= '{first_day_of_month}' "
                       f"and category_exp_codename in (select codename "
                       f"from category_exp where is_base_expense=true)")
        result = cursor.fetchone()
        base_today_expenses = result[0] if result[0] else 0
        expence_return = (f"Расходы в текущем месяце:\n"
                f"всего — {all_today_expenses} руб.\n"
                f"базовые — {base_today_expenses} руб. из "
                f"{now.day * _get_budget_limit()} руб.\n\n")
        exp = int(all_today_expenses)
    # достаем доходы за месяц
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) "
                   f"from income where date(created) >= '{first_day_of_month}'")
    result = cursor.fetchone()
    if not result[0]:
        income_return = "В этом месяце ещё нет доходов\n\n"
        inc = 0
    else:
        all_today_incomes = result[0]
        income_return = (f"Доходы в текущем месяце:\n"
                          f"всего — {all_today_incomes} руб.\n\n")
        inc = int(all_today_incomes)
    diff = inc - exp
    return (expence_return + income_return +
            f"Общая прибыль за месяц: {diff} руб.\n\n" 
            "Статистика за день: /today\n"
            "Главное меню: /back\n")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now

def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")

def _get_budget_limit() -> int:
    """Возвращает дневной лимит трат для основных базовых трат"""
    return db.fetchall("budget", ["daily_limit"])[0]["daily_limit"]