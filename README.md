# IvanInTech: Full-Stack AI-Powered Web Application

<p align="center">
  <img src="./ivan-in-tech-gif.gif" alt="IvanInTech Application Demo" width="800">
</p>

Welcome to **IvanInTech**, a modern, full-stack web application meticulously crafted to showcase advanced software development practices, seamless front-to-back integration, and the practical application of Artificial Intelligence. This project serves as a dynamic personal portfolio, an interactive blog platform, and a curated source for AI news and insights.

**Live Demo:** [ivanintech.com](https://www.ivanintech.com) _(Update with your actual deployment URL if available)_ 

<!-- Placeholder for a GIF demo of the application. -->
<!-- Replace this comment with: <p align="center"><img src="./ivan-in-tech-demo.gif" alt="IvanInTech Application Demo" width="800"></p> -->
<!-- You will need to create 'ivan-in-tech-demo.gif' from your 'ivan-in-tech-video.mp4' -->

## Core Philosophy & Objectives

IvanInTech is built with a focus on delivering a robust, scalable, and maintainable application while exploring and demonstrating proficiency in cutting-edge technologies. Key objectives include:

- **Showcasing Full-Stack Expertise:** Demonstrating end-to-end development capabilities from database design to UI/UX implementation.
- **Modern Development Practices:** Emphasizing clean code, modular architecture, containerization, and CI/CD.
- **AI Integration:** Exploring and implementing AI-driven features, such as news aggregation and potentially content generation or analysis.
- **Exceptional User & Developer Experience:** Creating an intuitive, performant interface for users and a streamlined, efficient environment for developers.

## Technology Stack & Architecture

This project leverages a powerful and modern technology stack, containerized with Docker for consistency and ease of deployment.

### Key Technologies:

<p align="left">
  <a href="https://www.python.org" target="_blank"><img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/" target="_blank"><img src="https://img.shields.io/badge/FastAPI-0.100+-05998B?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://sqlmodel.tiangolo.com/" target="_blank"><img src="https://img.shields.io/badge/SQLModel-0.0.14+-05998B?style=for-the-badge&logo=python&logoColor=white" alt="SQLModel"></a>
  <a href="https://www.postgresql.org" target="_blank"><img src="https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
  <a href="https://alembic.sqlalchemy.org/" target="_blank"><img src="https://img.shields.io/badge/Alembic-orange?style=for-the-badge&logo=python&logoColor=white" alt="Alembic"></a>
  <br>
  <a href="https://nextjs.org/" target="_blank"><img src="https://img.shields.io/badge/Next.js-14+-black?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js"></a>
  <a href="https://react.dev/" target="_blank"><img src="https://img.shields.io/badge/React-18+-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"></a>
  <a href="https://www.typescriptlang.org/" target="_blank"><img src="https://img.shields.io/badge/TypeScript-5+-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript"></a>
  <a href="https://ui.shadcn.com/" target="_blank"><img src="https://img.shields.io/badge/shadcn/ui-black?style=for-the-badge&logo=radix-ui&logoColor=white" alt="shadcn/ui"></a>
  <a href="https://tailwindcss.com/" target="_blank"><img src="https://img.shields.io/badge/Tailwind_CSS-3+-06B6D4?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS"></a>
  <br>
  <a href="https://www.docker.com/" target="_blank"><img src="https://img.shields.io/badge/Docker-20.10+-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"></a>
  <a href="https://docs.docker.com/compose/" target="_blank"><img src="https://img.shields.io/badge/Docker_Compose-blue?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Compose"></a>
  <a href="https://traefik.io/traefik/" target="_blank"><img src="https://img.shields.io/badge/Traefik-2.9+-07BEE0?style=for-the-badge&logo=traefik-mesh&logoColor=white" alt="Traefik"></a>
  <a href="https://github.com/features/actions" target="_blank"><img src="https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" alt="GitHub Actions"></a>
</p>

### Backend: Python & FastAPI

The backend is built with **FastAPI**, leveraging Python's ecosystem for high performance and developer efficiency.
- **Async Support:** Built on Starlette and Uvicorn for non-blocking I/O operations, ideal for I/O-bound tasks.
- **Pydantic Validation:** Ensures data integrity and provides clear, automatic API documentation.
- **SQLModel ORM:** Offers a Pythonic way to interact with the database, combining SQLAlchemy's power with Pydantic's validation.
- **Alembic Migrations:** Manages database schema evolution in a controlled, versioned manner.
- **JWT Authentication:** Secures API endpoints using JSON Web Tokens for stateless user authentication.

### Frontend: Next.js (React) & TypeScript

A responsive and interactive frontend experience is delivered using **Next.js** and **TypeScript**.
- **Optimized Performance:** Leverages Next.js features like Server-Side Rendering (SSR), Static Site Generation (SSG), and Image Optimization.
- **Rich User Interface:** Built with React and styled using **Tailwind CSS** via **shadcn/ui** for a modern, customizable, and accessible component library.
- **Type Safety:** TypeScript across the frontend ensures fewer runtime errors and improved code maintainability.
- **Generated API Client:** Interacts with the FastAPI backend via a type-safe client, often generated from the OpenAPI schema.

### DevOps & Infrastructure

- **Containerization:** Docker and Docker Compose ensure consistent development, testing, and production environments.
- **Reverse Proxy:** Traefik handles incoming HTTP/S requests, SSL termination, and routing to appropriate services.
- **CI/CD:** GitHub Actions automates testing, building, and potentially deployment processes.
- **Database Flexibility:** Supports SQLite for local development and PostgreSQL for production.

## Project Workflow

```mermaid
graph LR
    User[<img src='https://www.iconpacks.net/icons/2/free-user-icon-3296-thumb.png' width='40' /> User] -- Interacts --> Browser[<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Flat_Browser_Icon_-_Blue.svg/1200px-Flat_Browser_Icon_-_Blue.svg.png' width='40' /> Browser (Next.js Frontend)]
    Browser -- API Requests (HTTPS) --> Traefik[<img src='https://global.traefik.io/hubfs/assets/logos/traefik-proxy/traefik-proxy-logo-icon-white-rgb.png' width='40' style='background-color: #2496ED; border-radius:5px; padding:2px;' /> Traefik Reverse Proxy]
    Traefik -- Routes --> FastAPI[<img src='https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png' width='40' /> FastAPI Backend]
    FastAPI -- SQL Queries --> Database[(<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Postgresql_elephant.svg/1200px-Postgresql_elephant.svg.png' width='30' /> PostgreSQL/SQLite)]
    FastAPI -- Auth & Logic --> Auth[<img src='https://cdn-icons-png.flaticon.com/512/10488/10488261.png' width='30'/> Authentication (JWT)]
    FastAPI -- External APIs --> ExtAI[<img src='https://cdn-icons-png.flaticon.com/512/10869/10869671.png' width='30' /> AI Services/News APIs]
    Database -- Data --> FastAPI
    Auth -- Validation --> FastAPI
    ExtAI -- Data --> FastAPI
    FastAPI -- JSON Responses --> Browser
    subgraph Dockerized Environment
        Traefik
        FastAPI
        Browser
        Database
    end
```

1.  **User Interaction:** Users access the application via a web browser, interacting with the Next.js frontend.
2.  **API Communication:** The frontend sends API requests (typically over HTTPS) to the backend.
3.  **Request Handling:** Traefik, acting as a reverse proxy, receives these requests and routes them to the FastAPI backend service.
4.  **Backend Logic:** FastAPI processes the request, performing actions such as:
    *   Authenticating the user via JWT.
    *   Validating input data using Pydantic.
    *   Interacting with the PostgreSQL (production) or SQLite (development) database through SQLModel.
    *   Fetching data from external AI news APIs or other services.
5.  **Response Generation:** The backend sends a JSON response back to the frontend.
6.  **UI Update:** The Next.js frontend receives the data and dynamically updates the user interface.

## Key Features

- **AI-Powered News Feed:** Aggregates and displays relevant news articles from the world of Artificial Intelligence.
- **Interactive Blog Platform:** Allows for creation, viewing, and filtering of blog posts, with support for rich content and embedded media.
- **Secure User Authentication:** Robust registration, login, and session management using JWT tokens.
- **Role-Based Access Control:** Differentiates features available to regular users and superusers (e.g., content creation).
- **Responsive Design:** Ensures a seamless experience across desktops, tablets, and mobile devices.
- **Dark Mode:** Provides an alternative theme for user comfort.
- **Admin Interface:** (Work in Progress/Based on Template) Provides tools for managing users and application content.

## Current Status & Roadmap

IvanInTech is an actively evolving project. Current focus is on refining core features and enhancing the AI integration.

**Planned Enhancements:**
- Advanced AI-driven content suggestions or summaries.
- More sophisticated admin dashboard functionalities.
- Integration of further external APIs for richer content.
- End-to-end testing and performance optimization.

## Screenshots

*(Please replace these with updated screenshots from your actual application)*

**1. Modern Login Page:**
<!-- <img src="./path/to/your/login-screenshot.png" alt="Login Page" width="600"> -->

**2. Dynamic Blog Page with Filters & Embedded Content:**
<!-- <img src="./path/to/your/blog-page-screenshot.png" alt="Blog Page" width="600"> -->

**3. AI News Aggregation:**
<!-- <img src="./path/to/your/news-page-screenshot.png" alt="News Page" width="600"> -->

**4. Add News/Blog Post Modal (Admin):**
<!-- <img src="./path/to/your/add-content-modal-screenshot.png" alt="Add Content Modal" width="600"> -->

### Interactive API Documentation

FastAPI automatically generates interactive API documentation (Swagger UI). Once the backend is running, access it at `http://localhost:8000/docs` (or your backend's URL + `/docs`).
<!-- <img src="./path/to/your/api-docs-screenshot.png" alt="API Docs" width="600"> -->

## Getting Started

Setting up IvanInTech locally is streamlined with Docker.

### Prerequisites

-   [Docker](https://www.docker.com/get-started) & [Docker Compose](https://docs.docker.com/compose/install/)
-   [Git](https://git-scm.com/downloads)
-   A modern web browser

### Installation & Running

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/ivanmdev/ivanintech.git # Replace with your repo URL
    cd ivanintech
    ```

2.  **Configure Environment Variables:**
    Essential for application behavior and security. `.env` files are used for this and should **not** be committed to version control.
    -   **Root `.env`:** Copy `.env.example` to `.env` in the project root. This primarily contains `POSTGRES_PASSWORD` for the database.
        ```bash
        cp .env.example .env
        ```
    -   **Backend (`backend/.env`):** Copy `backend/.env.example` to `backend/.env`. Key variables include `PROJECT_NAME`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`, and `SECRET_KEY`. Generate secure secret keys:
        ```bash
        cp backend/.env.example backend/.env
        # Generate a strong SECRET_KEY:
        # python -c "import secrets; print(secrets.token_urlsafe(32))"
        ```
    -   **Frontend (`frontend/.env.local`):** Copy `frontend/.env.local.example` to `frontend/.env.local`. Set `NEXT_PUBLIC_API_BASE_URL` (usually `http://localhost:8000` for local Docker setup).
        ```bash
        cp frontend/.env.local.example frontend/.env.local
        ```

3.  **Launch with Docker Compose:**
    From the project root, the `docker compose watch` command builds images, starts all services (backend, frontend, database, Traefik), and enables hot-reloading for both frontend and backend development.
    ```bash
    docker compose watch
    ```
    -   Frontend: Access at `http://localhost:3000` (or your configured port).
    -   Backend API: Access at `http://localhost:8000`.

4.  **Initial Superuser & Database Setup:**
    -   On the first run with Docker, Alembic migrations will automatically set up the database schema.
    -   The `FIRST_SUPERUSER` and `FIRST_SUPERUSER_PASSWORD` from `backend/.env` will be used to create an initial admin account.

## Development Insights

### Backend (`backend/`)
- API routes in `app/api/routes/`, models in `app/db/models/`, schemas in `app/schemas/`.
- Run tests with `pytest`.

### Frontend (`frontend/`)
- Pages in `src/app/`, components in `src/components/`.
- Uses Next.js file-system routing.

### Database Migrations (`backend/`)
- When SQLModel definitions in `app/db/models/` change, generate new Alembic migrations:
  ```bash
  # From backend/ directory, with .venv active or via Docker exec:
  alembic revision -m "Your descriptive migration message" --autogenerate
  ```
- Apply migrations (Docker Compose handles this on startup, or manually):
  ```bash
  alembic upgrade head
  ```

## Author & Contact

Developed by **Iván Castro Martínez**.

- **GitHub Profile:** [ivanmdev](https://github.com/ivanmdev) _(Update with your GitHub username)_ 
- **LinkedIn:** [Iván Castro Martínez](https://www.linkedin.com/in/ivan-castro-martinez/) _(Update with your LinkedIn profile URL)_ 

Feedback and suggestions are welcome!

## License

The IvanInTech project code is proprietary.
This project was initially based on the **Full Stack FastAPI Template**, which is licensed under the MIT license. Aspects of that original template structure may still be present.
