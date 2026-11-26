"""Послуги та ціни."""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot import content
from bot.utils import show_main_menu

router = Router()


@router.callback_query(F.data == "services")
async def show_services(callback: CallbackQuery) -> None:
    """Показує перелік послуг із цінами."""
    await show_main_menu(callback, content.SERVICES_TEXT)
