""" Работа с расходами — их добавление, удаление, статистики"""
from typing import List, NamedTuple, Optional

import db
from categories import Categories
import general


class Expense(NamedTuple):
    """Структура добавленного в БД нового расхода"""
    id: Optional[int]
    amount: int
    category_exp_name: str


def add_expense(raw_message: str) -> Expense:
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    parsed_message = general._parse_message(raw_message)

    category_exp = Categories().get_category_exp(
        parsed_message.category_text.encode('utf-8').decode('cp1251'))
    inserted_row_id = db.insert("expense", {
        "amount": parsed_message.amount,
        "created": general._get_now_formatted(),
        "category_exp_codename": category_exp.codename,
        "raw_text": raw_message
    })
    return Expense(id=None,
                   amount=parsed_message.amount,
                   category_exp_name=category_exp.name)


def last() -> List[Expense]:
    """Возвращает последние несколько расходов"""
    cursor = db.get_cursor()
    cursor.execute(
        "select e.id, e.amount, c.name "
        "from expense e left join category_exp c "
        "on c.codename=e.category_exp_codename "
        "order by created desc limit 10")
    rows = cursor.fetchall()
    last_expenses = [Expense(id=row[0], amount=row[1], category_exp_name=row[2]) for row in rows]
    return last_expenses


def delete_expense(row_id: int) -> None:
    """Удаляет сообщение по его идентификатору"""
    db.delete("expense", row_id)







