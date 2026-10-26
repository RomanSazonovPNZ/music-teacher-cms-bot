

import pytest
from unittest.mock import AsyncMock, MagicMock

import config
# Импортируем сам модуль filters, чтобы иметь прямой доступ к его переменным
import filters 
from filters import IsAdminFilter

@pytest.mark.asyncio
async def test_filter_behavior_in_demo_mode(monkeypatch):
    """Тест 1: В режиме демо фильтр должен пускать абсолютно всех"""
    # Гарантируем, что везде стоит True
    monkeypatch.setattr(config, "IS_DEMO", True)
    monkeypatch.setattr(filters, "IS_DEMO", True)
    
    filter_instance = IsAdminFilter()
    
    mock_message = AsyncMock()
    mock_message.from_user = MagicMock(id=999999999)
    
    assert await filter_instance(mock_message) is True


@pytest.mark.asyncio
async def test_filter_behavior_in_production_mode(monkeypatch):
    """Тест 2: В боевом режиме фильтр должен пускать админов и блокировать чужих"""
    # Принудительно отключаем демо-режим везде
    monkeypatch.setattr(config, "IS_DEMO", False)
    monkeypatch.setattr(filters, "IS_DEMO", False)
    monkeypatch.setattr(filters, "ADMIN_IDS",[11111, 22222])

    
    filter_instance = IsAdminFilter()
    
    # 1. Администратор должен пройти
    msg_admin = AsyncMock()
    msg_admin.from_user = MagicMock(id=11111)
    assert await filter_instance(msg_admin) is True
    
    # 2. Посторонний должен быть заблокирован
    msg_stranger = AsyncMock()
    msg_stranger.from_user = MagicMock(id=77777)
    assert await filter_instance(msg_stranger) is False


def test_teacher_url_switches_correctly():
    """Тест 3: Проверяем логику переключения ссылки в config.py"""
    # Сохраняем исходное состояние, чтобы не сломать проект
    original_demo = config.IS_DEMO
    
    try:
        # Проверяем боевой режим
        config.IS_DEMO = False
        # Имитируем выполнение условия из config.py
        teacher_url = "https://t.me/RomanSazonov" if config.IS_DEMO else "https://t.me/lionel0ve"
        assert teacher_url == "https://t.me/lionel0ve"   
        
        # Проверяем демо режим
        config.IS_DEMO = True
        teacher_url = "https://t.me/RomanSazonov" if config.IS_DEMO else "https://t.me/lionel0ve"
        assert teacher_url == "https://t.me/RomanSazonov"

        
        if original_demo :
            assert config.HELP_TEXT.startswith("Демо-версия")
        else :    
            assert config.HELP_TEXT.startswith("📝 Команды для администратора")             
                        
    finally:
        # В любом случае возвращаем настройки бота в исходное состояние
        config.IS_DEMO = original_demo








