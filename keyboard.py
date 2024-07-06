from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

class Keyboard:
    def __init__(self):
        self.user_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="История"),
                KeyboardButton(text="Избранное")
            ],
            [
                KeyboardButton(text="Задать вопрос"),
                KeyboardButton(text="Поиск по теме")
            ],
            [
                KeyboardButton(text="Загрузить новое видео")
            ]

        ]
        )

        self.admin_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="История"),
                KeyboardButton(text="Избранное")
            ],
            [
                KeyboardButton(text="Задать вопрос"),
                KeyboardButton(text="Поиск по теме")
            ],
            [
                KeyboardButton(text="Загрузить новое видео"),
                KeyboardButton(text="Управление")
            ]

        ]
        )

        self.admin_panel = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Новые пользователи"),
                KeyboardButton(text="Активность")
            ],
            [
                KeyboardButton(text="Добавить токены"),
                KeyboardButton(text="Назад")
            ]
        ]
        )

        self.neir_quest_kb = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="вопрос для модель1"),
                    KeyboardButton(text="вопрос для модель2")
                ]
            ]
        )

        self.neir_theme_kb = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="тема для модель1"),
                    KeyboardButton(text="тема для модель2")
                ]
            ]
        )
        self.model_kb = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="llama3"),
                    KeyboardButton(text="ilyagusev/saiga_llama3")
                ]
            ]
        )