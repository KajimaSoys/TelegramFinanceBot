from aiogram.utils.helper import Helper, HelperMode, ListItem

class States(Helper):
    mode = HelperMode.snake_case
    START_STATE = ListItem()
    CONVERT_STATE = ListItem()