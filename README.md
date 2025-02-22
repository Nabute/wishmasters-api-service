# 🏆 Competition API (Django + DRF)

This is a **Django REST Framework (DRF)** API for skill-based competitions, supporting user authentication, competition management, score submission, and leaderboards.

---

## 🚀 Features

✅ **User Authentication**: Register, log in, and retrieve user profiles using **JWT authentication**.  
✅ **Competition Management**: Admins can create competitions with entry fees and player limits.  
✅ **Join Competition**: Players can join competitions by paying an entry fee.  
✅ **Submit Scores**: Users can submit scores for competitions.  
✅ **Leaderboard**: Returns the **top 10 players** dynamically.  
✅ **Security & Validation**: Prevent duplicate entries, enforce valid data, and apply rate-limiting.  

---

## 🛠️ Tech Stack

- **Django** (Backend framework)  
- **Django REST Framework (DRF)** (API development)  
- **PostgreSQL** (Database)  
- **JWT Authentication** (Secure authentication)  
- **Docker + Docker Compose** (Containerized deployment)  

---

## 📦 Setup & Installation

### 1️⃣ Clone the Repository  
```sh
git clone git@github.com:Nabute/wishmasters-api-service.git
cd backend
```

### 2️⃣ Set Up Environment Variables  
Create a **.env** file in the root directory with:

```env
SECRET_KEY = -)oij7%8urypzrl#k$5$!yts&&#e314+&zwumub+felb*pl-!0
ENV = development
DEBUG = true
SHOW_SWAGGER = true
ALLOWED_HOSTS = *
CORS_ALLOW_ALL_ORIGINS = true
CSRF_TRUSTED_ORIGINS = http://localhost:8000

APP_TITLE=Wishmasters – Compete. Win. Rise. 🏆
APP_DESCRIPTION=A skill-based competition platform where players join, submit scores, and climb the leaderboard to prove their mastery. Let your skills decide your success!
INDEX_TITLE=Manage All of your competitions in one place.


# DATABASE ENVIRONMENT VARIABLES
POSTGRES_DB = wishmaster
POSTGRES_USER = db_user
POSTGRES_PASSWORD = 1234 

PGADMIN_DEFAULT_EMAIL = admin@wishmaster.com
PGADMIN_DEFAULT_PASSWORD = 12211


# API ENVIRONMENT VARIABLES
DB_HOST = db
DB_PORT = 5432
DB_NAME = wishmaster
DB_USER = db_user
DB_PASSWORD = 1234

# UTC+3
TIME_ZONE = Africa/Nairobi
USE_TZ = false
```

### 3️⃣ Start the Application (Using Docker)  
Ensure **Docker** and **Docker Compose** are installed, then run:

```sh
docker-compose up --build
```
This will start:
- The **PostgreSQL database**  
- The **Django API** on `http://localhost:8000`  

---

## 🎮 Usage Guide

1️⃣ **Register & Log In**: Obtain a **JWT token**.  
2️⃣ **Create a Competition** *(Admin only)*.  
3️⃣ **Join a Competition** *(Users pay entry fees)*.  
4️⃣ **Submit Scores**: Players send their scores.  
5️⃣ **View Leaderboard**: Fetch top 10 players dynamically.  

---

## 🚀 Deployment

To deploy the API with **Docker Compose**, run:  
```sh
docker-compose up -d
```

To stop the services:  
```sh
docker-compose down
```

---

## 📌 Notes

- Ensure **Docker & PostgreSQL** are installed.  
- Update `.env` with correct **database credentials**.  
- The API runs on **port 8000** (`http://localhost:8000`).  

---

## 📄 License  
This project is for assessment purposes. Modify as needed.  
