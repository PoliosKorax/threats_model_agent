"""Pydantic схемы для валидации данных."""

from pydantic import BaseModel, Field
from typing import Optional


class SystemProfile(BaseModel):
    """Профиль информационной системы."""
    
    processes_pd: bool = Field(default=False, description="Обработка персональных данных")
    pd_security_level: Optional[int] = Field(default=None, ge=1, le=4, description="Уровень защищённости ПДн (1-4)")
    uses_cloud: bool = Field(default=False, description="Использование облачных технологий")
    uses_virtualization: bool = Field(default=False, description="Использование виртуализации")
    external_responsibility: Optional[str] = Field(default=None, description="Внешняя ответственность (например, 'ООО Кортэл')")
    uses_grid: bool = Field(default=False, description="Использование грид-технологий")
    uses_ics: bool = Field(default=False, description="Использование промышленных систем (ICS/SCADA)")
    uses_mobile: bool = Field(default=False, description="Использование мобильных устройств")
    uses_docker: bool = Field(default=False, description="Использование Docker/контейнеров")
    uses_wifi: bool = Field(default=False, description="Использование Wi-Fi")
    has_internet_access: bool = Field(default=False, description="Доступ в Интернет")
    uses_l3vpn: bool = Field(default=False, description="Использование L3VPN")
    uses_vipnet: bool = Field(default=False, description="Использование ViPNet")
    uses_removable_media: bool = Field(default=False, description="Использование съёмных носителей")
    uses_remote_desktop: bool = Field(default=False, description="Удалённый доступ (RDP/SSH)")
    uses_smartcard: bool = Field(default=False, description="Использование смарт-карт")
    uses_ml: bool = Field(default=False, description="Использование машинного обучения")
    uses_supercomputer: bool = Field(default=False, description="Использование суперкомпьютера")
    transborder: bool = Field(default=False, description="Трансграничная передача данных")


class ViolatorProfile(BaseModel):
    """Профиль нарушителя."""
    
    external_types: list[str] = Field(default_factory=list, description="Типы внешних нарушителей")
    external_level: Optional[str] = Field(default=None, description="Уровень внешних нарушителей (Н1-Н4)")
    internal_types: list[str] = Field(default_factory=list, description="Типы внутренних нарушителей")
    internal_level: Optional[str] = Field(default=None, description="Уровень внутренних нарушителей (Н1-Н4)")


class UserProfile(BaseModel):
    """Полный профиль пользователя (состояние wizard)."""
    
    system: SystemProfile = Field(default_factory=SystemProfile)
    violators: ViolatorProfile = Field(default_factory=ViolatorProfile)
    interfaces: list[str] = Field(default_factory=list, description="Выбранные интерфейсы")
    selected_objects: list[str] = Field(default_factory=list, description="Выбранные объекты воздействия")
    current_step: int = Field(default=1, ge=1, le=5, description="Текущий шаг wizard")


class ThreatFilter(BaseModel):
    """Фильтр для угроз."""
    
    user_profile: UserProfile
    exclude_impossible: bool = Field(default=True, description="Исключить невозможные угрозы")


class ExcelRow(BaseModel):
    """Строка для экспорта в Excel."""
    
    ubi_id: str = Field(description="Идентификатор УБИ")
    ubi_name: str = Field(description="Наименование УБИ")
    violator_internal: str = Field(description="Уровень нарушителя (Внутренний)")
    violator_external: str = Field(description="Уровень нарушителя (Внешний)")
    objects: str = Field(description="Объект воздействия")
    methods: str = Field(description="Способы реализации")
    consequences: str = Field(description="Негативные последствия")
    tactics: str = Field(description="Тактика")
    techniques: str = Field(description="Техника")
    notes: str = Field(default="", description="Примечания")
