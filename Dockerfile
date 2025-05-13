# 1. Python 기반 이미지 사용
FROM python:3.10-slim

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. 코드 복사
COPY . /app/

# 4. 패키지 설치 (requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# 5. 코드 재복사
COPY . /app/

# 6. 앱 실행
CMD ["python", "app.py"]