from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import TEACHER_URL

def get_main_menu() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="💰 Цены", callback_data="prices"),
        types.InlineKeyboardButton(text="❓ FAQ", callback_data="faq")
    )
    builder.row(types.InlineKeyboardButton(text="🎓 О преподавателе", callback_data="about"))
    builder.row(types.InlineKeyboardButton(text="📅 Записаться на урок", url=TEACHER_URL))
    return builder.as_markup()

def get_faq_menu() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()    
    builder.row(types.InlineKeyboardButton(text="🎸 С чего начать?", callback_data="faq_1"))
    builder.row(types.InlineKeyboardButton(text="⏳ Формат и расписание", callback_data="faq_2"))
    builder.row(types.InlineKeyboardButton(text="🎵 Программа и результаты", callback_data="faq_3"))
    builder.row(types.InlineKeyboardButton(text="🔙 Назад", callback_data="to_main"))
    return builder.as_markup()

def get_back_button(target: str = "to_main") -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    text = "🔙 Назад в FAQ" if target == "faq" else "🔙 Назад"
    builder.row(types.InlineKeyboardButton(text=text, callback_data=target))
    return builder.as_markup()