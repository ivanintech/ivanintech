# IvanInTech Full-Stack Showcase

[![Test](https://github.com/fastapi/full-stack-fastapi-template/workflows/Test/badge.svg)](https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3ATest)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/fastapi/full-stack-fastapi-template.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/fastapi/full-stack-fastapi-template)

Welcome to **IvanInTech**, a full-stack application built to showcase modern web development practices and explore the exciting world of Artificial Intelligence. This project serves as a personal portfolio, a blog, and a platform for sharing insights and news related to AI, technology, and software development.

## Core Philosophy

The development of IvanInTech is guided by the principles of creating a robust, scalable, and maintainable application. We emphasize:
- **Clean Code and Architecture:** Ensuring the codebase is easy to understand, modify, and extend.
- **Modern Technologies:** Leveraging the power of cutting-edge frameworks and tools.
- **Developer Experience:** Streamlining the development process with tools like Docker and hot-reloading.
- **User Experience:** Aiming for an intuitive and performant interface for end-users.

## Technology Stack & Architecture

IvanInTech employs a carefully selected stack of technologies to deliver a seamless full-stack experience. The application is containerized using Docker for consistent development and deployment environments.

### Backend: Python & FastAPI

The backend is powered by **FastAPI**, a modern, high-performance Python web framework chosen for its:
- **Speed:** Asynchronous support built on Starlette and Pydantic, making it one of the fastest Python frameworks available.
- **Ease of Use:** Intuitive syntax and automatic interactive API documentation (via Swagger UI and ReDoc).
- **Data Validation:** Robust data validation and serialization powered by Pydantic, reducing errors and improving reliability.
- **SQLModel:** Used as the ORM for elegant and Pythonic database interactions, supporting both SQLite (for local development) and PostgreSQL (for production).
- **Alembic:** Handles database migrations, allowing for schema changes in a structured and version-controlled manner.
- **JWT Authentication:** Secure user authentication and authorization using JSON Web Tokens.

### Frontend: React (Next.js) & TypeScript

The frontend is a dynamic and responsive user interface built with **Next.js**, a popular React framework, along with TypeScript for type safety.
- **Next.js:** Provides a rich development experience with features like:
    - Server-Side Rendering (SSR) and Static Site Generation (SSG) for optimal performance and SEO.
    - File-system routing for intuitive page creation.
    - API routes for backend-for-frontend patterns if needed.
- **TypeScript:** Enhances code quality and maintainability by adding static typing to JavaScript.
- **Chakra UI:** A simple, modular, and accessible component library that gives developers the building blocks to build React applications with speed and ease.
- **Generated API Client:** Utilizes an auto-generated client to interact with the FastAPI backend, ensuring type safety across the stack.

### DevOps & Infrastructure

- **Docker & Docker Compose:** Containerizes the application (frontend, backend, database) for consistent environments across development, testing, and production. `docker compose watch` is the recommended way to run the application locally, providing hot-reloading for both frontend and backend.
- **Traefik:** Acts as a reverse proxy and load balancer, simplifying SSL certificate management (e.g., via Let's Encrypt in production) and routing requests to the appropriate services.
- **GitHub Actions:** Implements CI/CD pipelines for automated testing and deployment.
- **Database:**
    - **PostgreSQL:** The primary database for production, known for its robustness and feature set.
    - **SQLite:** Used for local development for its simplicity and ease of setup.

### Project Workflow

1.  **User Interaction:** Users interact with the Next.js frontend in their browser.
2.  **API Requests:** The frontend makes HTTP requests to the FastAPI backend (e.g., to fetch news, submit data).
3.  **Backend Processing:** FastAPI processes these requests, interacts with the PostgreSQL/SQLite database via SQLModel, performs business logic, and handles authentication.
4.  **JSON Responses:** The backend returns responses in JSON format.
5.  **Dynamic Updates:** The Next.js frontend receives the JSON data and dynamically updates the UI.

## Key Features

- **AI News Aggregation:** Fetches and displays the latest news and articles in the field of Artificial Intelligence.
- **Blog Platform:** (Planned) A space for sharing articles and insights on technology and development.
- **User Authentication:** Secure registration and login functionality.
- **Admin Dashboard:** (Based on template) Interface for managing users and content.
- **Responsive Design:** Adapts to various screen sizes for a consistent experience on desktop and mobile devices.
- **Dark Mode Support:** Because why not?

_(The following screenshots are illustrative from the original template and will be updated as IvanInTech's UI evolves.)_

### Dashboard Login

[![API docs](img/login.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Admin

[![API docs](img/dashboard.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Create User

[![API docs](img/dashboard-create.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Items

[![API docs](img/dashboard-items.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - User Settings

[![API docs](img/dashboard-user-settings.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Dark Mode

[![API docs](img/dashboard-dark.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Interactive API Documentation

FastAPI automatically generates interactive API documentation. Once the backend is running, you can typically access it at `http://localhost:8000/docs`.
[![API docs](img/docs.png)](https://github.com/fastapi/full-stack-fastapi-template)

## Getting Started

This project is designed to be straightforward to set up and run.

### Prerequisites

-   [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
-   [Git](https://git-scm.com/downloads)
-   A code editor (e.g., VS Code)
-   Web browser

### Installation & Running

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url> ivanintech
    cd ivanintech
    ```

2.  **Configure Environment Variables:**
    This project uses `.env` files for configuration.
    -   **Backend:** Copy `backend/.env.example` to `backend/.env` and fill in the necessary values (e.g., `PROJECT_NAME`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`, `SECRET_KEY`).
        ```bash
        cp backend/.env.example backend/.env
        ```
        Generate secret keys using:
        ```bash
        python -c "import secrets; print(secrets.token_urlsafe(32))"
        ```
    -   **Frontend:** Copy `frontend/.env.local.example` to `frontend/.env.local` and set `NEXT_PUBLIC_API_BASE_URL` (typically `http://localhost:8000` for local development).
        ```bash
        cp frontend/.env.local.example frontend/.env.local
        ```
    -   **Database:** The main `.env` file in the root directory contains database credentials like `POSTGRES_PASSWORD`. Copy `.env.example` to `.env` if it doesn't exist and update it.
        ```bash
        cp .env.example .env
        ```

3.  **Run with Docker Compose:**
    The recommended way to run the entire stack (backend, frontend, database, Traefik) is using `docker compose watch` from the project root. This command builds the images if they don't exist, starts the services, and watches for file changes to automatically rebuild and restart services.
    ```bash
    docker compose watch
    ```
    -   Frontend will typically be available at `http://localhost:3000` (or your configured `frontend` service port if different).
    -   Backend API will typically be available at `http://localhost:8000`.

4.  **Manual Setup (Alternative - for individual component development):**

    *   **Backend (from `backend/` directory):**
        1.  Create and activate a Python virtual environment:
            ```bash
            python -m venv .venv
            source .venv/Scripts/activate  # On Windows (Git Bash/PowerShell)
            # or source .venv/bin/activate  # On macOS/Linux
            ```
        2.  Install dependencies:
            ```bash
            pip install -r requirements.txt
            pip install "fastapi[standard]" # If not already fully covered by requirements
            ```
        3.  Run the development server (ensure `backend/.env` is configured):
            ```bash
            uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
            ```
            *(Note: `fastapi dev app/main.py` might have issues with `sys.path` in some setups; `uvicorn` is more direct.)*

    *   **Frontend (from `frontend/` directory):**
        1.  Install dependencies:
            ```bash
            npm install
            ```
        2.  Run the development server (ensure `frontend/.env.local` is configured):
            ```bash
            npm run dev
            ```

### Initial Setup & Superuser

-   Once the backend is running (e.g., via `docker compose watch`), it will automatically run Alembic migrations to set up the database schema if it's the first time or if migrations are pending.
-   The `FIRST_SUPERUSER` and `FIRST_SUPERUSER_PASSWORD` defined in `backend/.env` will be used to create an initial admin user. You can use these credentials to log in to the application and the admin dashboard.

## Development

This section outlines key aspects of developing IvanInTech.

### Backend Development

-   Located in the `backend/` directory.
-   API endpoints are defined in `app/api/` and routers are mounted in `app/main.py`.
-   Database models and schemas are defined using SQLModel in `app/models/`.
-   Core settings are managed in `app/core/config.py` and loaded from `backend/.env`.
-   Run tests using `pytest` from the `backend/` directory.

### Frontend Development

-   Located in the `frontend/` directory.
-   Pages are primarily within `frontend/src/app/`. Next.js uses a file-system based router.
-   Components are in `frontend/src/components/`.
-   Static assets are in `frontend/public/`.
-   Environment variables specific to the frontend are managed in `frontend/.env.local`.
-   The API client for interacting with the backend is typically generated or located in `frontend/src/client/`.

### Database Migrations

-   Alembic is used for database migrations.
-   When you change SQLModel models, you'll need to generate a new migration script:
    ```bash
    # Ensure your backend .venv is active or run via Docker exec
    # From the backend/ directory:
    alembic revision -m "your_migration_message" --autogenerate
    ```
-   Apply migrations (Docker Compose typically handles this on startup, but manually you can run):
    ```bash
    # From the backend/ directory:
    alembic upgrade head
    ```
    Make sure your `alembic.ini` is correctly pointing to your database (it defaults to SQLite for local, but production setup with Docker uses PostgreSQL defined in `docker-compose.yml` and environment variables).

## How To Use The Original Template Features (Forking, Copier)

This project was originally based on the "Full Stack FastAPI Template". If you wish to understand how to update from the original template or use features like Copier, refer to the original template's documentation. For IvanInTech, these sections may be less relevant unless you plan to frequently merge updates from the upstream template.

### (Original Template Sections - Abridged for relevance to this project)

If you need to pull updates from the `fastapi/full-stack-fastapi-template`:
1. Add it as an `upstream` remote: `git remote add upstream git@github.com:fastapi/full-stack-fastapi-template.git`
2. Fetch and merge changes: `git pull --no-commit upstream master`, resolve conflicts, then `git merge --continue`.

The Copier setup is primarily for initializing new projects from the template and is likely not needed for ongoing development of IvanInTech unless you are starting a new, separate project based on it.

## Deployment

Refer to `deployment.md` for detailed instructions on deploying this application, typically using Docker Compose and managing secrets.

## Release Notes

Check the file `release-notes.md` for updates from the original template.

## License

The IvanInTech project itself is proprietary. The underlying "Full Stack FastAPI Template" it was based on is licensed under the terms of the MIT license.
