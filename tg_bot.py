from aiogram import Dispatcher, Bot
from aiogram.filters import Command, CommandStart, BaseFilter
from aiogram.types import Message, BotCommand
import config
import content
import db
from exchanges import main


# Bot init
bot: Bot = config.bot
dp: Dispatcher = Dispatcher()

# Data arrays with user_id`s: -> list[int]
admin_list = []
user_list = []

# My filters

class IsAdmin(BaseFilter):
    def __init__(self, admin_list: list[int]):
        self.admin_list = admin_list

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_list


class IsUser(BaseFilter):
    def __init__(self, user_list: list[int], admin_list: list[int]):
        self.admin_list = admin_list
        self.user_list = user_list

    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in self.user_list:
            return True
        elif message.from_user.id in admin_list:
            return True
        else:
            return False

# Menu button

async def menu_button(bot: Bot):
    menu_commands = [
        BotCommand(command='/cases', description='Cases'),
        BotCommand(command='/description', description='Bot description'),
    ]
    await bot.set_my_commands(menu_commands)

# Handlers

@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer(text='Hello, nice to meet u :)', parse_mode='HTML')
    await message.delete()


@dp.message(Command(commands=['cases']), IsUser(user_list, admin_list))
async def command_cases(message: Message):
    data = main()
    for i in data:
        await message.answer(text=str(i))
    await message.delete()


@dp.message(Command(commands=['description']))
async def command_descript(message: Message):
    if IsUser(user_list, admin_list):
        await message.answer(text=content.description_cryp, parse_mode='HTML')
    else:
        await message.answer(text='Go away...', parse_mode='HTML')

    await message.delete()
