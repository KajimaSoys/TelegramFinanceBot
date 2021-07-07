""" Работа с доходами — их добавление, удаление, статистики"""
from typing import List, NamedTuple, Optional

import db
from categories import Categories
import general


class Income(NamedTuple):
    """Структура добавленного в БД нового дохода"""
    id: Optional[int]
    amount: int
    category_inc_name: str


def add_income(raw_message: str) -> Income:
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    parsed_message = general._parse_message(raw_message)

    category_inc = Categories().get_category_inc(
        parsed_message.category_text.encode('utf-8').decode('cp1251'))
    inserted_row_id = db.insert("income", {
        "amount": parsed_message.amount,
        "created": general._get_now_formatted(),
        "category_inc_codename": category_inc.codename,
        "raw_text": raw_message
    })
    return Income(id=None,
                   amount=parsed_message.amount,
                   category_inc_name=category_inc.name)


def last() -> List[Income]:
    """Возвращает последние несколько доходов"""
    cursor = db.get_cursor()
    cursor.execute(
        "select e.id, e.amount, c.name "
        "from income e left join category_inc c "
        "on c.codename=e.category_inc_codename "
        "order by created desc limit 10")
    rows = cursor.fetchall()
    last_incomes = [Income(id=row[0], amount=row[1], category_inc_name=row[2]) for row in rows]
    return last_incomes


def delete_income(row_id: int) -> None:
    """Удаляет сообщение по его идентификатору"""
    db.delete("income", row_id)