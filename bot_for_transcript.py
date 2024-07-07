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
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from transcript_app import VideoTranscriptApp
from transcript_database import VideoTranscriptDB
logging.basicConfig(level=logging.INFO)
bot = Bot(token="6751020002:AAFABIoqzPaR2ezqBfuJbItO_pd2Y_dXG28")
dp = Dispatcher()
#963171423
admins_id = {963171423}
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
    waiting_for_model2 = State()
    waiting_for_favorite_url = State()
    waiting_for_favorite = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    db = VideoTranscriptDB()
    if not db.user_exists(user_id):
        db.insert_user_tokens(user_id, 5)
    await message.answer(
        f"Привет ✌️\nВы попали к боту, организующему удобный поиск по указанным вами видео.\n"
        f"У вас имеется 10 токенов, за использование функции тратится 1 токен.\n"
        f"\nЧтобы начать, выберите одну из функций на кнопках: ")
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

    db = VideoTranscriptDB()
    user_id = message.from_user.id
    current_date = datetime.now()  # сохраняем дату и время загрузки

    # Insert data into database first

    user_tokens = db.get_user_tokens(user_id)
    if user_tokens <= 0:
        await message.reply("У вас недостаточно токенов для использования этой функции.")
        await state.clear()
        await main_menu(message)
        return

    if not user_tokens <= 0:
        db.insert_tg_user(user_id, link, current_date)
    await message.reply(f"У вас осталось {user_tokens - 1} токенов.")
    if not db.decrease_user_tokens(user_id):
        await message.reply("Не удалось уменьшить количество токенов.")
        await state.clear()
        await main_menu(message)
        return

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
async def get_hist(message: types.Message, state: FSMContext):
    id = message.from_user.id

    db = VideoTranscriptDB()

    user_tokens = db.get_user_tokens(id)
    if user_tokens <= 0:
        await message.reply("У вас недостаточно токенов для использования этой функции.")
        await state.clear()
        await main_menu(message)
        return
    await message.reply(f"У вас осталось {user_tokens - 1} токенов.")
    if not db.decrease_user_tokens(id):
        await message.reply("Не удалось уменьшить количество токенов.")
        await state.clear()
        await main_menu(message)
        return
    try:
        loading = await message.reply("Загружаем ваши видео...")
        db = VideoTranscriptDB()
        cursor = db.conn.cursor()
        cursor.execute("SELECT url FROM tg_user WHERE user_id = ?", (id,))
        videos = cursor.fetchall()
        video_links = [row[0] for row in videos]
        if video_links:
            video_list = "\n".join(video_links)
            await message.reply(f"Ваша история видео:\n{video_list}")
        else:
            await message.reply("У вас нет добавленных видео.")
        await loading.delete()
    except Exception as e:
        await message.reply(f"Ошибка при обращении к базе данных: {str(e)}. Попробуйте позже...")
    await main_menu(message)


from aiogram.utils.keyboard import InlineKeyboardBuilder
import hashlib

@dp.message(F.text.lower() == "избранное")
async def get_fav(message: types.Message, state: FSMContext):
    id = message.from_user.id
    db = VideoTranscriptDB()
    user_tokens = db.get_user_tokens(id)
    if user_tokens <= 0:
        await message.reply("У вас недостаточно токенов для использования этой функции.")
        await state.clear()
        await main_menu(message)
        return
    await message.reply(f"У вас осталось {user_tokens - 1} токенов.")
    if not db.decrease_user_tokens(id):
        await message.reply("Не удалось уменьшить количество токенов.")
        await state.clear()
        await main_menu(message)
        return
    try:
        loading = await message.reply("Загружаем ваши видео...")

        favorites = db.get_favorites(id)
        if favorites:
            # Формируем список избранных видео
            favorite_list = "\n".join(f"• {url}" for url in favorites)
            await message.reply(f"Ваши избранные видео:\n\n{favorite_list}")
        else:
            await message.reply("У вас нет избранных видео.")
        await loading.delete()
    except Exception as e:
        await message.reply(f"Ошибка при обращении к базе данных: {str(e)}")
    await main_menu(message)


@dp.message(F.text.startswith("Добавить в избранное"))
async def add_to_favorites(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.reply("Отправьте ссылку на видео, которое хотите добавить в избранное:")
    await state.set_state(YourStates.waiting_for_favorite)

@dp.message(YourStates.waiting_for_favorite)
async def handle_favorite(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    video_url = message.text

    db = VideoTranscriptDB()

    # Check if user has tokens
    user_tokens = db.get_user_tokens(user_id)
    if user_tokens <= 0:
        await message.reply("У вас недостаточно токенов для использования этой функции.")
        await state.clear()
        await main_menu(message)
        return
    await message.reply(f"У вас осталось {user_tokens - 1} токенов.")
    # Decrease user tokens
    if not db.decrease_user_tokens(user_id):
        await message.reply("Не удалось уменьшить количество токенов.")
        await state.clear()
        await main_menu(message)
        return
    if video_url.startswith("http"):
        try:
            db = VideoTranscriptDB()
            db.add_favorite(user_id, video_url)
            await message.reply(f"Видео {video_url} добавлено в избранное.")
        except Exception as e:
            await message.reply(f"Ошибка при добавлении в избранное: {str(e)}")
    else:
        await message.reply("Пожалуйста, укажите корректный URL видео.")
    await state.clear()
    await main_menu(message)

@dp.callback_query(lambda c: c.data and c.data.startswith('del_fav:'))
async def process_delete_favorite(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    video_url = callback_query.data.split(':', 1)[1]
    db = VideoTranscriptDB()
    db.remove_favorite(user_id, video_url)
    await callback_query.answer(f"Видео {video_url} удалено из избранного")
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await get_fav(callback_query.message)

@dp.message(F.text.lower() == "задать вопрос")
async def find_for_quest(message: types.Message, state: FSMContext):
    db = VideoTranscriptDB()
    user_id = message.from_user.id
    user_tokens = db.get_user_tokens(user_id)
    if user_tokens <= 0:
        await message.reply("У вас недостаточно токенов для использования этой функции.")
        await state.clear()
        await main_menu(message)
        return
    await message.reply(f"У вас осталось {user_tokens - 1} токенов.")
    if not db.decrease_user_tokens(user_id):
        await message.reply("Не удалось уменьшить количество токенов.")
        await state.clear()
        await main_menu(message)
        return
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

async def update_loading_message(message, dots):
    new_text = f"Ищем ответ на вопрос{dots}"
    if message.text != new_text:
        await message.edit_text(new_text)

@dp.message(F.text.lower() == "поиск по теме")
async def find_for_theme(message: types.Message, state: FSMContext):

    db = VideoTranscriptDB()
    user_id = message.from_user.id

    user_tokens = db.get_user_tokens(user_id)
    if user_tokens <= 0:
        await message.reply("У вас недостаточно токенов для использования этой функции.")
        await state.clear()
        await main_menu(message)
        return
    await message.reply(f"У вас осталось {user_tokens - 1} токенов.")
    if not db.decrease_user_tokens(user_id):
        await message.reply("Не удалось уменьшить количество токенов.")
        await state.clear()
        await main_menu(message)
        return

    await message.reply("Выберите языковую модель Ollama:", reply_markup=Keyboard().model_kb)
    await state.set_state(YourStates.waiting_for_model2)

@dp.message(YourStates.waiting_for_model2)
async def process_model_choice(message: types.Message, state: FSMContext):
    model_name = message.text
    await message.reply("Введите тему для поиска видео:")
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


@dp.message(F.text.isdigit(), YourStates.waiting_for_time_nu)
async def get_new_users_by_days(message: types.Message, state: FSMContext):
    days = int(message.text)
    try:
        db = VideoTranscriptDB()
        new_users = db.get_new_users_by_days(days)

        if new_users:
            user_info = "\n".join(
                f"ID: {user_id}, Дата регистрации: {date_publication}" for user_id, date_publication in new_users)
            await message.reply(f"Новые пользователи за последние {days} дней:\n\n{user_info}")
        else:
            await message.reply("За указанный период новых пользователей нет.")

        await state.clear()
        await main_menu(message)
    except Exception as e:
        await message.reply(f"Ошибка при получении новых пользователей: {str(e)}")
        await state.clear()
        await main_menu(message)


@dp.message(F.text.lower() == "назад", YourStates.control)
async def back_to_user_menu(message: types.Message, state: FSMContext):
    await main_menu(message)
    await state.clear()


@dp.message(F.text.lower() == "активность")
async def get_activities(message: types.Message):
    await message.reply("Введите дату для просмотра активности в формате ГГГГ-ММ-ДД:",
                        reply_markup=types.ReplyKeyboardRemove())


@dp.message(lambda m: len(m.text.split("-")) == 3)
async def get_activities_by_date(message: types.Message):
    try:
        date_str = message.text
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        db = VideoTranscriptDB()
        user_activities = db.get_activities_by_date(date)

        if user_activities:
            activity_info = "\n".join(
                f"ID: {user_id}, Добавленные видео: {videos}" for user_id, videos in user_activities)
            await message.reply(f"Активность за дату {date}:\n\n{activity_info}")
        else:
            await message.reply("За указанную дату активности нет.")

        await main_menu(message)
    except ValueError:
        await message.reply("Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")
    except Exception as e:
        await message.reply(f"Ошибка при получении активности: {str(e)}")
        await main_menu(message)


@dp.message(F.text.lower() == "добавить токены", YourStates.control)
async def add_token(message: types.Message, state: FSMContext):
    await message.reply("Введите ID пользователя и количество токенов через пробел",
                        reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(YourStates.waiting_for_user_id)


@dp.message(YourStates.waiting_for_user_id)
async def add_token_db(message: types.Message, state: FSMContext):
    input = message.text.strip().split(" ")
    user_id = int(input[0].strip())
    token_count = int(input[1].strip())
    try:
        loading = await message.reply("Добавляем токены...")
        db = VideoTranscriptDB()
        db.add_tokens(user_id, token_count)
        await loading.delete()
        await message.reply(f"Пользователю с ID {user_id} добавлено {token_count} токенов.")
    except Exception as e:
        await message.reply(f"Ошибка при добавлении токенов: {str(e)}")
    await state.set_state(YourStates.control)
    await main_menu(message)


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