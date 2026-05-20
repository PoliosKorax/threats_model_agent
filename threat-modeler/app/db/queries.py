"""CRUD операции и запросы к БД."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.db_models import (
    Threat, Violator, Object, Method, 
    Consequence, Tactic, Technique
)


async def get_all_threats(db: AsyncSession) -> List[Threat]:
    """Получить все угрозы с связями."""
    result = await db.execute(
        select(Threat)
        .options(
            selectinload(Threat.violator_int),
            selectinload(Threat.violator_ext),
            selectinload(Threat.objects),
            selectinload(Threat.methods),
            selectinload(Threat.consequences),
            selectinload(Threat.tactics),
            selectinload(Threat.techniques),
        )
    )
    return list(result.scalars().all())


async def get_threat_by_id(db: AsyncSession, threat_id: str) -> Optional[Threat]:
    """Получить угрозу по ID."""
    result = await db.execute(
        select(Threat)
        .where(Threat.id == threat_id)
        .options(
            selectinload(Threat.violator_int),
            selectinload(Threat.violator_ext),
            selectinload(Threat.objects),
            selectinload(Threat.methods),
            selectinload(Threat.consequences),
            selectinload(Threat.tactics),
            selectinload(Threat.techniques),
        )
    )
    return result.scalar_one_or_none()


async def get_all_violators(db: AsyncSession) -> List[Violator]:
    """Получить все уровни нарушителей."""
    result = await db.execute(select(Violator).order_by(Violator.level))
    return list(result.scalars().all())


async def get_all_objects(db: AsyncSession) -> List[Object]:
    """Получить все объекты воздействия."""
    result = await db.execute(select(Object).order_by(Object.code))
    return list(result.scalars().all())


async def get_all_methods(db: AsyncSession) -> List[Method]:
    """Получить все методы."""
    result = await db.execute(select(Method).order_by(Method.code))
    return list(result.scalars().all())


async def get_all_consequences(db: AsyncSession) -> List[Consequence]:
    """Получить все последствия."""
    result = await db.execute(select(Consequence).order_by(Consequence.code))
    return list(result.scalars().all())


async def get_all_tactics(db: AsyncSession) -> List[Tactic]:
    """Получить все тактики."""
    result = await db.execute(select(Tactic).order_by(Tactic.code))
    return list(result.scalars().all())


async def get_all_techniques(db: AsyncSession) -> List[Technique]:
    """Получить все техники."""
    result = await db.execute(select(Technique).order_by(Technique.code))
    return list(result.scalars().all())


async def get_threats_count(db: AsyncSession) -> int:
    """Получить количество угроз в БД."""
    result = await db.execute(select(func.count()).select_from(Threat))
    return result.scalar_one()
