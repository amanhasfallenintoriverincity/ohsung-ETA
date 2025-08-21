import requests

# 발급받은 인증키 입력
API_KEY = '036c9c29def24c10b5348669d54a77e5'

# API 엔드포인트
url = 'https://open.neis.go.kr/hub/mealServiceDietInfo'

# 파라미터 설정
params = {
    'KEY': API_KEY,
    'Type': 'json',
    'ATPT_OFCDC_SC_CODE': 'N10',      # 예: 전북교육청 코드
    'SD_SCHUL_CODE': '8140246',       # 예: 특정 학교 코드
    'MLSV_YMD': '20250707'            # 예: 2025년 7월 23일
}

# API 요청
response = requests.get(url, params=params)

# 응답 확인
if response.status_code == 200:
    data = response.json()
    try:
        meals = data['mealServiceDietInfo'][1]['row']
        for meal in meals:
            if meal['MMEAL_SC_NM'] == "중식":
                print(f"학교명: {meal['SCHUL_NM']}")
                print(f"급식일자: {meal['MLSV_YMD']} - 중식")
                print(f"급식메뉴:\n{meal['DDISH_NM'].replace('<br/>', '\n')}")
                print(f"칼로리: {meal['CAL_INFO']}")
                print(f"영양정보: {meal['NTR_INFO']}")
                print("-" * 40)
            if meal['MMEAL_SC_NM'] == "석식":
                print(f"학교명: {meal['SCHUL_NM']}")
                print(f"급식일자: {meal['MLSV_YMD']} - 석식")
                print(f"급식메뉴:\n{meal['DDISH_NM'].replace('<br/>', '\n')}")
                print(f"칼로리: {meal['CAL_INFO']}")
                print(f"영양정보: {meal['NTR_INFO']}")
                print("-" * 40)
    except KeyError:
        print("데이터가 없습니다.")
else:
    print("API 호출 실패:", response.status_code)
