import config
import datetime
from db_map import create_db
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
import sqlite3

if os.path.exists('dbase.db'):
    print("base is exist")
else: create_db()

class OrderReg(StatesGroup):
    st1 = State()
    st2 = State()
    st3 = State()
    st4 = State()

bot = Bot (token = config.token)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands = ['start'], state="*")
async def process_start_command(msg: types.Message):
    sqlite_connection = sqlite3.connect('dbase.db')
    cursor = sqlite_connection.cursor()
    sql_select_query = """select id from users where id = ?"""
    cursor.execute(sql_select_query, [msg.from_user.id])
    id_users = cursor.fetchall()
    print(id_users)
    if id_users == []:
        await msg.answer('Здравствуйте, для регистрации введите свои учетные данные')
        await msg.answer('Имя')
        await OrderReg.st1.set()
    else: await msg.answer('Вы уже зарегистрированы, наберите команду /help')


@dp.message_handler(state=OrderReg.st1, content_types=types.ContentTypes.TEXT)
async def echo_message(msg: types.Message, state: FSMContext):
    await OrderReg.st2.set()
    await bot.send_message(msg.from_user.id, 'Фамилия')
    await state.update_data(user_name=msg.text)

@dp.message_handler(state=OrderReg.st2, content_types=types.ContentTypes.TEXT)
async def echo_message(msg: types.Message, state: FSMContext):
    if  msg.text == 'Назад':
        await OrderReg.st1.set()
    await OrderReg.next()
    await bot.send_message(msg.from_user.id, 'Должность')
    await state.update_data(user_lastname=msg.text)


@dp.message_handler(state=OrderReg.st3, content_types=types.ContentTypes.TEXT)
async def echo_message(msg: types.Message, state: FSMContext):
    await OrderReg.next()
    await state.update_data(user_position=msg.text.lower())
    user_data = await state.get_data()
    await bot.send_message(msg.from_user.id, f"Данные верны? \n Имя: {user_data['user_name']} \n Фамилия: {user_data['user_lastname']} \n Должность: {user_data['user_position']}")


@dp.message_handler(state=OrderReg.st4, content_types=types.ContentTypes.TEXT)
async def echo_message(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if msg.text.lower() == 'да':
        await msg.reply("Ок")
        try:
            sqlite_connection = sqlite3.connect('dbase.db')
            cursor = sqlite_connection.cursor()
            sqlite_insert_with_param = """INSERT INTO users
                                  (id, name, lastname, position, registration_date, last_time)
                                  VALUES
                                  (?, ?, ?, ?, ?, ?);"""
            data_tuple = (msg.from_user.id, user_data['user_name'], user_data['user_lastname'], user_data['user_position'], 123582, 2586328)
            print(data_tuple)
            cursor.execute(sqlite_insert_with_param, data_tuple)
            sqlite_connection.commit()
            print("Запись успешно вставлена ​​в таблицу sqlitedb_developers ", cursor.rowcount)
            cursor.close()

        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
    else:
        await msg.reply("/start")
    await OrderReg.next()
    user_data = await state.get_data()
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp)
