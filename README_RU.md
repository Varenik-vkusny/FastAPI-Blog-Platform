[Read in English](README.md)
---

# ✒️ FastAPI & Telegram Bot: Блог-платформа

[![Start Python tests](https://github.com/Varenik-vkusny/FastAPI_with_TgBot/actions/workflows/ci.yml/badge.svg)](https://github.com/Varenik-vkusny/FastAPI_with_TgBot/actions/workflows/ci.yml)

Современный бэкенд для блог-платформы с полнофункциональным Telegram-ботом в качестве основного клиента.

---

## 🚀 О проекте

Этот проект представляет собой полноценную веб-платформу для ведения блога, построенную на микросервисной архитектуре. Он состоит из двух независимых компонентов:

*   **REST API на FastAPI:** Высокопроизводительный асинхронный бэкенд, который управляет всей бизнес-логикой и данными: пользователями, постами, лайками.
*   **Telegram-бот на aiogram 3:** Интерактивный клиент, который позволяет пользователям взаимодействовать с платформой, не покидая мессенджер.

Проект демонстрирует навыки создания современных веб-сервисов, асинхронного программирования и разработки чат-ботов.

---

## 🛠️ Стек технологий

*   **Бэкенд:**
    *   ![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
    *   ![FastAPI](https://img.shields.io/badge/FastAPI-0.100-009688?style=for-the-badge&logo=fastapi)
    *   ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-DB4437?style=for-the-badge&logo=sqlalchemy)
    *   ![Pydantic](https://img.shields.io/badge/Pydantic-2.0-E96F00?style=for-the-badge)
*   **Telegram-бот:**
    *   ![aiogram](https://img.shields.io/badge/aiogram-3.x-26A5E4?style=for-the-badge)
    *   ![httpx](https://img.shields.io/badge/httpx-async-000000?style=for-the-badge)
*   **База данных:**
    *   ![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite)
*   **Аутентификация и инструменты:**
    *   `python-jose` (JWT Tokens)
    *   `passlib` & `bcrypt` (Хэширование паролей)
    *   `Uvicorn` (ASGI-сервер)
    *   `python-dotenv` (Переменные окружения)

---

## ✨ Ключевые возможности

*   **Аутентификация и Авторизация:**
    *   🔐 Регистрация и вход пользователей по email/паролю.
    *   🛡️ Безопасное хранение паролей с использованием хэширования (bcrypt).
    *   🔑 Система авторизации на основе JWT-токенов (стандарт OAuth2).
*   **Управление контентом:**
    *   ✍️ CRUD-операции для постов (в данном проекте реализованы Create, Update и Read).
    *   👍 Система лайков с привязкой к пользователю и защитой от накрутки.
*   **Telegram-бот как клиент:**
    *   🤖 Полное управление аккаунтом (`/register`, `/login`) через интерфейс бота.
    *   ✍️ Создание постов прямо из Telegram.
    *   📈 Интерактивные inline-кнопки для лайков с обновлением сообщения "на лету" (AJAX-like experience).
    *   💬 Удобная навигация с помощью постоянной Reply-клавиатуры.
    *   🧠 Использование машины состояний (FSM) для реализации пошаговых диалогов.
*   **API:**
    *   📄 Автоматически генерируемая интерактивная документация (Swagger UI, ReDoc).

---

## 🏁 Начало работы

### Требования
*   Python 3.10+
*   Менеджер пакетов `pip`
*   Токен Telegram-бота от [@BotFather](https://t.me/BotFather)

### Установка и запуск

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/Varenik-vkusny/FastAPI_with_TgBot.git
    cd FastAPI_with_TgBot
    ```

2.  **Настройте бэкенд (FastAPI):**
    *   Перейдите в папку бэкенда: `cd backend_project_folder_name`
    *   Создайте и активируйте виртуальное окружение:
        ```bash
        python -m venv venv
        source venv/bin/activate  # Для Windows: venv\Scripts\activate
        ```
    *   Установите зависимости:
        ```bash
        pip install -r requirements.txt
        ```
    *   Запустите сервер:
        ```bash
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
        ```

3.  **Настройте Telegram-бота:**
    *   Откройте **новый терминал** и перейдите в папку с ботом: `cd bot_project_folder_name`
    *   Создайте и активируйте свое виртуальное окружение.
    *   Установите зависимости из `requirements.txt`.
    *   Создайте файл `.env` в корне папки бота и добавьте в него ваш токен:
        ```dotenv
        BOT_TOKEN="12345:ABC-DEF12345z_..."
        ```
    *   Запустите бота:
        ```bash
        python bot.py
        ```

4.  **Готово!** Найдите вашего бота в Telegram и начните работу с команды `/start`.

---

## 📖 API Документация

После запуска бэкенда интерактивная документация API будет доступна по адресам:
*   **Swagger UI:** `http://localhost:8000/docs`
*   **ReDoc:** `http://localhost:8000/redoc`
