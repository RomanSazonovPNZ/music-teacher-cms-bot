import json
import os
from config import ETALON_TEXTS

DATA_FILE = "bot_texts.json"

def load_texts() -> dict:
    """Загружает тексты из JSON. Если файла нет, создает его на базе эталонов."""
    if not os.path.exists(DATA_FILE):
        save_texts(ETALON_TEXTS)
        return ETALON_TEXTS.copy()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            # Объединяем на случай, если в будущем добавятся новые ключи
            return {**ETALON_TEXTS, **json.load(f)}
    except Exception:
        return ETALON_TEXTS.copy()

def save_texts(texts: dict):
    """Сохраняет текущие тексты на диск."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=4)

def update_text(key: str, new_text: str):
    """Обновляет один конкретный ключ и сохраняет файл."""
    texts = load_texts()
    texts[key] = new_text
    save_texts(texts)

def reset_text(key: str):
    """Сбрасывает текст к эталонному значению."""
    texts = load_texts()
    texts[key] = ETALON_TEXTS[key]
    save_texts(texts)