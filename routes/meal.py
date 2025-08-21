from flask import Blueprint, jsonify, request
import requests
from datetime import datetime
from utils.config_util     import ConfigManager as Config

meal_bp  = Blueprint('meal', __name__)
Config().read_file("config.json")

API_KEY = Config().get()["NICEAPI"]["KEY"]
BASE_URL = Config().get()["NICEAPI"]["MEAL"]


def fetch_meal(meal_type, date):
    params = {
        'KEY': API_KEY,
        'Type': 'json',
        'ATPT_OFCDC_SC_CODE': Config().get()["NICEAPI"]["SCHULSC"],
        'SD_SCHUL_CODE': Config().get()["NICEAPI"]["SCHULC"],
        'MLSV_YMD': date
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            meals = data['mealServiceDietInfo'][1]['row']
            filtered = [
                {
                    '학교명': meal['SCHUL_NM'],
                    '급식일자': meal['MLSV_YMD'],
                    '메뉴': meal['DDISH_NM'].replace('<br/>', '\n'),
                    '칼로리': meal['CAL_INFO'],
                    '영양정보': meal['NTR_INFO']
                }
                for meal in meals if meal['MMEAL_SC_NM'] == meal_type
            ]
            return filtered
        except KeyError:
            return []
    else:
        return []

@meal_bp.route("/meal_lunch")
def meal_lunch():
    today = datetime.now().strftime('%Y%m%d')  # 오늘 날짜
    date = request.args.get('date', today)
    result = fetch_meal("중식", date)
    return jsonify(result)

@meal_bp.route("/meal_dinner")
def meal_dinner():
    today = datetime.now().strftime('%Y%m%d')  # 오늘 날짜
    date = request.args.get('date', today)
    result = fetch_meal("석식", date)
    return jsonify(result)
