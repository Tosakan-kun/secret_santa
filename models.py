from peewee import *

db = SqliteDatabase('santa.db')


class User(Model):
    name = CharField()
    telegram_id = CharField()

    class Meta:
        database = db


class Team(Model):
    title = CharField()
    ref_number = CharField()

    class Meta:
        database = db


class UserInTeam(Model):
    user = ForeignKeyField(User, backref='info')
    team = ForeignKeyField(Team, backref='info')
    casualty = ForeignKeyField(User, backref='info')

    class Meta:
        database = db


db.connect()
db.create_tables([User, Team, UserInTeam])
