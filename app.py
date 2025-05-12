from flask import Flask, jsonify
from pymongo import MongoClient
from datetime import datetime  # 이 줄을 추가하세요
import os

app = Flask(__name__)

# MongoDB 연결
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/jungdry')
client = MongoClient(mongo_uri)
db = client.get_database()


@app.route('/')
def home():
    return 'This is Home!'


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
    app.run('0.0.0.0', port=5001, debug=True)