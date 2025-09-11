[Read in Russian](README.ru.md)
---

# ✒️ FastAPI & Telegram Bot: Blog Platform

[![Start Python tests](https://github.com/Varenik-vkusny/FastAPI_with_TgBot/actions/workflows/ci.yml/badge.svg)](https://github.com/Varenik-vkusny/FastAPI_with_TgBot/actions/workflows/ci.yml)

An asynchronous backend for a blog platform built with FastAPI, featuring a full-featured Telegram bot (Aiogram 3) as the primary client. The project is fully containerized with Docker and is ready for deployment in Kubernetes.

---

## 🚀 Architecture and Technologies

The project is built on a microservice architecture and demonstrates the full backend development lifecycle.

*   **REST API with FastAPI:** A high-performance, asynchronous backend that manages all business logic and data: users, posts, and likes.
*   **Telegram Bot with Aiogram 3:** An isolated client service that allows users to interact with the platform via Telegram.
*   **Database (PostgreSQL):** A reliable storage for all data.
*   **Cache (Redis):** Used for caching user post lists, which reduces the load on the database and speeds up responses.

### 🛠️ Tech Stack

*   **Backend:** Python 3.12, **FastAPI**, **SQLAlchemy 2.0 (async)**, Pydantic V2, Alembic
*   **Databases:** **PostgreSQL**, **Redis**
*   **Authentication:** **JWT** (python-jose), **OAuth2**, passlib[bcrypt]
*   **Infrastructure and DevOps:** **Docker**, **Docker Compose**, **Kubernetes (K8s)**, **CI/CD (GitHub Actions)**
*   **Testing:** **Pytest**, httpx

---

## ✨ Key Features

*   **Security:**
    *   Complete registration and authorization system based on **JWT tokens** (OAuth2).
    *   Secure password hashing using `bcrypt`.
    *   Endpoint protection against unauthorized access.
*   **Reliability and Code Quality:**
    *   **Full test coverage:** E2E tests for all API endpoints.
    *   **Isolated test environment:** Pytest configured to work with an in-memory SQLite and a test Redis database.
    *   **Automated quality checks:** A CI pipeline on GitHub Actions runs tests on every commit.
    *   **DB Migrations:** PostgreSQL schema management with Alembic.
*   **User Functionality (via Telegram Bot):**
    *   Full account management (`/register`, `/login`).
    *   CRUD operations for posts.
    *   Interactive liking system with protection against manipulation.
    *   Use of Finite State Machine (FSM) for step-by-step dialogues.

---

## 🏁 Launch and Deployment

### Using Docker Compose (for local development)

#### Prerequisites
*   Docker
*   Docker Compose

#### Installation and Startup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Varenik-vkusny/FastAPI-Blog-Platform.git
    cd FastAPI-Blog-Platform
    ```

2.  **Set up environment variables:**
    *   Copy `.env.example` to `.env` and `.env.db.example` to `.env.db`.
    *   Fill in `BOT_TOKEN` and `SECRET_KEY` in the `.env` file.

3.  **Run the application:**
    ```bash
    docker-compose up --build
    ```

4.  **Apply migrations (in a separate terminal):**
    *   Wait for the containers to start, then run:
    ```bash
    docker-compose exec web alembic upgrade head
    ```
5.  **Done!**
    *   The API is available at `http://localhost:8000`
    *   Interactive API documentation: `http://localhost:8000/docs`
    *   Your Telegram bot is running and ready to use.

#### Stopping the Application
```bash
docker-compose down
```

---

### In Kubernetes (for a production-like environment)

This section describes how to deploy the application in a local Kubernetes cluster, such as Minikube.

#### Prerequisites

1.  **kubectl**: An installed and configured Kubernetes command-line client.
2.  **Minikube**: An installed local Kubernetes cluster.
3.  **Nginx Ingress Controller**: Installed in Minikube. It can be enabled with the command:
    ```bash
    minikube addons enable ingress
    ```

#### 2. Applying the Manifests

All Kubernetes resources (Deployments, Services, ConfigMaps, etc.) are defined in the `k8s/` directory.

1.  **Create the Namespace where all application components will reside:**
    ```bash
    kubectl apply -f k8s/00-namespace.yaml
    ```
    
2.  **Apply all other manifests:**
    ```bash
    kubectl apply -f k8s/
    ```

3.  **Checking Deployment Status**
    ```bash
    kubectl get all --namespace=fastapi-with-bot
    ```

You should see running pods for `app`, `bot`, `postgres`, and `redis`. Ensure that the migration job `migration-job` has a `Completed` status.


#### 4. Accessing the Application

To access the API via Ingress in Minikube, we will use a direct port-forward to the Ingress controller.

1.  **Get the direct access URL (run in a terminal):**

    This command will find the Ingress controller service and create a temporary "bridge" to it from your machine.
    ```bash
    minikube service ingress-nginx-controller -n ingress-nginx --url
    ```
    The command will output one or two URLs, for example, `http://127.0.0.1:57135`. **Copy this URL (including the port)**.

2.  **Test the API using `curl` (run in another terminal):**

    Now, send a request using the URL you obtained.
    ```bash
    # Replace http://127.0.0.1:XXXXX with the URL from the previous step
    curl -v -H "Host: fastapi-with-bot.local" http://127.0.0.1:XXXXX/docs
    ```
    
    **What to look for in the `curl` output:**
    *   At the very beginning, you should see `* Connected to 127.0.0.1 (...)`.
    *   At the end, you should receive an `HTTP/1.1 200 OK` response and the HTML content of the Swagger documentation.

    If you get a `200 OK`, everything is working perfectly! The application is accessible, and Ingress is routing traffic correctly.

#### 5. Verification and Debugging (if something goes wrong)

If you encounter issues in step 4, here is how to check each component in the chain:

1.  **Check if the Ingress Controller is running:**
    ```bash
    kubectl get pods -n ingress-nginx
    ```
    *   **Expected result:** The pod named `ingress-nginx-controller-...` should be in the `Running` status.

2.  **Check the configuration of your Ingress resource:**
    ```bash
    kubectl describe ingress app-ingress -n fastapi-with-bot
    ```
    *   **What to look for in the output:**
        *   `Ingress Class`: Should be `nginx`.
        *   `Host`: Should be `fastapi-with-bot.local`.
        *   `Backends`: The `Backend` section should contain the IP addresses and ports of your `app-service` pods. If it's empty, Ingress cannot find your application.

#### 6. Cleanup

To delete all the Kubernetes resources created, simply delete the namespace:

```bash
kubectl delete namespace fastapi-with-bot
