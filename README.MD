# Jimin Chat

Django + Channels 기반의 1:1 실시간 채팅 웹 프로젝트입니다.  
회원가입, 로그인, 친구 추가, 친구 별명 관리, 이미지 업로드, 읽지 않은 메시지 수 표시, WebSocket 기반 실시간 채팅 기능을 포함합니다.

이 README는 다음 내용을 설명합니다.

1. Django가 무엇인지
2. 이 프로젝트의 폴더 구조
3. 어떤 파일이 백엔드이고 어떤 파일이 프론트엔드인지
4. 서로 다른 `.py`, `.html`, `.css` 파일이 어떻게 연결되는지
5. 주요 함수와 주요 화면의 역할

---

## 1. Django가 무엇인가

Django는 Python으로 웹 서비스를 만들기 위한 웹 프레임워크입니다.

쉽게 말하면 Django는 아래 역할을 체계적으로 나눠서 처리하게 도와줍니다.

- URL 처리: 어떤 주소로 요청이 들어왔는지 확인
- View 처리: 그 요청에 대해 어떤 동작을 할지 결정
- Model 처리: 데이터베이스에 어떤 데이터를 저장하고 읽을지 정의
- Template 처리: 사용자에게 보여줄 HTML 화면 생성
- Form 처리: 로그인, 회원가입, 프로필 수정 같은 입력 검증

이 프로젝트는 기본 Django 위에 `channels`를 추가해서 실시간 채팅 기능도 구현했습니다.

- 일반 HTTP 요청: 페이지 이동, 친구 추가, 닉네임 수정, 이미지 업로드
- WebSocket 요청: 채팅 메시지를 실시간으로 주고받는 연결

즉,

- Django는 웹사이트의 전체 구조를 담당하고
- Channels는 실시간 채팅을 담당합니다.

---

## 2. 기술 스택

- Backend: Python, Django, Django Channels
- Frontend: Django Template, HTML, CSS, Bootstrap, Vanilla JavaScript
- Database: SQLite
- Real-time: WebSocket
- File Upload: Pillow, Django `ImageField`
- Styling: 공통 CSS 파일 + Bootstrap 보조 사용

---

## 3. 프로젝트 구조

```text
jimin-chat/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── README.MD
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── context_processors.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── chat/
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── base.html
│   ├── includes/
│   │   └── form_field.html
│   ├── accounts/
│   │   ├── login.html
│   │   ├── password_change.html
│   │   ├── profile_edit.html
│   │   └── signup.html
│   └── chat/
│       ├── add_friend.html
│       ├── friend_list.html
│       └── room.html
└── static/
    └── css/
        └── app.css
```

---

## 4. 어떤 파일이 백엔드이고 어떤 파일이 프론트엔드인가

### 백엔드

Python 파일들이 백엔드입니다.

- `config/settings.py`
- `config/urls.py`
- `config/asgi.py`
- `config/context_processors.py`
- `accounts/models.py`, `accounts/forms.py`, `accounts/views.py`, `accounts/urls.py`
- `chat/models.py`, `chat/services.py`, `chat/views.py`, `chat/urls.py`
- `chat/consumers.py`, `chat/routing.py`

이 파일들은 다음을 담당합니다.

- 데이터베이스 구조 정의
- 로그인/회원가입/친구관리/채팅 로직 처리
- URL 연결
- WebSocket 연결 처리
- 템플릿에 어떤 데이터를 넘길지 결정

### 프론트엔드

브라우저에 직접 보이는 화면과 스타일이 프론트엔드입니다.

- `templates/**/*.html`
- `static/css/app.css`
- 각 HTML 안의 JavaScript

이 파일들은 다음을 담당합니다.

- 사용자에게 보이는 화면 구성
- 버튼, 카드, 채팅 말풍선, 폼 UI
- 클릭/전송/스크롤 같은 브라우저 동작
- WebSocket 연결 후 메시지 화면 갱신

---

## 5. 이 프로젝트의 큰 흐름

이 프로젝트는 크게 두 흐름으로 나뉩니다.

### A. 일반 페이지 요청 흐름

예: 로그인, 친구 목록 보기, 채팅방 입장, 친구 추가

```text
브라우저 요청
→ config/urls.py
→ accounts/urls.py 또는 chat/urls.py
→ 해당 view 함수 실행
→ model/service에서 데이터 조회 또는 저장
→ template 렌더링
→ HTML 응답 반환
```

### B. 실시간 채팅 흐름

예: 채팅방에서 메시지 보내기

```text
room.html의 JavaScript
→ WebSocket 연결 생성
→ config/asgi.py
→ chat/routing.py
→ chat/consumers.py
→ DB 저장 + 그룹 브로드캐스트
→ 같은 방 사용자들에게 실시간 반영
```

---

## 6. 파일들이 어떻게 유기적으로 연결되는가

이 프로젝트를 이해할 때 가장 중요한 연결은 아래 4개입니다.

### 1. URL → View 연결

- `config/urls.py` 는 전체 라우터입니다.
- 여기서 `accounts/urls.py`, `chat/urls.py` 로 요청을 넘깁니다.
- 각 앱의 `urls.py` 는 특정 `view` 함수나 클래스와 연결됩니다.

예시:

- `/accounts/login/` → 로그인 뷰
- `/chat/friends/` → 친구/채팅 목록 뷰
- `/chat/room/<room_name>/` → 채팅방 페이지 뷰

### 2. View → Model / Service 연결

`view`는 직접 모든 로직을 처리하지 않고,

- `models.py` 로 DB 구조를 사용하고
- `services.py` 로 공통 규칙을 분리합니다.

예를 들어 `chat/views.py`는

- 방 이름 생성 규칙
- 상대방 찾기
- 표시 이름 계산

같은 반복 규칙을 `chat/services.py` 함수로 위임합니다.

이 구조 덕분에 하드코딩이 줄고, 여러 파일이 같은 규칙을 공유할 수 있습니다.

### 3. View → Template 연결

`render(request, "템플릿경로", context)` 형태로 데이터를 HTML에 전달합니다.

예시:

- `chat/views.py` 의 `friend_list()` 는 `rooms`, `friends`, `unread_total` 을 `templates/chat/friend_list.html` 로 넘깁니다.
- `chat/views.py` 의 `room()` 은 `chat_messages`, `display_title`, `ws_path` 를 `templates/chat/room.html` 로 넘깁니다.

### 4. Template → JavaScript → WebSocket → Consumer 연결

채팅방에서는 HTML만으로 끝나지 않습니다.

- `templates/chat/room.html` 에서 WebSocket을 열고
- 메시지를 보내면
- `chat/consumers.py` 가 받아 DB에 저장하고
- 다시 브라우저로 보내서 화면을 갱신합니다.

즉, 채팅 화면은 프론트엔드와 백엔드가 가장 강하게 연결된 부분입니다.

---

## 7. config 폴더 설명

### `config/settings.py`

프로젝트 전체 설정 파일입니다.

주요 역할:

- 앱 등록: `accounts`, `chat`, `channels`
- DB 설정: SQLite
- 템플릿 설정
- 정적 파일 / 미디어 파일 설정
- 커스텀 유저 모델 설정: `AUTH_USER_MODEL = 'accounts.User'`
- 개발 중 로컬 IP를 자동으로 `ALLOWED_HOSTS` 에 추가
- 앱 이름, 태그라인, 버전 같은 공통 메타 정보 설정

### `config/urls.py`

프로젝트 최상위 URL 라우터입니다.

주요 역할:

- `/admin/`
- `/accounts/`
- `/chat/`
- `/` 접속 시 로그인 여부에 따라 홈 이동

주요 함수:

- `home_view(request)`
  - 로그인된 사용자는 친구 목록으로
  - 로그인 안 된 사용자는 로그인 페이지로 리다이렉트

### `config/asgi.py`

ASGI 애플리케이션 진입점입니다.

Channels를 사용하기 때문에 중요합니다.

주요 역할:

- 일반 HTTP 요청은 Django가 처리
- WebSocket 요청은 Channels가 처리

여기서 `chat.routing.websocket_urlpatterns` 와 연결됩니다.

### `config/context_processors.py`

템플릿 전체에서 공통으로 쓸 값을 넣는 파일입니다.

주요 함수:

- `app_meta(request)`
  - `app_name`
  - `app_tagline`
  - `app_version`

이 값들은 모든 템플릿에서 공통 브랜딩 정보로 사용됩니다.

---

## 8. accounts 앱 설명

`accounts` 앱은 사용자 인증과 계정 화면을 담당합니다.

### `accounts/models.py`

주요 클래스:

- `User(AbstractUser)`

기본 Django 사용자 모델을 확장해서 아래 필드를 추가합니다.

- `name`
- `age`

즉, 로그인에 필요한 기본 정보는 Django가 제공하고, 프로젝트용 사용자 정보는 여기서 확장합니다.

### `accounts/forms.py`

폼과 UI 입력 스타일을 담당합니다.

주요 클래스:

- `StyledFieldsMixin`
  - 폼 입력에 공통 CSS 클래스 `app-input` 적용
  - placeholder, autocomplete 속성 정리
- `CustomAuthenticationForm`
  - 로그인 폼
- `CustomUserCreationForm`
  - 회원가입 폼
- `UserProfileForm`
  - 프로필 수정 폼
- `CustomPasswordChangeForm`
  - 비밀번호 변경 폼

이 파일은 백엔드 검증과 프론트엔드 입력 스타일 사이를 연결해주는 중간층입니다.

### `accounts/views.py`

주요 동작을 처리합니다.

주요 요소:

- `SignUpView`
  - 회원가입 처리
- `profile_edit(request)`
  - 로그인한 사용자의 이름/나이 수정
- `CustomPasswordChangeView`
  - 비밀번호 변경 처리

### `accounts/urls.py`

계정 관련 URL을 정의합니다.

- `/accounts/signup/`
- `/accounts/login/`
- `/accounts/logout/`
- `/accounts/profile/edit/`
- `/accounts/password/change/`

### `accounts/tests.py`

현재는 인증 흐름 중 로그아웃을 테스트합니다.

주요 테스트:

- 로그아웃 요청 후 세션이 비워지고 로그인 페이지로 이동하는지 확인

---

## 9. chat 앱 설명

`chat` 앱은 친구 관계, 채팅 목록, 채팅방, 이미지 업로드, WebSocket 실시간 메시지를 담당합니다.

### `chat/models.py`

주요 모델:

- `Friendship`
  - 친구 관계 저장
  - `user`, `friend`, `nickname`, `created_at`
- `ChatMessage`
  - 채팅 메시지 저장
  - `sender`, `receiver`, `room_name`, `message`, `image`, `is_read`, `timestamp`

즉,

- `Friendship` 는 관계 데이터
- `ChatMessage` 는 채팅 데이터

입니다.

### `chat/services.py`

이 프로젝트에서 하드코딩을 줄이고 규칙을 공통화하는 핵심 파일입니다.

주요 함수:

- `build_room_name(user_a, user_b)`
  - 두 사용자 ID 기반 방 이름 생성
- `parse_room_name(room_name)`
  - 방 이름을 해석
- `is_room_participant(room_name, user)`
  - 현재 사용자가 해당 방 참여자인지 확인
- `get_other_user_for_room(room_name, current_user)`
  - 채팅 상대방 찾기
- `get_or_create_room_name(current_user, other_user)`
  - 기존 방이 있으면 재사용, 없으면 새 방 이름 생성
- `get_display_name(current_user, other_user, friendship=None)`
  - 친구 별명 우선, 없으면 이름/아이디로 표시
- `get_websocket_path(room_name)`
  - 채팅방 WebSocket 경로 생성

이 파일 덕분에

- 방 이름 규칙
- 권한 검사 규칙
- 상대방 찾기 규칙

을 여러 곳에서 중복하지 않고 재사용할 수 있습니다.

### `chat/views.py`

HTTP 기반 채팅 동작을 담당합니다.

주요 함수:

- `friend_list(request)`
  - 친구 목록 + 최근 채팅 목록 + 읽지 않은 메시지 수 계산
- `room(request, room_name)`
  - 채팅방 입장
  - 권한 확인
  - 메시지 읽음 처리
- `start_chat(request, user_id)`
  - 특정 사용자와 대화 시작
- `add_friend(request)`
  - 친구 추가
- `update_nickname(request)`
  - 친구 별명 수정
- `delete_friend(request)`
  - 친구 삭제
- `upload_image(request)`
  - 이미지 업로드 후 `ChatMessage` 레코드 생성

이 파일은 채팅 앱의 일반 HTTP 요청 진입점입니다.

### `chat/consumers.py`

WebSocket 실시간 채팅을 담당합니다.

주요 메서드:

- `connect()`
  - 채팅방 참여 가능 여부 확인
  - 채널 그룹에 참가
- `disconnect()`
  - 채널 그룹 탈퇴
- `receive()`
  - 브라우저에서 보낸 메시지 수신
  - 텍스트 메시지는 DB 저장
  - 방의 모든 사용자에게 브로드캐스트
- `chat_message()`
  - 브라우저로 최종 JSON 전송
- `save_message()`
  - 메시지를 DB에 저장

즉, `views.py` 가 일반 페이지 처리라면, `consumers.py` 는 실시간 채팅 처리입니다.

### `chat/routing.py`

WebSocket URL을 연결합니다.

예:

- `/ws/chat/<room_name>/`

이 경로는 `ChatConsumer` 와 연결됩니다.

### `chat/urls.py`

HTTP URL을 연결합니다.

- `/chat/friends/`
- `/chat/room/<room_name>/`
- `/chat/start/<user_id>/`
- `/chat/add_friend/`
- `/chat/update_nickname/`
- `/chat/delete_friend/`
- `/chat/upload_image/`

### `chat/tests.py`

채팅 핵심 규칙을 테스트합니다.

주요 테스트:

- 새 채팅 시작 시 ID 기반 방 이름을 사용하는지
- 기존 채팅방이 있으면 그 방을 재사용하는지
- 비슷한 사용자명이 있어도 권한 없는 사용자는 방에 접근하지 못하는지

---

## 10. 주요 HTML 설명

이 프로젝트의 프론트엔드는 Django Template 기반입니다.

### `templates/base.html`

모든 주요 화면의 공통 뼈대입니다.

주요 역할:

- 공통 `<head>` 구성
- Google Fonts 로드
- Bootstrap 로드
- 공통 CSS `static/css/app.css` 연결
- 페이지별 `block` 구조 제공

즉, 모든 페이지의 공통 외형을 책임집니다.

### `templates/includes/form_field.html`

폼 필드 렌더링용 재사용 조각입니다.

주요 역할:

- label 출력
- input 출력
- help text 출력
- error text 출력

반복되는 폼 HTML을 줄여줍니다.

### `templates/accounts/login.html`

로그인 화면입니다.

주요 역할:

- 로그인 폼 렌더링
- 공통 브랜딩 표시
- 회원가입 화면으로 이동 링크 제공

### `templates/accounts/signup.html`

회원가입 화면입니다.

주요 역할:

- 사용자 생성 폼 렌더링
- 이름, 나이, 아이디, 비밀번호 입력
- 오류 메시지 표시

### `templates/accounts/profile_edit.html`

프로필 수정 화면입니다.

주요 역할:

- 이름/나이 수정 폼 렌더링
- 저장/취소 동작 제공

### `templates/accounts/password_change.html`

비밀번호 변경 화면입니다.

주요 역할:

- 현재 비밀번호 / 새 비밀번호 입력
- 보안 관련 help text 표시

### `templates/chat/add_friend.html`

친구 추가 화면입니다.

주요 역할:

- 상대 아이디 입력
- 친구 추가 요청 전송
- 에러 메시지 표시

### `templates/chat/friend_list.html`

채팅 앱의 메인 대시보드 화면입니다.

주요 역할:

- 읽지 않은 메시지 총합 표시
- 최근 채팅 목록 표시
- 친구 목록 표시
- 친구 관리 모달 표시
- 친구 추가 / 로그아웃 / 프로필 이동

이 화면은 프로젝트에서 가장 많은 정보가 모이는 허브입니다.

### `templates/chat/room.html`

실시간 채팅방 화면입니다.

주요 역할:

- 기존 메시지 렌더링
- 텍스트 메시지 입력
- 이미지 업로드
- WebSocket 연결 생성
- 새 메시지를 HTML에 바로 반영
- 페이지 스크롤을 하단으로 이동

---

## 11. 주요 CSS 설명

### `static/css/app.css`

이 프로젝트의 공통 디자인 시스템 파일입니다.

주요 역할:

- 색상 변수 정의
- 카드, 버튼, 폼 입력, 배지, 모달 스타일 통일
- 친구 목록 대시보드 레이아웃
- 채팅방 레이아웃
- 반응형 스타일 조정

특히 아래 요소들을 공통화합니다.

- `.auth-card`
- `.panel-card`
- `.btn-app`
- `.btn-app-secondary`
- `.btn-app-ghost`
- `.btn-chip`
- `.chat-panel`
- `.chat-header`
- `.bubble`

즉, 개별 HTML이 직접 모든 스타일을 가지는 구조가 아니라, 공통 CSS가 전체 화면 일관성을 유지합니다.

---

## 12. HTTP와 WebSocket이 실제로 어떻게 이어지는가

### 친구 목록 진입

```text
브라우저
→ /chat/friends/
→ chat/urls.py
→ chat/views.py::friend_list()
→ Friendship / ChatMessage 조회
→ friend_list.html 렌더링
```

### 채팅 시작

```text
friend_list.html의 "채팅" 버튼
→ /chat/start/<user_id>/
→ chat/views.py::start_chat()
→ chat/services.py::get_or_create_room_name()
→ /chat/room/<room_name>/ 로 이동
```

### 채팅방 페이지 렌더링

```text
브라우저
→ /chat/room/<room_name>/
→ chat/views.py::room()
→ 권한 확인 + 메시지 조회 + 읽음 처리
→ room.html 렌더링
```

### 채팅 메시지 전송

```text
room.html JavaScript
→ WebSocket("/ws/chat/<room_name>/")
→ config/asgi.py
→ chat/routing.py
→ chat/consumers.py::receive()
→ DB 저장
→ group_send()
→ chat_message()
→ 브라우저에 새 메시지 표시
```

### 이미지 전송

```text
room.html JavaScript
→ POST /chat/upload_image/
→ chat/views.py::upload_image()
→ 이미지 파일 저장 + ChatMessage 생성
→ image_url 반환
→ WebSocket으로 image_url 브로드캐스트
→ 브라우저 화면 즉시 갱신
```

---

## 13. 이 프로젝트에서 백엔드와 프론트엔드의 경계

이 프로젝트는 전통적인 SPA 구조가 아니라 Django Template 기반 MPA + 실시간 채팅 구조입니다.

### 백엔드가 책임지는 것

- 사용자 인증
- 친구 관계 저장
- 채팅 메시지 저장
- 읽음 상태 계산
- 채팅방 권한 검사
- WebSocket 연결 검증
- 템플릿에 넘길 데이터 구성

### 프론트엔드가 책임지는 것

- 화면 렌더링
- 스타일 표현
- 버튼 클릭 처리
- WebSocket 메시지 수신 후 DOM 갱신
- 업로드 폼 전송
- 스크롤 보정

즉,

- “무엇을 할지 결정”하는 것은 백엔드
- “어떻게 보여줄지 표현”하는 것은 프론트엔드

입니다.

---

## 14. 주요 함수 빠른 요약

### 인증/계정

- `accounts/views.py::SignUpView`
- `accounts/views.py::profile_edit`
- `accounts/views.py::CustomPasswordChangeView`

### 친구/채팅 HTTP

- `chat/views.py::friend_list`
- `chat/views.py::room`
- `chat/views.py::start_chat`
- `chat/views.py::add_friend`
- `chat/views.py::update_nickname`
- `chat/views.py::delete_friend`
- `chat/views.py::upload_image`

### 채팅 규칙/공통 로직

- `chat/services.py::build_room_name`
- `chat/services.py::parse_room_name`
- `chat/services.py::is_room_participant`
- `chat/services.py::get_other_user_for_room`
- `chat/services.py::get_or_create_room_name`
- `chat/services.py::get_display_name`
- `chat/services.py::get_websocket_path`

### 실시간 채팅

- `chat/consumers.py::connect`
- `chat/consumers.py::receive`
- `chat/consumers.py::chat_message`
- `chat/consumers.py::save_message`

---

## 15. 실행 방법

### 1. 가상환경 생성 및 활성화

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. DB 초기화 방법

개발 중 데이터베이스를 완전히 새로 시작하고 싶다면 아래 순서로 초기화할 수 있습니다.

주의:

- 이 방법은 현재 `db.sqlite3` 안의 데이터를 모두 삭제합니다.
- 회원 정보, 친구 관계, 채팅 메시지, 업로드된 기록 연결 정보가 초기화됩니다.

macOS / Linux:

```bash
rm -f db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

Windows:

```bash
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

이미지 파일까지 완전히 비우고 싶다면 필요에 따라 `media/` 폴더도 함께 정리하면 됩니다.

### 4. 마이그레이션 적용

```bash
python manage.py migrate
```

### 5. 관리자 계정 생성

```bash
python manage.py createsuperuser
```

### 6. 서버 실행

로컬 브라우저에서만 볼 때:

```bash
python manage.py runserver
```

같은 와이파이의 휴대폰에서도 접속할 때:

```bash
python manage.py runserver 0.0.0.0:8000
```

이후 브라우저에서 접속:

- `http://127.0.0.1:8000`
- 또는 `http://내_로컬_IP:8000`

---

## 16. 테스트

프로젝트의 핵심 흐름 일부는 테스트로 확인할 수 있습니다.

```bash
python manage.py check
python manage.py test accounts chat
```

테스트 내용 예시:

- 로그아웃이 세션을 정상적으로 정리하는지
- 채팅방 이름 규칙이 올바른지
- 채팅방 접근 권한이 안전한지

---

## 17. 핵심 요약

이 프로젝트는 아래처럼 이해하면 가장 쉽습니다.

1. `config`는 전체 설정과 진입점을 관리한다.
2. `accounts`는 사용자 인증과 계정 화면을 담당한다.
3. `chat`은 친구/채팅 로직과 실시간 메시지를 담당한다.
4. `templates`는 사용자에게 보이는 화면이다.
5. `static/css/app.css`는 모든 화면의 공통 디자인 시스템이다.
6. `views.py`는 일반 웹 요청을 처리하고, `consumers.py`는 실시간 WebSocket 요청을 처리한다.
7. `services.py`는 여러 파일에서 공통으로 써야 하는 채팅 규칙을 모아두는 핵심 파일이다.

즉, 이 프로젝트는

- Django가 전체 웹 구조를 담당하고
- Channels가 실시간 채팅을 담당하며
- Template + CSS + JavaScript가 화면을 담당하는 구조입니다.
