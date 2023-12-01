from pathlib import Path
from typing import Dict

import pandas as pd


def analyze_cashback_categories(data: Path, year: int, month: int) -> Dict[str, float]:
    """
    Analyze cashback categories
    :param data: str
    :param year: int
    :param month: int
    :return: Dict[str, float]
    """
    df = pd.read_excel(data)
    # Преобразуем столбец с датой в формат datetime
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y")
    # Фильтруем данные для указанного года и месяца
    filtered_data = df[(df["Дата платежа"].dt.year == year) & (df["Дата платежа"].dt.month == month)]
    # Создаем словарь для хранения суммы кэшбэка по категориям
    cashback_by_category: dict = {}

    for _, row in filtered_data.iterrows():
        category = row["Категория"]
        cashback = row["Кэшбэк"]

        if pd.notna(cashback):
            if category in cashback_by_category:
                cashback_by_category[category] += int(cashback)
            else:
                cashback_by_category[category] = int(cashback)

    return cashback_by_category
