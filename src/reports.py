import json
import logging
import pathlib
from datetime import datetime
from functools import wraps
from typing import Any

import pandas as pd

ROOT_PATH = pathlib.Path(__file__).parent.parent
FILE_PATH_XLSX = ROOT_PATH.joinpath("data", "operations.xls")
USER_SETTINGS_FILE = ROOT_PATH.joinpath("user_settings.json")
MY_FUNC_REPORT = ROOT_PATH.joinpath("my_func.json")


def report_to_file(log_file_path):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(log_file_path, "w", encoding="utf-8") as file:
                logging.info(f"Result: {result}")
                json.dump(result, file, ensure_ascii=False)  # Записываем результат в файл
            return result

        return wrapper

    return decorator


@report_to_file(MY_FUNC_REPORT)
def spending_by_category(transactions: str | Any, category: str, date: Any = None) -> dict:
    """
    Функция подсчета трат по категориям
    :param transactions: str | Any
    :param category: str
    :param date: Any
    :return: dict
    """
    logging.basicConfig(filename=MY_FUNC_REPORT, level=logging.INFO, encoding="utf-8")
    df = pd.read_excel(transactions, index_col=4)
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y")
    if date is None:
        date = pd.to_datetime(datetime.now())
    else:
        date = pd.to_datetime(date)

    three_months_ago = date - pd.DateOffset(months=3)

    filtered_transactions = df[
        (df["Дата платежа"] >= three_months_ago) & (df["Дата платежа"] <= date) & (df["Категория"] == category)
    ]

    total_spending = filtered_transactions["Сумма платежа"].sum()

    result_dict = {
        "category": category,
        "start_date": three_months_ago.strftime("%d.%m.%Y"),
        "end_date": date.strftime("%d.%m.%Y"),
        "total_spending": total_spending,
    }

    return result_dict
