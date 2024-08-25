# -*- coding: cp1251 -*-
import logging

import os
import shutil

import psycopg2
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, timedelta
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import plotly.figure_factory as ff #Отрисовка таблицы
import pandas #Анализ данных
import kaleido #Генерация изображений (движок)

#Создание директорий
try:
    os.mkdir("materials")
except:
    pass
try:
    os.mkdir("homeworks")
except:
    pass
try:
    os.mkdir("homeworks_uploaded")
except:
    pass

#Токен бота
API_TOKEN = 'BOT_TOKEN'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
registration = True

#Подключение к базе данных
def db_connect():
    host = "HOST_IP"
    dbname = "DB_NAME"
    user = "DB_USER"
    password = "DB_PASSWORD"
    try:
        connection = psycopg2.connect(host=host,
                                dbname=dbname,
                                user=user,
                                password=password,
                                sslmode="require")
        connection.autocommit = True
        print(f"Connected to DB \"{dbname}\"")
        return connection
    except:
        print(f"Unable to connect to DB \"{dbname}\"")


try:
    conn = db_connect()
    db = conn.cursor()
except:
    pass


#Получение имени пользователя
def select_user_name(tgid=None, tgname=None):
    try:
        if tgid == None:
            db.execute(f"SELECT * FROM waspusers WHERE telegramname = '{tgname}';")
        else:
            db.execute(f"SELECT * FROM waspusers WHERE telegramid = {tgid};")
        user = db.fetchone()
        fullname = user[4] + ' ' + user[3]
        return fullname
    except:
        print(f"Unable to select user's name")


#Получение имени пользователя
def select_users_id():
    try:
        db.execute(f"SELECT telegramid FROM waspusers;")
        users = db.fetchall()
        return users
    except:
        print(f"Unable to select users' ids")


#Получение имени администратора
def select_admin_name(tgid=None, tgname=None):
    try:
        if tgid == None:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramname = '{tgname}';")
        else:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramid = {tgid};")
        admin = db.fetchone()
        fullname = admin[3] + ' ' + admin[2]
        return fullname
    except:
        print(f"Unable to select admin's name")


#Получение telegram id администратора
def select_admins_id():
    try:
        db.execute(f"SELECT telegramid FROM waspadmins;")
        admins = db.fetchall()
        return admins
    except:
        print(f"Unable to select admins' ids")


#Проверка нахождения в участниках
def is_user(tgid=None, tgname=None):
    try:
        if tgid == None:
            db.execute(f"SELECT * FROM waspusers WHERE telegramname = '{tgname}';")
        else:
            db.execute(f"SELECT * FROM waspusers WHERE telegramid = {tgid};")
        users = db.fetchall()
        if users:
            return True
        return False
    except:
        print(f"Unable to check if user is registered")


#Проверка нахождения в администраторах
def is_admin(tgid=None, tgname=None):
    try:
        if tgid == None:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramname = '{tgname}';")
        else:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramid = {tgid};")
        users = db.fetchall()
        if users:
            return True
        return False
    except:
        print(f"Unable to check if user is admin")


#Проверка нахождения в исключённых участниках
def is_removed(tgid=None, tgname=None):
    try:
        if tgid == None:
            db.execute(f"SELECT * FROM removedusers WHERE telegramname = '{tgname}';")
        else:
            db.execute(f"SELECT * FROM removedusers WHERE telegramid = {tgid};")
        users = db.fetchall()
        if users:
            return True
    except:
        print(f"Unable to check if user is removed")
    return False


#Проверка, отправляет ли ученик дз
def sending_homework(tgid=None, tgname=None):
    try:
        if tgid == None:
            db.execute(f"SELECT * FROM waspusers WHERE telegramname = {tgname} AND sending_homework = TRUE;")
        else:
            db.execute(f"SELECT * FROM waspusers WHERE telegramid = {tgid} AND sending_homework = TRUE;")
        users = db.fetchall()
        if users:
            return True
    except:
        print(f"Unable to check if user is sending homework")
    return False


#Проверка, создаёт ли администратор материал
def creating_material(tgid=None, tgname=None):
    try:
        if tgid == None:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramname = {tgname} AND creating_material = TRUE;")
        else:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramid = {tgid} AND creating_material = TRUE;")
        users = db.fetchall()
        if users:
            return True
    except:
        print(f"Unable to check if user is creating material")
    return False


#Проверка, создаёт ли администратор дз
def creating_homework(tgid=None, tgname=None):
    try:
        if tgid == None:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramname = {tgname} AND creating_homework = TRUE;")
        else:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramid = {tgid} AND creating_homework = TRUE;")
        users = db.fetchall()
        if users:
            return True
    except:
        print(f"Unable to check if user is creating homework")
    return False


#Проверка, ищет ли администратор ученика
def finding_user(tgid=None, tgname=None):
    try:
        if tgid == None:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramname = {tgname} AND finding_user = TRUE;")
        else:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramid = {tgid} AND finding_user = TRUE;")
        users = db.fetchall()
        if users:
            return True
    except:
        print(f"Unable to check if user is finding student")
    return False


#Проверка, удаляет ли администратор участника
def removing_user(tgid=None, tgname=None):
    try:
        if tgid == None:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramname = {tgname} AND removing_user = TRUE;")
        else:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramid = {tgid} AND removing_user = TRUE;")
        users = db.fetchall()
        if users:
            return True
    except:
        print(f"Unable to check if user is removing student")
    return False


#Проверка, отправляет ли администратор объявление
def announcing(tgid=None, tgname=None):
    try:
        if tgid == None:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramname = {tgname} AND announcing = TRUE;")
        else:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramid = {tgid} AND announcing = TRUE;")
        users = db.fetchall()
        if users:
            return True
    except:
        print(f"Unable to check if user is announcing")
    return False


#Проверка, добавляет ли администратор организатора
def setting_admin(tgid=None, tgname=None):
    try:
        if tgid == None:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramname = {tgname} AND setting_admin = TRUE;")
        else:
            db.execute(f"SELECT * FROM waspadmins WHERE telegramid = {tgid} AND setting_admin = TRUE;")
        users = db.fetchall()
        if users:
            return True
    except:
        print(f"Unable to check if user is setting admin")
    return False


#Регистрация нового пользователя
def tgreg_user(tgid, tgname, name, surname, lastname):
    try:
        db.execute(f"SELECT * FROM waspusers WHERE telegramid = {tgid};")
        users = db.fetchall()
        if not users:
            db.execute(f"INSERT INTO waspusers(telegramid, telegramname, name, surname, lastname, stingers) VALUES({tgid}, '{tgname}', '{name}', '{surname}', '{lastname}', 0);")
    except:
        print(f"Unable to register a new user")


#Регистрация нового администратора
def tgreg_admin(tgid, tgname, name, surname, lastname):
    try:
        db.execute(f"SELECT * FROM waspadmins WHERE telegramid = {tgid};")
        users = db.fetchall()
        if not users:
            db.execute(f"INSERT INTO waspadmins(telegramid, telegramname, name, surname, lastname) VALUES({tgid}, '{tgname}', '{name}', '{surname}', '{lastname}');")
    except:
        print(f"Unable to register a new admin")


#Добавить ученику стингеры
def add_stingers(tgid=None, tgname=None, stingers=0):
    try:
        if tgid == None:
            db.execute(f"SELECT stingers FROM waspusers WHERE telegramname = '{tgname}';")
            stingers_amount = db.fetchone()[0]
            db.execute(f"UPDATE waspusers SET stingers = {stingers_amount+stingers} WHERE telegramname = '{tgname}';")
        else:
            db.execute(f"SELECT stingers FROM waspusers WHERE telegramid = '{tgid}';")
            stingers_amount = db.fetchone()[0]
            db.execute(f"UPDATE waspusers SET stingers = {stingers_amount+stingers} WHERE telegramid = '{tgid}';")
    except:
        print(f"Unable to add stingers to user")


#Домашняя страница
async def homepage(message: types.Message):
    global registration
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if is_admin(tgid=message.from_user.id):
        if registration:
            registration_button = "\U0001F6AB Закрыть регистрацию"
        else:
            registration_button = "\u2705 Открыть регистрацию"
        keyboard.add("\U0001F9CD Ученики")
        keyboard.add("\U0001F4DA Материалы текущего модуля")
        keyboard.add("\U0001F4CA Оценки и посещаемость")
        keyboard.add("\U0001F4E2 Сделать объявление")
        keyboard.add("\U0001F3EE Назначить организатора")
        keyboard.add(registration_button)
        await message.answer(f"Добрый день, {select_admin_name(message.from_user.id)}", reply_markup=keyboard)
    else:
        keyboard.add("\U0001F41D Профиль")
        keyboard.add("\U0001F4DA Материалы текущего модуля")
        keyboard.add("\U0001F4CA Оценки и посещаемость")
        await message.answer(f"Добрый день, {select_user_name(message.from_user.id)}", reply_markup=keyboard)


#Страница участников
async def students_page(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row_width = 2
    keyboard.add(*["\U0001F9FE Список участников", "\U0001F50E Найти участника", "\U0001F6AB Исключить участника"])
    keyboard.add("\U00002b05 Назад на главную")
    await message.answer("\U0001F9CD Ученики", reply_markup=keyboard)


#Страница выбора материалов или дз
async def overall_materials_page(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row_width = 2
    keyboard.add(*["\U0001F4D2 Материалы", "\U0001F4CB Задания", "\U00002b05 Назад на главную"])
    await message.answer("\U0001F4DA Материалы текущего модуля", reply_markup=keyboard)


#Страница материалов
async def materials_page(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row_width = 2
    if is_admin(tgid=message.from_user.id):
        keyboard.add(*["\U0001F4DD Выложить материал", "\U0001F4CB Просмотреть материалы", "\U00002b05 Назад на главную"])
    else:
        keyboard.add(*["\U0001F4CB Просмотреть материалы", "\U00002b05 Назад на главную"])
    await message.answer("\U0001F4D2 Материалы", reply_markup=keyboard)


#Страница дз
async def homeworks_page(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if is_admin(tgid=message.from_user.id):
        keyboard.row_width = 3
        keyboard.add(*["\U0001F4DD Выложить дз", "\U0001F4CB Просмотреть загруженные дз", "\U0001F4D2 Просмотреть выполненные дз", "\U0001FAA3 Очистить загруженные дз", "\U00002b05 Назад на главную"])
    else:
        keyboard.row_width = 2
        keyboard.add(*["\U0001F4D2 Отправить домашнее задание", "\U0001F4CB Просмотреть домашние задания", "\U00002b05 Назад на главную"])
    await message.answer("\U0001F4CB Задания", reply_markup=keyboard)


#Страница оценок и посещаемости
async def attendance_page(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if is_admin(tgid=message.from_user.id):
        keyboard.row_width = 2
        keyboard.add(*["\U0001F4CA Просмотреть оценки и посещаемость", "\u269C Выставить оценку за урок", "\U00002b05 Назад на главную"])
    else:
        keyboard.add(*["\U0001F4CA Просмотреть оценки и посещаемость", "\U00002b05 Назад на главную"])
    await message.answer("\U0001F4CA Оценки и посещаемость", reply_markup=keyboard)


#Список материалов
async def materials_list(message: types.Message, text: str, symbol: str):
    db.execute("SELECT date, time FROM materialscreated;")
    materials = db.fetchall()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("\U00002b05 Назад к материалам")
    for material in materials:
        keyboard.add(*[f"{symbol}{material[0]} {material[1]}"])
    await message.answer(text, reply_markup=keyboard)


#Список дз
async def homeworks_list(message: types.Message, text: str, symbol: str):
    db.execute("SELECT date, time FROM hwcreated;")
    homeworks = db.fetchall()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("\U00002b05 Назад к домашним заданиям")
    for homework in homeworks:
        keyboard.add(*[f"{symbol}{homework[0]} {material[1]}"])
    await message.answer(text, reply_markup=keyboard)


#Список учеников
async def students_list(message: types.Message, text: str, symbol: str):
    db.execute("SELECT surname, name, lastname FROM hwuploaded INNER JOIN waspusers ON hwuploaded.telegramid = waspusers.telegramid;")
    students = db.fetchall()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("\U00002b05 Назад на главную")
    for student in students:
        keyboard.add(*[f"{symbol}{student[0]} {student[1]} {student[2]}"])
    await message.answer(text, reply_markup=keyboard)


#Добавление оценки
async def add_mark(mark, callback_query):
    await bot.answer_callback_query(callback_query.id)
    if not is_admin(tgid=callback_query.from_user.id):
        return
    db.execute(f"SELECT checking_marks_student, setting_mark_date, checking_homework_student, checking_homework_date FROM waspadmins WHERE telegramid = {callback_query.from_user.id};")
    user = db.fetchone()
    if user[0] and user[1]:
        db.execute(f"SELECT * from attendance WHERE telegramid = {user[0]} AND date = '{user[1]}' AND mark != '-';")
        users = db.fetchall()
        if not users:
            add_stingers(tgid=user[0], stingers=mark)
        db.execute(f"UPDATE attendance SET mark = '{mark}' WHERE telegramid = {user[0]} and date = '{user[1]}';")
        await bot.send_message(chat_id=user[0], text=f"\U0001F4E3 Вы получили оценку {mark} за урок {user[1]}")
    if user[2] and user[3]:
        db.execute(f"SELECT * from hwuploaded WHERE telegramid = {user[2]} AND homework_date = '{user[3]}' AND mark != '-';")
        users = db.fetchall()
        if not users:
            add_stingers(tgid=user[2], stingers=mark)
        db.execute(f"UPDATE hwuploaded SET mark = '{mark}' WHERE telegramid = {user[2]} and homework_date = '{user[3]}';")
        await bot.send_message(chat_id=user[2], text=f"\U0001F4E3 Вы получили оценку {mark} за домашнее задание от {user[3]}")
    if user[0] and user[1] or user[2] and user[3]:
        db.execute(f"UPDATE waspadmins SET checking_marks_student = NULL, setting_mark_date = NULL, checking_homework_student = NULL, checking_homework_date = NULL WHERE telegramid = {callback_query.from_user.id};")
        await callback_query.message.answer("\U0001F4E3 Оценка выставлена.")


#Клавиатура оценок, встроенная в сообщение
def inline_marks():
    button0 = InlineKeyboardButton(text="\U0001F41D 0", callback_data="button0")
    button1 = InlineKeyboardButton(text="\U0001F41D 1", callback_data="button1")
    button2 = InlineKeyboardButton(text="\U0001F41D 2", callback_data="button2")
    button3 = InlineKeyboardButton(text="\U0001F41D 3", callback_data="button3")
    button4 = InlineKeyboardButton(text="\U0001F41D 4", callback_data="button4")
    button5 = InlineKeyboardButton(text="\U0001F41D 5", callback_data="button5")
    keyboard = InlineKeyboardMarkup().add(*[button0, button1, button2, button3, button4, button5])
    return keyboard


#Обработка inline-кнопок
@dp.callback_query_handler(lambda c: c.data == 'button0')
async def button0(callback_query: types.CallbackQuery):
    await add_mark(0, callback_query)
    return


@dp.callback_query_handler(lambda c: c.data == 'button1')
async def button1(callback_query: types.CallbackQuery):
    await add_mark(1, callback_query)
    return


@dp.callback_query_handler(lambda c: c.data == 'button2')
async def button2(callback_query: types.CallbackQuery):
    await add_mark(2, callback_query)
    return


@dp.callback_query_handler(lambda c: c.data == 'button3')
async def button3(callback_query: types.CallbackQuery):
    await add_mark(3, callback_query)
    return


@dp.callback_query_handler(lambda c: c.data == 'button4')
async def button4(callback_query: types.CallbackQuery):
    await add_mark(4, callback_query)
    return


@dp.callback_query_handler(lambda c: c.data == 'button5')
async def button5(callback_query: types.CallbackQuery):
    await add_mark(5, callback_query)
    return


#Обработка нажатия кнопок
@dp.message_handler(content_types=types.ContentType.ANY)
async def on_message(message: types.Message):
    global registration
    if is_removed(tgid=message.from_user.id):
        await message.answer(str(message.from_user.full_name) + ", вы были исключены из курса. \nОбратитесь к организатору.")
        return
    if not is_user(message.from_user.id) and not is_admin(tgid=message.from_user.id):
        if not registration:
            await message.answer("\u2757 В настоящий момент регистрация на курс закрыта.")
            return
        try:
            msg = message.text.split(" ")
            surname = msg[0]
            name = msg[1]
            lastname = msg[2]
            tgreg_user(message.from_user.id, message.from_user.username, name, surname, lastname)
            await homepage(message)
        except:
            await message.answer("Добрый день, для регистрации введите ваши ФИО.")
    if message.text == "\U00002b05 Отмена":
        if sending_homework(message.from_user.id):
            db.execute(f"DELETE FROM hwuploaded WHERE telegramid = {message.from_user.id} AND upload_date ISNULL;")
            db.execute(f"UPDATE waspusers SET sending_homework = FALSE WHERE telegramid = {message.from_user.id};")
            await overall_materials_page(message)
        if creating_material(message.from_user.id):
            db.execute(f"UPDATE waspadmins SET creating_material = FALSE WHERE telegramid = {message.from_user.id};")
            await homeworks_page(message)
        if creating_homework(message.from_user.id):
            db.execute(f"UPDATE waspadmins SET creating_homework = FALSE WHERE telegramid = {message.from_user.id};")
            await homeworks_page(message)
        if finding_user(message.from_user.id):
            db.execute(f"UPDATE waspadmins SET finding_user = FALSE WHERE telegramid = {message.from_user.id};")
            await students_page(message)
        if removing_user(message.from_user.id):
            db.execute(f"UPDATE waspadmins SET removing_user = FALSE WHERE telegramid = {message.from_user.id};")
            await students_page(message)
        if announcing(message.from_user.id):
            db.execute(f"UPDATE waspadmins SET announcing = FALSE WHERE telegramid = {message.from_user.id};")
            await homepage(message)
        return
    if message.text == "\U0001F6AB Закрыть регистрацию":
        if not is_admin(tgid=message.from_user.id):
            return
        registration = False
        await message.answer("\U0001F6AB Регистрация на курс закрыта.")
        await homepage(message)
    if message.text == "\u2705 Открыть регистрацию":
        if not is_admin(tgid=message.from_user.id):
            return
        registration = True
        await message.answer("\u2705 Регистрация на курс открыта.")
        await homepage(message)
    if message.text == "\U0001F3EE Назначить организатора":
        if not is_admin(tgid=message.from_user.id):
            return
        await message.answer("Напишите telegram-ник зарегистрированного участника")
        db.execute(f"UPDATE waspadmins SET setting_admin = TRUE WHERE telegramid = {message.from_user.id};")
        return
    if message.text == "\U00002b05 Назад к оценкам и посещаемости":
        await attendance_page(message)
        return
    if message.text == "\U00002b05 Назад к материалам":
        if is_admin(tgid=message.from_user.id):
            db.execute(f"UPDATE waspadmins SET checking_homework_date = NULL, checking_homework_student = NULL, checking_marks_student = NULL, setting_mark_date = NULL;")
        await materials_page(message)
        return
    if message.text == "\U00002b05 Назад к домашним заданиям":
        if is_admin(tgid=message.from_user.id):
            db.execute(f"UPDATE waspadmins SET checking_homework_date = NULL, checking_homework_student = NULL, checking_marks_student = NULL, setting_mark_date = NULL;")
        await homeworks_page(message)
        return
    if message.text == "\U00002b05 Назад на главную":
        if is_admin(tgid=message.from_user.id):
            db.execute(f"UPDATE waspadmins SET checking_homework_date = NULL, checking_homework_student = NULL, checking_marks_student = NULL, setting_mark_date = NULL;")
        await homepage(message)
        return
    if creating_material(message.from_user.id):
        if not message.text and not message.photo and not message.document:
            await message.answer("\U0001F53A Отправьте Текст/Фото/Файл")
            return
        date_sent = datetime.now().strftime("%d/%m/%Y")
        time_sent = datetime.now().strftime("%H:%M")
        try:
            if message.text:
                file_name = f'{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M")}.txt'
                with open("materials/" + file_name, 'w') as f:
                    f.write(message.text)
            if message.photo:
                file_name = f'{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M")}.png'
                file = await bot.download_file_by_id(message.photo[-1].file_id)
                with open("materials/" + file_name, 'wb') as f:
                    f.write(file.read())
            if message.document:
                file_format = message.document.file_name.split('.')[1]
                file_name = f'{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M")}.{file_format}'
                file = await bot.download_file_by_id(message.document.file_id)
                with open("materials/" + file_name, 'wb') as f:
                    f.write(file.read())
            db.execute(f"INSERT INTO materialscreated(telegramid, filename, date, time) VALUES({message.from_user.id}, '{file_name}', '{date_sent}', '{time_sent}');")
            if message.caption:
                text_file_name = f'text_{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M")}.txt'
                with open("homeworks/" + text_file_name, 'w') as f:
                    f.write(message.caption)
                db.execute(f"UPDATE materialscreated SET text_filename = '{text_file_name}' WHERE telegramid = {message.from_user.id};")
            db.execute(f"UPDATE waspadmins SET creating_material = FALSE WHERE telegramid = {message.from_user.id};")
            await message.answer("\U0001F53A Материал выложен.")
            await overall_materials_page(message)
            db.execute(f"SELECT name, surname, lastname FROM waspadmins WHERE telegramid = {message.from_user.id};")
            return
        except:
            await message.answer("\u2757 Не удалось отправить файл. Попробуйте ещё раз.")
    if creating_homework(message.from_user.id):
        if not message.text and not message.photo and not message.document:
            await message.answer("\U0001F53A Отправьте Текст/Фото/Файл")
            return
        date_sent = datetime.now().strftime("%d/%m/%Y")
        time_sent = datetime.now().strftime("%H:%M")
        try:
            if message.text:
                file_name = f'{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M")}.txt'
                with open("homeworks/" + file_name, 'w') as f:
                    f.write(message.text)
            if message.photo:
                file_name = f'{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M")}.png'
                file = await bot.download_file_by_id(message.photo[-1].file_id)
                with open("homeworks/" + file_name, 'wb') as f:
                    f.write(file.read())
            if message.document:
                file_format = message.document.file_name.split('.')[1]
                file_name = f'{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M")}.{file_format}'
                file = await bot.download_file_by_id(message.document.file_id)
                with open("homeworks/" + file_name, 'wb') as f:
                    f.write(file.read())
            db.execute(f"INSERT INTO hwcreated(telegramid, filename, date, time) VALUES({message.from_user.id}, '{file_name}', '{date_sent}', '{time_sent}');")
            if message.caption:
                text_file_name = f'text_{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M")}.txt'
                with open("homeworks/" + text_file_name, 'w') as f:
                    f.write(message.caption)
                db.execute(f"UPDATE hwcreated SET text_filename = '{text_file_name}' WHERE telegramid = {message.from_user.id};")
            db.execute(f"UPDATE waspadmins SET creating_homework = FALSE WHERE telegramid = {message.from_user.id};")
            await message.answer("\U0001F53A Дз выложено.")
            await overall_materials_page(message)
            db.execute(f"SELECT name, surname, lastname FROM waspadmins WHERE telegramid = {message.from_user.id};")
            return
        except:
            await message.answer("\u2757 Не удалось отправить файл. Попробуйте ещё раз.")
    if sending_homework(message.from_user.id):
        if not message.text and not message.photo and not message.document:
            await message.answer("\U0001F53A Отправьте Текст/Фото/Файл")
            return
        date_sent = datetime.now().strftime("%d/%m/%Y")
        time_sent = datetime.now().strftime("%H:%M")
        db.execute(f"SELECT surname, name, lastname FROM waspusers WHERE telegramid = {message.from_user.id};")
        user_fullname = " ".join(db.fetchone())
        db.execute(f"SELECT homework_date FROM hwuploaded WHERE telegramid = {message.from_user.id};")
        homework_date = str(db.fetchone()[0]).replace("/", "_")
        try:
            os.makedirs(f"homeworks_uploaded/{user_fullname}/{homework_date}")
        except:
            pass
        if message.text:
            file_name = f'{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M")}_{str(message.from_user.id)}.txt'
            with open(f"homeworks_uploaded/{user_fullname}/{homework_date}/{file_name}", 'w') as f:
                f.write(message.text)
        if message.photo:
            file_name = f'{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M")}_{str(message.from_user.id)}.png'
            file = await bot.download_file_by_id(message.photo[-1].file_id)
            with open(f"homeworks_uploaded/{user_fullname}/{homework_date}/{file_name}", 'wb') as f:
                f.write(file.read())
        if message.document:
            file_format = message.document.file_name.split('.')[1]
            file_name = f'{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M")}_{str(message.from_user.id)}.{file_format}'
            file = await bot.download_file_by_id(message.document.file_id)
            with open(f"homeworks_uploaded/{user_fullname}/{homework_date}/{file_name}", 'wb') as f:
                f.write(file.read())
        db.execute(f"UPDATE hwuploaded SET filename = '{file_name}', upload_date = '{date_sent}', upload_time = '{time_sent}' WHERE telegramid = {message.from_user.id} AND upload_date ISNULL;")
        if message.caption:
            text_file_name = f'text_{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M")}_{str(message.from_user.id)}.txt'
            with open(f"homeworks_uploaded/{user_fullname}/{homework_date}/{text_file_name}", 'w') as f:
                f.write(message.caption)
            db.execute(f"UPDATE hwuploaded SET text_filename = '{text_file_name}' WHERE telegramid = {message.from_user.id};")
        db.execute(f"UPDATE waspusers SET sending_homework = FALSE WHERE telegramid = {message.from_user.id};")
        await message.answer("\U0001F53A Дз отправлено.")
        await overall_materials_page(message)
        print(f'{user_fullname} отправил дз {str(date_sent)} в {str(time_sent)}')
        return
    if finding_user(message.from_user.id):
        msg = message.text.split(' ')
        try:
            surname = msg[0]
            name = msg[1]
        except:
            await message.answer("\U0001F464 Введите фамилию и имя")
            return
        db.execute(f"SELECT telegramid FROM waspusers WHERE name = '{name}' AND surname = '{surname}';")
        users = db.fetchall()
        db.execute(f"UPDATE waspadmins SET finding_user = FALSE WHERE telegramid = {message.from_user.id};")
        if not users:
            await message.answer(f"{surname} {name} не зарегистрирован на курсе.")
            return
        for user in users:
            db.execute(f"SELECT surname, name, lastname, telegramname, discordid FROM waspusers WHERE telegramid = '{user[0]}';")
            data = db.fetchone()
            if data[4]:
                discord_link = "\u2705 Discord привязан"
            else:
                discord_link = "\u274C Discord не привязан"
            await message.answer(f'ФИО: {data[0]} {data[1]} {data[2]}\nТелеграм – @{data[3]}\n{discord_link}')
        await students_page(message)
        return
    if removing_user(message.from_user.id):
        msg = str(message.text)
        telegramname = msg.replace('@', '')
        if not is_user(tgname=telegramname):
            await message.answer(f"@{telegramname} не зарегистрирован на курсе.")
            return
        db.execute(f"UPDATE waspadmins SET removing_user = FALSE WHERE telegramid = {message.from_user.id};")
        db.execute(f"SELECT telegramid FROM waspusers WHERE telegramname = '{telegramname}';")
        user = db.fetchone()
        user_id = user[0]
        if is_admin(tgid=user_id):
            await message.answer("Вы не можете исключить организатора.")
            db.execute(f"UPDATE waspadmins SET removing_user = FALSE WHERE telegramid = {message.from_user.id};")
            await students_page(message)
            return
        db.execute(f"DELETE FROM waspusers WHERE telegramname = '{telegramname}';")
        db.execute(f"INSERT INTO removedusers(telegramid, telegramname) VALUES({user_id}, '{telegramname}');")
        await message.answer(f"Участник @{telegramname} исключён из курса.")
        return
    if announcing(message.from_user.id):
        db.execute(f"UPDATE waspadmins SET announcing = FALSE WHERE telegramid = {message.from_user.id};")
        users = select_users_id()
        db.execute(f"SELECT name, surname, lastname FROM waspadmins WHERE telegramid = {message.from_user.id};")
        user_fullname = " ".join(db.fetchone())
        for user in users:
            await bot.send_message(chat_id=user[0], text=f"{user_fullname} отправил объявление:")
            await bot.send_message(chat_id=user[0], text=message.text)
        await homepage(message)
        await message.answer("Рассылка отправлена ученикам.")
        return
    if setting_admin(message.from_user.id):
        db.execute(f"UPDATE waspadmins SET setting_admin = FALSE WHERE telegramid = {message.from_user.id};")
        telegramname = message.text.replace('@', '')
        db.execute(f"SELECT * FROM waspusers WHERE telegramname = '{telegramname}';")
        data = db.fetchone()
        if not data:
            await message.answer("Участник с таким ником не зарегистрирован.")
            return
        db.execute(f"DELETE FROM waspusers WHERE telegramname = '{telegramname}';")
        tgreg_admin(data[1], telegramname, data[2], data[3], data[4])
        await bot.send_message(data[1], "\U0001F4E3 Вы получили права администратора.")
        await message.answer(f"@{telegramname} назначен организатором.")
        return
    if message.text == "\U0001F41D Профиль":
        if not is_user(message.from_user.id):
            return
        db.execute(f"SELECT surname, name, lastname, stingers, discordid FROM waspusers WHERE telegramid = {message.from_user.id};")
        data = db.fetchone()
        if data[4]:
            discord_link = "\u2705 Discord привязан"
        else:
            discord_link = "\u274C Discord не привязан"
        if str(data[3])[-1] == '1': #Проверка количества стингеров
            amount_name = "стингер"
        elif str(data[3])[-1] == '2' or str(data[3])[-1] == '3' or str(data[3])[-1] == '4':
            amount_name = "стингера"
        else:
            amount_name = "стингеров"
        try:
            if data[3] < 10:
                photo = open('waspcoin.png', 'rb')
            if data[3] >= 10 and data[3] < 25:
                photo = open('waspcoin-2.png', 'rb')
            if data[3] >= 25 and data[3] < 50:
                photo = open('waspcoin-3.png', 'rb')
            if data[3] >= 50 and data[3] < 100:
                photo = open('waspcoin-4.png', 'rb')
            if data[3] >= 100:
                photo = open('waspcoin-5.png', 'rb')
            await message.answer_photo(photo=photo, caption=f"\U0001F464 {data[0]} {data[1]} {data[2]}\n\n{discord_link}\n\U0001F41D {data[3]} {amount_name}")
        except:
            await message.answer(text=f"\U0001F464 {data[0]} {data[1]} {data[2]}\n\n{discord_link}\n\U0001F41D {data[3]} {amount_name}")
        return
    if message.text == "\U0001F4CA Оценки и посещаемость":
        await attendance_page(message)
        return
    if message.text == "\U0001FAA3 Очистить выполненные дз":
        if not is_admin(tgid=message.from_user.id):
            return
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("\U00002b05 Назад к домашним заданиям", "\u2705 Очистить")
        await message.answer("Вы уверены, что хотите очистить все выполненные домашние задания?", reply_markup=keyboard)
        return
    if message.text == "\u2705 Очистить":
        if not is_admin(tgid=message.from_user.id):
            return
        try:
            shutil.rmtree(f"homeworks/")
            os.mkdir("homeworks")
            db.execute(f"DELETE FROM hwuploaded;")
            await message.answer("\u2705 Загруженные дз очищены.")
        except:
            await message.answer("\u2757 Не удалось очистить папку с дз.")
        await homeworks_page(message)
        return
    if message.text == "\U0001F4CA Просмотреть оценки и посещаемость":
        if is_admin(tgid=message.from_user.id):
            db.execute("SELECT surname, name, lastname FROM waspusers;")
            students = db.fetchall()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("\U00002b05 Назад на главную")
            for student in students:
                keyboard.add(*[f"\U0001F300 {student[0]} {student[1]} {student[2]}"])
            await message.answer("\U0001F4D2 Выберите ученика", reply_markup=keyboard)
            return
        else:
            db.execute(f"SELECT date, mark, attendance_time, attendance FROM attendance WHERE telegramid = '{message.from_user.id}';")
            data = db.fetchall()
            if not data:
                await message.answer(f"\u2757 Вы ещё не посещали занятия.")
                return
            dates = []
            marks = []
            attendance_time = []
            attendance = []
            for datum in data:
                dates.append(datum[0])
                marks.append(datum[1])
                time = str(timedelta(seconds=datum[2])).replace('0 days ', '')
                attendance_time.append(time)
                percentage = int(str(datum[3]).replace('%', ''))
                check = '\u274C'
                if percentage >= 70:
                    check = "\u2705"
                attendance.append(f"{datum[3]} {check}")
            loading_message = await message.answer("\U0001F551 Загрузка...")
            df = pandas.DataFrame()
            df['Дата'] = dates
            df['Оценка'] = marks
            df['Время на уроке'] = attendance_time
            df['Посещаемость'] = attendance
            fig = ff.create_table(df)
            fig.update_layout(
                autosize=False,
                width=500,
                height=200,
            )
            try:
                fig.write_image("student_grades.png", scale=2)
                await bot.send_photo(chat_id=message.from_user.id, photo=open('student_grades.png', 'rb'), caption=f"Оценки и посещаемость")
                os.remove("student_grades.png")
                await loading_message.delete()
                return
            except:
                message.answer("\u2757 Не удалось отправить изображение таблицы.")
    if message.text and "\U0001F300 " in message.text:
        if not is_admin(tgid=message.from_user.id):
            return
        fullname = message.text.replace("\U0001F300 ", "")
        db.execute(f"SELECT date, mark, attendance_time, attendance FROM attendance WHERE fullname = '{fullname}';")
        data = db.fetchall()
        if not data:
            await message.answer(f"\u2757 {fullname} ещё не посещал занятия.")
            return
        dates = []
        marks = []
        attendance_time = []
        attendance = []
        for datum in data:
            dates.append(datum[0])
            marks.append(datum[1])
            time = str(timedelta(seconds=datum[2])).replace('0 days ', '')
            attendance_time.append(time)
            percentage = int(str(datum[3]).replace('%', ''))
            check = '\u274C'
            if percentage >= 70:
                check = "\u2705"
            attendance.append(f"{datum[3]} {check}")
        loading_message = await message.answer("\U0001F551 Загрузка...")
        df = pandas.DataFrame()
        df['Дата'] = dates
        df['Оценка'] = marks
        df['Время на уроке'] = attendance_time
        df['Посещаемость'] = attendance
        fig = ff.create_table(df)
        fig.update_layout(
            autosize=False,
            width=500,
            height=200,
        )
        try:
            fig.write_image("grades.png", scale=2)
            await bot.send_photo(chat_id=message.from_user.id, photo=open('grades.png', 'rb'), caption=f"Оценки {fullname}")
            os.remove("grades.png")
            await loading_message.delete()
        except:
            message.answer("\u2757 Не удалось отправить изображение таблицы.")
        return
    if message.text == "\u269C Выставить оценку за урок":
        if not is_admin(tgid=message.from_user.id):
            return
        db.execute("SELECT surname, name, lastname FROM waspusers;")
        students = db.fetchall()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("\U00002b05 Назад на главную")
        for student in students:
            keyboard.add(*[f"\U0001F4AE{student[0]} {student[1]} {student[2]}"])
        await message.answer("\U0001F4D2 Выберите ученика", reply_markup=keyboard)
        return
    if message.text and "\u2668 " in message.text:
        if not is_admin(tgid=message.from_user.id):
            return
        date = message.text.replace("\u2668 ", "")
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["\U00002b05 Отмена"])
        db.execute(f"UPDATE waspadmins SET setting_mark_date = '{date}' WHERE telegramid = {message.from_user.id};")
        keyboard = inline_marks()
        await message.answer(f"Оценка за урок {date}", reply_markup=keyboard)
        return
    if message.text == "\U0001F9CD Ученики":
        if not is_admin(tgid=message.from_user.id):
            return
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row_width = 2
        keyboard.add(*["\U0001F9FE Список участников", "\U0001F50E Найти участника", "\U0001F6AB Исключить участника"])
        keyboard.add("\U00002b05 Назад на главную")
        await message.answer("Информация об участниках курса", reply_markup=keyboard)
        return
    if message.text == "\U0001F9FE Список участников":
        if not is_admin(tgid=message.from_user.id):
            await message.answer("У вас недостаточно прав.")
            return
        db.execute(f"SELECT surname, name, lastname, telegramname FROM waspusers;")
        users = db.fetchall()
        userslist = "Список учеников:"
        user_num = 1
        for user in users:
            userslist += f"\n{user_num}. {user[0]} {user[1]} {user[2]} | Telegram – @{user[3]}"
            user_num += 1
        await message.answer(userslist)
        return
    if message.text == "\U0001F50E Найти участника":
        if not is_admin(tgid=message.from_user.id):
            return
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["\U00002b05 Отмена"])
        await message.answer("\U0001F464 Введите фамилию и имя участника", reply_markup=keyboard)
        db.execute(f"UPDATE waspadmins SET finding_user = TRUE WHERE telegramid = {message.from_user.id};")
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["\U00002b05 Отмена"])
        return
    if message.text == "\U0001F6AB Исключить участника":
        if not is_admin(tgid=message.from_user.id):
            return
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["\U00002b05 Отмена"])
        await message.answer("Введите Telegram ник участника, которого хотите исключить.", reply_markup=keyboard)
        db.execute(f"UPDATE waspadmins SET removing_user = TRUE WHERE telegramid = {message.from_user.id};")
        return
    if message.text == "\U0001F4DA Материалы текущего модуля":
        await overall_materials_page(message)
        return
    if message.text == "\U0001F4D2 Материалы":
        await materials_page(message)
        return
    if message.text == "\U0001F4DD Выложить материал":
        if not is_admin(tgid=message.from_user.id):
            return
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["\U00002b05 Отмена"])
        db.execute(f"UPDATE waspadmins SET creating_material = TRUE WHERE telegramid = {message.from_user.id};")
        await message.answer("\U0001F53A Выложите материал (Текст/Фото/Файл)", reply_markup=keyboard)
        return
    if message.text == "\U0001F4CB Задания":
        await homeworks_page(message)
        return
    if message.text == "\U0001F515 Отменить отправку":
        db.execute(f"SELECT telegramid, surname, name, lastname, checked_homework_date FROM waspusers WHERE telegramid = {message.from_user.id};")
        user = db.fetchone()
        if user:
            db.execute(f"DELETE from hwuploaded WHERE telegramid = {user[0]} AND homework_date = '{user[4]}';")
            db.execute(f"SELECT checking_homework_date FROM waspadmins WHERE telegramid = {message.from_user.id};")
            date = str(user[4]).replace('/', '_')
            shutil.rmtree(f"homeworks_uploaded/{user[1]} {user[2]} {user[3]}/{date}")
            db.execute(f"UPDATE waspusers SET checked_homework_date = NULL WHERE telegramid = {message.from_user.id};")
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.row_width = 2
            keyboard.add(*["\U0001F4D2 Отправить домашнее задание", "\U0001F4CB Просмотреть домашние задания", "\U00002b05 Назад на главную"])
            await message.answer("Отправка дз отменена.", reply_markup=keyboard)
            return
    if message.text == "\U0001F4DD Выложить дз":
        if not is_admin(tgid=message.from_user.id):
            return
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["\U00002b05 Отмена"])
        db.execute(f"UPDATE waspadmins SET creating_homework = TRUE WHERE telegramid = {message.from_user.id};")
        await message.answer("\U0001F53A Выложите дз (Текст/Фото/Файл)", reply_markup=keyboard)
        return
    if message.text == "\U0001F4D2 Отправить домашнее задание":
        await homeworks_list(message, "Выберите, дз за какую дату вы хотите отправить", "\U00002620")
        return
    if message.text == "\U0001F4E2 Сделать объявление":
        if not is_admin(tgid=message.from_user.id):
            return
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["\U00002b05 Отмена"])
        await message.answer("\U0001F53A Напишите текст объявления.", reply_markup=keyboard)
        db.execute(f"UPDATE waspadmins SET announcing = TRUE WHERE telegramid = {message.from_user.id};")
        return
    if message.text == "\U0001F4CB Просмотреть материалы":
        await materials_list(message, "\U0001F4D2 Материалы", "\u267B")
        return
    if message.text == "\U0001F4CB Просмотреть домашние задания" or message.text == "\U0001F4CB Просмотреть загруженные дз":
        await homeworks_list(message, "\U0001F4CB Домашние задания", "\U0001F5C2")
        return
    if message.text == "\U0001F4D2 Просмотреть выполненные дз":
        if not is_admin(tgid=message.from_user.id):
            return
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row_width = 2
        keyboard.add(*["\U0001F5D3 Просмотреть дз по датам", "\U0001F464 Просмотреть дз по ученикам", "\U00002b05 Назад на главную"])
        await message.answer("\U0001F4D2 Просмотреть дз", reply_markup=keyboard)
        return
    if message.text == "\U0001F5D3 Просмотреть дз по датам":
        if not is_admin(tgid=message.from_user.id):
            return
        await homeworks_list(message, "\U0001F4D2 Выберите дату", "\U0001F4CD")
        return
    if message.text == "\U0001F464 Просмотреть дз по ученикам":
        if not is_admin(tgid=message.from_user.id):
            return
        await students_list(message, "\U0001F4D2 Выберите ученика", "\U0001F530")
        return
    if message.text == "\U0001F9F7 Назад":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row_width = 2
        keyboard.add(*["\U0001F5D3 Просмотреть дз по датам", "\U0001F464 Просмотреть дз по ученикам", "\U00002b05 Назад на главную"])
        return
    if message.text and "\U0001F530" in message.text:
        if not is_admin(tgid=message.from_user.id):
            return
        fullname = message.text.replace("\U0001F530", "").split(' ')
        db.execute(f"SELECT telegramid from waspusers WHERE name = '{fullname[1]}' AND surname = '{fullname[0]}' AND lastname = '{fullname[2]}';")
        id = db.fetchone()[0]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["\U00002b05 Назад на главную"])
        db.execute(f"UPDATE waspadmins SET checking_homework_student = '{id}' WHERE telegramid = {message.from_user.id};")
        db.execute(f"SELECT homework_date FROM hwuploaded WHERE telegramid = {id};")
        dates = db.fetchall()
        for date in dates:
            keyboard.add(*[f"\U0001F5D2 {date[0]}"])
        await message.answer(f"Выполненные дз ученика {fullname[0]} {fullname[1]}", reply_markup=keyboard)
        return
    if message.text and "\U0001F4AE" in message.text:
        if not is_admin(tgid=message.from_user.id):
            return
        fullname = message.text.replace("\U0001F4AE", "").split(' ')
        db.execute(f"SELECT telegramid from waspusers WHERE name = '{fullname[1]}' AND surname = '{fullname[0]}' AND lastname = '{fullname[2]}';")
        id = db.fetchone()[0]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["\U00002b05 Назад к оценкам и посещаемости"])
        db.execute(f"UPDATE waspadmins SET checking_marks_student = '{id}' WHERE telegramid = {message.from_user.id};")
        db.execute(f"SELECT date FROM attendance WHERE telegramid = {id};")
        dates = db.fetchall()
        for date in dates:
            keyboard.add(*[f"\u2668 {date[0]}"])
        await message.answer(f"\U0001F4D2 Выберите дату", reply_markup=keyboard)
        return
    if message.text and "\U00002620" in message.text:
        date = message.text.replace("\U00002620", "")
        db.execute(f"SELECT * FROM hwuploaded WHERE telegramid = {message.from_user.id} AND homework_date = '{date}';")
        users = db.fetchall()
        if users:
            db.execute(f"UPDATE waspusers SET checked_homework_date = '{date}' WHERE telegramid = {message.from_user.id};")
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*["\U0001F515 Отменить отправку", "\U00002b05 Назад на главную"])
            await message.answer("Вы уже отправили это дз.", reply_markup=keyboard)
            return
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["\U00002b05 Отмена"])
        db.execute(f"UPDATE waspusers SET sending_homework = TRUE WHERE telegramid = {message.from_user.id};")
        db.execute(f"INSERT INTO hwuploaded(telegramid, homework_date) VALUES({message.from_user.id}, '{date}');")
        await message.answer("\U0001F53A Отправьте своё дз (Текст/Фото/Файл)", reply_markup=keyboard)
        return
    if message.text and "\U0001F5C2" in message.text:
        try:
            date = message.text.replace("\U0001F5C2", "")
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*["\U00002b05 Отмена"])
            db.execute(f"SELECT * FROM hwcreated WHERE date = '{date}';")
            homework = db.fetchone()
            file_name = homework[1]
            text_file_name = homework[2]
            text_content = None
            if text_file_name:
                with open(f"homeworks/{text_file_name}", 'r') as f:
                    text_content = f.read()
                    f.close()
            await bot.send_document(chat_id=message.from_user.id, document=open(f'homeworks/{file_name}', 'rb'), caption=text_content) #Отправка файла
            return
        except:
            await message.answer("\u2757 Не удалось просмотреть это дз.")
    if message.text and "\u267B" in message.text:
        try:
            date = message.text.replace("\u267B", "")
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*["f Отмена"]);
            db.execute(f"SELECT * FROM materialscreated WHERE date = '{date}';")
            homework = db.fetchone()
            file_name = homework[1]
            text_file_name = homework[2]
            text_content = None
            if text_file_name:
                with open(f"materials/{text_file_name}", 'r') as f:
                    text_content = f.read()
                    f.close()
            await bot.send_document(chat_id=message.from_user.id, document=open(f'materials/{file_name}', 'rb'), caption=text_content) #Отправка файла
            return
        except:
            await message.answer("\u2757 Не удалось просмотреть этот материал.")
    if message.text and "\U0001F4CD" in message.text:
        if not is_admin(tgid=message.from_user.id):
            return
        date = message.text.replace("\U0001F4CD", "")
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["\U00002b05 Назад на главную"])
        db.execute(f"UPDATE waspadmins SET checking_homework_date = '{date}' WHERE telegramid = {message.from_user.id};")
        db.execute(f"SELECT name, surname, lastname FROM hwuploaded INNER JOIN waspusers ON hwuploaded.telegramid = waspusers.telegramid WHERE homework_date = '{date}';")
        names = db.fetchall()
        for name in names:
            keyboard.add(*[f"\U0001F4DC {name[1]} {name[0]} {name[2]}"])
        await message.answer(f"Выполненные дз на {date}", reply_markup=keyboard)
        return
    if message.text and "\U0001F4DC" in message.text:
        if not is_admin(tgid=message.from_user.id):
            return
        fullname = message.text.replace("\U0001F4DC ", "")
        db.execute(f"SELECT checking_homework_date FROM waspadmins WHERE telegramid = {message.from_user.id};")
        date = str(db.fetchone()[0]).replace('/', '_')
        files = os.listdir(f"homeworks_uploaded/{fullname}/{date}")
        for file in files: #Отправка файла
            await message.answer_document(open(f"homeworks_uploaded/{fullname}/{date}/{file}", 'rb'))
        keyboard = inline_marks()
        await message.answer(f"Дз {fullname}", reply_markup=keyboard)
        return
    if message.text and "\U0001F5D2" in message.text:
        if not is_admin(tgid=message.from_user.id):
            return
        date = message.text.replace("\U0001F5D2 ", "")
        db.execute(f"UPDATE waspadmins SET checking_homework_date = '{date}' WHERE telegramid = {message.from_user.id};")
        db.execute(f"SELECT checking_homework_student FROM waspadmins WHERE telegramid = {message.from_user.id};")
        id = db.fetchone()[0]
        db.execute(f"SELECT surname, name, lastname FROM waspusers WHERE telegramid = {id};")
        date = date.replace('/', '_')
        fullname = " ".join(db.fetchone())
        files = os.listdir(f"homeworks_uploaded/{fullname}/{date}")
        for file in files: #Отправка файла
            await message.answer_document(open(f"homeworks_uploaded/{fullname}/{date}/{file}", 'rb'))
        keyboard = inline_marks()
        await message.answer(f"Дз {fullname}", reply_markup=keyboard)
        return


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
