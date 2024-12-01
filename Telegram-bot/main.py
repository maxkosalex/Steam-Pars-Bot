import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message


from config import TOKEN
from data import calculate_info

router = Router()


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Для того чтобы получить информацию по предметам за сегодняшнюю дату введите команду '/info'\nВалюта USD!")


@router.message(Command("info"))
async def start_handler(msg: Message):
    info = calculate_info()
    for mess in info:
        await msg.answer(f"{mess}")



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
