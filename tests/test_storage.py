import os
import json
import pytest

# Подтягиваем ваши реальные функции и эталоны
from storage import load_texts, save_texts, update_text, reset_text, DATA_FILE
from config import ETALON_TEXTS

@pytest.fixture(autouse=True)
def clean_test_environment():
    """Фикстура: выполняется ДО и ПОСЛЕ каждого теста.
    Она сохраняет вашу реальную базу, а после теста возвращает её на место."""
    backup_exists = os.path.exists(DATA_FILE)
    if backup_exists:
        os.rename(DATA_FILE, "backup_bot_texts.json")
    
    yield  # Здесь запускается сам тест
    
    # После теста удаляем мусор и возвращаем бэкап
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    if backup_exists:
        os.rename("backup_bot_texts.json", DATA_FILE)


def test_load_texts_creates_file_if_not_exists():
    """Тест 1: Проверяем, что если файла нет, он создается с эталонами"""
    assert not os.path.exists(DATA_FILE)
    
    texts = load_texts()
    
    assert os.path.exists(DATA_FILE)
    assert texts == ETALON_TEXTS


def test_update_text():
    """Тест 2: Проверяем, что текст успешно обновляется в файле"""
    # Берем первый попавшийся ключ из ваших эталонов
    test_key = list(ETALON_TEXTS.keys())[0] 
    new_value = "Это совершенно новый тестовый текст"
    
    update_text(test_key, new_value)
    
    # Читаем файл заново и проверяем, записалось ли
    updated_texts = load_texts()
    assert updated_texts[test_key] == new_value


def test_load_texts_handles_corrupted_json():
    """Тест 3: Проверяем отказоустойчивость при битом JSON"""
    # Записываем в файл сломанный JSON (не закрыли скобку)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write("{ 'invalid_json': ") 
        
    # Вызываем загрузку. Бот не должен упасть по Exception!
    texts = load_texts()
    
    # Проверяем, что функция вернула эталоны вместо падения
    assert texts == ETALON_TEXTS
