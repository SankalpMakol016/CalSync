# CalSync

A collaborative event scheduling platform built with Flask and MySQL. CalSync allows multiple users to create, manage, and share events while demonstrating advanced relational database concepts such as stored procedures, triggers, views, and normalized schema design. The application is fully deployed and publicly accessible.

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white">
  <img alt="Flask" src="https://img.shields.io/badge/Flask-Backend-000000?logo=flask&logoColor=white">
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-ORM-CA1E1E?logo=python&logoColor=white">
  <img alt="MySQL" src="https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white">
  <img alt="Render" src="https://img.shields.io/badge/Render-Hosting-46E3B7?logo=render&logoColor=white">
  <img alt="Railway" src="https://img.shields.io/badge/Railway-MySQL%20Hosting-0B0D0E?logo=railway&logoColor=white">
  <img alt="GitHub Actions" src="https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
</p>

## Live Demo

The application is deployed and publicly accessible at:

**[https://calsync-dn23.onrender.com/](https://calsync-dn23.onrender.com/)**

The production instance runs on Render with a MySQL database hosted on Railway.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Database Design](#database-design)
6. [Screenshots](#screenshots)
7. [Installation](#installation)
8. [Database Setup](#database-setup)
9. [Environment Variables](#environment-variables)
10. [Running the Application](#running-the-application)
11. [API Reference](#api-reference)
12. [CI/CD](#cicd)
13. [Deployment](#deployment)
14. [Future Improvements](#future-improvements)
15. [License](#license)
16. [Author](#author)

---

## Features

**Authentication**
- Secure user registration with input validation
- Session-managed login powered by Flask-Login
- Logout with full session invalidation

**Event Management**
- Create and delete events
- Dashboard with real-time statistics
- Dedicated views for today's and upcoming events

**Collaboration**
- Invite other users to events
- Live email search while composing invitations
- Accept or decline invitations
- Participants panel for tracking attendance per event

**Database**
- Stored procedures for core data operations
- Triggers for automated state consistency
- Views for simplified read access
- Audit logging of key state changes
- Transaction-wrapped multi-step operations
- Normalized (3NF) relational schema

**DevOps**
- Centralized error handling and structured logging
- Modular Flask application architecture
- Environment-based configuration
- Dockerized build and deployment
- Gunicorn as the production WSGI server
- Automated validation via GitHub Actions

---

## Architecture

```
Browser
  │
  │  HTTPS
  ▼
Render (Hosting)
  │
  ▼
Gunicorn
  │
  ▼
Flask
  │
  ▼
Business Logic (SQLAlchemy)
  │
  ▼
Railway (Managed MySQL)
  │
  ├── Stored Procedures
  ├── Triggers
  └── Views
```

---

## Technology Stack

| Category              | Technologies                                                              |
|------------------------|----------------------------------------------------------------------------|
| Backend                | Python, Flask, Flask-Login, SQLAlchemy, Gunicorn                          |
| Frontend               | HTML, CSS, JavaScript, Jinja2                                              |
| Database               | MySQL, Stored Procedures, Triggers, Views, Transactions, 3NF Schema        |
| Hosting & Infrastructure| Docker, Render (Application Hosting), Railway (Managed MySQL)             |
| CI/CD                  | GitHub Actions                                                             |

---

## Project Structure

```
CalSync/
├── .github/
│   └── workflows/
│       └── ci.yml
├── assets/
├── config/
├── database/
│   ├── 01_schema.sql
│   ├── 02_procedures.sql
│   ├── 03_triggers.sql
│   ├── 04_views.sql
│   └── 05_seed.sql
├── docs/
├── exception/
├── logger/
├── logs/
├── routes/
├── static/
├── templates/
├── utils/
├── app.py
├── db.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Database Design

The database is designed around a fully normalized relational schema and leverages core MySQL capabilities rather than relying solely on application-layer logic.

- **Third Normal Form (3NF)** — Tables are structured to eliminate redundancy and maintain data integrity across users, events, invitations, and participants.
- **Stored Procedures** — Encapsulate reusable data operations directly at the database layer.
- **Triggers** — Automatically maintain derived state (e.g., participant records) in response to data changes.
- **Views** — Provide simplified, reusable read models over the underlying normalized tables.
- **Referential Integrity** — Foreign key constraints enforce valid relationships between users, events, invitations, and participants.
- **Transactions** — Multi-step operations are wrapped in transactions to ensure atomicity and consistency.
- **Audit Logging** — Key state-changing operations are recorded for traceability.
- **SQLAlchemy** — Used as the application's data access layer for executing queries, stored procedures, and managing connections to the MySQL database.

---

## Screenshots

| Login | Registration |
|-------|--------------|
| _placeholder_ | _placeholder_ |

| Dashboard | Invitation Search |
|-----------|--------------------|
| _placeholder_ | _placeholder_ |

| Participants Panel |
|---------------------|
| _placeholder_ |

---

## Installation

The application is live at [https://calsync-dn23.onrender.com/](https://calsync-dn23.onrender.com/). To run it locally, use one of the methods below.

### Method 1: Docker (Recommended)

```bash
docker compose up --build
```

This builds and starts the Flask application alongside a MySQL database using the provided `docker-compose.yml`.

### Method 2: Local Development

```bash
# Clone the repository
git clone https://github.com/SankalpMakol016/CalSync.git
cd CalSync

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Import the SQL files (see Database Setup)
# Run the application
python app.py
```

---

## Database Setup

Run the SQL files in the `database/` directory in the following order:

1. `01_schema.sql`
2. `02_procedures.sql`
3. `03_triggers.sql`
4. `04_views.sql`
5. `05_seed.sql`

This order is required because procedures, triggers, and views depend on tables already existing in the schema, and seed data is inserted last to avoid unintended trigger side effects during setup.

---

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
SECRET_KEY=
FLASK_ENV=
FLASK_DEBUG=
MYSQL_HOST=
MYSQL_PORT=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DATABASE=
```

In production, these values point to the Railway-hosted MySQL instance and are configured as environment variables on Render rather than committed to the repository.

---

## Running the Application

### Local

```bash
python app.py
```

### Docker

```bash
docker compose up --build
```

### Production

The live instance runs via Gunicorn inside a Docker container, hosted on Render, connected to a MySQL database hosted on Railway.

---

## API Reference

| Method | Endpoint                          | Description                                  |
|--------|------------------------------------|-----------------------------------------------|
| POST   | `/api/register`                   | Register a new user                            |
| POST   | `/api/login`                      | Authenticate a user and start a session        |
| GET    | `/api/events`                     | Retrieve events for the logged-in user         |
| POST   | `/api/events`                     | Create a new event                             |
| DELETE | `/api/events/<id>`                | Delete an event owned by the logged-in user    |
| GET    | `/api/users/search`               | Live search users by email                     |
| POST   | `/api/invite`                     | Invite a user to an event                      |
| GET    | `/api/invitations`                | Retrieve pending invitations for the user       |
| POST   | `/api/invitations/<id>`           | Accept or decline an invitation                 |
| GET    | `/api/events/<id>/participants`   | Retrieve participants for an event (owner only)|
| GET    | `/api/stats`                      | Retrieve dashboard statistics                   |

---

## CI/CD

GitHub Actions automatically validates every push by installing project dependencies and building the Docker image, ensuring the application remains in a buildable and deployable state at all times.

---

## Deployment

CalSync is deployed as a containerized application using the following components:

- **Docker** — Packages the application and its dependencies into a portable, reproducible image.
- **Render** — Hosts the containerized Flask application and serves the live instance.
- **Railway** — Hosts the production MySQL database, including all stored procedures, triggers, and views.
- **Gunicorn** — Serves the Flask application as the production WSGI server inside the container.

### Production Deployment

- The application is packaged as a Docker image and deployed to Render.
- The production MySQL database is hosted on Railway and accessed over a secure connection.
- Gunicorn runs as the WSGI server inside the container, handling production traffic.
- All sensitive configuration (database credentials, secret keys) is supplied via environment variables rather than hardcoded values, keeping the deployment secure and environment-agnostic.

---

## Future Improvements

- Event editing
- Recurring events
- Calendar month and week views
- Email notifications
- Role-based access control
- Automated unit and integration testing
- Expanded API documentation

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

**Sankalp Makol**
B.Tech Data Science & Engineering
Manipal Institute of Technology

- GitHub: [https://github.com/SankalpMakol016](https://github.com/SankalpMakol016)
- LinkedIn: _placeholder_

---

<p align="center">
  If you find this project useful, consider giving it a star.
  <br><br>
  <strong>⭐ Star this repository</strong>
</p>
