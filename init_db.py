# 데이터베이스 초기화 스크립트
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# MongoDB 연결
# client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
client = MongoClient("mongodb://localhost:27017/jungdry")
db = client.jungdry

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
user_id = db.user.insert_one({
    "email": "user@example.com",
    "pw": "password123",
}).inserted_id

# 세탁기 데이터 추가 (8대)
laundry_ids = []
for i in range(8):
    laundry_id = db.laundry.insert_one({
        "id": i + 1  # 세탁기 번호
    }).inserted_id
    laundry_ids.append(laundry_id)

print("데이터베이스 초기화 완료!")
print(f"캠퍼스 ID: {campus_id}")
print(f"사용자 ID: {user_id}")
print("세탁기 IDs:", laundry_ids)