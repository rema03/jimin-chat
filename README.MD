# Jimin Chat

Django + Channels 기반의 1:1 실시간 채팅 웹 서비스입니다.  
중앙 통합 계정 시스템(`accounts.jimindev.com`)과의 JWT SSO 연동, 실시간 1:1 메시징, 친구 관리, 이미지 업로드 등의 기능을 포함합니다.

---

## 1. 아키텍처 및 기술 스택

- **Backend**: Python 3.12, Django 5.x, Django Channels 4.x (ASGI/WebSocket)
- **SSO 연동**: `jimin_token` (JWT 쿠키 기반 자동 회원 동기화 및 세션 발급)
- **Database**: SQLite3
- **Frontend**: Django Template, Vanilla JavaScript, HTML5, CSS3
- **Infrastructure**: Docker / Docker Compose, Caddy Reverse Proxy

---

## 2. 프로젝트 구조

```text
jimin-chat/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-entrypoint.sh
├── config/
│   ├── asgi.py                # ASGI 진입점 (HTTP & WebSocket 라우팅)
│   ├── context_processors.py  # 공통 메타데이터 전시기
│   ├── settings.py           # 프로젝트 환경 설정 & SSO/JWT 세팅
│   ├── urls.py               # 최상위 URL 라우터
│   └── wsgi.py
├── chat/
│   ├── accounts.py           # [SSO 전담] JWT 자동 로그인 미들웨어 & 리다이렉트 뷰
│   ├── admin.py              # 모델 어드민 등록
│   ├── apps.py
│   ├── consumers.py          # WebSocket 커넥션 및 실시간 브로드캐스팅
│   ├── models.py             # User, ChatMessage, Friendship 모델
│   ├── routing.py            # WebSocket URL 라우팅 (`/ws/chat/...`)
│   ├── services.py           # 비즈니스 공통 헬퍼 함수
│   ├── tests.py              # 단위 테스트
│   ├── urls.py               # HTTP 뷰 라우팅 (`/chat/...`)
│   └── views.py              # 채팅방/친구목록 HTTP 뷰
├── templates/
│   ├── base.html             # 레이아웃 공통 뼈대
│   └── chat/
│       ├── add_friend.html   # 친구 추가 모달/페이지
│       ├── friend_list.html # 메인 친구 목록 및 채팅방 대시보드
│       └── room.html        # 실시간 1:1 채팅방
└── static/
    └── css/
        └── app.css           # 커스텀 전용 스타일시트
```

---

## 3. 인증 및 SSO 연동 동작 방식

1. **중앙 계정 로그인 (`accounts.jimindev.com`)**:
   - 사용자가 로그인 또는 회원가입을 시도하면 `chat/accounts.py` 내의 `login_view` / `signup_view`를 통해 중앙 서비스로 이동합니다.
2. **JWT 토큰 쿠키 전송**:
   - 로그인 성공 시 도메인 공유 쿠키인 `jimin_token`이 저장됩니다.
3. **자동 사용자 동기화 (`JiminAccountsMiddleware`)**:
   - `jimin-chat`으로 되돌아오면, 미들웨어가 `jimin_token`을 해독하여 로컬 `User` 모델에 `update_or_create`로 계정을 동기화하고 세션을 연결합니다.

---

## 4. 주요 기능

- **친구 관리**: 친구 추가, 친구 별명(닉네임) 변경, 친구 삭제
- **실시간 대화**: WebSocket 기반 대화 송수신, 읽음 처리, 읽지 않은 메시지 카운트
- **미디어 업로드**: 이미지 파일 첨부 및 대화창 즉시 표시
- **성능 최적화**: 채팅방별 최신 메시지 Subquery 로딩, 인덱싱 적용

---

## 5. 실행 및 테스트

### Docker Compose 환경 실행
```bash
docker compose up -d --build jimin-chat
```

### 테스트 실행
```bash
docker compose exec jimin-chat python manage.py test
```
