#
# демо-версия для GitHub
#

import logging
import os
from aiogram import Router, F, types, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile

import config
import storage
import keyboards
from filters import IsAdminFilter
from config import HELP_TEXT 

# Создаем роутер, к которому привяжем обработчики
router = Router()

# Состояния для редактирования разделов
class BotEditStates(StatesGroup):
    waiting_for_welcome = State()
    waiting_for_about = State()
    waiting_for_prices = State()
    waiting_for_faq1 = State()
    waiting_for_faq2 = State()
    waiting_for_faq3 = State()

# Вспомогательная функция для отправки контента (с фото или без)
async def send_or_edit_content(callback: types.CallbackQuery, text: str, reply_markup):
    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await callback.message.edit_text(text=text, reply_markup=reply_markup, parse_mode="Markdown")

# --- ПОЛЬЗОВАТЕЛЬСКИЕ КОМАНДЫ ---

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    texts = storage.load_texts()
    welcome_text = texts["welcome"]
    
    try:
        photo = FSInputFile(config.PHOTO_FILENAME)
        await message.answer_photo(photo=photo, caption=welcome_text, reply_markup=keyboards.get_main_menu())
    except Exception as e:
        logging.error(f"Не удалось отправить фото: {e}")
        await message.answer(text=welcome_text, reply_markup=keyboards.get_main_menu())

@router.callback_query(F.data == "prices")
async def process_prices(callback: types.CallbackQuery):
    text = storage.load_texts()["prices"]
    await send_or_edit_content(callback, text, keyboards.get_back_button("to_main"))
    await callback.answer()

@router.callback_query(F.data == "about")
async def process_about(callback: types.CallbackQuery):
    text = storage.load_texts()["about"]
    await send_or_edit_content(callback, text, keyboards.get_back_button("to_main"))
    await callback.answer()

@router.callback_query(F.data == "faq")
async def show_faq_list(callback: types.CallbackQuery):
    await send_or_edit_content(callback, "❓ **Часто задаваемые вопросы**\n\nВыберите интересующий вас вопрос ниже:", keyboards.get_faq_menu())
    await callback.answer()

@router.callback_query(F.data.startswith("faq_"))
async def show_faq_item(callback: types.CallbackQuery):
    text = storage.load_texts()[callback.data]
    await send_or_edit_content(callback, text, keyboards.get_back_button("faq"))
    await callback.answer()

@router.callback_query(F.data == "to_main")
async def process_to_main(callback: types.CallbackQuery):
    text = storage.load_texts()["welcome"]
    await send_or_edit_content(callback, text, keyboards.get_main_menu())
    await callback.answer()

# --- АДМИНИСТРАТИВНЫЕ КОМАНДЫ (Защищены фильтры IsAdminFilter) ---

@router.message(Command("help"), IsAdminFilter())
async def cmd_help(message: types.Message):
    help_text = (HELP_TEXT)
    await message.answer(help_text)

# Инициация редактирования текста
@router.message(Command("edit_welcome"), IsAdminFilter())
async def edit_welcome(message: types.Message, state: FSMContext):
    await message.answer("📝 Пожалуйста, введите новый приветственный текст:")
    await state.set_state(BotEditStates.waiting_for_welcome)

@router.message(Command("edit_about"), IsAdminFilter())
async def edit_about(message: types.Message, state: FSMContext):
    await message.answer("📝 Пожалуйста, введите новый текст в блок о преподавателе:")
    await state.set_state(BotEditStates.waiting_for_about)

@router.message(Command("edit_prices"), IsAdminFilter())
async def edit_prices(message: types.Message, state: FSMContext):
    await message.answer("📝 Пожалуйста, введите новый текст в блок о ценах:")
    await state.set_state(BotEditStates.waiting_for_prices)

@router.message(Command("edit_faq1"), IsAdminFilter())
async def edit_faq1(message: types.Message, state: FSMContext):
    await message.answer("📝 Пожалуйста, введите новый текст FAQ1:")
    await state.set_state(BotEditStates.waiting_for_faq1)
    
@router.message(Command("edit_faq2"), IsAdminFilter())
async def edit_faq2(message: types.Message, state: FSMContext):
    await message.answer("📝 Пожалуйста, введите новый текст FAQ2:")
    await state.set_state(BotEditStates.waiting_for_faq2)
    
@router.message(Command("edit_faq3"), IsAdminFilter())
async def edit_faq3(message: types.Message, state: FSMContext):
    await message.answer("📝 Пожалуйста, введите новый текст FAQ3:")
    await state.set_state(BotEditStates.waiting_for_faq3)
    
# Перехват ввода текста для каждого состояния
@router.message(BotEditStates.waiting_for_welcome)
async def process_new_welcome(message: types.Message, state: FSMContext):
    storage.update_text("welcome", message.text)
    await message.answer(f"✅ Текст приветствия успешно сохранен!\nВы ввели: *{message.text}*", parse_mode="Markdown")
    await state.clear()

@router.message(BotEditStates.waiting_for_about)
async def process_new_about(message: types.Message, state: FSMContext):
    storage.update_text("about", message.text)
    await message.answer(f"✅ Текст о преподавателе успешно сохранен!\nВы ввели: *{message.text}*", parse_mode="Markdown")
    await state.clear()

@router.message(BotEditStates.waiting_for_prices)
async def process_new_prices(message: types.Message, state: FSMContext):
    storage.update_text("prices", message.text)
    await message.answer(f"✅ Текст цен успешно сохранен!\nВы ввели: *{message.text}*", parse_mode="Markdown")
    await state.clear()
    
@router.message(BotEditStates.waiting_for_faq1)
async def process_new_faq1(message: types.Message, state: FSMContext):
    storage.update_text("faq_1", message.text)
    await message.answer(f"✅ Текст FAQ1 успешно сохранен!\nВы ввели: *{message.text}*", parse_mode="Markdown")
    await state.clear()
    
@router.message(BotEditStates.waiting_for_faq2)
async def process_new_faq2(message: types.Message, state: FSMContext):
    storage.update_text("faq_2", message.text)
    await message.answer(f"✅ Текст FAQ2 успешно сохранен!\nВы ввели: *{message.text}*", parse_mode="Markdown")
    await state.clear() 

@router.message(BotEditStates.waiting_for_faq3)
async def process_new_faq3(message: types.Message, state: FSMContext):
    storage.update_text("faq_3", message.text)
    await message.answer(f"✅ Текст FAQ3 успешно сохранен!\nВы ввели: *{message.text}*", parse_mode="Markdown")
    await state.clear()    
    

# Команды сброса текста (Reset)
@router.message(Command("reset_welcome"), IsAdminFilter())
async def reset_welcome(message: types.Message):
    storage.reset_text("welcome")
    await message.answer("📝 Возвращаем приветствию первоначальный текст.")

@router.message(Command("reset_about"), IsAdminFilter())
async def reset_about(message: types.Message):
    storage.reset_text("about")
    await message.answer("📝 Возвращаем первоначальный текст в блок информации о преподавателе.")

@router.message(Command("reset_prices"), IsAdminFilter())
async def reset_prices(message: types.Message):
    storage.reset_text("prices")
    await message.answer("📝 Возвращаем первоначальный текст в блок информации о ценах.")
    
@router.message(Command("reset_faq1"), IsAdminFilter())
async def reset_faq1(message: types.Message):
    storage.reset_text("faq_1")
    await message.answer("📝 Возвращаем первоначальный текст FAQ1")
    
@router.message(Command("reset_faq2"), IsAdminFilter())
async def reset_faq2(message: types.Message):
    storage.reset_text("faq_2")
    await message.answer("📝 Возвращаем первоначальный текст FAQ2")    
         
@router.message(Command("reset_faq3"), IsAdminFilter())
async def reset_faq3(message: types.Message):
    storage.reset_text("faq_3")
    await message.answer("📝 Возвращаем первоначальный текст FAQ3")   
    
# Загрузка фото
@router.message(Command("edit_photo"), IsAdminFilter())
async def save_new_photo(message: types.Message, bot: Bot):
    if not message.photo:
        await message.answer("⚠️ Пожалуйста, отправьте команду `/edit_photo` вместе с фотографией в качестве подписи!")
        return

    await message.answer("⏳ Начинаю загрузку фото...")
    try:
        new_photo = message.photo[-1]
        file_info = await bot.get_file(new_photo.file_id)
        await bot.download_file(file_path=file_info.file_path, destination=config.PHOTO_FILENAME)
        await message.answer("✅ Новое фото успешно сохранено на диск!")
    except Exception as e:
        logging.error(f"Ошибка при скачивании фото: {e}")
        await message.answer(f"❌ Не удалось обновить фото. Ошибка: {e}")
        
  # этот обработчик в САМЫЙ КОНЕЦ файла handlers.py
@router.message(F.text.startswith("/"))
async def cmd_unknown_or_restricted(message: types.Message):
    """Срабатывает на любые команды, которые не обработались выше (включая админские от не-админов)."""
    await message.answer("Извините, эта команда мне неизвестна или доступна только администратору.")
