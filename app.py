from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from redis_service import save_refresh_token, get_refresh_token, delete_refresh_token
import bcrypt
import functools


# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# JWT 설정
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=int(os.getenv("ACCESS_TOKEN_EXPIRES", 1800)))
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=int(os.getenv("REFRESH_TOKEN_EXPIRES", 1209600)))
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False  # 개발 환경 : False, 프로덕션 : True
app.config["JWT_COOKIE_CSRF_PROTECT"] = True

jwt = JWTManager(app)


# MongoDB 연결 - 도커 컴포즈 환경에 맞게 수정
# docker-compose.yml에서 설정한 MONGO_URI 환경 변수 사용
mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
client = MongoClient(mongo_uri)
db = client["jungdry"]


# JWT가 필요한 엔드포인트용 데코레이터
def jwt_login_required(f):
    @functools.wraps(f)  # 원본 함수의 메타데이터 유지
    def decorated_function(*args, **kwargs):
        try:
            # JWT 토큰 검증 시도
            verify_jwt_in_request()
            # JWT에서 사용자 ID 가져오기
            current_user_id = get_jwt_identity()
            return f(current_user_id, *args, **kwargs)
        except:
            # JWT 검증 실패 시 로그인 페이지로 리디렉션
            return redirect(url_for("login"))

    return decorated_function


# # 현재 사용자가 로그인되어 있는지 확인하는 데코레이터
# def login_required(f):
#     def decorated_function(*args, **kwargs):
#         if "user_id" not in session:
#             return redirect(url_for("login"))
#         return f(*args, **kwargs)
#
#     decorated_function.__name__ = f.__name__
#     return decorated_function


@app.route("/")
def home():
    # JWT 토큰이 있는지 확인 (로그인 상태 확인)
    try:
        verify_jwt_in_request(optional=True)
        current_user = get_jwt_identity()
        if current_user:
            # 로그인된 경우 인덱스 페이지로
            return redirect(url_for("index"))
    except:
        pass

    # 로그인되지 않은 경우 로그인 페이지로
    return redirect(url_for("login"))


@app.route("/index")
@jwt_required()
def index():
    # 현재 사용자 ID 가져오기
    current_user_id = get_jwt_identity()

    # 모든 세탁기와 건조기 정보 가져오기
    laundries = list(db.laundry.find())

    # 현재 시간
    now = datetime.now()

    # 각 기기의 사용 가능 여부 확인
    for laundry in laundries:
        # 현재 시간으로부터 기기 사용 시간 이내에 예약이 있는지 확인
        duration_hours = 2 if laundry.get("type") == "dryer" else 1
        end_time = now + timedelta(hours=duration_hours)

        # 해당 기기에 대한 현재 활성화된 예약이 있는지 확인
        reservation = db.use.find_one({
            "laundry_id": laundry["_id"],
            "$or": [
                # 현재 진행 중인 예약
                {"start_time": {"$lte": now}, "end_time": {"$gte": now}},
                # 현재부터 사용 시간 이내에 시작하는 예약
                {"start_time": {"$gt": now, "$lt": end_time}}
            ]
        })

        # 예약이 없으면 사용 가능(0), 있으면 사용 불가(1)
        laundry["status"] = 1 if reservation else 0

    return render_template("index.html", laundries=laundries)


@app.route("/reserve/<laundry_id>", methods=["GET", "POST"])
@jwt_required()
def reserve(laundry_id):
    current_user_id = get_jwt_identity()
    laundry = db.laundry.find_one({"_id": ObjectId(laundry_id)})

    if request.method == "POST":
        # 예약 날짜와 시간 가져오기
        reserve_date = request.form.get("reserve_date")
        reserve_time = request.form.get("reserve_time")

        # 시작 시간 생성
        start_time = datetime.strptime(f"{reserve_date} {reserve_time}", "%Y-%m-%d %H:%M")

        # 종료 시간 (세탁기: 1시간, 건조기: 2시간)
        duration_hours = 2 if laundry.get("type") == "dryer" else 1
        end_time = start_time + timedelta(hours=duration_hours)

        # 0시~6시 사이의 예약은 거부
        if start_time.hour < 6 and start_time.hour >= 0:
            return render_template("reserve.html", laundry=laundry, error="오전 0시부터 6시까지는 예약할 수 없습니다.")

        # 해당 시간에 이미 예약이 있는지 확인
        existing_reservation = db.use.find_one({
            "laundry_id": ObjectId(laundry_id),
            "$or": [
                # 새 예약 시간이 기존 예약 시간과 겹치는 경우
                {"start_time": {"$lt": end_time}, "end_time": {"$gt": start_time}}
            ]
        })

        if existing_reservation:
            return render_template("reserve.html", laundry=laundry, error="이미 예약된 시간입니다.")

        # 새 예약 생성
        new_reservation = {
            "laundry_id": ObjectId(laundry_id),
            "user_id": ObjectId(current_user_id),
            "status": "reserved",
            "start_time": start_time,
            "end_time": end_time,
            "created_at": datetime.now()
        }

        db.use.insert_one(new_reservation)
        return redirect(url_for("index"))

    # 예약 가능한 시간 확인
    available_times = get_available_times(laundry_id)

    return render_template("reserve.html", laundry=laundry, available_times=available_times)


def get_available_times(laundry_id):
    # 세탁기/건조기 정보 가져오기
    laundry = db.laundry.find_one({"_id": ObjectId(laundry_id)})

    # 현재 날짜부터 7일간의 예약 가능 시간 생성
    available_times = {}
    now = datetime.now()

    # 시작 시간을 현재 시간의 다음 시간 단위로 맞춤
    start_hour = now.hour
    if now.minute > 0:  # 현재 분이 0분이 아니면 다음 시간으로
        start_hour = (now.hour + 1) % 24

    # 현재 날짜부터 7일 동안의 예약 가능 시간 생성
    for day_offset in range(7):
        check_date = (now + timedelta(days=day_offset)).date()
        date_str = check_date.strftime("%Y-%m-%d")
        available_times[date_str] = []

        # 첫날은 현재 시간 이후의 시간만 표시
        if day_offset == 0:
            hour_range = range(start_hour, 24)
        else:
            hour_range = range(0, 24)

        for hour in hour_range:
            # 00시~05시(새벽 시간)는 제외
            if hour < 6:
                continue

            time_slot = f"{hour:02d}:00"
            check_time = datetime.strptime(f"{date_str} {time_slot}", "%Y-%m-%d %H:%M")

            # 예약 종료 시간 (세탁기: 1시간, 건조기: 2시간)
            duration_hours = 2 if laundry.get("type") == "dryer" else 1
            end_time = check_time + timedelta(hours=duration_hours)

            # 해당 시간에 예약이 있는지 확인
            existing_reservation = db.use.find_one({
                "laundry_id": ObjectId(laundry_id),
                "$or": [
                    # 새 예약 시간이 기존 예약 시간과 겹치는 경우
                    {"start_time": {"$lt": end_time}, "end_time": {"$gt": check_time}}
                ]
            })

            if not existing_reservation:
                available_times[date_str].append(time_slot)

    return available_times


@app.route("/my_reservations")
@jwt_required()
def my_reservations():
    current_user_id = get_jwt_identity()

    # 현재 시간
    now = datetime.now()

    # 현재 로그인한 사용자의 예약 목록 가져오기
    reservations = list(db.use.find({"user_id": ObjectId(current_user_id)}).sort("start_time", 1))

    # 세탁기 정보 추가
    for reservation in reservations:
        laundry = db.laundry.find_one({"_id": reservation["laundry_id"]})
        reservation["laundry_info"] = laundry

    return render_template("my_reservations.html", reservations=reservations, now=now)


@app.route("/cancel_reservation/<reservation_id>")
@jwt_required()
def cancel_reservation(reservation_id):
    current_user_id = get_jwt_identity()

    # 예약 삭제
    db.use.delete_one({
        "_id": ObjectId(reservation_id),
        "user_id": ObjectId(current_user_id)
    })

    return redirect(url_for("my_reservations"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")

        # 이메일 중복 확인
        existing_user = db.user.find_one({"email": email})
        if existing_user:
            return render_template("register.html", error="이미 등록된 이메일입니다.")

        # 비밀번호 해싱 (bcrypt 사용)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # 새 사용자 등록
        new_user = {
            "email": email,
            "pw": hashed_password,
            "phone": phone,
            "created_at": datetime.now()
        }

        user_id = db.user.insert_one(new_user).inserted_id

        # JWT 토큰 생성
        access_token = create_access_token(identity=str(user_id))
        refresh_token = create_refresh_token(identity=str(user_id))

        # Redis에 리프레시 토큰 저장
        save_refresh_token(
            str(user_id),
            refresh_token,
            int(os.getenv("REFRESH_TOKEN_EXPIRES", 1209600))
        )

        response = make_response(redirect(url_for("index")))

        # 쿠키에 토큰 설정
        response.set_cookie(
            'access_token_cookie',
            access_token,
            max_age=int(os.getenv("ACCESS_TOKEN_EXPIRES", 1800)),
            httponly=True
        )
        response.set_cookie(
            'refresh_token_cookie',
            refresh_token,
            max_age=int(os.getenv("REFRESH_TOKEN_EXPIRES", 1209600)),
            httponly=True
        )

        return response

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.user.find_one({"email": email})

        # 사용자가 존재하는지 확인
        if not user:
            return render_template("login.html", error="이메일 또는 비밀번호가 올바르지 않습니다.")

        try:
            if isinstance(user['pw'], bytes):
                login_success = bcrypt.checkpw(password.encode('utf-8'), user['pw'])
            # 평문인 경우
            else:
                login_success = (user['pw'] == password)
        except:
            login_success = False


        if login_success:
            # JWT 토큰 생성
            access_token = create_access_token(identity=str(user["_id"]))
            refresh_token = create_refresh_token(identity=str(user["_id"]))

            # Redis에 리프레시 토큰 저장
            save_refresh_token(
                str(user["_id"]),
                refresh_token,
                int(os.getenv("REFRESH_TOKEN_EXPIRES", 1209600))
            )

            response = make_response(redirect(url_for("index")))

            # 쿠키에 토큰 설정 (HttpOnly)
            response.set_cookie(
                'access_token_cookie',
                access_token,
                max_age=int(os.getenv("ACCESS_TOKEN_EXPIRES", 1800)),
                httponly=True
            )
            response.set_cookie(
                'refresh_token_cookie',
                refresh_token,
                max_age=int(os.getenv("REFRESH_TOKEN_EXPIRES", 1209600)),
                httponly=True
            )

            return response
        else:
            return render_template("login.html", error="이메일 또는 비밀번호가 올바르지 않습니다.")

    return render_template("login.html")


# 토큰 갱신 엔드포인트
@app.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()

    # Redis에서 저장된 리프레시 토큰 확인
    stored_token = get_refresh_token(current_user_id)

    # 요청의 리프레시 토큰
    refresh_token = request.cookies.get('refresh_token_cookie')

    # 토큰 불일치 시 거부 (토큰 재사용 시도)
    if stored_token != refresh_token:
        return jsonify({"msg": "유효하지 않은 리프레시 토큰입니다."}), 401

    # 새로운 액세스 토큰 생성
    access_token = create_access_token(identity=current_user_id)

    response = jsonify({"access_token": access_token})
    response.set_cookie(
        'access_token_cookie',
        access_token,
        max_age=int(os.getenv("ACCESS_TOKEN_EXPIRES", 1800)),
        httponly=True
    )

    return response


@app.route("/logout")
@jwt_required(optional=True)
def logout():
    current_user_id = get_jwt_identity()

    # 사용자가 로그인된 상태면 토큰 삭제
    if current_user_id:
        delete_refresh_token(current_user_id)

    response = make_response(redirect(url_for("login")))

    # 쿠키 삭제
    response.delete_cookie('access_token_cookie')
    response.delete_cookie('refresh_token_cookie')

    return response


@app.context_processor
def inject_user():
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
        if current_user_id:
            return {'is_logged_in': True}
    except:
        pass
    return {'is_logged_in': False}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)