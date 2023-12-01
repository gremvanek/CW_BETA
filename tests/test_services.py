import pandas as pd
import pytest

from src.services import analyze_cashback_categories


@pytest.fixture
def excel_data_file(tmp_path):
    # Создаем временный Excel-файл с данными
    data = [
        {"Дата платежа": "01.11.2023", "Категория": "Category 1", "Кэшбэк": 10},
        {"Дата платежа": "02.11.2023", "Категория": "Category 2", "Кэшбэк": 20},
        {"Дата платежа": "03.11.2023", "Категория": "Category 1", "Кэшбэк": 5},
        {"Дата платежа": "04.11.2023", "Категория": "Category 3", "Кэшбэк": 15},
    ]

    excel_file = tmp_path / "test_data.xlsx"
    df = pd.DataFrame(data)
    df.to_excel(excel_file, index=False)
    return excel_file


def test_analyze_cashback_categories(excel_data_file):
    year = 2023
    month = 11

    cashback_by_category = analyze_cashback_categories(excel_data_file, year, month)

    # Проверяем, что результат является словарем
    assert isinstance(cashback_by_category, dict)

    # Проверяем, что суммы кэшбэка по категориям правильно суммируются
    assert cashback_by_category["Category 1"] == 15
    assert cashback_by_category["Category 2"] == 20
    assert cashback_by_category["Category 3"] == 15

    # Проверяем, что другие категории отсутствуют в результате
    assert "Category 4" not in cashback_by_category
    assert "Category 5" not in cashback_by_category
