import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN, ADMINS
import os

USERS_FILE = "users.json"
LOG_FILE = "logs.txt"
PRIZE_FILE = "prize.jpeg"

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def add_user(user_id: str, username: str | None):
    users = load_users()
    users[user_id] = username
    save_users(users)

def log_reward(user_id, username):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"Пользователь {username or 'без ника'} с ID {user_id} получил вознаграждение.\n")

@dp.message(Command("start"))
async def handle_start(message: types.Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or None
    users = load_users()

    if user_id in users:
        await message.answer("Вы уже получили приз 🙂.")
    else:
        add_user(user_id, username)
        log_reward(user_id, username)
        prize = FSInputFile(PRIZE_FILE)
        await message.answer_photo(prize, caption="Спасибо, что прошли опрос! Это очень важно для нас.")

@dp.message(Command("show_logs"))
async def handle_show_logs(message: types.Message):
    if message.from_user.id in ADMINS:
        if os.path.exists(LOG_FILE):
            doc = FSInputFile(LOG_FILE)
            await message.answer_document(doc, caption="Логи выдачи призов:")
        else:
            await message.answer("Логов пока нет.")
    else:
        await message.answer("У вас нет доступа к этой команде.")

@dp.message(Command("show_users"))
async def handle_show_users(message: types.Message):
    if message.from_user.id in ADMINS:
        if os.path.exists(USERS_FILE):
            doc = FSInputFile(USERS_FILE)
            await message.answer_document(doc, caption="Список пользователей:")
        else:
            await message.answer("Пользователи пока не зарегистрированы.")
    else:
        await message.answer("У вас нет доступа к этой команде.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("✅ Бот запущен!")
    asyncio.run(main())