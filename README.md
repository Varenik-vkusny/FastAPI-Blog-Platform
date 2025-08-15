[Читать на русском](README_RU.md)
---

# ✒️ FastAPI & Telegram Bot: Blog Platform

A modern backend for a blog platform with a full-featured Telegram bot as the primary client.

---

## 🚀 About The Project

This project is a complete web platform for blogging, built on a microservice-style architecture. It consists of two independent components:

*   **REST API on FastAPI:** A high-performance asynchronous backend that manages all business logic and data: users, posts, and likes.
*   **Telegram Bot on aiogram 3:** An interactive client that allows users to interact with the platform without leaving the messenger.

This project showcases skills in building modern web services, asynchronous programming, and chatbot development.

---

## 🛠️ Tech Stack

*   **Backend:**
    *   ![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
    *   ![FastAPI](https://img.shields.io/badge/FastAPI-0.100-009688?style=for-the-badge&logo=fastapi)
    *   ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-DB4437?style=for-the-badge&logo=sqlalchemy)
    *   ![Pydantic](https://img.shields.io/badge/Pydantic-2.0-E96F00?style=for-the-badge)
*   **Telegram Bot:**
    *   ![aiogram](https://img.shields.io/badge/aiogram-3.x-26A5E4?style=for-the-badge)
    *   ![httpx](https://img.shields.io/badge/httpx-async-000000?style=for-the-badge)
*   **Database:**
    *   ![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite)
*   **Authentication & Tools:**
    *   `python-jose` (JWT Tokens)
    *   `passlib` & `bcrypt` (Password Hashing)
    *   `Uvicorn` (ASGI Server)
    *   `python-dotenv` (Environment Variables)

---

## ✨ Key Features

*   **Authentication & Authorization:**
    *   🔐 User registration and login via email/password.
    *   🛡️ Secure password storage using hashing (bcrypt).
    *   🔑 JWT-based authentication system (OAuth2 standard).
*   **Content Management:**
    *   ✍️ CRUD operations for posts (Create, Update and Read implemented).
    *   👍 Like system tied to users with protection against duplicate likes.
*   **Telegram Bot as a Client:**
    *   🤖 Full account management (`/register`, `/login`) through the bot's interface.
    *   ✍️ Post creation directly from Telegram.
    *   📈 Interactive inline buttons for likes with on-the-fly message updates (AJAX-like experience).
    *   💬 Convenient navigation using a persistent Reply Keyboard.
    *   🧠 Use of a Finite-State Machine (FSM) to implement step-by-step dialogs.
*   **API:**
    *   📄 Auto-generated interactive API documentation (Swagger UI, ReDoc).

---

## 🏁 Getting Started

### Prerequisites
*   Python 3.10+
*   `pip` package manager
*   A Telegram bot token from [@BotFather](https://t.me/BotFather)

### Installation & Launch

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Varenik-vkusny/FastAPI_with_TgBot.git
    cd FastAPI_with_TgBot
    ```

2.  **Set up the Backend (FastAPI):**
    *   Navigate to the backend directory: `cd backend_project_folder_name`
    *   Create and activate a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate  # For Windows: venv\Scripts\activate
        ```
    *   Install the dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   Run the server:
        ```bash
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
        ```

3.  **Set up the Telegram Bot:**
    *   Open a **new terminal** and navigate to the bot directory: `cd bot_project_folder_name`
    *   Create and activate its own virtual environment.
    *   Install dependencies from its `requirements.txt`.
    *   Create a `.env` file in the bot's root directory and add your token:
        ```dotenv
        BOT_TOKEN="12345:ABC-DEF12345z_..."
        ```
    *   Run the bot:
        ```bash
        python bot.py
        ```

4.  **Done!** Find your bot on Telegram and start with the `/start` command.

---

## 📖 API Documentation

Once the backend is running, the interactive API documentation will be available at:
*   **Swagger UI:** `http://localhost:8000/docs`
*   **ReDoc:** `http://localhost:8000/redoc`
