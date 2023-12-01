import pathlib
from pprint import pprint

from src import reports
from src.services import analyze_cashback_categories
from src.views import generate_report

ROOT_PATH = pathlib.Path(__file__).parent
FILE_PATH_XLSX = ROOT_PATH.joinpath("data", "operations.xls")
USER_SETTINGS_FILE = ROOT_PATH.joinpath("user_settings.json")
FILE_FOR_JSON = ROOT_PATH.joinpath("data", "report_json.json")


input_date = "2023-05-20"
report_json = generate_report(input_date, USER_SETTINGS_FILE)
year = 2023
month = 5

print(generate_report(input_date, USER_SETTINGS_FILE))
pprint(analyze_cashback_categories(FILE_PATH_XLSX, year, month))
pprint(reports.spending_by_category(FILE_PATH_XLSX, "Аптеки"))
