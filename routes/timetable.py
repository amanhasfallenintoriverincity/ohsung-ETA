from flask import Blueprint, request, jsonify
import requests
from datetime import datetime
from utils.config_util     import ConfigManager as Config

timetable_bp = Blueprint('timetable', __name__)
config = Config()
config.read_file("config.json")

API_KEY = config.get()["NICEAPI"]["KEY"]
BASE_URL = config.get()["NICEAPI"]["TIMETABLE"]

DEFAULT_PARAMS = {
    'KEY': API_KEY,
    'Type': 'json',
    'ATPT_OFCDC_SC_CODE': config.get()["NICEAPI"]["SCHULSC"],
    'SD_SCHUL_CODE': config.get()["NICEAPI"]["SCHULC"]
}

def fetch_timetable(date: str, grade: str, class_nm: str):
    params = DEFAULT_PARAMS.copy()
    params['GRADE'] = grade
    params['CLASS_NM'] = class_nm
    params['TI_FROM_YMD'] = date
    params['TI_TO_YMD'] = date

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        return {"data": [], "message": "시간표 API 요청 실패"}

    try:
        data = response.json()
        print(data)

        # 정상 데이터
        rows = data['hisTimetable'][1]['row']
        result = [
            {
                'grade': row['GRADE'],
                'class': row['CLASS_NM'],
                'period': row['PERIO'],
                'subject': row['ITRT_CNTNT']
            }
            for row in rows
        ]
        return {"data": result, "message": ""}

    except (KeyError, IndexError, TypeError):
        # CODE 가져와야함
        try:
            code = data['hisTimetable'][0]['head'][1]['RESULT']['CODE']
        except (KeyError, IndexError, TypeError):
            code = None
        print(code)
        if code == 'INFO-200':
            return {"data": [], "message": "오늘은 쉬는날"}
        return {"data": [], "message": "시간표 데이터가 없습니다."}



@timetable_bp.route('/timetable', methods=['POST'])
def get_timetable():
    payload = request.get_json(silent=True) or {}
    input_grade = payload.get('grade')
    input_class = payload.get('class')
    date = datetime.now().strftime('%Y%m%d')

    result = fetch_timetable(date, input_grade, input_class)
    return jsonify(result), 200

## date에서 CODE를 추출하고 그 값에 따라 뱉어내는 메시지가 달라야함