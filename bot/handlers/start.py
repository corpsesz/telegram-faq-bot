"""Привітання та головне меню."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot import content
from bot.keyboards.main import main_menu_keyboard
from bot.utils import show_welcome

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Вітає користувача та показує головне меню."""
    await message.answer(
        content.WELCOME_TEXT,
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(lambda callback: callback.data == "menu")
async def show_menu(callback: CallbackQuery) -> None:
    """Повертає головне меню."""
    await show_welcome(callback, content.WELCOME_TEXT)
