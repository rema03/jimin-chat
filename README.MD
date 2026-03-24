

Project name : Jimin Chat In webPage
프로젝트 설명 : Django channels(ASGI)를 이용해 Python과 html, sqlite로 사이트를 구현하였다.


프로젝트 구조 
jimin-chat/
├── manage.py              # 프로젝트 실행 및 관리 스크립트
├── db.sqlite3             # 테스트 데이터가 포함된 데이터베이스
├── requirements.txt       # 설치가 필요한 라이브러리 목록
├── config/                # 프로젝트 설정 폴더 (settings, asgi, routing)
├── accounts/              # 회원가입, 로그인, 프로필 관리 앱
└── chat/                  # 채팅방 생성, 메시지 송수신, 친구 관리 앱







실행 가이드
1. 최상위 폴더에서 쉘터미널을 연다.
2. 가상환경 생성 및 활성화 (python -m venv venv )
2.1 MAC/LINUX -> source venv/bin/activate
2.2 windows -> venv/Scripts/activate
//개발 환경은 MAC이였구 윈도우에선 테스트 하지 못했습니다.

3. pip install -r requirements.txt

DB 초기화
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser


4. python manage.py runserver
5. 브라우저에서 http://127.0.0.1:8000 접속



