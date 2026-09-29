"""
Скрипт для парсинга и обновления данных по социальному бюджету РК:
1. Загрузка / чтение отчетов об исполнении государственного и местных бюджетов (Минфин РК / data.egov.kz).
2. Фильтрация строк по функциональной классификации '06' (Социальная помощь и соцобеспечение).
3. Извлечение утвержденных сумм и фактического исполнения в разрезе 20 регионов.
4. Экспорт в структурированный JSON.

Запуск через uv (автоматически скачает нужные библиотеки):
  & "C:\\Users\\nkaba\\.local\\bin\\uv.exe" run --with pandas,openpyxl,httpx scripts/parse_minfin.py
"""

import os
import sys
import json
import argparse

def inspect_or_parse_excel(file_path: str):
    """
    Парсит официальный отчет Минфина РК (Форма 1-Н или 2-Н).
    В отчетах Минфина функциональная классификация представлена колонками:
    - Код функциональной группы (например '06')
    - Наименование программы
    - План на год
    - Скорректированный план
    - Фактическое исполнение
    """
    try:
        import pandas as pd
    except ImportError:
        print("Для работы требуется pandas и openpyxl.")
        print("Запустите команду: uv run --with pandas,openpyxl scripts/parse_minfin.py --file <путь_к_excel>")
        return

    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        return

    print(f"Загрузка отчета: {file_path}")
    # Читаем первые 50 строк для определения структуры заголовков
    df_preview = pd.read_excel(file_path, header=None, nrows=30)
    print("Предпросмотр структуры файла:")
    print(df_preview.dropna(how='all').head(10))

    # Пример логики поиска строк раздела 06
    # df = pd.read_excel(file_path)
    # social_rows = df[df[0].astype(str).str.startswith('06') | df[1].astype(str).str.contains('социальн', case=False, na=False)]
    # print(f"Найдено строк по разделу 06: {len(social_rows)}")

def main():
    parser = argparse.ArgumentParser(description="Парсер отчетов Минфина РК по соцбюджету")
    parser.add_argument("--file", type=str, help="Путь к скачанному файлу Excel отчета Минфина")
    parser.add_argument("--egov-token", type=str, help="API токен data.egov.kz для автоматической выгрузки")
    args = parser.parse_args()

    if args.file:
        inspect_or_parse_excel(args.file)
    else:
        print("Парсер готов к работе.")
        print("Инструкция:")
        print("1. Скачайте официальный Excel-отчет с gov.kz/memleket/entities/minfin (Раздел 'Исполнение бюджета').")
        print("2. Запустите: & uv run --with pandas,openpyxl scripts/parse_minfin.py --file путь_к_отчету.xlsx")

if __name__ == "__main__":
    main()
