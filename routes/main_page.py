from flask import Blueprint, jsonify

mainpage_bp = Blueprint('main', __name__)

@mainpage_bp.route("/main")
def main_page():
    return jsonify({
        "message": "메인페이지 정보 불러오기 성공",
        "icons": [
            {"name": "프로필", "route": "/profile"},
            {"name": "급식", "route": "/meal"},
            {"name": "시간표", "route": "/timetable"},
            {"name": "학사일정", "route": "/schedule"},
        ],
        "sections": [
            {"name": "게시물", "route": "/posts"}
        ]
    }), 200