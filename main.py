#from dotenv import load_dotenv
import asyncio
import logging
from aiogram import Bot, Dispatcher  
import config  
from handlers import router

async def main():
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Инициализация бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрируем роутер с обработчиками
    dp.include_router(router)
    
    # Запуск пуллинга
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())