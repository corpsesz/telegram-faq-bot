"""Часті питання, графік роботи, адреса та контакти."""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot import content
from bot.utils import show_main_menu

router = Router()


@router.callback_query(F.data == "faq")
async def show_faq(callback: CallbackQuery) -> None:
    """Показує відповіді на часті питання."""
    await show_main_menu(callback, content.FAQ_TEXT)


@router.callback_query(F.data == "hours")
async def show_hours(callback: CallbackQuery) -> None:
    """Показує графік роботи студії."""
    await show_main_menu(callback, content.WORKING_HOURS)


@router.callback_query(F.data == "address")
async def show_address(callback: CallbackQuery) -> None:
    """Показує адресу студії."""
    await show_main_menu(callback, content.ADDRESS)


@router.callback_query(F.data == "contact")
async def show_contact(callback: CallbackQuery) -> None:
    """Показує контакти студії."""
    await show_main_menu(callback, content.CONTACT_TEXT)
