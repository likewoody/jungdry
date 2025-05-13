from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from pymongo import MongoClient
from datetime import datetime, timedelta  # 날짜와 시간 관련 모듈
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import re
import os

app = Flask(__name__)
app.secret_key = 'your-flask-secret'  # flash 메시지를 위해 설정

# MongoDB 연결
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/jungdry')
client = MongoClient(mongo_uri)
db = client.get_database()

# JWT 설정
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # 비밀키 (안전하게 관리해야 함)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # 토큰 만료 시간 1시간
jwt = JWTManager(app)

# -------------------------------
# 로그인 페이지 라우트
# -------------------------------
@app.route('/')
def login_page():
    return render_template('login.html')

# -------------------------------
# 회원가입 페이지 렌더링
# -------------------------------
@app.route('/register')
def reg_page():
    return render_template('reg.html')
# -------------------------------
# 회원가입 처리
# -------------------------------
# 회원가입 처리 라우트
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email_id = request.form['emaile']
        domain = request.form['userdomain']
        password = request.form['password']
        confirm = request.form['confirm']
        phone_prefix = request.form['phonePrefix']
        phone_num = request.form['phoneNum']

        # 이메일 유효성 검사
        if not email_id or not domain:
            session['message'] = "이메일을 입력해주세요."
            session['message_type'] = 'error'
            return redirect(url_for('register'))

        full_email = f"{email_id}@{domain}"

        # 비밀번호 확인
        if password != confirm:
            session['message'] = "비밀번호가 일치하지 않습니다."
            session['message_type'] = 'error'
            return redirect(url_for('register'))

        # 전화번호 유효성 검사
        if not re.match(r'^\d{7,8}$', phone_num):
            session['message'] = "전화번호는 숫자 7~8자리여야 합니다."
            session['message_type'] = 'error'
            return redirect(url_for('register'))

        # 전화번호 형식 지정
        formatted_phone = format_phone_number(phone_prefix, phone_num)

        # 사용자 데이터 저장 (예: MongoDB)
        db.user.insert_one({
            'email': full_email,
            'password': password,  # 실제로는 해싱된 비밀번호를 저장해야 합니다.
            'phone': formatted_phone,
            'created_at': datetime.now()
        })

        session['message'] = "회원가입이 완료되었습니다. 로그인해주세요."
        session['message_type'] = 'success'
        return redirect(url_for('login'))

    return render_template('register.html')
# -------------------------------
# 로그인 처리
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_id = request.form['username']
        domain = request.form['userdomain']
        password = request.form['password']

        full_email = f"{email_id}@{domain}"

        user = db.user.find_one({'email': full_email})

        if user and user['password'] == password:
            session['user'] = full_email
            session['message'] = "로그인 성공!"
            session['message_type'] = 'success'
            return redirect(url_for('dashboard'))
        else:
            session['message'] = "이메일 또는 비밀번호가 올바르지 않습니다."
            session['message_type'] = 'error'
            return redirect(url_for('login'))

    return render_template('login.html')
# -------------------------------
# JWT 인증 테스트용 보호된 라우트
# -------------------------------
@app.route('/api/protected')
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return f'{current_user}님 안녕하세요!'

@app.route('/test-mongo')
def test_mongo():
    try:
        # 서버 정보 가져오기
        server_info = client.server_info()
        # 테스트용 데이터 삽입
        test_collection = db.test_collection
        test_id = test_collection.insert_one({"test": "data", "timestamp": str(datetime.now())}).inserted_id
        # 삽입한 데이터 조회
        test_data = test_collection.find_one({"_id": test_id})

        return jsonify({
            "status": "success",
            "message": "MongoDB 연결 및 테스트 성공",
            "server_info": {
                "version": server_info.get("version", "unknown"),
                "uptime": server_info.get("uptime", 0)
            },
            "test_data": str(test_data)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"MongoDB 연결 오류: {str(e)}"
        }), 500


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)