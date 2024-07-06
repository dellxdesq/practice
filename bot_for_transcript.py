import asyncio
import datetime
import logging
from datetime import datetime
from keyboard import Keyboard
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import ReplyKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from transcript_app import VideoTranscriptApp

logging.basicConfig(level=logging.INFO)
bot = Bot(token="6751020002:AAFABIoqzPaR2ezqBfuJbItO_pd2Y_dXG28")
dp = Dispatcher()
admins_id = {5795388409}
class YourStates(StatesGroup):
    waiting_for_link = State()
    waiting_for_duration = State()
    control = State()
    waiting_for_time_act = State()
    waiting_for_time_nu = State()
    waiting_for_theme_m1 = State()
    waiting_for_theme_m2 = State()
    waiting_for_quest_m1 = State()
    waiting_for_quest_m2 = State()
    waiting_for_user_id = State()
    waiting_for_quest = State()
    waiting_for_model = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет ✌️\nВы попали к боту, организующему удобный поиск по указанным вами видео. \nЧтобы начать, выберите одну из функций на кнопках")
    await main_menu(message)


@dp.message(F.text.lower() == "загрузить новое видео")
async def provide_link(message: types.Message, state: FSMContext):
    await message.reply("Отправьте ссылку на видео", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(YourStates.waiting_for_link)


@dp.message(YourStates.waiting_for_link)
async def handle_link(message: types.Message, state: FSMContext):
    link = message.text
    await state.update_data(link=link)

    await message.reply("Выберите максимальную длительность объединения сегментов (в секундах):")
    await message.reply("1. 5 секунд")
    await message.reply("2. 15 секунд")
    await message.reply("3. 30 секунд")

    await state.set_state(YourStates.waiting_for_duration)

@dp.message(YourStates.waiting_for_duration)
async def handle_duration(message: types.Message, state: FSMContext):
    choice = message.text
    data = await state.get_data()
    link = data.get("link")

    if choice == '1':
        max_duration = 5.0
    elif choice == '2':
        max_duration = 15.0
    elif choice == '3':
        max_duration = 30.0
    else:
        await message.reply("Неверный выбор. Используется значение по умолчанию: 60 секунд.")
        max_duration = 60.0

    try:
        loading = await message.reply("Добавляем видео...")
        app = VideoTranscriptApp()
        result = app.add_video(link, max_duration)
        if result:
            await message.reply(result)
        else:
            await loading.delete()
            await message.reply("Видео добавлено успешно!")
    except Exception:
        await message.reply("Не удалось распознать ссылку.")
    await state.clear()
    await main_menu(message)


@dp.message(F.text.lower() == "история")
async def get_hist(message: types.Message):
    id = message.from_user.id
    time = datetime.now()
    try:
        loading = await message.reply("Загружаем ваши видео...")
        #получаем из бд по id видео, добавленные пользователем
        #выводим ответ
        await loading.delete()
    except Exception:
        await message.reply("Ошибка при обращении к базе данных. Попробуйте позже...")
    await main_menu(message)


@dp.message(F.text.lower() == "избранное")
async def get_fav(message: types.Message):
    id = message.from_user.id
    time = datetime.datetime.now()
    try:
        loading = await message.reply("Загружаем ваши видео...")
        # получаем из бд по id видео, добавленные пользователем
        # выводим ответ
        await loading.delete()
    except Exception:
        await message.reply("Ошибка при обращении к базе данных. Попробуйте позже...")
    await main_menu(message)


@dp.message(F.text.lower() == "задать вопрос")
async def find_for_quest(message: types.Message, state: FSMContext):
    await message.reply("Выберите модель для обработки вопроса:", reply_markup=Keyboard().model_kb)
    await state.set_state(YourStates.waiting_for_model)

@dp.message(YourStates.waiting_for_model)
async def process_model_choice(message: types.Message, state: FSMContext):
    model_name = message.text
    await message.reply("Введите ваш вопрос:", reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(model_name=model_name)
    await state.set_state(YourStates.waiting_for_quest)

@dp.message(YourStates.waiting_for_quest)
async def find_quest_m1(message: types.Message, state: FSMContext):
    quest = message.text
    data = await state.get_data()
    model_name = data.get('model_name')
    try:
        loading = await message.reply("Ищем ответ на вопрос...")
        app = VideoTranscriptApp()
        response = app.generate_answer(quest, model_name)
        await loading.delete()
        await message.reply(f"Ответ на вопрос: {response}")
    except Exception:
        await message.reply("Во время поиска ответа возникла ошибка. Пожалуйста, попробуйте позже.")
    await state.clear()
    await main_menu(message)

@dp.message(F.text.lower() == "поиск по теме")
async def find_for_theme(message: types.Message, state: FSMContext):
    await message.reply("Выберите языковую модель Ollama:", reply_markup=Keyboard().model_kb)
    await state.set_state(YourStates.waiting_for_model)

@dp.message(YourStates.waiting_for_model)
async def process_model_choice(message: types.Message, state: FSMContext):
    model_name = message.text
    await message.reply("Введите тему для поиска ресурсов:")
    await state.update_data(model_name=model_name)
    await state.set_state(YourStates.waiting_for_theme_m1)

@dp.message(YourStates.waiting_for_theme_m1)
async def process_theme_choice(message: types.Message, state: FSMContext):
    theme = message.text
    data = await state.get_data()
    model_name = data.get('model_name')
    await message.reply("Ищем материалы по теме...")
    app = VideoTranscriptApp()
    similar_segments = app.find_similar_segments(theme, model_name)

    if similar_segments:
        await message.reply("Найдены похожие сегменты:")
        for brief_content, start_time, url in similar_segments:
            await message.reply(f"По вашему запросу было найдено: {url} на таймкоде {start_time} с кратким содержанием '{brief_content}'")
    else:
        await message.reply("К сожалению, не найдено похожих сегментов.")

    await state.clear()
    await main_menu(message)


@dp.message(F.text.lower() == "управление")
async def to_admin_menu(message: types.Message, state: FSMContext):
    if message.from_user.id in admins_id:
        await message.reply("Добро пожаловать в меню администрации!", reply_markup=Keyboard().admin_panel)
        await state.set_state(YourStates.control)


@dp.message(F.text.lower() == "новые пользователи", YourStates.control)
async def get_new_users(message: types.Message, state: FSMContext):
    await message.reply("Введите количество дней для просмотра новых пользователей:",
                        reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(YourStates.waiting_for_time_nu)


@dp.message(F.text.lower() == "назад", YourStates.control)
async def back_to_user_menu(message: types.Message, state: FSMContext):
    await main_menu(message)
    await state.clear()


@dp.message(F.text.lower() == "активность", YourStates.control)
async def get_activities(message: types.Message, state: FSMContext):
    await message.reply("Введите дату для просмотра активности в формате ДД.ММ.ГГГГ:",
                        reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(YourStates.waiting_for_time_act)


@dp.message(F.text.lower() == "добавить токены", YourStates.control)
async def add_token(message: types.Message, state: FSMContext):
    await message.reply("Введите ID пользователя и количество токенов через пробел",
                        reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(YourStates.waiting_for_user_id)


@dp.message(YourStates.waiting_for_time_act)
async def add_token_db(message: types.Message, state: FSMContext):
    input = message.text.strip().split(" ")
    id = int(input[0].strip())
    t_count = int(input[1].strip())
    try:
        loading = await message.reply("Добовляем токены...")
        #метод для добавления токенов в бд
        await loading.delete()
    except Exception:
        await message.reply("Во время загрузки статистики произошла непредвиденная ошибка...")
    await state.set_state(YourStates.control)
    await message.reply("Токены успешно добавлены", reply_markup=Keyboard().admin_panel)


@dp.message(YourStates.waiting_for_time_act)
async def time_for_act(message: types.Message, state: FSMContext):
    input = str.split(message.text, ".", -1)
    date = datetime(int(input[2]), int(input[1]), int(input[0]))
    try:
        loading = await message.reply("Загружаем статистику...")
        #Тут получаем из бд активность по дате и отправляем админу ответ
        await loading.delete()
    except Exception:
        await message.reply("Во время загрузки статистики произошла непредвиденная ошибка...")
    await state.set_state(YourStates.control)
    await message.reply("Главное меню администрации:", reply_markup=Keyboard().admin_panel)


@dp.message(YourStates.waiting_for_time_nu)
async def time_for_nu(message: types.Message, state: FSMContext):
    days = int(message.text)
    try:
        loading = await message.reply("Загружаем статистику...")
        #Тут получаем из бд активность по последним дням и отправляем админу ответ
        await loading.delete()
    except Exception:
        await message.reply("Во время загрузки статистики произошла непредвиденная ошибка...")
    await state.set_state(YourStates.control)
    await message.reply("Главное меню администрации:", reply_markup=Keyboard().admin_panel)


async def main_menu(message: types.Message):
    kb: ReplyKeyboardMarkup
    if (message.from_user.id in admins_id):
        kb = Keyboard().admin_kb
    else:
        kb = Keyboard().user_kb
    await message.answer("Выберите одну из опций меню",
                         reply_markup=kb)

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())