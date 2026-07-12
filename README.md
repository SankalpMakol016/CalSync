# CalSync

A collaborative event scheduling platform built with Flask and MySQL. CalSync allows multiple users to create, manage, and share events while demonstrating advanced relational database concepts such as stored procedures, triggers, views, and normalized schema design.

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white">
  <img alt="Flask" src="https://img.shields.io/badge/Flask-Backend-000000?logo=flask&logoColor=white">
  <img alt="MySQL" src="https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white">
  <img alt="GitHub Actions" src="https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
</p>

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
- User registration
- User login
- Logout
- Session management

**Event Management**
- Create events
- Delete events
- Dashboard statistics
- Today's events
- Upcoming events

**Collaboration**
- Invite users
- Live email search
- Accept invitations
- Decline invitations
- Participants panel

**Database**
- Stored procedures
- Triggers
- Views
- Audit logging
- Transaction handling
- 3NF normalized database

**DevOps**
- Centralized error handling
- Logging
- Modular Flask architecture
- Environment variables
- Dockerized deployment
- Gunicorn production server
- GitHub Actions continuous integration

---

## Architecture

```
Browser
  │
  │  HTTP
  ▼
Gunicorn
  │
  ▼
Flask
  │
  ▼
Business Logic
  │
  ▼
MySQL
  │
  ├── Stored Procedures
  ├── Triggers
  └── Views
```

---

## Technology Stack

| Category       | Technologies                                                          |
|----------------|------------------------------------------------------------------------|
| Backend        | Python, Flask, Gunicorn                                                |
| Frontend       | HTML, CSS, JavaScript                                                  |
| Database       | MySQL, Stored Procedures, Triggers, Views, Transactions, 3NF Schema    |
| Authentication | Session-based authentication, Bcrypt password hashing, Regex validation|
| DevOps         | Docker, Docker Compose, GitHub Actions                                 |

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

### Method 1: Docker (Recommended)

```bash
docker compose up --build
```

This builds and starts the Flask application alongside its MySQL database using the provided `docker-compose.yml`.

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

CalSync is production-ready and designed to run behind Gunicorn as the WSGI server, packaged with Docker, and orchestrated via Docker Compose for consistent deployment across environments.

---

## Future Improvements

- Event editing
- Recurring events
- Calendar month view
- Calendar week view
- Email notifications
- Role-based access control
- Unit testing
- Integration testing
- REST API documentation

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