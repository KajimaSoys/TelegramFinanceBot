"""Работа с категориями расходов"""
from typing import Dict, List, NamedTuple

import db


class Category(NamedTuple):
    """Структура категории"""
    codename: str
    name: str
    is_base_expense: bool
    aliases: List[str]


class Categories:
    def __init__(self):
        self._categories_expense, self._categories_income = self._load_categories()

    def _load_categories(self) -> List[Category]:
        """Возвращает справочник категорий из БД"""
        categories_expense = db.fetchall(
            "category_exp", "codename name is_base_expense aliases".split()
        )
        categories_expense = self._fill_aliases(categories_expense)

        categories_income = db.fetchall(
            "category_inc", "codename name is_base_expense aliases".split()
        )
        categories_income = self._fill_aliases(categories_income)
        return categories_expense, categories_income

    def _fill_aliases(self, categories: List[Dict]) -> List[Category]:
        """Заполняет по каждой категории aliases, то есть возможные
        названия этой категории, которые можем писать в тексте сообщения.
        Например, категория «кафе» может быть написана как cafe,
        ресторан и тд."""
        categories_result = []
        for index, category in enumerate(categories):
            aliases = category["aliases"].split(",")
            aliases = list(filter(None, map(str.strip, aliases)))
            aliases.append(category["codename"])
            aliases.append(category["name"])
            categories_result.append(Category(
                codename=category['codename'],
                name=category['name'],
                is_base_expense=category['is_base_expense'],
                aliases=aliases
            ))
        return categories_result

    def get_all_categories(self, value) -> List[Dict]:
        """Возвращает справочник категорий."""
        if value == 2:
            return self._categories_expense
        elif value == 1:
            return self._categories_income

    def get_category_exp(self, category_exp_name: str) -> Category:
        """Возвращает категорию по одному из её алиасов."""
        finded = None
        other_category_exp = None
        for category_exp in self._categories_expense:
            if category_exp.codename == "other":
                other_category_exp = category_exp
            for alias in category_exp.aliases:
                if category_exp_name in alias:
                    finded = category_exp
        if not finded:
            finded = other_category_exp
        return finded

    def get_category_inc(self, category_inc_name: str) -> Category:
        """Возвращает категорию по одному из её алиасов."""
        finded = None
        other_category_inc = None
        for category_inc in self._categories_income:
            if category_inc.codename == "other":
                other_category_inc = category_inc
            for alias in category_inc.aliases:
                if category_inc_name in alias:
                    finded = category_inc
        if not finded:
            finded = other_category_inc
        return finded
