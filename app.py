from flask                 import Flask
from flask_cors            import CORS
from flask_session         import Session
from utils.database_util   import DatabaseManager
from utils.config_util     import ConfigManager as Config
from flask import redirect, url_for

from routes.auth import auth_bp
from routes.main_page import mainpage_bp
from routes.meal import meal_bp
from routes.schedule import schedule_bp
from routes.timetable import timetable_bp
from routes.post import post_bp

app = Flask(__name__)

# 프론트엔드와 세션 유지 가능하게 설정 (프론트엔드에서 꼭 withCredentials: true 확인!)
CORS(app, supports_credentials=True)
Config().read_file("config.json")


# Flask 세션 설정 추가
app.config['SECRET_KEY']         = Config().get()["Session"]["Key"]
app.config['SESSION_TYPE']       = Config().get()["Session"]["Type"]
app.config['SESSION_PERMANENT']  = Config().get()["Session"]["Permanent"]
app.config['SESSION_USE_SIGNER'] = Config().get()["Session"]["UseSigner"]
app.config['SESSION_KEY_PREFIX'] = Config().get()["Session"]["KeyPrefix"]

Session(app)

# 데이터베이스 연결 초기화
DatabaseManager().connect(
    host     = Config().get()["Database"]["Host"],
    username = Config().get()["Database"]["Username"],
    password = Config().get()["Database"]["Password"],
)

app.register_blueprint(auth_bp)
app.register_blueprint(mainpage_bp)
app.register_blueprint(meal_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(timetable_bp)
app.register_blueprint(post_bp)

@app.route("/")
def home():
    return redirect(url_for('main.main_page'))

if __name__ == "__main__":
    try:
        app.run(debug=False)
    except Exception as e:
        print(e)
