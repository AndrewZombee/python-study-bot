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

class OrderMtr(StatesGroup):
    st1 = State()
    st2 = State()
    st3 = State()
    st4 = State()
    st5 = State()

bot = Bot (token = config.token)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands = ['start'], state="*")
async def process_start_command(msg: types.Message):
    sqlite_connection = sqlite3.connect('dbase.db')
    cursor = sqlite_connection.cursor()
    sql_select_query = """select id from users where id = ?"""
    cursor.execute(sql_select_query, [msg.from_user.id])
    id_users = cursor.fetchall()
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
    await OrderReg.next()
    await bot.send_message(msg.from_user.id, 'Должность')
    await state.update_data(user_lastname=msg.text)


@dp.message_handler(state=OrderReg.st3, content_types=types.ContentTypes.TEXT)
async def echo_message(msg: types.Message, state: FSMContext):
    await OrderReg.next()
    await state.update_data(user_position=msg.text.lower())
    user_data = await state.get_data()
    await bot.send_message(msg.from_user.id, f"Данные верны? \n Имя: {user_data['user_name']} \n Фамилия: {user_data['user_lastname']} \n Должность: {user_data['user_position']} \n Если все верно наберите 'ДА' если нет 'Нет' и начните регистрацию занова")


@dp.message_handler(state=OrderReg.st4, content_types=types.ContentTypes.TEXT)
async def echo_message(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if msg.text.lower() == 'да':
        await msg.reply("Ок")
        await bot.send_message(msg.from_user.id, 'Регистрация прошла успешно, инструкцию по использованию бота, можно посмотреть по команде /help')
        try:
            sqlite_connection = sqlite3.connect('dbase.db')
            cursor = sqlite_connection.cursor()
            sqlite_insert_with_param = """INSERT INTO users
                                  (id, name, lastname, position, registration_date, last_time)
                                  VALUES
                                  (?, ?, ?, ?, ?, ?);"""
            data_tuple = (msg.from_user.id, user_data['user_name'], user_data['user_lastname'], user_data['user_position'], msg.date, 2586328)
            print(data_tuple)
            cursor.execute(sqlite_insert_with_param, data_tuple)
            sqlite_connection.commit()
            print("Запись успешно вставлена ​​в таблицу users ", cursor.rowcount)
            cursor.close()

        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
    else:
        await msg.reply("/start")
    await OrderReg.next()
    user_data = await state.get_data()
    await state.finish()

@dp.message_handler(commands = ['help'], state="*")
async def help_spravka(msg: types.Message):
   await bot.send_message(msg.from_user.id, config.help_msg)

@dp.message_handler(commands = ['order'], state="*")
async def order_mtr(msg: types.Message):
    await msg.answer('Что требуется заказать?')
    await msg.answer('Наименование:')
    await OrderMtr.st1.set()

@dp.message_handler(state=OrderMtr.st1, content_types=types.ContentTypes.TEXT)
async def echo_message(msg: types.Message, state: FSMContext):
    await OrderMtr.st2.set()
    await bot.send_message(msg.from_user.id, 'Сколько?')
    await state.update_data(name_mtr=msg.text)

@dp.message_handler(state=OrderMtr.st2, content_types=types.ContentTypes.TEXT)
async def echo_message(msg: types.Message, state: FSMContext):
    await OrderMtr.st3.set()
    await bot.send_message(msg.from_user.id, 'Когда?')
    await state.update_data(count_mtr=msg.text)

@dp.message_handler(state=OrderMtr.st3, content_types=types.ContentTypes.TEXT)
async def echo_message(msg: types.Message, state: FSMContext):
    await OrderMtr.st4.set()
    await bot.send_message(msg.from_user.id, 'Комментарий:')
    await state.update_data(when_mtr=msg.text)

@dp.message_handler(state=OrderMtr.st4, content_types=types.ContentTypes.TEXT)
async def echo_message(msg: types.Message, state: FSMContext):
    await OrderMtr.st5.set()
    await state.update_data(user_comment=msg.text.lower())
    user_data = await state.get_data()
    await bot.send_message(msg.from_user.id,f"Данные верны?\n Наименование: {user_data['name_mtr']}\n Сколько: {user_data['count_mtr']}\n Когда: {user_data['when_mtr']}\n Комментарий: {user_data['user_comment']}\n Если все верно наберите 'ДА' если нет 'Нет' и начните заказ занова")

@dp.message_handler(state=OrderMtr.st5, content_types=types.ContentTypes.TEXT)
async def echo_message(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if msg.text.lower() == 'да':
        await msg.reply("Ок")
        await bot.send_message(msg.from_user.id,'Заказ зарегистрирован, Ваши заказы можно посмотреть по команде "Мои заказы"')
        try:
            sqlite_connection = sqlite3.connect('dbase.db')
            cursor = sqlite_connection.cursor()
            sqlite_insert_with_param = """INSERT INTO work_table
                                          (id_user, date_event, name_object, Count_o, where_need, comments)
                                          VALUES
                                          (?, ?, ?, ?, ?, ?);"""
            data_tuple = (msg.from_user.id, msg.date, user_data['name_mtr'], user_data['count_mtr'], user_data['when_mtr'], user_data['user_comment'])
            print(data_tuple)
            cursor.execute(sqlite_insert_with_param, data_tuple)
            sqlite_connection.commit()
            print("Запись успешно вставлена ​в таблицу work_table ", cursor.rowcount)
            cursor.close()

        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
    else:
        await msg.reply("/start")
    user_data = await state.get_data()
    await state.finish()

@dp.message_handler()
async def info_other(msg: types.Message):
    if msg.text.lower() == 'мои данные':
        sqlite_connection = sqlite3.connect('dbase.db')
        cursor = sqlite_connection.cursor()
        sql_select_query = """select * from users where id = ?"""
        cursor.execute(sql_select_query, [msg.from_user.id])
        user_data = cursor.fetchall()
        await msg.reply(f"Имя: {user_data[0][1]}\nФамилия: {user_data[0][2]}\nДолжность: {user_data[0][3]}\nДата регистрации: {user_data[0][4]}")

    if msg.text.lower() == 'мои заказы':
        sqlite_connection = sqlite3.connect('dbase.db')
        cursor = sqlite_connection.cursor()
        sql_select_query = """select * from work_table where id_user = ?"""
        cursor.execute(sql_select_query, [msg.from_user.id])
        user_data = cursor.fetchall()
        if not user_data == []:
            print(len(user_data))
            cz = (len(user_data))
            for z in range(cz):
                await msg.reply(f"Дата: {user_data[z][1]}\nЧто надо: {user_data[z][3]}\nКогда надо: {user_data[z][4]}\nСколько надо: {user_data[z][5]}\nКомментарий: {user_data[z][7]}")
        else: await msg.reply('У вас нет заказов')




if __name__ == '__main__':
    executor.start_polling(dp)
