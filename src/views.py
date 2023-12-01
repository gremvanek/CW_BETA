import datetime
import json
import pathlib
from pprint import pprint
from typing import Any, Dict, List, Union

import pandas as pd
import requests
from yfinance import Ticker

ROOT_PATH = pathlib.Path(__file__).parent.parent
FILE_PATH_XLSX = ROOT_PATH.joinpath("data", "operations.xls")
USER_SETTINGS_FILE = ROOT_PATH.joinpath("user_settings.json")
FILE_FOR_JSON = ROOT_PATH.joinpath("data", "report_json.json")


def hello_function_day_time() -> str:
    """
    Функция приветствия сервиса
    :return: str
    """
    now = datetime.datetime.now()
    time = now.strftime("%H")
    if 5 < int(time) < 12:
        return "Доброе утро"
    elif 12 <= int(time) < 17:
        return "Добрый день"
    elif 17 <= int(time) < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def card_reader(file_name: Any, start_date: str | Any, end_date: str | Any) -> Dict[str, Dict[str, Union[float, int]]]:
    """
    Функция вывода информации по карте
    :param file_name:
    :param start_date:
    :param end_date:
    :return:
    """
    data = pd.read_excel(file_name)
    card_info = {}
    data["Дата платежа"] = pd.to_datetime(data["Дата платежа"], format="%d.%m.%Y")
    filtered_data = data[(data["Дата платежа"] >= start_date) & (data["Дата платежа"] <= end_date)]
    grouped_data = (
        filtered_data.groupby("Номер карты")
        .agg({"Сумма платежа": "sum", "Бонусы (включая кэшбэк)": "sum"})
        .reset_index()
    )
    for index, row in grouped_data.iterrows():
        total_expenses = row["Сумма платежа"]
        cashback = row["Бонусы (включая кэшбэк)"]
        card_number = str(row["Номер карты"])  # Преобразуем в строку
        if total_expenses < 0:
            card_info[card_number] = {
                "Общая сумма расходов": -total_expenses,
                "Бонусы (включая кэшбэк)": cashback,
            }

    return card_info


def top_5_transactions(file_name: Any, start_date: datetime.date, end_date: datetime.date) -> dict:
    """
    Функция вывода топ 5 транзакций
    :param file_name: Any
    :param start_date: datetime.date
    :param end_date: datetime.date
    :return: dict
    """

    data = pd.read_excel(file_name)
    data["Дата платежа"] = pd.to_datetime(data["Дата платежа"], format="%d.%m.%Y")
    filtered_data = data[(data["Дата платежа"] >= start_date) & (data["Дата платежа"] <= end_date)]
    sorted_df = filtered_data.sort_values(by="Сумма платежа", ascending=False)

    top_transactions = []
    for index, row in sorted_df.head(5).iterrows():
        transaction = {
            "date": row["Дата платежа"].strftime("%d.%m.%Y"),
            "amount": float(row["Сумма платежа"]),
            "category": row["Категория"],
            "description": row["Описание"],
        }
        top_transactions.append(transaction)

    info_dict = {"top_transactions": top_transactions}

    return info_dict


def currency_api(user_currencies: List[str]) -> dict[str, list[dict[str, str | Any]]]:
    """
    Функция получения курса валют
    :param user_currencies: Файл с настройками
    :return: dict[str, list[dict[str, str | Any]]]
    """

    info_dict = {}
    response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    currency_data = response.json()
    currency_values = {}

    for currency in user_currencies:
        if currency in currency_data["Valute"]:
            currency_rate = {
                "currency": currency,
                "rate": currency_data["Valute"][currency]["Value"],
            }
            currency_values[currency] = currency_rate

    info_dict["currency_rates"] = list(currency_values.values())
    return info_dict


def stock_prices_api(input_date: str, user_settings_file: pathlib.Path) -> Any:
    """
    Функция получения цен на акции
    :param input_date: date
    :param user_settings_file: pathlib. Path
    :return: Any
    """
    try:
        with open(user_settings_file, "r", encoding="utf-8") as file:
            user_settings = json.load(file)

        user_stocks = user_settings.get("user_stocks", [])
        stock_prices = []

        for stock_symbol in user_stocks:
            stock = Ticker(stock_symbol)
            historical_data = stock.history(period="1mo", interval="1d")
            if not historical_data.empty:
                price = historical_data["Close"].values[-1]
                stock_info = {"stock": stock_symbol, "price": round(price, 2)}
                stock_prices.append(stock_info)

        return stock_prices

    except Exception as e:
        return {"error": str(e)}


def generate_report(input_date: str, user_settings_file: Any) -> Any:
    """
    Главная функция для формирования отчета
    :param input_date: datetime.date
    :param user_settings_file: str
    :return: Any
    """
    start_date = datetime.datetime.strptime(f"{input_date[:7]}-01", "%Y-%m-%d")
    end_date = datetime.datetime.strptime(input_date, "%Y-%m-%d")

    # Чтение пользовательских настроек из файла
    with open(user_settings_file, "r") as f:
        user_settings = json.load(f)

    user_currencies = user_settings.get("user_currencies", [])

    greeting = hello_function_day_time()
    card_info = card_reader(FILE_PATH_XLSX, start_date, end_date)
    top_transactions_info = top_5_transactions(FILE_PATH_XLSX, start_date, end_date)
    currency_rates_info = currency_api(user_currencies)
    stock_prices_info = stock_prices_api(input_date, user_settings_file)

    # Преобразование данных о картах в формат "cards"
    cards_info = []
    for card_number, card_data in card_info.items():
        last_digits = card_number[-4:]
        total_spent = card_data.get("Общая сумма расходов", 0)
        cashback = total_spent * 0.01  # Рассчитываем кэшбэк как 1% от общей суммы расходов
        card_info_entry = {
            "last_digits": last_digits,
            "total_spent": round(total_spent, 2),
            "cashback": round(cashback, 2),
        }
        cards_info.append(card_info_entry)

    # Формирование окончательного отчета
    report = {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions_info["top_transactions"],
        "currency_rates": currency_rates_info["currency_rates"],
        "stock_prices": stock_prices_info,
    }

    # Сохранение JSON-отчета в файл
    with open(FILE_FOR_JSON, "w", encoding="utf-8") as json_file:
        json.dump(report, json_file, ensure_ascii=False, indent=4)

    return json.dumps(report, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    input_date = "2023.05.20"
    pprint(stock_prices_api(input_date, USER_SETTINGS_FILE))
