#
# Демо-версия для GitHub
#

from aiogram.filters import BaseFilter
from aiogram.types import Message
from config import ADMIN_IDS, IS_DEMO

class IsAdminFilter(BaseFilter):
    """Фильтр проверяет, является ли пользователь администратором бота.
    Поддерживает безопасный демо-режим для демонстрации рекрутерам.
    """
    async def __call__(self, message: Message) -> bool:
        # Если включен демо-режим, даем доступ всем пользователям
        if IS_DEMO:
            return True
            
        # В обычном режиме строго проверяем наличие ID в списке администраторов
        if not message.from_user:
            return False
        return message.from_user.id in ADMIN_IDS
