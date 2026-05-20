"""Валидация входных данных wizard."""

from typing import List, Dict, Any, Tuple
from app.models.schemas import UserProfile, SystemProfile, ViolatorProfile


VALID_VIOLATOR_LEVELS = {"Н1", "Н2", "Н3", "Н4"}
VALID_PD_LEVELS = {1, 2, 3, 4}

VALID_EXTERNAL_TYPES = {
    "criminal_groups",
    "hackers", 
    "competitors",
    "former_employees",
    "vendors",
    "isp"
}

VALID_INTERNAL_TYPES = {
    "users",
    "admins",
    "isp_internal",
    "vendors_internal"
}

VALID_INTERFACES = {
    "web",
    "remote_desktop",
    "vpn",
    "physical",
    "wireless"
}


def validate_system_profile(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Валидация профиля системы.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Проверка уровня ПДн
    if data.get("processes_pd") and data.get("pd_security_level"):
        level = data["pd_security_level"]
        if isinstance(level, str):
            try:
                level = int(level)
            except ValueError:
                errors.append("Уровень ПДн должен быть числом")
        
        if isinstance(level, int) and level not in VALID_PD_LEVELS:
            errors.append(f"Уровень ПДн должен быть в диапазоне 1-4, получено {level}")
    
    # Проверка: если есть внешняя ответственность, должно быть указано название
    if data.get("external_responsibility") and not data["external_responsibility"].strip():
        errors.append("Укажите организацию с внешней ответственностью")
    
    return len(errors) == 0, errors


def validate_violator_profile(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Валидация профиля нарушителя.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Проверка уровней
    ext_level = data.get("external_level")
    if ext_level and ext_level not in VALID_VIOLATOR_LEVELS:
        errors.append(f"Неверный уровень внешнего нарушителя: {ext_level}")
    
    int_level = data.get("internal_level")
    if int_level and int_level not in VALID_VIOLATOR_LEVELS:
        errors.append(f"Неверный уровень внутреннего нарушителя: {int_level}")
    
    # Проверка типов нарушителей
    ext_types = data.get("external_types", [])
    for ext_type in ext_types:
        if ext_type not in VALID_EXTERNAL_TYPES:
            errors.append(f"Неверный тип внешнего нарушителя: {ext_type}")
    
    int_types = data.get("internal_types", [])
    for int_type in int_types:
        if int_type not in VALID_INTERNAL_TYPES:
            errors.append(f"Неверный тип внутреннего нарушителя: {int_type}")
    
    return len(errors) == 0, errors


def validate_interfaces(interfaces: List[str]) -> Tuple[bool, List[str]]:
    """
    Валидация интерфейсов.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    for interface in interfaces:
        if interface not in VALID_INTERFACES:
            errors.append(f"Неверный интерфейс: {interface}")
    
    return len(errors) == 0, errors


def validate_user_profile(profile: UserProfile) -> Tuple[bool, List[str]]:
    """
    Полная валидация профиля пользователя.
    
    Returns:
        (is_valid, list_of_errors)
    """
    all_errors = []
    
    # Валидация системного профиля
    system_dict = profile.system.model_dump()
    sys_valid, sys_errors = validate_system_profile(system_dict)
    all_errors.extend(sys_errors)
    
    # Валидация профиля нарушителей
    violator_dict = profile.violators.model_dump()
    viol_valid, viol_errors = validate_violator_profile(violator_dict)
    all_errors.extend(viol_errors)
    
    # Валидация интерфейсов
    intf_valid, intf_errors = validate_interfaces(profile.interfaces)
    all_errors.extend(intf_errors)
    
    return len(all_errors) == 0, all_errors


class WizardValidator:
    """Валидатор для wizard."""
    
    def __init__(self):
        self.errors: List[str] = []
    
    def validate_step(self, step: int, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Валидация конкретного шага wizard.
        
        Args:
            step: Номер шага (1-5)
            data: Данные шага
        
        Returns:
            (is_valid, errors)
        """
        if step == 1:
            return validate_system_profile(data)
        elif step == 2:
            return validate_violator_profile(data)
        elif step == 3:
            return validate_interfaces(data.get("interfaces", []))
        elif step == 4:
            # Объекты - опциональны, валидация не требуется
            return True, []
        elif step == 5:
            # Финальный шаг - полная валидация
            # Требуется UserProfile, который собирается из всех шагов
            return True, []
        else:
            return False, [f"Неверный номер шага: {step}"]
    
    def clear_errors(self):
        """Очистить список ошибок."""
        self.errors = []
