from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
import bcrypt

# 환경 변수 로드
load_dotenv()

# MongoDB 연결
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client["jungdry"]

# 컬렉션 초기화
db.user.drop()
db.campus.drop()
db.laundry.drop()
db.use.drop()

# 캠퍼스 데이터 추가
campus_id = db.campus.insert_one({
    "email": "campus@example.com",
    "entry_date": datetime.now(),
    "status": "active"
}).inserted_id

# 사용자 데이터 추가
for i in range(1, 30):
    # 비밀번호 해싱
    password = "password123"
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user_id = db.user.insert_one({
        "email": f"user{i}@example.com",
        "pw": hashed_pw,  # 해싱된 비밀번호 저장
        "phone": "01012341234",
    }).inserted_id


# 세탁기 데이터 추가 (7대)
laundry_ids = []
for i in range(7):
    laundry_id = db.laundry.insert_one({
        "id": i + 1,          # 세탁기 번호
        "type": "washer",     # 세탁기 타입
        "name": f"세탁기 {i+1}"  # 세탁기 이름
    }).inserted_id
    laundry_ids.append(laundry_id)

# 건조기 데이터 추가 (7대)
dryer_ids = []
for i in range(7):
    dryer_id = db.laundry.insert_one({
        "id": i + 1,          # 건조기 번호
        "type": "dryer",      # 건조기 타입
        "name": f"건조기 {i+1}"  # 건조기 이름
    }).inserted_id
    dryer_ids.append(dryer_id)

print("데이터베이스 초기화 완료!")
print(f"캠퍼스 ID: {campus_id}")
print(f"사용자 ID: {user_id}")
print("세탁기 IDs:", laundry_ids)
print("건조기 IDs:", dryer_ids)