import json
import os
import pathlib
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytest

from src.reports import spending_by_category

ROOT_PATH = pathlib.Path(__file__).parent.parent
FILE_PATH_XLSX = ROOT_PATH.joinpath("data", "operations.xls")
USER_SETTINGS_FILE = ROOT_PATH.joinpath("user_settings.json")
FILE_FOR_JSON = ROOT_PATH.joinpath("data", "report_json.json")
MY_FUNC_REPORT = ROOT_PATH.joinpath("my_func.json")

test_date = datetime.now().strftime("%d.%m.%Y")
test_start_date = datetime.now() - relativedelta(months=3)


@pytest.mark.parametrize(
    "file_path, category, expected_result",
    [
        (
                FILE_PATH_XLSX,
                "Аптеки",
                {
                    "category": "Аптеки",
                    "start_date": test_start_date.strftime("%d.%m.%Y"),
                    "end_date": test_date,
                    "total_spending": 19702.0,
                },
        ),
        # Add more test cases if needed
    ],
)
def test_spending_by_category(file_path, category, expected_result):
    result = spending_by_category(file_path, category)
    assert result == expected_result


def test_report_to_file_decorator():
    # Проверяем, что файл отчета был создан
    assert os.path.exists(MY_FUNC_REPORT)

    # Читаем результат из файла
    with open(MY_FUNC_REPORT, "r", encoding="utf-8") as file:
        file_content = json.load(file)

    # Проверяем, что содержимое файла соответствует ожидаемому результату
    expected_result = {
        "category": "Аптеки",
        "start_date": test_start_date.strftime("%d.%m.%Y"),
        "end_date": test_date,
        "total_spending": 19702.0,
    }
    assert file_content == expected_result
