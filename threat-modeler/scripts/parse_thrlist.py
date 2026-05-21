"""Скрипт парсинга thrlist.xlsx в JSON для seed-данных."""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import pandas as pd
except ImportError:
    print("❌ pandas не установлен. Установите: pip install pandas openpyxl")
    sys.exit(1)


def parse_thrlist_xlsx(xlsx_path: str) -> Dict[str, Any]:
    """
    Парсинг файла thrlist.xlsx (БДУ ФСТЭК).
    
    Args:
        xlsx_path: Путь к файлу thrlist.xlsx
    
    Returns:
        Словарь с нормализованными данными
    """
    path = Path(xlsx_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")
    
    # Чтение Excel файла
    xls = pd.ExcelFile(path)
    sheet_names = xls.sheet_names
    
    print(f"📄 Листы в файле: {sheet_names}")
    
    # Предполагаемая структура:
    # - threats: основные угрозы
    # - tactics: тактики
    # - techniques: техники
    
    result = {
        "threats": [],
        "tactics": [],
        "techniques": []
    }
    
    # Парсинг угроз (предполагаем первый лист или лист "Угрозы")
    threats_sheet = None
    for name in ["Угрозы", "Threats", sheet_names[0]]:
        if name in sheet_names:
            threats_sheet = name
            break
    
    if threats_sheet:
        print(f"📥 Читаем угрозы из листа '{threats_sheet}'...")
        df_threats = pd.read_excel(xlsx_path, sheet_name=threats_sheet)
        result["threats"] = parse_threats_dataframe(df_threats)
    
    # Парсинг тактик
    tactics_sheet = None
    for name in ["Тактики", "Tactics"]:
        if name in sheet_names:
            tactics_sheet = name
            break
    
    if tactics_sheet:
        print(f"📥 Читаем тактики из листа '{tactics_sheet}'...")
        df_tactics = pd.read_excel(xlsx_path, sheet_name=tactics_sheet)
        result["tactics"] = parse_tactics_dataframe(df_tactics)
    
    # Парсинг техник
    techniques_sheet = None
    for name in ["Техники", "Techniques"]:
        if name in sheet_names:
            techniques_sheet = name
            break
    
    if techniques_sheet:
        print(f"📥 Читаем техники из листа '{techniques_sheet}'...")
        df_techniques = pd.read_excel(xlsx_path, sheet_name=techniques_sheet)
        result["techniques"] = parse_techniques_dataframe(df_techniques)
    
    return result


def parse_threats_dataframe(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Парсинг DataFrame с угрозами."""
    threats = []
    
    # Ожидаемые колонки (адаптируйте под реальный формат thrlist.xlsx)
    # УБИ.001 | Наименование | Н2 | Н2,Н3 | О6,О15 | СП1,СП3 | П14,П17 | Т2,Т6 | Т2.5,Т6.3 | Примечание
    
    for idx, row in df.iterrows():
        try:
            threat = {
                "id": str(row.get("УБИ", row.get("id", f"УБИ.{idx:03d}"))).strip(),
                "name": str(row.get("Наименование", row.get("name", ""))).strip(),
                "violator_int": parse_list_field(row.get("Н2внутр", row.get("violator_int", ""))),
                "violator_ext": parse_list_field(row.get("Н2внеш", row.get("violator_ext", ""))),
                "objects": parse_list_field(row.get("Объекты", row.get("objects", ""))),
                "methods": parse_list_field(row.get("Методы", row.get("methods", ""))),
                "consequences": parse_list_field(row.get("Последствия", row.get("consequences", ""))),
                "tactics": parse_list_field(row.get("Тактика", row.get("tactics", ""))),
                "techniques": parse_list_field(row.get("Техника", row.get("techniques", ""))),
                "exclusion_note": str(row.get("Примечание", row.get("note", ""))).strip() or None,
                "exclusion_flags": extract_exclusion_flags(row)
            }
            
            if threat["id"] and threat["name"]:
                threats.append(threat)
        
        except Exception as e:
            print(f"⚠️  Ошибка при парсинге строки {idx}: {e}")
            continue
    
    return threats


def parse_tactics_dataframe(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Парсинг DataFrame с тактиками."""
    tactics = []
    
    for idx, row in df.iterrows():
        try:
            tactic = {
                "code": str(row.get("Код", row.get("code", f"Т{idx}"))).strip(),
                "name": str(row.get("Наименование", row.get("name", ""))).strip()
            }
            
            if tactic["code"] and tactic["name"]:
                tactics.append(tactic)
        
        except Exception as e:
            print(f"⚠️  Ошибка при парсинге тактики {idx}: {e}")
            continue
    
    return tactics


def parse_techniques_dataframe(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Парсинг DataFrame с техниками."""
    techniques = []
    
    for idx, row in df.iterrows():
        try:
            technique = {
                "code": str(row.get("Код", row.get("code", f"Т{idx}.0"))).strip(),
                "name": str(row.get("Наименование", row.get("name", ""))).strip()
            }
            
            if technique["code"] and technique["name"]:
                techniques.append(technique)
        
        except Exception as e:
            print(f"⚠️  Ошибка при парсинге техники {idx}: {e}")
            continue
    
    return techniques


def parse_list_field(value: Any) -> List[str]:
    """Парсинг поля со списком (через запятую)."""
    if pd.isna(value) or value is None:
        return []
    
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    
    if isinstance(value, (int, float)):
        return [str(int(value))]
    
    # Разделяем по запятой, точке с запятой или новому строке
    str_value = str(value)
    separators = [",", ";", "\n", "|"]
    
    for sep in separators:
        if sep in str_value:
            items = [item.strip() for item in str_value.split(sep)]
            return [item for item in items if item]
    
    # Если один элемент
    str_value = str_value.strip()
    return [str_value] if str_value else []


def extract_exclusion_flags(row: pd.Series) -> Dict[str, bool]:
    """Извлечение флагов исключений из примечания."""
    note = str(row.get("Примечание", row.get("note", ""))).lower()
    
    flags = {
        "requires_grid": any(word in note for word in ["грид", "grid", "суперкомпьютер"]),
        "requires_wifi": any(word in note for word in ["wi-fi", "wifi", "беспроводн", "wireless"]),
        "requires_mobile": any(word in note for word in ["мобильн", "mobile", "смартфон", "планшет"]),
        "requires_docker": any(word in note for word in ["docker", "контейнер", "container"]),
        "requires_cloud": any(word in note for word in ["облак", "cloud", "saas", "paas", "iaas"]),
        "requires_smartcard": any(word in note for word in ["смарт-карт", "smartcard", "токен"]),
        "requires_ml": any(word in note for word in ["машинн обуч", "ml", "ai", "искусствен интеллект"]),
        "requires_supercomputer": any(word in note for word in ["суперкомпьютер", "supercomputer"]),
        "requires_ics": any(word in note for word in ["асу тп", "scada", "ics", "промышленн"]),
        "external_responsibility": any(word in note for word in ["кортэл", "внешн ответствен", "external responsibility"]),
        "transborder": any(word in note for word in ["трансгранич", "transborder", "foreign"])
    }
    
    return flags


def main():
    """Главная функция парсинга."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Парсинг thrlist.xlsx в JSON")
    parser.add_argument("input", nargs="?", default="data/seed/thrlist.xlsx", 
                        help="Путь к входному файлу thrlist.xlsx")
    parser.add_argument("-o", "--output", default="data/seed/threats_full.json",
                        help="Путь к выходному JSON файлу")
    parser.add_argument("--pretty", action="store_true", 
                        help="Форматированный вывод JSON")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"❌ Файл не найден: {input_path}")
        print("\nПожалуйста, поместите файл thrlist.xlsx в директорию data/seed/")
        sys.exit(1)
    
    print(f"🚀 Начинаем парсинг {input_path}...")
    
    try:
        result = parse_thrlist_xlsx(str(input_path))
        
        # Сохранение результата
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            if args.pretty:
                json.dump(result, f, ensure_ascii=False, indent=2)
            else:
                json.dump(result, f, ensure_ascii=False)
        
        print(f"\n✅ Успешно!")
        print(f"📊 Угроз: {len(result['threats'])}")
        print(f"📊 Тактик: {len(result['tactics'])}")
        print(f"📊 Техник: {len(result['techniques'])}")
        print(f"💾 Сохранено в: {output_path}")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
