"""Движок корреляции для фильтрации угроз."""

from typing import List, Dict, Set, Optional
from app.models.schemas import UserProfile, SystemProfile, ViolatorProfile
from app.models.db_models import Threat


# Уровень нарушителя: Н1 > Н2 > Н3 > Н4 (Н1 - самый высокий)
VIOLATOR_LEVEL_ORDER = {"Н1": 1, "Н2": 2, "Н3": 3, "Н4": 4}


def level_gte(profile_level: str, threat_level: str) -> bool:
    """
    Проверка: уровень нарушителя в профиле >= уровня в угрозе.
    Н1 >= Н2 (True), Н2 >= Н1 (False)
    """
    if not profile_level or not threat_level:
        return True
    
    profile_rank = VIOLATOR_LEVEL_ORDER.get(profile_level, 4)
    threat_rank = VIOLATOR_LEVEL_ORDER.get(threat_level, 4)
    
    # Чем меньше число, тем выше уровень
    return profile_rank <= threat_rank


def check_violator_levels(
    profile: ViolatorProfile, 
    threat: Threat
) -> bool:
    """
    Проверка соответствия уровней нарушителей.
    Если в профиле указан уровень, угроза должна иметь уровень <= профиля.
    """
    # Проверка внешних нарушителей
    if profile.external_level and threat.violator_ext:
        threat_levels_ext = [v.level for v in threat.violator_ext]
        if not any(level_gte(profile.external_level, lvl) for lvl in threat_levels_ext):
            return False
    
    # Проверка внутренних нарушителей
    if profile.internal_level and threat.violator_int:
        threat_levels_int = [v.level for v in threat.violator_int]
        if not any(level_gte(profile.internal_level, lvl) for lvl in threat_levels_int):
            return False
    
    return True


def check_objects(
    selected_objects: List[str], 
    threat: Threat
) -> bool:
    """
    Проверка объектов воздействия.
    Если выбраны объекты, угроза должна затрагивать хотя бы один из них.
    """
    if not selected_objects:
        return True  # Если объекты не выбраны, пропускаем все
    
    threat_objects = {obj.code for obj in threat.objects}
    selected_set = set(selected_objects)
    
    return bool(threat_objects & selected_set)


def check_exclusion_flags(
    system: SystemProfile, 
    threat: Threat
) -> bool:
    """
    Проверка флагов исключений из Таблицы 10.
    Если угроза требует технологию, которая не используется → исключать.
    """
    # Grid-технологии
    if threat.requires_grid and not system.uses_grid:
        return False
    
    # Wi-Fi
    if threat.requires_wifi and not system.uses_wifi:
        return False
    
    # Мобильные устройства
    if threat.requires_mobile and not system.uses_mobile:
        return False
    
    # Docker/контейнеры
    if threat.requires_docker and not system.uses_docker:
        return False
    
    # Облачные технологии
    if threat.requires_cloud and not system.uses_cloud:
        return False
    
    # Смарт-карты
    if threat.requires_smartcard and not system.uses_smartcard:
        return False
    
    # Машинное обучение
    if threat.requires_ml and not system.uses_ml:
        return False
    
    # Суперкомпьютер
    if threat.requires_supercomputer and not system.uses_supercomputer:
        return False
    
    # Промышленные системы (ICS)
    if threat.requires_ics and not system.uses_ics:
        return False
    
    # Внешняя ответственность
    if threat.external_responsibility:
        # Если в угрозе указано "Ответственность на внешней организации"
        # и пользователь НЕ подтвердил внешнюю ответственность → исключать
        if not system.external_responsibility:
            return False
    
    # Трансграничная передача
    if threat.transborder and not system.transborder:
        return False
    
    return True


def check_interfaces(
    interfaces: List[str], 
    threat: Threat
) -> bool:
    """
    Проверка интерфейсов.
    Некоторые угрозы требуют определённые интерфейсы.
    """
    if not interfaces:
        return True
    
    # Удалённый доступ (RDP/SSH)
    if "remote_desktop" in interfaces:
        return True  # Угрозы с удалённым доступом применимы
    
    # Веб-интерфейсы
    if "web" in interfaces:
        return True
    
    # VPN
    if "vpn" in interfaces:
        return True
    
    # Физический доступ
    if "physical" in interfaces:
        return True
    
    # Беспроводные сети
    if "wireless" in interfaces and threat.requires_wifi:
        return True
    
    return True


def filter_threats(
    threats: List[Threat], 
    profile: UserProfile
) -> List[Threat]:
    """
    Главная функция фильтрации угроз.
    
    Цепочка: Нарушитель → Интерфейс → Объект → Воздействие → Метод → Последствие → УБИ
    
    Args:
        threats: Список всех угроз из БД
        profile: Профиль пользователя
    
    Returns:
        Отфильтрованный список угроз
    """
    filtered = []
    
    for threat in threats:
        # 1. Проверка уровней нарушителей
        if not check_violator_levels(profile.violators, threat):
            continue
        
        # 2. Проверка объектов воздействия
        if not check_objects(profile.selected_objects, threat):
            continue
        
        # 3. Проверка флагов исключений
        if not check_exclusion_flags(profile.system, threat):
            continue
        
        # 4. Проверка интерфейсов
        if not check_interfaces(profile.interfaces, threat):
            continue
        
        # Все проверки пройдены
        filtered.append(threat)
    
    return filtered


def get_possible_consequences(
    object_code: str, 
    impact_code: str,
    consequence_map: Dict[str, Dict[str, List[str]]]
) -> List[str]:
    """
    Получить возможные последствия для объекта и воздействия.
    Использует таблицу соответствий из методик ФСТЭК.
    """
    return consequence_map.get(object_code, {}).get(impact_code, [])


class CorrelationEngine:
    """
    Движок корреляции для определения релевантных угроз.
    """
    
    def __init__(self, consequence_map: Optional[Dict] = None):
        self.consequence_map = consequence_map or {}
    
    def correlate(
        self, 
        threats: List[Threat], 
        profile: UserProfile
    ) -> List[Threat]:
        """Выполнить корреляцию и фильтрацию угроз."""
        return filter_threats(threats, profile)
    
    def validate_profile(self, profile: UserProfile) -> List[str]:
        """
        Валидация профиля пользователя.
        Возвращает список ошибок.
        """
        errors = []
        
        # Проверка: если ПДн обрабатываются, должен быть уровень
        if profile.system.processes_pd and not profile.system.pd_security_level:
            errors.append("Укажите уровень защищённости ПДн")
        
        # Проверка: уровни нарушителей должны быть валидными
        valid_levels = {"Н1", "Н2", "Н3", "Н4"}
        if profile.violators.external_level and \
           profile.violators.external_level not in valid_levels:
            errors.append("Неверный уровень внешнего нарушителя")
        
        if profile.violators.internal_level and \
           profile.violators.internal_level not in valid_levels:
            errors.append("Неверный уровень внутреннего нарушителя")
        
        return errors
