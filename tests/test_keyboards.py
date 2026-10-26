import pytest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards import get_main_menu, get_faq_menu, get_back_button
from config import TEACHER_URL

def test_main_menu():
    """Тестируем структуру главного меню"""
    kb = get_main_menu()
    
    # 1. Проверяем, что возвращается правильный тип данных
    assert isinstance(kb, InlineKeyboardMarkup)
    
    # 2. Проверяем количество рядов (строк с кнопками)
    assert len(kb.inline_keyboard) == 3
    
    # 3. Проверяем первый ряд (Цены и FAQ)
    row_1 = kb.inline_keyboard[0]
    assert len(row_1) == 2
    assert row_1[0].text == "💰 Цены"
    assert row_1[0].callback_data == "prices"
    assert row_1[1].text == "❓ FAQ"
    assert row_1[1].callback_data == "faq"
    
    # 4. Проверяем второй ряд (О преподавателе)
    row_2 = kb.inline_keyboard[1]
    assert len(row_2) == 1
    assert row_2[0].text == "🎓 О преподавателе"
    assert row_2[0].callback_data == "about"
    
    # 5. Проверяем третий ряд (Ссылка на запись)
    row_3 = kb.inline_keyboard[2]
    assert len(row_3) == 1
    assert row_3[0].text == "📅 Записаться на урок"
    assert row_3[0].url == TEACHER_URL


def test_faq_menu():
    """Тестируем меню FAQ"""
    kb = get_faq_menu()
    
    assert isinstance(kb, InlineKeyboardMarkup)
    # В FAQ 4 ряда кнопок, по одной в каждом
    assert len(kb.inline_keyboard) == 4
    
    # Собираем все кнопки в плоский список для быстрой проверки callback_data
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    
    assert buttons[0].text == "🎸 С чего начать?"
    assert buttons[0].callback_data == "faq_1"
    
    assert buttons[1].text == "⏳ Формат и расписание"
    assert buttons[1].callback_data == "faq_2"
    
    assert buttons[2].text == "🎵 Программа и результаты"
    assert buttons[2].callback_data == "faq_3"
    
    assert buttons[3].text == "🔙 Назад"
    assert buttons[3].callback_data == "to_main"


@pytest.mark.parametrize("target, expected_text, expected_callback", [
    ("to_main", "🔙 Назад", "to_main"),
    ("faq", "🔙 Назад в FAQ", "faq"),
    ("custom_target", "🔙 Назад", "custom_target"),
])
def test_back_button(target, expected_text, expected_callback):
    """Тестируем динамическую кнопку назад с использованием параметров"""
    kb = get_back_button(target=target)
    
    assert isinstance(kb, InlineKeyboardMarkup)
    assert len(kb.inline_keyboard) == 1
    
    btn = kb.inline_keyboard[0][0]
    assert btn.text == expected_text
    assert btn.callback_data == expected_callback
