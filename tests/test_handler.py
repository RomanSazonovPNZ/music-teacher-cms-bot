import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

# Импортируем хэндлеры и состояния из вашего основного файла
from handlers import (
    process_prices, 
    show_faq_list, 
    show_faq_item, 
    process_new_welcome,
    BotEditStates,
    cmd_help
)

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_callback():
    """Фикстура для создания базового объекта CallbackQuery"""
    mock_msg = AsyncMock(spec=Message)
    # По умолчанию считаем, что фото в сообщении нет
    mock_msg.photo = None
    mock_msg.edit_text = AsyncMock()
    mock_msg.edit_caption = AsyncMock()
    
    callback = AsyncMock(spec=CallbackQuery)
    callback.message = mock_msg
    callback.answer = AsyncMock()
    return callback


# 1. ТЕСТИРУЕМ НАЖАТИЕ КНОПКИ "ЦЕНЫ" (Когда в сообщении НЕТ фото)
@patch('storage.load_texts')
async def test_process_prices_text_only(mock_load_texts, mock_callback):
    # Настраиваем фейковый возврат текста из хранилища
    mock_load_texts.return_value = {"prices": "Актуальные цены: 1000р"}
    
    # Вызываем хэндлер
    await process_prices(mock_callback)
    
    # Проверяем, что вызвался edit_text (так как сообщения с фото нет)
    mock_callback.message.edit_text.assert_called_once()
    mock_callback.answer.assert_called_once()
    
    # Проверяем переданный текст
    _, kwargs = mock_callback.message.edit_text.call_args
    assert "Актуальные цены: 1000р" in kwargs.get("text")


# 2. ТЕСТИРУЕМ НАЖАТИЕ КНОПКИ "FAQ" (Когда в сообщении ЕСТЬ фото)
async def test_show_faq_list_with_photo(mock_callback):
    # Имитируем, что у сообщения есть фото
    mock_callback.message.photo = ["fake_photo_object"]
    
    await show_faq_list(mock_callback)
    
    # Должен вызваться edit_caption, а не edit_text!
    mock_callback.message.edit_caption.assert_called_once()
    mock_callback.message.edit_text.assert_not_called()
    mock_callback.answer.assert_called_once()


# 3. ТЕСТИРУЕМ ДИНАМИЧЕСКИЙ ХЭНДЛЕР FAQ (Запрос конкретного пункта)
@patch('storage.load_texts')
async def test_show_faq_item(mock_load_texts, mock_callback):
    # Наш клик имитирует нажатие на вторую кнопку FAQ
    mock_callback.data = "faq_2"
    mock_load_texts.return_value = {"faq_2": "Ответ на второй вопрос"}
    
    await show_faq_item(mock_callback)
    
    # Проверяем, что подтянулся верный ключ из хранилища по callback.data
    mock_load_texts.assert_called_once()
    _, kwargs = mock_callback.message.edit_text.call_args
    assert "Ответ на второй вопрос" in kwargs.get("text")


# 4. ТЕСТИРУЕМ АДМИНСКИЙ ВВОД: ПЕРЕХВАТ ТЕКСТА И ОЧИСТКУ СОСТОЯНИЯ (FSM)
@patch('storage.update_text')
async def test_process_new_welcome(mock_update_text):
    # Создаем фейковое сообщение от админа с новым текстом
    mock_message = AsyncMock(spec=Message)
    mock_message.text = "Новый крутой текст приветствия"
    mock_message.answer = AsyncMock()
    
    # Мокаем контекст FSM (состояния)
    mock_state = AsyncMock(spec=FSMContext)
    
    # Запускаем хэндлер перехвата
    await process_new_welcome(mock_message, mock_state)
    
# Допишите этот код в конец файла tests/test_handler.py

from handlers import (
    edit_welcome,
    edit_about,
    reset_welcome,
    reset_about
)

# ---ТЕСТЫ ДЛЯ КОМАНД РЕДАКТИРОВАНИЯ (EDIT) ---

async def test_edit_welcome_command():
    """Тестируем команду /edit_welcome"""
    mock_message = AsyncMock(spec=Message)
    mock_message.answer = AsyncMock()
    
    # Создаем асинStrategic мок для стейта напрямую
    mock_state = AsyncMock(spec=FSMContext)
    
    await edit_welcome(mock_message, mock_state)
    
    mock_message.answer.assert_called_once_with("📝 Пожалуйста, введите новый приветственный текст:")
    # Теперь await внутри хэндлера отработает корректно
    mock_state.set_state.assert_called_once_with(BotEditStates.waiting_for_welcome)


async def test_edit_about_command():
    """Тестируем команду /edit_about"""
    mock_message = AsyncMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_state = AsyncMock(spec=FSMContext)
    
    await edit_about(mock_message, mock_state)
    
    # ВНИМАНИЕ: Если этот тест упадет, значит у вас в handlers.py 
    # функции для FAQ перетерли функцию edit_about (из-за одинаковых названий 'async def edit_about')
    mock_message.answer.assert_called_once_with("📝 Пожалуйста, введите новый текст в блок о преподавателе:")
    mock_state.set_state.assert_called_once_with(BotEditStates.waiting_for_about)


# --- ТЕСТЫ ДЛЯ КОМАНД СБРОСА (RESET) ---

@patch('storage.reset_text')
async def test_reset_welcome_command(mock_reset_text):
    """Тестируем команду /reset_welcome"""
    mock_message = AsyncMock(spec=Message)
    mock_message.answer = AsyncMock()
    
    await reset_welcome(mock_message)
    
    mock_reset_text.assert_called_once_with("welcome")
    mock_message.answer.assert_called_once_with("📝 Возвращаем приветствию первоначальный текст.")


@patch('storage.reset_text')
async def test_reset_about_command(mock_reset_text):
    """Тестируем команду /reset_about"""
    mock_message = AsyncMock(spec=Message)
    mock_message.answer = AsyncMock()
    
    await reset_about(mock_message)
    
    mock_reset_text.assert_called_once_with("about")
    mock_message.answer.assert_called_once_with("📝 Возвращаем первоначальный текст в блок информации о преподавателе.")


#—— ТЕСТЫ ДЛЯ КОМАНД РЕДАКТИРОВАНИЯ FAQ
#
import handlers  # Импортируем сам модуль, чтобы динамически брать функции по имени
from handlers import BotEditStates

# Используем параметризацию: передаем имя функции-хэндлера, ожидаемый текст вопроса и целевой стейт
@pytest.mark.parametrize("handler_name, expected_text, expected_state", [
    ("edit_faq1", "📝 Пожалуйста, введите новый текст FAQ1:", BotEditStates.waiting_for_faq1),
    ("edit_faq2", "📝 Пожалуйста, введите новый текст FAQ2:", BotEditStates.waiting_for_faq2), # Исправьте опечатку в тексте, если в handlers.py написано FAQ1
    ("edit_faq3", "📝 Пожалуйста, введите новый текст FAQ3:", BotEditStates.waiting_for_faq3),
])
async def test_edit_faq_commands(handler_name, expected_text, expected_state):
    """Универсальный тест для команд редактирования FAQ 1, 2 и 3"""
    mock_message = AsyncMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_state = AsyncMock(spec=FSMContext)
    
    # Динамически достаем функцию из модуля handlers по её имени
    handler_function = getattr(handlers, handler_name)
    
    # Вызываем её
    await handler_function(mock_message, mock_state)
    
    # Проверяем текст и стейт
    mock_message.answer.assert_called_once_with(expected_text)
    mock_state.set_state.assert_called_once_with(expected_state)


#— ТЕСТЫ ДЛЯ КОМАНД reset_faq ——
#
@pytest.mark.parametrize("handler_name, expected_key, expected_message", [
    ("reset_faq1", "faq_1", "📝 Возвращаем первоначальный текст FAQ1"),
    ("reset_faq2", "faq_2", "📝 Возвращаем первоначальный текст FAQ2"),
    ("reset_faq3", "faq_3", "📝 Возвращаем первоначальный текст FAQ3"),
])
@patch('storage.reset_text')
async def test_reset_faq_commands(mock_reset_text, handler_name, expected_key, expected_message):
    """Универсальный тест для команд сброса FAQ 1, 2 и 3"""
    mock_message = AsyncMock(spec=Message)
    mock_message.answer = AsyncMock()
    
    # Динамически достаем функцию сброса из модуля handlers по её имени
    handler_function = getattr(handlers, handler_name)
    
    # Вызываем хэндлер
    await handler_function(mock_message)
    
    # Проверяем, что в storage ушел правильный ключ ("faq_1", "faq_2" или "faq_3")
    mock_reset_text.assert_called_once_with(expected_key)
    
    # Проверяем ответ бота пользователю
    # ВНИМАНИЕ: Если тексты сообщений в вашем handlers.py отличаются, скопируйте их точь-в-точь сюда
    mock_message.answer.assert_called_once_with(expected_message)



async def test_cmd_help():
    """Тестируем административную команду /help"""
    # 1. Создаем фейковое сообщение от пользователя
    mock_message = AsyncMock(spec=Message)
    mock_message.answer = AsyncMock()
    
    # 2. Вызываем хэндлер напрямую
    await cmd_help(mock_message)
    
    # 3. Проверяем, что бот отправил ответ ровно один раз
    mock_message.answer.assert_called_once()
    
    # 4. Достаем аргументы вызова
    args, kwargs = mock_message.answer.call_args
    
    # Текст может быть либо первым позиционным аргументом (args[0]), либо в kwargs["text"]
    help_text = args[0] if args else kwargs.get("text", "")
    
    # 5. Проверяем наличие ключевых строк
    assert "📝 Команды для администратора бота:" in help_text
    assert "/edit_welcome" in help_text
    assert "/reset_prices" in help_text








