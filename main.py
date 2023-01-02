from aiogram import Bot, Dispatcher, types, executor
import logging

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from dotenv import load_dotenv, find_dotenv

import utils
import os
from models import Team, User

storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())
bot = Bot(token='5300873799:AAHI2Tel_yCprOkXnEJm2LlGoQE9gl1LsAo')
dp = Dispatcher(bot, storage=storage)


class Info(StatesGroup):
    name = State()
    selection = State()
    text = State()
    team_create = State()
    team_search = State()


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['args'] = message.get_args()
    user_id = str(message.from_id)
    users = [user.telegram_id for user in User.select()]
    if user_id not in users:
        await Info.name.set()

        await message.answer(text='Добро пожаловать, путешественник, расскажи, как нам тебя величать?')
    else:
        await Info.text.set()
        await message.answer(text='Желаете присоединиться к уже существующей команде или создать свою?',
                             reply_markup=utils.create_markup('Создать', 'Присоединиться'))


@dp.message_handler(state=Info.name)
async def process_name(message: types.Message):
    await Info.text.set()
    await message.answer(f'Привет, {message.text} '
                         f'Желаете присоединиться к уже существующей команде или создать свою?',
                         reply_markup=utils.create_markup('Создать', 'Присоединиться'))

    utils.create_player(message.text, message.from_id)


@dp.message_handler(text="Создать", state=Info.text)
async def without_puree(message: types.Message):
    await Info.team_create.set()

    await message.reply('Введите название команды: ', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text == "Присоединиться", state=Info.text)
async def without_puree(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        if data['args'] is not None:
            await message.answer('У тебя есть ссылка, хочешь присоединиться по ней?',
                                 reply_markup=utils.create_markup('По ссылке', 'Ввести самому'))
            await Info.team_search.set()


@dp.message_handler(state=Info.team_create)
async def team_create(message: types.Message):
    team = utils.create_team(message.text)
    user = User.get(User.telegram_id == str(message.from_id))
    utils.add_player(user.telegram_id, team.title)
    await message.answer(f'Поздравляем, команда {message.text} создана\n'
                         f'вы - первый игрок вашей команды\n'
                         f'чтобы пригласить друзей отправьте им ссылку https://t.me/Aloxa_Antoxa_bot?start={team.ref_number}')


@dp.message_handler(lambda message: message.text == "По ссылке", state=Info.team_search)
async def foo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        team = Team.get(Team.ref_number == str(data['args']))
        user = User.get(User.telegram_id == str(message.from_id))
        utils.add_player(user.telegram_id, team.title)
        await message.answer(f'Поздравляем, вы присоединились к команде {team.title}', reply_markup=types.ReplyKeyboardRemove() )


@dp.message_handler(lambda message: message.text == "Ввести самому", state=Info.team_search)
async def team_search():
    await Info.text.set()


@dp.message_handler(state=Info.text)
async def bar(message: types.Message):
    teams = [team.title for team in Team.select()]
    if message.text in teams:
        team = Team.get(Team.title == message.text)
        user = User.get(User.telegram_id == str(message.from_id))
        utils.add_player(user.telegram_id, team.title)
        await message.answer(f'Поздравляем, вы присоединились к команде {team.title}')
    else:
        await message.answer('Увы, но такой команды нет')


@dp.message_handler(commands=["dice"])
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")


executor.start_polling(dp)
