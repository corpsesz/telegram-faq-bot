"""Клавиатура главного меню."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import content


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-меню з розділами бота."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💰 Послуги та ціни",
                    callback_data="services",
                ),
                InlineKeyboardButton(
                    text="❓ Часті питання",
                    callback_data="faq",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🕘 Графік роботи",
                    callback_data="hours",
                ),
                InlineKeyboardButton(
                    text="📍 Адреса",
                    callback_data="address",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✉️ Зв'язатися",
                    callback_data="contact",
                ),
            ],
        ]
    )


def back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка повернення до головного меню."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Головне меню",
                    callback_data="menu",
                )
            ],
        ]
    )
