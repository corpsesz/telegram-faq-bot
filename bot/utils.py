"""Допоміжні функції для обробників."""

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from bot.keyboards.main import back_keyboard, main_menu_keyboard


async def safe_edit(
    callback: CallbackQuery,
    text: str,
    reply_markup=None,
) -> None:
    """Редагує повідомлення, ігноруючи помилку «message is not modified».

    Telegram повертає помилку, якщо текст і клавіатура не змінилися —
    наприклад, при повторному натисканні на ту саму кнопку.
    """
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise
    await callback.answer()


async def show_main_menu(callback: CallbackQuery, text: str) -> None:
    """Показує текст розділу з кнопкою повернення до меню."""
    await safe_edit(callback, text, reply_markup=back_keyboard())


async def show_welcome(callback: CallbackQuery, text: str) -> None:
    """Показує головне меню."""
    await safe_edit(callback, text, reply_markup=main_menu_keyboard())
