"""Точка входу: python -m bot"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.config import settings
from bot.handlers import faq, services, start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def build_dispatcher() -> Dispatcher:
    """Збирає роутери в порядку обробки."""
    dispatcher = Dispatcher()
    dispatcher.include_router(start.router)
    dispatcher.include_router(services.router)
    dispatcher.include_router(faq.router)
    return dispatcher


def build_bot(token: str | None = None) -> Bot:
    """Створює бота з HTML-розміткою за замовчуванням.

    Без DefaultBotProperties(parse_mode="HTML") Telegram отримує текст
    як є і показує користувачеві теги <b> буквально.
    """
    return Bot(
        token=token or settings.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )


async def main() -> None:
    """Запускає бота в режимі long polling."""
    bot = build_bot()
    dispatcher = build_dispatcher()

    logger.info("Бот %s запущено", settings.bot_name)
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
