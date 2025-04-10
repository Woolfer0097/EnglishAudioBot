# englishAudioBot/main.py

import logging
import tempfile
from io import BytesIO
import re

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode, ChatType
from aiogram.types import Message, FSInputFile
from aiogram.client.default import DefaultBotProperties

from englishAudioBot.textToSpeech import generate_audio_bytes
from englishAudioBot.extract import extract_data

import os
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

DISCUSSION_CHAT_ID = os.getenv("DISCUSSION_CHAT_ID")
ENGLISH_PATTERN = re.compile(r"^[A-Za-z0-9\s.,!?\"'’\-]+$")


@dp.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def handle_start_command(message: Message):
    await message.answer(
        "👋 Привет! Я бот для канала @Fluently_Channel для озвучки английского текста.\n"
        "Напиши мне текст на английском языке, и я отправлю тебе его озвучку!"
    )


@dp.message(F.chat.type == ChatType.PRIVATE, F.text)
async def handle_private_tts_request(message: Message):
    text = message.text.strip()

    if len(text) > 200:
        await message.answer("⚠️ Слишком длинный текст. Максимум — 200 символов")
        return

    if not ENGLISH_PATTERN.fullmatch(text):
        await message.answer("🚫 Пожалуйста, напишите текст на английском языке (без русского текста и смайликов)")
        return

    try:
        logging.info(f"📨 Пользователь запросил озвучку: {text}")
        audio_fp: BytesIO = await generate_audio_bytes(text)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(audio_fp.read())
            tmp_path = tmp_file.name

        voice_file = FSInputFile(tmp_path)

        await message.answer_voice(
            voice=voice_file,
            caption="🎧 Готово!"
        )

        os.remove(tmp_path)

    except Exception as e:
        logging.exception(f"❌ Ошибка при озвучке пользовательского текста: {e}")
        await message.answer("🚫 Ошибка при генерации озвучки.")


@dp.message(F.sender_chat)
async def handle_comment_entry_point(message: Message):
    if message.sender_chat.username != "fluently_channel":
        return

    text = message.text or message.caption
    if not text:
        logging.warning("Пустое сообщение без текста и подписи")
        return

    data = extract_data(text)

    english_items = (
        [("✏️ Предложение", s) for s in data["sentences"]] +
        [("💬 Фраза", p) for p in data["phrases"]] +
        [("🔤 Слово", w) for w in data["words"]]
    )

    if not english_items:
        logging.info("🛑 Нечего озвучивать.")
        return

    for label, item_text in english_items:
        try:
            logging.info(f"🎧 Генерация озвучки для: {item_text}")
            audio_fp = await generate_audio_bytes(item_text)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file.write(audio_fp.read())
                tmp_path = tmp_file.name

            voice_file = FSInputFile(tmp_path)

            await bot.send_voice(
                chat_id=message.chat.id,
                voice=voice_file,
                caption=f"{label}: <b>{item_text}</b>",
                reply_to_message_id=message.message_id
            )

            os.remove(tmp_path)
            await asyncio.sleep(1)

        except Exception as e:
            logging.exception(f"❌ Ошибка при озвучке «{item_text}»: {e}")


def main():
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
