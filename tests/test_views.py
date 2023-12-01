import json
import pathlib

import pandas as pd
import pytest

from src.views import (
    card_reader,
    currency_api,
    generate_report,
    hello_function_day_time,
    stock_prices_api,
    top_5_transactions,
)

ROOT_PATH = pathlib.Path(__file__).parent.parent
FILE_PATH_XLSX = ROOT_PATH.joinpath("data", "operations.xls")
USER_SETTINGS_FILE = ROOT_PATH.joinpath("user_settings.json")
FILE_FOR_JSON = ROOT_PATH.joinpath("data", "report_json.json")


@pytest.fixture
def user_settings_file(tmp_path):
    # Создаем временный файл для пользовательских настроек
    user_settings = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "GOOGL"],
    }
    settings_file = tmp_path / "user_settings.json"
    with open(settings_file, "w") as f:
        json.dump(user_settings, f)
    return settings_file


@pytest.fixture
def sample_excel_data(tmp_path):
    # Создаем временный Excel-файл с примером данных
    excel_data = [
        {
            "Дата платежа": "01.11.2023",
            "Номер карты": "1234567890123456",
            "Сумма платежа": -100,
            "Бонусы (включая кэшбэк)": 1,
            "Категория": "Category 1",
            "Описание": "Transaction 1",
        },
        {
            "Дата платежа": "02.11.2023",
            "Номер карты": "1234567890123456",
            "Сумма платежа": -200,
            "Бонусы (включая кэшбэк)": 2,
            "Категория": "Category 2",
            "Описание": "Transaction 2",
        },
        {
            "Дата платежа": "03.11.2023",
            "Номер карты": "9876543210987654",
            "Сумма платежа": -150,
            "Бонусы (включая кэшбэк)": 3,
            "Категория": "Category 1",
            "Описание": "Transaction 3",
        },
        {
            "Дата платежа": "04.11.2023",
            "Номер карты": "9876543210987654",
            "Сумма платежа": -50,
            "Бонусы (включая кэшбэк)": 1,
            "Категория": "Category 3",
            "Описание": "Transaction 4",
        },
    ]
    excel_file = tmp_path / "sample_data.xlsx"
    df = pd.DataFrame(excel_data)
    df.to_excel(excel_file, index=False)
    return excel_file


def test_hello_function_day_time():
    # Проверка функции hello_function_day_time
    assert hello_function_day_time() in [
        "Доброе утро",
        "Добрый день",
        "Добрый вечер",
        "Доброй ночи",
    ]


def test_card_reader():
    # Проверка функции card_reader
    start_date = pd.to_datetime("01.11.2023", format="%d.%m.%Y")
    end_date = pd.to_datetime("04.11.2023", format="%d.%m.%Y")
    result = card_reader(FILE_PATH_XLSX, start_date, end_date)

    assert isinstance(result, dict)
    assert "*6943" in result
    assert result["*6943"]["Общая сумма расходов"] == 4431.15
    assert result["*6943"]["Бонусы (включая кэшбэк)"] == 31


def test_top_5_transactions():
    # Проверка функции top_5_transactions
    start_date = pd.to_datetime("01.11.2023", format="%d.%m.%Y")
    end_date = pd.to_datetime("04.11.2023", format="%d.%m.%Y")
    result = top_5_transactions(FILE_PATH_XLSX, start_date, end_date)

    assert isinstance(result, dict)
    assert "top_transactions" in result
    transactions = result["top_transactions"]
    assert len(transactions) == 5
    assert all(isinstance(transaction, dict) for transaction in transactions)


def test_currency_api():
    # Проверка функции currency_api
    user_currencies = ["USD", "EUR"]
    result = currency_api(user_currencies)

    assert isinstance(result, dict)
    assert "currency_rates" in result
    currency_rates = result["currency_rates"]
    assert len(currency_rates) == 2
    assert all(isinstance(rate, dict) for rate in currency_rates)


def test_stock_prices_api(user_settings_file):
    input_date = "2023-11-01"
    result = stock_prices_api(input_date, user_settings_file)

    assert isinstance(result, list)
    assert all(isinstance(stock_info, dict) for stock_info in result)


def test_generate_report(user_settings_file):
    input_date = "2023-11-01"
    result = generate_report(input_date, user_settings_file)

    assert isinstance(result, str)
    report_data = json.loads(result)
    assert "greeting" in report_data
    assert "cards" in report_data
    assert "top_transactions" in report_data
    assert "currency_rates" in report_data
    assert "stock_prices" in report_data
