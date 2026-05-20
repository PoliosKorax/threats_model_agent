"""Вспомогательные утилиты."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("threat-modeler")


def get_timestamp() -> str:
    """Получить текущую метку времени в формате для имён файлов."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def generate_filename(prefix: str, extension: str = "xlsx") -> str:
    """
    Сгенерировать имя файла с меткой времени.
    
    Args:
        prefix: Префикс имени файла
        extension: Расширение файла
    
    Returns:
        Имя файла вида "{prefix}_{timestamp}.{extension}"
    """
    return f"{prefix}_{get_timestamp()}.{extension}"


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Безопасное получение значения из словаря.
    
    Args:
        data: Словарь
        key: Ключ
        default: Значение по умолчанию
    
    Returns:
        Значение или default
    """
    return data.get(key, default)


def join_non_empty(items: List[Any], separator: str = ", ") -> str:
    """
    Объединить непустые элементы списка.
    
    Args:
        items: Список элементов
        separator: Разделитель
    
    Returns:
        Строка с объединёнными элементами
    """
    return separator.join(str(item) for item in items if item)


def normalize_level(level: Optional[str]) -> str:
    """
    Нормализовать уровень нарушителя.
    
    Args:
        level: Уровень (Н1, Н2, Н3, Н4)
    
    Returns:
        Нормализованный уровень или пустую строку
    """
    if not level:
        return ""
    return str(level).strip().upper()


class Helpers:
    """Набор вспомогательных функций."""
    
    @staticmethod
    def format_threat_id(threat_id: str) -> str:
        """Форматировать ID угрозы."""
        return threat_id.strip().upper()
    
    @staticmethod
    def is_valid_threat_id(threat_id: str) -> bool:
        """Проверить валидность ID угрозы (формат УБИ.XXX)."""
        if not threat_id:
            return False
        return threat_id.upper().startswith("УБИ.")
    
    @staticmethod
    def truncate_string(s: str, max_length: int = 100) -> str:
        """Обрезать строку до максимальной длины."""
        if not s or len(s) <= max_length:
            return s or ""
        return s[:max_length - 3] + "..."
