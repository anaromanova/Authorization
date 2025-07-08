# Authorization by Phone Number

Сервис авторизации пользователей по номеру телефона с отправкой SMS-кодов и реферальной системой.

---

## 📁 Структура проекта

```
.
├── manage.py
├── pyproject.toml
├── README.md
├── htmlcov/                # отчёты покрытия (после pytest --cov-report=html)
├── users/                  # Django-приложение "users"
│   ├── migrations/
│   ├── models.py           # User, SMSCode
│   ├── serializers.py      # SendCodeSerializer, VerifyCodeSerializer, ProfileSerializer
│   ├── views.py            # SendCodeView, VerifyCodeView, ProfileView
│   ├── urls.py             # маршруты auth и profile
│   └── tests/
│       ├── test_auth_api.py
│       └── test_profile_api.py
└── config/           # настройки Django-проекта
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

---

## 🚀 Установка

1. **Клонировать репозиторий**  
   ```bash
   git clone https://github.com/anaromanova/Authorization.git
   cd Authorization_by_number
   ```

2. **Установить зависимости**  
   ```bash
   poetry install
   ```

3. **Настроить переменные окружения**  
   Скопируйте `env.example` в `.env` и заполните:
   ```
   SECRET_KEY=ваш_секретный_ключ
   DEBUG=True
   POSTGRES_USER=
   POSTGRES_PASSWORD=
   POSTGRES_DB=
   POSTGRES_HOST=
   POSTGRES_PORT=
   ```

4. **Применить миграции**  
   ```bash
   poetry run python manage.py migrate
   ```

5. **Запустить сервер**  
   ```bash
   poetry run python manage.py runserver
   ```
   Доступно по `http://127.0.0.1:8000/`.

---

## 🧪 Тесты и покрытие

- Запуск тестов:
  ```bash
  poetry run pytest -q
  ```
- Отчёт покрытия:
  ```bash
  poetry run pytest --cov=. --cov-report=term-missing --cov-report=html
  ```
  HTML-отчёт в `htmlcov/index.html`.

---

## 📡 API

Все эндпоинты под `/api/`.

### 1. Отправка кода

- **POST** `/api/auth/send-code/`
- **Body:**
  ```json
  { "phone": "+71234567890" }
  ```
- **Ответ 201:**
  ```json
  { "detail": "Code sent" }
  ```
- **Ошибки 400**: формат телефона, частые запросы.

### 2. Проверка кода

- **POST** `/api/auth/verify-code/`
- **Body:**
  ```json
  {
    "phone": "+71234567890",
    "code": "1234"
  }
  ```
- **Ответ 200:**
  ```json
  { "token": "<your_token_here>" }
  ```
- **Ошибки 400**: неверный или просроченный код.

### 3. Профиль пользователя

#### 3.1 Получение профиля

- **GET** `/api/profile/`
- **Header:** `Authorization: Token <your_token>`
- **Ответ 200:**
  ```json
  {
    "phone": "+71234567890",
    "invite_code": "ABC123",
    "used_invite_id": null
  }
  ```

#### 3.2 Применить реферальный код

- **PATCH** `/api/profile/`
- **Header:** `Authorization: Token <your_token>`
- **Body:**
  ```json
  { "invite_code": "ABC123" }
  ```
- **Ответ 200:**
  ```json
  {
    "phone": "+7…",
    "invite_code": "XYZ789",
    "used_invite_id": 1
  }
  ```
- **Ошибки 400**: неверный, свой или уже использованный код.

---
