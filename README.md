# 🧼 Jungdry - 기숙사 세탁기 예약 서비스

`Jungdry`는 크래프톤 정글 기숙사 세탁기/건조기를 예약하여 이용할 수 있는 서비스입니다.

</br>

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: MongoDB
- **Authentication**: JWT
- **Deployment**: AWS EC2 (Ubuntu), Nginx

</br>

## 🚀 주요 기능

- 사용자 회원가입 (JWT 토큰 발급)
- 로그인 및 인증 처리
- 세탁기/건조기 예약하기
- 내 예약 확인하기

</br>

## 📌 API 명세서 (회원가입/로그인)

### ✅ 공통 사항

| 항목 | 설명 |
| --- | --- |
| 인증 필요 API | `/`, `/reserve/<laundry_id>`, `/my_reservations`, `/cancel_reservation/<reservation_id>` |
| 인증 방식 | Flask `session` 사용 |

### 🧾 API 명세 테이블

| 기능 | **method** | URL | **request** | **response** |
| --- | --- | --- | --- | --- |
| 로그인 페이지 조회 | GET | `/login` | - | 로그인 화면 렌더링 |
| 로그인 요청 | POST | `/login` | `email`, `password` | 세션 저장 후 `/` 리다이렉트실패 시 로그인 페이지에 에러 표시 |
| 로그아웃 | GET | `/logout` | - | 세션 초기화 후 로그인 페이지로 리다이렉트 |
| 회원가입 페이지 조회 | GET | `/register` | - | 회원가입 화면 렌더링 |
| 회원가입 요청 | POST | `/register` | `email`, `password`, `phone_number` | 쿠키에 access/refresh token 저장 후 `/index` 리다이렉트실패 시 에러 표시 |
| 메인 페이지 (기기 목록) | GET | `/` | - | 세탁기/건조기 리스트, 사용 가능 여부(status: 0=가능, 1=사용중) |
| 예약 페이지 조회 | GET | `/reserve/<laundry_id>` | - | 기기 정보, 7일간 예약 가능 시간대 |
| 예약 요청 | POST | `/reserve/<laundry_id>` | `reserve_date`, `reserve_time` | 성공: `/` 리다이렉트실패: 에러 메시지 표시 |
| 내 예약 목록 조회 | GET | `/my_reservations` | - | 예약 리스트 및 기기 정보 |
| 예약 취소 | GET | `/cancel_reservation/<reservation_id>` | - | `/my_reservations` 리다이렉트 |

</br>

## ⚙️ 실행 방법

### ✅ 로컬 개발 환경

```bash
# 1. 레포지토리 클론
git clone <https://github.com/likewoody/jungdry.git>
cd jungdry

# 2. .env 파일 추가

# 3. Docker Desktop 설치 
https://www.docker.com/products/docker-desktop/
# Apple Silicon Mac의 경우 설치 과정에서 Rosetta 2 설치 메시지가 나타나면, 다음 명령어로 설치
softwareupdate --install-rosetta --agree-to-license

# 4. 설치 확인
docker --version
docker-compose --version

# 5. Docker 컨테이너 시작/빌드
# docker-compose.yml이 있는 디렉토리로 이동
cd jungdry

# 빌드 및 시작
docker-compose up --build

# 5. 컨테이너 실행 후 http://127.0.0.1:5000/에 접속하여 테스트
# MacOs의 경우 http://127.0.0.1:5001/에 접속하여 테스트
```

### 🚀 배포 (EC2 + Nginx)
http://54.180.95.109/

test 계정:
i : 1~20
email: user{i}@example.com
pass: password123

</br>

## 📁 디렉토리 구조

```
jungdry/
├── static/
│   ├── icons/           
│   ├── manifest.json     
│   ├── service-worker.js
├── templates/
│   ├── base.html        
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── reserve.html
│   ├──my_reservation.html
├── redis_service.py
├── init_db.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── app.py
└── README.md
```
