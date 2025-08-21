from flask import Blueprint, request, jsonify
import requests
from datetime import datetime
from utils.config_util     import ConfigManager as Config

schedule_bp = Blueprint('schedule', __name__)
Config().read_file("config.json")

API_KEY = Config().get()["NICEAPI"]["KEY"]
BASE_URL = Config().get()["NICEAPI"]["SCHEDULE"]

DEFAULT_PARAMS = {
    'KEY': API_KEY,
    'Type': 'json',
    'ATPT_OFCDC_SC_CODE': Config().get()["NICEAPI"]["SCHULSC"],
    'SD_SCHUL_CODE': Config().get()["NICEAPI"]["SCHULC"]
}

def fetch_schedule_by_month(year: str, month: str):
    from_date = f"{year}{month}01"
    to_date = f"{year}{month}31"

    params = DEFAULT_PARAMS.copy()
    params['AA_FROM_YMD'] = from_date
    params['AA_TO_YMD'] = to_date

    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        try:
            data = response.json()
            rows = data['SchoolSchedule'][1]['row']
            result = [
                {
                    '날짜': row['AA_YMD'],
                    '행사명': row.get('EVENT_NM', ''),
                    '행사내용': row.get('EVENT_CNTNT', '')
                }
                for row in rows
            ]
            return result
        except (KeyError, IndexError):
            return []
    else:
        return []

@schedule_bp.route("/schedule", methods = ['GET'])
def get_schedule():
    year = request.args.get('year', datetime.now().strftime('%Y'))
    month = request.args.get('month', datetime.now().strftime('%m'))
    result = fetch_schedule_by_month(year, month)
    return jsonify(result)
