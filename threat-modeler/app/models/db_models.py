"""SQLAlchemy модели для базы данных."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Text
from sqlalchemy.orm import relationship, DeclarativeBase
from typing import List


class Base(DeclarativeBase):
    """Базовый класс для моделей."""
    pass


# Таблицы многие-ко-многим
threat_violator_int = Table(
    "threat_violator_int",
    Base.metadata,
    Column("threat_id", String, ForeignKey("threats.id"), primary_key=True),
    Column("violator_level", String, ForeignKey("violators.level"), primary_key=True),
)

threat_violator_ext = Table(
    "threat_violator_ext",
    Base.metadata,
    Column("threat_id", String, ForeignKey("threats.id"), primary_key=True),
    Column("violator_level", String, ForeignKey("violators.level"), primary_key=True),
)

threat_objects = Table(
    "threat_objects",
    Base.metadata,
    Column("threat_id", String, ForeignKey("threats.id"), primary_key=True),
    Column("object_code", String, ForeignKey("objects.code"), primary_key=True),
)

threat_methods = Table(
    "threat_methods",
    Base.metadata,
    Column("threat_id", String, ForeignKey("threats.id"), primary_key=True),
    Column("method_code", String, ForeignKey("methods.code"), primary_key=True),
)

threat_consequences = Table(
    "threat_consequences",
    Base.metadata,
    Column("threat_id", String, ForeignKey("threats.id"), primary_key=True),
    Column("consequence_code", String, ForeignKey("consequences.code"), primary_key=True),
)

threat_tactics = Table(
    "threat_tactics",
    Base.metadata,
    Column("threat_id", String, ForeignKey("threats.id"), primary_key=True),
    Column("tactic_code", String, ForeignKey("tactics.code"), primary_key=True),
)

threat_techniques = Table(
    "threat_techniques",
    Base.metadata,
    Column("threat_id", String, ForeignKey("threats.id"), primary_key=True),
    Column("technique_code", String, ForeignKey("techniques.code"), primary_key=True),
)


class Threat(Base):
    """Модель угрозы (УБИ)."""
    
    __tablename__ = "threats"
    
    id = Column(String, primary_key=True, index=True)  # УБИ.001
    name = Column(Text, nullable=False)  # Наименование
    exclusion_note = Column(Text, nullable=True)  # Примечание из Таблицы 10
    
    # Флаги исключений (JSON как текст)
    requires_grid = Column(Boolean, default=False)
    requires_wifi = Column(Boolean, default=False)
    requires_mobile = Column(Boolean, default=False)
    requires_docker = Column(Boolean, default=False)
    requires_cloud = Column(Boolean, default=False)
    requires_smartcard = Column(Boolean, default=False)
    requires_ml = Column(Boolean, default=False)
    requires_supercomputer = Column(Boolean, default=False)
    requires_ics = Column(Boolean, default=False)
    external_responsibility = Column(Boolean, default=False)
    transborder = Column(Boolean, default=False)
    
    # Связи
    violator_int = relationship("Violator", secondary=threat_violator_int, backref="threats_int")
    violator_ext = relationship("Violator", secondary=threat_violator_ext, backref="threats_ext")
    objects = relationship("Object", secondary=threat_objects, backref="threats")
    methods = relationship("Method", secondary=threat_methods, backref="threats")
    consequences = relationship("Consequence", secondary=threat_consequences, backref="threats")
    tactics = relationship("Tactic", secondary=threat_tactics, backref="threats")
    techniques = relationship("Technique", secondary=threat_techniques, backref="threats")


class Violator(Base):
    """Модель нарушителя."""
    
    __tablename__ = "violators"
    
    level = Column(String, primary_key=True, index=True)  # Н1, Н2, Н3, Н4
    description = Column(Text, nullable=True)


class Object(Base):
    """Модель объекта воздействия."""
    
    __tablename__ = "objects"
    
    code = Column(String, primary_key=True, index=True)  # О1, О2, ... О17
    name = Column(Text, nullable=False)


class Method(Base):
    """Модель способа реализации угрозы."""
    
    __tablename__ = "methods"
    
    code = Column(String, primary_key=True, index=True)  # СП1, СП2, ... СП9
    name = Column(Text, nullable=False)


class Consequence(Base):
    """Модель негативного последствия."""
    
    __tablename__ = "consequences"
    
    code = Column(String, primary_key=True, index=True)  # П1, П2, ... П17
    name = Column(Text, nullable=False)


class Tactic(Base):
    """Модель тактики."""
    
    __tablename__ = "tactics"
    
    code = Column(String, primary_key=True, index=True)  # Т2, Т6, ...
    name = Column(Text, nullable=False)


class Technique(Base):
    """Модель техники."""
    
    __tablename__ = "techniques"
    
    code = Column(String, primary_key=True, index=True)  # Т2.5, Т6.3, ...
    name = Column(Text, nullable=False)
