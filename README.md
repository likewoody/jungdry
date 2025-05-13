# jungdry

정글 크래프톤 9기 0주차 프로젝트


</br>


## 프로젝트 실행 방법

1. 레포지토리 클론
    
    ```bash
     git clone <https://github.com/likewoody/jungdry.git>
     cd jungdry
    ```
    
2. .env 파일 추가
    
    ```bash
    MONGODB_URI=mongodb://mongo:2701
    ```
    
3. Docker Desktop 설치
https://www.docker.com/products/docker-desktop/
    
    Apple Silicon Mac의 경우
    설치 과정에서 Rosetta 2 설치 메시지가 나타나면, 다음 명령어로 설치
    
    ```bash
    softwareupdate --install-rosetta --agree-to-license
    ```
    
4. 설치 확인
    
    ```bash
    docker --version
    docker-compose --version
    ```
    
5. Docker 컨테이너 시작/빌드
    
    ```bash
    # docker-compose.yml이 있는 디렉토리로 이동
    cd 프로젝트_디렉토리
    
    # 빌드 및 시작
    docker-compose up --build
    ```
    

1. 컨테이너 실행 후
<http://127.0.0.1:5001/test-mongo> 에 접속하여 테스트

</br>

### Docker 참고 명령어

```bash
# Docker 실행 상태 확인
docker info

# 백그라운드에서 실행
docker-compose up -d

# Docker 컨테이너 중지
docker-compose down

# 실행 중인 컨테이너
docker ps

# 모든 컨테이너 (중지된 것 포함)
docker ps -a
```
