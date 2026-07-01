# Vivah Sutra — Matrimony Platform

**Stack:** Django 5.2 (ASGI) + PostgreSQL + Redis + Docker

A modern matrimony platform built with Django Channels for real-time chat, featuring user profiles, search/filter, premium plans, and an admin dashboard.

---

## 🚀 One-Step Deployment

### Option 1: Railway (Recommended — 1 click)

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template)

1. Fork or push this repo to your GitHub account
2. Go to [railway.app](https://railway.app) and click **New Project → Deploy from GitHub repo**
3. Railway auto-detects the `Dockerfile` and builds/deploys automatically
4. Add these environment variables in the Railway dashboard:

| Variable | Value |
|---|---|
| `SECRET_KEY` | (generate a long random string) |
| `EMAIL_HOST_USER` | VivahSutramatrimony@gmail.com |
| `EMAIL_HOST_PASSWORD` | (your Gmail app password) |

Railway automatically provisions **PostgreSQL** and **Redis** — the app picks them up via `DATABASE_URL` and `REDIS_URL`.

That's it. One step, deployed ✅

---

### Option 2: Docker Compose (Local)

```bash
# 1. Clone the repo
git clone https://github.com/lakshayjindal/vivah-sutra.git
cd vivah-sutra

# 2. Start everything with one command
docker compose up -d

# 3. Open http://localhost:8000
```

This starts **PostgreSQL**, **Redis**, and the **Django app** in three containers. The app auto-runs migrations and collects static files on startup.

To stop:
```bash
docker compose down
```

---

### Option 3: Manual (Local Dev)

```bash
# 1. Clone and enter the project
git clone https://github.com/lakshayjindal/vivah-sutra.git
cd vivah-sutra

# 2. Create virtual env & install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env to taste — defaults work for SQLite local dev

# 4. Run database migrations
python manage.py migrate

# 5. Start the dev server
python manage.py runserver

# Open http://127.0.0.1:8000
```

---

## 📁 Project Structure

```
├── connect/          # Real-time chat (Django Channels, WebSockets)
├── main/             # Django project config (settings, URLs, ASGI)
├── plans/            # Premium subscriptions & payments
├── search/           # Profile search & filtering
├── siteadmin/        # Custom operator/admin tools
├── templates/        # HTML templates (admin, user, emails)
├── user/             # User auth, profiles, dashboard
├── Dockerfile        # Production container build
├── docker-compose.yml # One-command local stack
├── docker-entrypoint.sh # Automatic migration + static files + daphne
├── railway.json      # Railway deploy config
└── .env.example      # Environment variable template
```

---

## 🌐 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | No | Set `True` for dev (default), `False` for prod |
| `DATABASE_URL` | For prod | PostgreSQL connection string (Railway sets this) |
| `REDIS_URL` | For chat | Redis connection string (Railway sets this) |
| `EMAIL_HOST_USER` | For email | Gmail address for transactional emails |
| `EMAIL_HOST_PASSWORD` | For email | Gmail app password |
| `PORT` | No | Server port (default: 8000) |

---

## 🔑 Key Features

- **Real-time messaging** via Django Channels + Redis
- **Profile management** with photo uploads
- **Advanced search** with filters (age, location, caste, etc.)
- **Premium subscription plans**
- **Admin dashboard** with bulk user import & CSV tools
- **Email OTP verification**
- **Responsive design** with dark mode support

---

## 🛠 Tech Stack

- **Backend:** Django 5.2, Django Channels 4.2, Daphne
- **Database:** PostgreSQL (prod), SQLite (dev)
- **Cache/Realtime:** Redis + channels-redis
- **Static Files:** WhiteNoise
- **Containerization:** Docker, Docker Compose
- **Cloud:** Railway (deployment)
