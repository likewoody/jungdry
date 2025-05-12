# jungdry
정글 크래프톤 9기 0주차 프로젝트


## 프로젝트 실행 방법

1. 레포지토리 클론
  ``` bash
   git clone https://github.com/likewoody/jungdry.git
   cd jungdry
```

2. Docker Desktop 설치
   https://www.docker.com/products/docker-desktop/

   Apple Silicon Mac의 경우
   설치 과정에서 Rosetta 2 설치 메시지가 나타나면, 다음 명령어로 설치
   ``` bash
   softwareupdate --install-rosetta --agree-to-license
  ```

3. 설치 확인

``` bash
   docker --version
   docker-compose --version
```

4. Docker 컨테이너 시작/빌드
   ``` bash
   # docker-compose.yml이 있는 디렉토리로 이동
   cd 프로젝트_디렉토리

   # 빌드 및 시작
   docker-compose up --build

   # 백그라운드에서 실행
   docker-compose up -d

   # Docker 컨테이너 중지
   docker-compose down
```

5. 컨테이너 실행 후
   http://127.0.0.1:5001/test-mongo 에 접속하여 테스트
