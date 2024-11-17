from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import router

# Инициализация бота и диспетчера
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# Регистрация роутеров
dp.include_router(router)

# Функция, выполняемая при запуске
async def on_startup():
    print("Бот успешно запущен!")

# Запуск бота
if __name__ == "__main__":
    dp.startup.register(on_startup)
    dp.run_polling(bot, skip_updates=True)
