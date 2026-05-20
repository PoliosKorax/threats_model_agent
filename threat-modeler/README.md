# Генератор моделей угроз ФСТЭК

Локальное Python-приложение для генерации моделей угроз безопасности информации согласно методике ФСТЭК 2021.

## 🚀 Быстрый старт

### Через Docker (рекомендуется)

```bash
cd threat-modeler

# Копирование .env.example в .env
cp .env.example .env

# Сборка и запуск
docker-compose up --build

# Приложение доступно по адресу http://localhost:8000
```

### Локальный запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Инициализация БД
python -m app.db.init

# Запуск сервера
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Структура проекта

```
threat-modeler/
├── app/
│   ├── main.py                 # FastAPI приложение
│   ├── config.py               # Настройки
│   ├── api/
│   │   ├── endpoints/
│   │   │   └── wizard.py       # Wizard endpoints
│   │   └── dependencies.py     # Зависимости
│   ├── core/
│   │   ├── correlation.py      # Логика фильтрации угроз
│   │   ├── rules_loader.py     # Загрузка YAML правил
│   │   └── validator.py        # Валидация данных
│   ├── models/
│   │   ├── schemas.py          # Pydantic схемы
│   │   └── db_models.py        # SQLAlchemy модели
│   ├── db/
│   │   ├── engine.py           # DB движок
│   │   ├── init.py             # Seed данные
│   │   └── queries.py          # CRUD операции
│   └── utils/
│       ├── excel_export.py     # Экспорт в Excel
│       └── helpers.py          # Утилиты
├── data/
│   ├── rules/                  # YAML правила
│   └── seed/                   # Seed данные (threats_full.json)
├── frontend/
│   ├── templates/
│   │   ├── base.html           # Базовый шаблон
│   │   └── wizard/             # Шаги wizard
│   └── static/
│       └── css/style.css       # Стили
├── scripts/
│   └── parse_thrlist.py        # Парсер БДУ ФСТЭК
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```

## 🔧 Настройка

### Переменные окружения (.env)

```env
APP_NAME="Threat Modeler FSTEC"
APP_PORT=8000
ENV="development"
DB_PATH="./data/threats.db"
DATA_DIR="./data"
REPORTS_DIR="./reports"
```

## 📊 Импорт данных из БДУ ФСТЭК

Для загрузки полной базы угроз из ФСТЭК БДУ:

```bash
# Поместите файл thrlist.xlsx в data/seed/
python scripts/parse_thrlist.py data/seed/thrlist.xlsx --pretty
```

## 🛠 Технологический стек

- **Backend**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy 2.0 (асинхронный)
- **БД**: SQLite
- **Валидация**: Pydantic v2
- **Frontend**: Jinja2 + HTMX + TailwindCSS
- **Экспорт**: openpyxl (Excel в формате ФСТЭК)
- **Контейнеризация**: Docker + docker-compose

## 📝 Пошаговый wizard

1. **О системе** - ПДн, технологии, сетевые возможности
2. **Нарушители** - внешние и внутренние, уровни Н1-Н4
3. **Интерфейсы** - веб, RDP/SSH, VPN, физический доступ
4. **Объекты** - О1-О17 (БД, ОС, сеть, криптография и т.д.)
5. **Отчёт** - предпросмотр и экспорт в Excel

## 📤 Экспорт

Приложение генерирует Excel-файл в формате Таблицы 11 ФСТЭК:
- Идентификатор УБИ
- Наименование УБИ
- Уровень нарушителя (Внутренний/Внешний)
- Объект воздействия
- Способы реализации
- Негативные последствия
- Тактика
- Техника
- Примечания

## 🧪 Тестирование

```bash
# Проверка health endpoint
curl http://localhost:8000/health

# Запуск тестов (будут добавлены)
pytest tests/
```

## 📄 Лицензия

Локальное приложение для внутреннего использования.

## 🤝 Поддержка

Соответствует методике ФСТЭК 2021 и документу "Модель угроз Юнитех".
