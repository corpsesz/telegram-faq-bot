"""Перевірка обробників без звернення до Telegram API (mock-сесія)."""

import asyncio
import datetime as dt
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiogram.client.default import Default
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import AnswerCallbackQuery, EditMessageText, SendMessage
from aiogram.types import CallbackQuery, Chat, Message, Update, User

from bot import content
from bot.__main__ import build_bot, build_dispatcher


class MockSession:
    """Імітація Telegram API: запам'ятовує виклики, повторні правки -> 400.

    Так само, як справжня сесія aiogram, підставляє parse_mode з
    bot.default у тіло запиту — так перевіряється, що HTML справді
    доїде до Telegram.
    """

    def __init__(self):
        self.calls = []
        self.last_edit = None
        self.sent_parse_modes = []

    async def close(self):
        pass

    def _resolve_parse_mode(self, bot, method):
        """Повторює логіку aiogram: Default -> bot.default[parse_mode]."""
        value = method.parse_mode
        if isinstance(value, Default):
            value = bot.default[value.name]
        return value

    async def __call__(self, bot, method, timeout=None):
        self.calls.append(method)
        if isinstance(method, (SendMessage, EditMessageText)):
            self.sent_parse_modes.append(self._resolve_parse_mode(bot, method))
        if isinstance(method, SendMessage):
            return SendMessage(
                message_id=100,
                date=dt.datetime.now(),
                chat=Chat(id=1, type="private"),
                text=method.text,
            )
        if isinstance(method, EditMessageText):
            signature = (method.text, method.reply_markup)
            if signature == self.last_edit:
                raise TelegramBadRequest(
                    method="editMessageText",
                    message="Bad Request: message is not modified",
                )
            self.last_edit = signature
            return True
        if isinstance(method, AnswerCallbackQuery):
            return True
        raise AssertionError(f"Неочікуваний метод: {method}")


def make_callback(data, user, chat):
    return CallbackQuery(
        id=data,
        from_user=user,
        chat_instance="1",
        data=data,
        message=Message(
            message_id=2,
            date=dt.datetime.now(),
            chat=chat,
            from_user=user,
            text="menu",
        ),
    )


class TagCheck(HTMLParser):
    """Перевіряє, що HTML-теги коректно відкриті й закриті."""

    ALLOWED = {"b", "i", "u", "s", "code", "pre", "a"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.ALLOWED:
            self.errors.append(f"непідтримуваний тег <{tag}>")
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack:
            self.errors.append(f"зайвий </{tag}>")
        elif self.stack[-1] != tag:
            self.errors.append(f"</{tag}> закриває <{self.stack[-1]}>")
            self.stack.pop()
        else:
            self.stack.pop()

    def run(self, text):
        self.feed(text)
        self.close()
        errors = list(self.errors)
        if self.stack:
            errors.append(f"не закритий <{self.stack[-1]}>")
        return errors


def check_content():
    """Перевіряє контент: ціни в грн, HTML-теги, відсутність рублів."""
    print("--- Контент ---")

    texts = {
        "WELCOME": content.WELCOME_TEXT,
        "SERVICES": content.SERVICES_TEXT,
        "HOURS": content.WORKING_HOURS,
        "ADDRESS": content.ADDRESS,
        "FAQ": content.FAQ_TEXT,
        "CONTACT": content.CONTACT_TEXT,
    }

    for name, text in texts.items():
        errors = TagCheck().run(text)
        assert not errors, f"{name}: помилки HTML — {errors}"
    print(f"[OK] HTML-теги коректні у {len(texts)} текстах")

    for service in content.SERVICES:
        assert "грн" in service.price, f"ціна без грн: {service.price}"
        assert "₽" not in service.price, f"залишилися рублі: {service.price}"
    print(f"[OK] Усі {len(content.SERVICES)} цін у гривнях, рублів немає")

    all_text = "\n".join(texts.values())
    assert "₽" not in all_text, "у текстах залишилися рубли"
    assert " руб" not in all_text.lower(), "у текстах залишилося слово 'руб'"
    print("[OK] Рублів у всьому контенті немає")

    assert re.search(r"\d\s?грн", content.FAQ_TEXT), "у FAQ немає цін у грн"
    print("[OK] У FAQ ціни у гривнях")


async def main():
    bot = build_bot(token="123456:TEST")
    session = MockSession()
    bot.session = session

    dp = build_dispatcher()
    chat = Chat(id=1, type="private")
    user = User(id=1, is_bot=False, first_name="Test")

    msg = Message(
        message_id=1,
        date=dt.datetime.now(),
        chat=chat,
        from_user=user,
        text="/start",
    )
    await dp.feed_update(bot, Update(update_id=1, message=msg))
    assert isinstance(session.calls[-1], SendMessage)
    assert session.calls[-1].reply_markup is not None
    print("[OK] /start          ->", repr(session.calls[-1].text[:40]))

    # Кожна кнопка двічі: другий раз — «message is not modified».
    for data in ("services", "faq", "hours", "address", "contact", "menu"):
        for attempt in (1, 2):
            cb = make_callback(data, user, chat)
            before = len(session.calls)
            await dp.feed_update(
                bot, Update(update_id=len(session.calls) + 1, callback_query=cb)
            )
            new_calls = session.calls[before:]
            edits = [c for c in new_calls if isinstance(c, EditMessageText)]
            answers = [c for c in new_calls if isinstance(c, AnswerCallbackQuery)]
            assert edits, f"{data} (спроба {attempt}): немає editMessageText"
            assert answers, f"{data} (спроба {attempt}): немає answerCallbackQuery"
            assert edits[0].reply_markup is not None, f"{data}: немає клавіатури"
        print(f"[OK] {data:8s} x2 -> {edits[0].text[:38]!r}")

    # Кожен запит до Telegram має йти з parse_mode="HTML",
    # інакше теги <b> покажуться буквально.
    assert session.sent_parse_modes, "не зафіксовано жодного повідомлення"
    wrong = [m for m in session.sent_parse_modes if m != "HTML"]
    assert not wrong, f"повідомлення без HTML parse_mode: {wrong}"
    print(
        f"\n[OK] parse_mode=\"HTML\" у всіх {len(session.sent_parse_modes)} "
        "повідомленнях — теги <b> відмалюються, а не покажуться текстом."
    )

    print("\nУсі обробники відпрацювали, повторні натискання не падають.")


check_content()
asyncio.run(main())
