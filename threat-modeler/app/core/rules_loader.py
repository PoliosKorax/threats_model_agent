"""Загрузка YAML-правил корреляции."""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from app.config import settings


def load_yaml_rules(filename: str) -> Dict[str, Any]:
    """
    Загрузить YAML-файл с правилами.
    
    Args:
        filename: Имя файла в директории data/rules/
    
    Returns:
        Словарь с правилами
    """
    rules_path = Path(settings.data_dir) / "rules" / filename
    
    if not rules_path.exists():
        return {}
    
    with open(rules_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_correlation_rules() -> Dict[str, Any]:
    """Загрузить правила корреляции из correlation.yaml."""
    return load_yaml_rules("correlation.yaml")


def load_exclusion_flags() -> Dict[str, List[str]]:
    """
    Загрузить флаги исключений из exclusion_flags.yaml.
    
    Returns:
        Dict[UBI_ID, List[flag_names]]
    """
    return load_yaml_rules("exclusion_flags.yaml")


def load_consequence_map() -> Dict[str, Dict[str, List[str]]]:
    """
    Загрузить карту последствий (Таблица 3).
    
    Returns:
        Dict[object_code, Dict[impact_code, List[consequence_codes]]]
    """
    return load_yaml_rules("consequence_map.yaml")


def get_threat_exclusion_flags(
    threat_id: str, 
    exclusion_flags: Optional[Dict[str, List[str]]] = None
) -> Dict[str, bool]:
    """
    Получить флаги исключений для конкретной угрозы.
    
    Args:
        threat_id: ID угрозы (например, "УБИ.001")
        exclusion_flags: Словарь флагов из YAML
    
    Returns:
        Dict[flag_name, is_required]
    """
    if exclusion_flags is None:
        exclusion_flags = load_exclusion_flags()
    
    flags_for_threat = exclusion_flags.get(threat_id, [])
    
    # Преобразуем список флагов в dict
    result = {
        "requires_grid": "requires_grid" in flags_for_threat,
        "requires_wifi": "requires_wifi" in flags_for_threat,
        "requires_mobile": "requires_mobile" in flags_for_threat,
        "requires_docker": "requires_docker" in flags_for_threat,
        "requires_cloud": "requires_cloud" in flags_for_threat,
        "requires_smartcard": "requires_smartcard" in flags_for_threat,
        "requires_ml": "requires_ml" in flags_for_threat,
        "requires_supercomputer": "requires_supercomputer" in flags_for_threat,
        "requires_ics": "requires_ics" in flags_for_threat,
        "external_responsibility": "external_responsibility" in flags_for_threat,
        "transborder": "transborder" in flags_for_threat,
    }
    
    return result


class RulesLoader:
    """Загрузчик правил корреляции из YAML."""
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else Path(settings.data_dir)
        self._correlation_rules: Optional[Dict] = None
        self._exclusion_flags: Optional[Dict] = None
        self._consequence_map: Optional[Dict] = None
    
    @property
    def correlation_rules(self) -> Dict:
        """Ленивая загрузка правил корреляции."""
        if self._correlation_rules is None:
            self._correlation_rules = load_correlation_rules()
        return self._correlation_rules
    
    @property
    def exclusion_flags(self) -> Dict:
        """Ленивая загрузка флагов исключений."""
        if self._exclusion_flags is None:
            self._exclusion_flags = load_exclusion_flags()
        return self._exclusion_flags
    
    @property
    def consequence_map(self) -> Dict:
        """Ленивая загрузка карты последствий."""
        if self._consequence_map is None:
            self._consequence_map = load_consequence_map()
        return self._consequence_map
    
    def reload_all(self):
        """Перезагрузить все правила."""
        self._correlation_rules = None
        self._exclusion_flags = None
        self._consequence_map = None
        _ = self.correlation_rules
        _ = self.exclusion_flags
        _ = self.consequence_map
