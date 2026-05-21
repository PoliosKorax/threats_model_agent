"""Инициализация БД и seed-данные."""

import json
import asyncio
from pathlib import Path
from sqlalchemy import select, insert
from app.db.engine import engine, AsyncSessionLocal
from app.models.db_models import (
    Threat, Violator, Object, Method, 
    Consequence, Tactic, Technique, Base,
    threat_violator_int, threat_violator_ext,
    threat_objects, threat_methods, threat_consequences,
    threat_tactics, threat_techniques
)
from app.config import settings


async def seed_database():
    """Заполнение БД начальными данными из JSON."""
    
    seed_path = Path(settings.data_dir) / "seed" / "threats_full.json"
    
    if not seed_path.exists():
        print(f"⚠️  Seed file not found: {seed_path}")
        print("Creating empty database schema...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return
    
    print(f"📥 Loading seed data from {seed_path}...")
    
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Создаём таблицы через sync connection
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        
        # Вставка нарушителей (Н1-Н4)
        violators = [
            {"level": "Н1", "description": "Нарушитель с высоким уровнем возможностей"},
            {"level": "Н2", "description": "Нарушитель со средним уровнем возможностей"},
            {"level": "Н3", "description": "Нарушитель с низким уровнем возможностей"},
            {"level": "Н4", "description": "Нарушитель с минимальным уровнем возможностей"},
        ]
        for v in violators:
            stmt = insert(Violator).values(**v).prefix_with("OR IGNORE")
            await session.execute(stmt)
        
        # Вставка объектов (О1-О17)
        objects = [
            {"code": "О1", "name": "Персональные данные"},
            {"code": "О2", "name": "Информационные системы"},
            {"code": "О3", "name": "Средства вычислительной техники"},
            {"code": "О4", "name": "Системы хранения данных"},
            {"code": "О5", "name": "Сетевое оборудование"},
            {"code": "О6", "name": "Программное обеспечение"},
            {"code": "О7", "name": "Средства защиты информации"},
            {"code": "О8", "name": "Криптографические средства"},
            {"code": "О9", "name": "BIOS/UEFI"},
            {"code": "О10", "name": "Мобильные устройства"},
            {"code": "О11", "name": "Съёмные носители"},
            {"code": "О12", "name": "Промышленные системы"},
            {"code": "О13", "name": "Облачные сервисы"},
            {"code": "О14", "name": "Виртуальные машины"},
            {"code": "О15", "name": "Контейнеры"},
            {"code": "О16", "name": "Сетевые протоколы"},
            {"code": "О17", "name": "Физическая инфраструктура"},
        ]
        for o in objects:
            stmt = insert(Object).values(**o).prefix_with("OR IGNORE")
            await session.execute(stmt)
        
        # Вставка методов (СП1-СП9)
        methods = [
            {"code": "СП1", "name": "Несанкционированный доступ"},
            {"code": "СП2", "name": "Перехват данных"},
            {"code": "СП3", "name": "Модификация данных"},
            {"code": "СП4", "name": "Уничтожение данных"},
            {"code": "СП5", "name": "Блокирование доступа"},
            {"code": "СП6", "name": "Анализ трафика"},
            {"code": "СП7", "name": "Социальная инженерия"},
            {"code": "СП8", "name": "Эксплуатация уязвимостей"},
            {"code": "СП9", "name": "Внедрение вредоносного ПО"},
        ]
        for m in methods:
            stmt = insert(Method).values(**m).prefix_with("OR IGNORE")
            await session.execute(stmt)
        
        # Вставка последствий (П1-П17)
        consequences = [
            {"code": "П1", "name": "Утечка ПДн"},
            {"code": "П2", "name": "Нарушение конфиденциальности"},
            {"code": "П3", "name": "Нарушение целостности"},
            {"code": "П4", "name": "Нарушение доступности"},
            {"code": "П5", "name": "Финансовые потери"},
            {"code": "П6", "name": "Репутационный ущерб"},
            {"code": "П7", "name": "Юридическая ответственность"},
            {"code": "П8", "name": "Остановка бизнес-процессов"},
            {"code": "П9", "name": "Компрометация ключей"},
            {"code": "П10", "name": "Нарушение работы СКЗИ"},
            {"code": "П11", "name": "Потеря данных"},
            {"code": "П12", "name": "Несанкционированное изменение конфигурации"},
            {"code": "П13", "name": "Отказ в обслуживании"},
            {"code": "П14", "name": "Компрометация системы"},
            {"code": "П15", "name": "Распространение вредоносного ПО"},
            {"code": "П16", "name": "Нарушение физической безопасности"},
            {"code": "П17", "name": "Другие последствия"},
        ]
        for c in consequences:
            stmt = insert(Consequence).values(**c).prefix_with("OR IGNORE")
            await session.execute(stmt)
        
        # Вставка тактик
        tactics_data = data.get("tactics", [])
        for t in tactics_data:
            stmt = insert(Tactic).values(**t).prefix_with("OR IGNORE")
            await session.execute(stmt)
        
        # Вставка техник
        techniques_data = data.get("techniques", [])
        for tech in techniques_data:
            stmt = insert(Technique).values(**tech).prefix_with("OR IGNORE")
            await session.execute(stmt)
        
        # Вставка угроз
        threats_data = data.get("threats", [])
        for threat in threats_data:
            # Основная запись угрозы
            threat_data = {
                "id": threat["id"],
                "name": threat["name"],
                "exclusion_note": threat.get("exclusion_note"),
                "requires_grid": threat.get("exclusion_flags", {}).get("requires_grid", False),
                "requires_wifi": threat.get("exclusion_flags", {}).get("requires_wifi", False),
                "requires_mobile": threat.get("exclusion_flags", {}).get("requires_mobile", False),
                "requires_docker": threat.get("exclusion_flags", {}).get("requires_docker", False),
                "requires_cloud": threat.get("exclusion_flags", {}).get("requires_cloud", False),
                "requires_smartcard": threat.get("exclusion_flags", {}).get("requires_smartcard", False),
                "requires_ml": threat.get("exclusion_flags", {}).get("requires_ml", False),
                "requires_supercomputer": threat.get("exclusion_flags", {}).get("requires_supercomputer", False),
                "requires_ics": threat.get("exclusion_flags", {}).get("requires_ics", False),
                "external_responsibility": threat.get("exclusion_flags", {}).get("external_responsibility", False),
                "transborder": threat.get("exclusion_flags", {}).get("transborder", False),
            }
            stmt = insert(Threat).values(**threat_data).prefix_with("OR IGNORE")
            await session.execute(stmt)
            
            # Связи с нарушителями (внутренние)
            for violator_level in threat.get("violator_int", []):
                stmt = insert(threat_violator_int).values(
                    threat_id=threat["id"],
                    violator_level=violator_level
                ).prefix_with("OR IGNORE")
                await session.execute(stmt)
            
            # Связи с нарушителями (внешние)
            for violator_level in threat.get("violator_ext", []):
                stmt = insert(threat_violator_ext).values(
                    threat_id=threat["id"],
                    violator_level=violator_level
                ).prefix_with("OR IGNORE")
                await session.execute(stmt)
            
            # Связи с объектами
            for obj_code in threat.get("objects", []):
                stmt = insert(threat_objects).values(
                    threat_id=threat["id"],
                    object_code=obj_code
                ).prefix_with("OR IGNORE")
                await session.execute(stmt)
            
            # Связи с методами
            for method_code in threat.get("methods", []):
                stmt = insert(threat_methods).values(
                    threat_id=threat["id"],
                    method_code=method_code
                ).prefix_with("OR IGNORE")
                await session.execute(stmt)
            
            # Связи с последствиями
            for consequence_code in threat.get("consequences", []):
                stmt = insert(threat_consequences).values(
                    threat_id=threat["id"],
                    consequence_code=consequence_code
                ).prefix_with("OR IGNORE")
                await session.execute(stmt)
            
            # Связи с тактиками
            for tactic_code in threat.get("tactics", []):
                stmt = insert(threat_tactics).values(
                    threat_id=threat["id"],
                    tactic_code=tactic_code
                ).prefix_with("OR IGNORE")
                await session.execute(stmt)
            
            # Связи с техниками
            for technique_code in threat.get("techniques", []):
                stmt = insert(threat_techniques).values(
                    threat_id=threat["id"],
                    technique_code=technique_code
                ).prefix_with("OR IGNORE")
                await session.execute(stmt)
        
        await session.commit()
        print(f"✅ Database seeded with {len(threats_data)} threats")


if __name__ == "__main__":
    asyncio.run(seed_database())
