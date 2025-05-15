import os
import redis
from datetime import timedelta

# Redis 연결
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))

# 리프레시 토큰 Redis에 저장
def save_refresh_token(user_id, token, expires_delta=None):
    key = f"refresh_token:{user_id}"
    if expires_delta:
        redis_client.setex(key, expires_delta, token)
    else:
        # 기본 2주 만료
        redis_client.setex(key, 1209600, token)

# 사용자의 리프레시 토큰 조회
def get_refresh_token(user_id):
    key = f"refresh_token:{user_id}"
    token = redis_client.get(key)
    if token:
        return token.decode('utf-8')
    return None

# 로그아웃 시 사용자의 리프레시 토큰 삭제
def delete_refresh_token(user_id):
    key = f"refresh_token:{user_id}"
    redis_client.delete(key)

# 특정 사용자의 모든 세션 토큰 삭제 (전체 로그아웃)
def delete_all_refresh_tokens(user_id):
    key = f"refresh_token:{user_id}"
    redis_client.delete(key)

def test_redis_connection():
    try:
        # Redis에 간단한 키-값 저장 테스트
        redis_client.set('test_key', 'test_value')
        value = redis_client.get('test_key')
        if value and value.decode('utf-8') == 'test_value':
            print("Redis 연결 성공!!!!")
            return True
        else:
            print("Redis 연결 실패...ㅠㅠ: 값 검증 오류")
            return False
    except Exception as e:
        print(f"Redis 연결 실패...ㅠㅠ: {e}")
        return False

# 애플리케이션 시작 시 Redis 연결 테스트
if __name__ == "__main__":
    test_redis_connection()