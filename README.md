[Читать на русском](README_RU.md)
---

# ✒️ FastAPI & Telegram Bot: Blog Platform

[![Start Python tests](https://github.com/Varenik-vkusny/FastAPI_with_TgBot/actions/workflows/ci.yml/badge.svg)](https://github.com/Varenik-vkusny/FastAPI_with_TgBot/actions/workflows/ci.yml)

An asynchronous backend for a blog platform built with FastAPI, featuring a full-featured Telegram bot (Aiogram 3) as the primary client. The project is fully containerized using Docker.

---

## 🚀 Architecture & Technology

This project is built on a microservice-style architecture and demonstrates a full-cycle backend development process.

*   **REST API on FastAPI:** A high-performance asynchronous backend that manages all business logic and data: users, posts, and likes.
*   **Telegram Bot on Aiogram 3:** An isolated client service that allows users to interact with the platform via Telegram.
*   **Database (PostgreSQL):** A reliable storage for all data.
*   **Cache (Redis):** Used for caching user post lists to reduce database load and speed up responses.

### 🛠️ Tech Stack

*   **Backend:** Python 3.12, **FastAPI**, **SQLAlchemy 2.0 (async)**, Pydantic V2, Alembic
*   **Databases:** **PostgreSQL**, **Redis**
*   **Authentication:** **JWT** (python-jose), **OAuth2**, passlib[bcrypt]
*   **Infrastructure & DevOps:** **Docker**, **Docker Compose**, **CI/CD (GitHub Actions)**
*   **Testing:** **Pytest**, httpx

---

## ✨ Key Features

*   **Security:**
    *   Full registration and authentication system based on **JWT tokens** (OAuth2).
    *   Secure password hashing using `bcrypt`.
    *   Endpoint protection against unauthorized access.
*   **Reliability & Code Quality:**
    *   **Comprehensive Test Coverage:** E2E tests for all API endpoints.
    *   **Isolated Test Environment:** Pytest is configured to work with an in-memory SQLite database and a separate test Redis database.
    *   **Automated Quality Assurance:** A CI pipeline on GitHub Actions runs tests on every commit.
    *   **DB Migrations:** PostgreSQL schema management with Alembic.
*   **User Features (via Telegram Bot):**
    *   Full account management (`/register`, `/login`).
    *   CRUD operations for posts.
    *   Interactive like system with protection against duplicate likes.
    *   Use of a Finite-State Machine (FSM) for step-by-step dialogs.

---

## 🏁 Getting Started

### Prerequisites
*   Docker
*   Docker Compose

### Installation & Launch

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Varenik-vkusny/FastAPI_with_TgBot.git
    cd FastAPI_with_TgBot
    ```

2.  **Set up environment variables:**
    *   Copy `.env.example` to `.env` and `.env.db.example` to `.env.db`.
    *   Fill in `BOT_TOKEN` and `SECRET_KEY` in the `.env` file.

3.  **Run the application:**
    ```bash
    docker-compose up --build
    ```

4.  **Apply migrations (in a separate terminal):**
    *   Wait for the containers to start up, then execute:
    ```bash
    docker-compose exec web alembic upgrade head
    ```
5.  **Done!**
    *   The API is available at `http://localhost:8000`
    *   Interactive API documentation: `http://localhost:8000/docs`
    *   Your Telegram bot is now running and ready to use.

---

### Running Tests

A running Redis container is required to run the E2E tests.

1.  **Start Redis in detached mode:**
    ```bash
    docker-compose up -d redis
    ```
2.  **Install dependencies and run tests:**
    ```bash
    pip install -r requirements.txt
    pytest
    ```
3.  **Stop Redis after testing:**
    ```bash
    docker-compose down
    ```

---
### Stopping the Application
```bash
docker-compose down