<div align="center">

# 📅 CalSync

### A Multi-User Calendar Management System built with Flask & MySQL

![Python](https://img.shields.io/badge/Python-3.13+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-black?style=for-the-badge&logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A database-driven collaborative calendar application that enables users to create, manage, and share events while demonstrating advanced relational database concepts including stored procedures, triggers, views, normalization, and transactional workflows.

</div>

---

# 📌 Features

- 🔐 User Authentication
- 📅 Create & Delete Events
- 👥 Multi-user Event Invitations
- ✅ Accept / Decline Invitations
- 📊 Dashboard Statistics
- ⏰ Upcoming & Today's Event Tracking
- 🗃️ Normalized Relational Database
- ⚡ Stored Procedures
- 🔄 Database Triggers
- 👀 SQL Views
- 📝 Logging & Exception Handling
- 🔒 Environment Variable Configuration

---

# 🖼️ Screenshots

## Login Page

> Add screenshot here

```
docs/screenshots/login.png
```

---

## Dashboard

> Add screenshot here

```
docs/screenshots/dashboard.png
```

---

## Invite User

> Add screenshot here

```
docs/screenshots/invite.png
```

---

# 🏗️ Project Architecture

```
                +----------------+
                |   Web Browser  |
                +--------+-------+
                         |
                     HTTP Requests
                         |
                +--------v-------+
                |     Flask      |
                |  Application   |
                +--------+-------+
                         |
                Business Logic
                         |
                +--------v-------+
                | MySQL Database |
                +--------+-------+
                         |
     -----------------------------------------
     | Stored Procedures | Triggers | Views |
     -----------------------------------------
```

---

# 🗂️ Project Structure

```
CalcSync
│
├── assets/
├── config/
│   └── config.py
│
├── database/
│   ├── schema.sql
│   ├── seed.sql
│   ├── procedures.sql
│   ├── triggers.sql
│   ├── views.sql
│   └── database_design.md
│
├── docs/
│   ├── architecture.png
│   └── screenshots/
│
├── exception/
├── logger/
├── static/
├── templates/
│
├── app.py
├── requirements.txt
├── .env.example
└── README.md
```

---

# 🛠️ Tech Stack

## Backend

- Python
- Flask

## Database

- MySQL
- Stored Procedures
- Triggers
- Views

## Frontend

- HTML
- CSS
- JavaScript

## Tools

- Git
- GitHub
- VS Code
- MySQL Workbench

---

# 🗄️ Database Design

The database follows **Third Normal Form (3NF)** and consists of **30 interconnected tables** supporting collaborative event management.

Key concepts implemented:

- Primary Keys
- Foreign Keys
- Composite Relationships
- Referential Integrity
- Views
- Triggers
- Stored Procedures
- Transaction Handling

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/CalcSync.git

cd CalcSync
```

Create virtual environment

```bash
python -m venv venv
```

Activate

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🗄️ Database Setup

Import the SQL files in the following order:

```
schema.sql
↓
procedures.sql
↓
triggers.sql
↓
views.sql
↓
seed.sql
```

Create a `.env` file using `.env.example`.

---

# ▶️ Running the Project

```bash
python app.py
```

Open

```
http://127.0.0.1:8000
```

---

# 🔑 Environment Variables

Create a `.env` file.

```env
SECRET_KEY=your_secret_key

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=CalcSync
```

---

# 📡 API Endpoints

| Method | Endpoint | Description |
|----------|----------------------------|----------------------------|
| POST | /api/login | User Login |
| GET | /api/events | Fetch Events |
| POST | /api/events | Create Event |
| DELETE | /api/events/<id> | Delete Event |
| GET | /api/users | List Users |
| POST | /api/invite | Send Invitation |
| GET | /api/invitations | View Invitations |
| POST | /api/invitations/<id> | Accept/Decline Invitation |
| GET | /api/stats | Dashboard Statistics |

---

# 🚀 Future Improvements

- Password Hashing (bcrypt)
- Event Editing
- Recurring Events
- Calendar Views
- Email Notifications
- Docker Deployment
- Unit Testing
- REST API Documentation

---

# 👨‍💻 Author

**Sankalp Makol**

B.Tech Data Science  
Manipal Institute of Technology

GitHub:

```
https://github.com/SankalpMakol016
```

---

# 📄 License

This project is licensed under the MIT License.

---

<div align="center">

### ⭐ If you found this project interesting, consider giving it a star!

</div>