from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from models import UserInTeam, Team, User
from aiogram import types
import random
import string


def create_markup(*items):
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def add_player(player, team):
    UserInTeam(user=player, team=team, casualty=player).save()


def create_team(title):
    ref_number = create_ref_number()
    team = Team(title=title, ref_number=ref_number)
    team.save()
    return team


def create_ref_number():
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, 8))
    return rand_string


def create_player(name, telegram_id):
    user = User.create(name=name, telegram_id=telegram_id)
    user.save()
    return user



