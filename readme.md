# Deployment & Operations Guide

**Project:** Vivah Sutra
**Stack:** Django (ASGI) + PostgreSQL + AWS EC2

---

## 1. Overview

This document describes:

* How to run the application on a developer machine
* How to deploy and update the application on AWS
* How to back up application data, configuration, and resources

The instructions assume familiarity with Linux, SSH, Python, and PostgreSQL.

---

## 2. Running the Application on a Developer Machine

### 2.1 System Requirements

* OS: Ubuntu 20.04+ / macOS / Windows (WSL recommended)
* Python: 3.10+
* PostgreSQL: 14+
* Git
* Virtual environment support (`.venv`)

---

### 2.2 Project Setup

```bash
git clone https://github.com/juricerp/Vivah-Python.git
cd Vivah-Python
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source ./.venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

### 2.3 Environment Configuration

Create a `.env` file in the project root:

```env
DEBUG=True

DB_NAME=Vivah_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

---

### 2.4 Database Setup

Create the PostgreSQL database:

```bash
sudo -u postgres psql
CREATE DATABASE Vivah_db;
```

Apply migrations:

```bash
python manage.py migrate
```

Create an admin user:

```bash
python manage.py createsuperuser
```

---

### 2.5 Start Development Server

```bash
python manage.py runserver
```

The application will be available at:

```
http://127.0.0.1:8000
```

---

## 3. Deployment and Updates on AWS

### 3.1 Connect to AWS EC2

```bash
ssh -i <key.pem> ubuntu@ec2-13-50-211-140.eu-north-1.compute.amazonaws.com
```
key.pem should be requested by the devloper
---

### 3.2 Application Directory

The application is expected to reside at:

```
/home/ubuntu/Vivah
```

---

### 3.3 Update Application Code

Navigate to the project directory:

```bash
cd Vivah
```

Pull the latest changes:

```bash
git pull origin main
```

Activate the virtual environment:

```bash
source ./.venv/bin/activate
```

Install/update dependencies:

```bash
pip install -r requirements.txt
```

Apply database migrations:

```bash
python manage.py migrate --noinput
```

Collect static files:

```bash
python manage.py collectstatic --noinput
```

Restart application services:

```bash
sudo systemctl daemon-reload
sudo systemctl restart daphne
sudo systemctl restart nginx
```

---

### 3.4 Port Binding

The application listens on:

```
0.0.0.0:8000
```

Nginx is expected to proxy requests to the application server.

---

## 4. Backup Procedures

### 4.1 PostgreSQL Database Backup

Create a database dump:

```bash
pg_dump -U <db_user> <db_name> > db_backup_$(date +%F).sql
```

Restore from backup:

```bash
psql -U <db_user> <db_name> < db_backup_YYYY-MM-DD.sql
```

---

### 4.2 Media and Static Files Backup

Backup uploaded media:

```bash
tar -czvf media_backup_$(date +%F).tar.gz media/
```

Backup static files:

```bash
tar -czvf static_backup_$(date +%F).tar.gz static/
```

---

### 4.3 Configuration Backup

Backup critical configuration files:

```bash
cp .env .env.backup
```

If applicable:

```bash
sudo cp /etc/nginx/sites-available/<project_name> nginx_<project_name>.backup
sudo cp /etc/systemd/system/<service_name>.service service_<project_name>.backup
```

---

### 4.4 Optional Automation (Cron)

Example of a daily database backup at 02:00 AM:

```bash
crontab -e
```

```cron
0 2 * * * pg_dump -U <db_user> <db_name> > /backups/db_$(date +\%F).sql
```

---

## 4. Operational Notes

* Database migrations must be applied after every schema change.
* Static files must be recollected after frontend or asset updates.
* Backups should be verified periodically.
* Application services should be monitored for uptime and errors.

---

## 5. Scope Clarification

This document covers the current deployment and operational setup.

Advanced features such as:

* Automated recovery
* Multi-region backups
* Infrastructure scaling
* Monitoring and alerting systems

are not included and can be implemented separately.

---

## 6. Support

For deployment-related clarifications or enhancements, changes should be reviewed and planned before implementation.

---

## 7. Directory Info

There are many directories in this project 

```
.
├── connect                        // Real-time communication module (chat, messaging, WebSocket consumers)
│   ├── admin.py                   // Django admin registrations for connect app
│   ├── apps.py                    // App configuration
│   ├── consumers.py               // WebSocket consumers (Django Channels)
│   ├── migrations/                // Database migrations for chat and messaging models
│   ├── models.py                  // Chat-related database models
│   ├── routing.py                 // WebSocket routing configuration
│   ├── urls.py                    // HTTP URL routes for connect app
│   └── views.py                   // HTTP views for messaging features
│
├── main                           // Core project configuration and entry point
│   ├── asgi.py                    // ASGI application entry point
│   ├── consumers.py               // Project-level WebSocket consumers
│   ├── settings.py                // Global Django settings
│   ├── urls.py                    // Root URL configuration
│   ├── views.py                   // Global views (landing, redirects, etc.)
│   ├── wsgi.py                    // WSGI entry point (if needed)
│   └── static/                    // App-level static assets
│       └── user/                  // User-facing CSS, images, and assets
│
├── manage.py                      // Django management command entry point
│
├── media                          // User-uploaded files (runtime data)
│   ├── profile_images/            // Uploaded user profile images and documents
│   └── qr_codes/                  // Generated QR codes
│
├── plans                          // Subscription, payment, and premium features
│   ├── admin.py                   // Admin configuration for plans and payments
│   ├── decorators.py              // Access control decorators (premium checks, etc.)
│   ├── models.py                  // Plan, payment, promo code, and feature models
│   ├── services/                  // Business logic layer (e.g., promo code handling)
│   ├── static/                    // Static JS/CSS related to plans and admin tools
│   ├── templatetags/              // Custom Django template tags
│   ├── urls.py                    // Routes for plan-related pages
│   └── views.py                   // Views handling subscriptions and payments
│
├── search                         // Search and filtering functionality
│   ├── models.py                  // Search-related models (if any)
│   ├── templatetags/              // Custom filters for query handling
│   ├── urls.py                    // Search endpoints
│   └── views.py                   // Search result handling
│
├── siteadmin                      // Custom internal admin and operator tools
│   ├── admin.py                   // Admin registrations
│   ├── feild_config.py            // Dynamic field configurations
│   ├── forms.py                   // Admin/operator forms
│   ├── models.py                  // Operator and admin-specific models
│   ├── urls.py                    // Admin tool routes
│   └── views.py                   // Views for bulk entry, content management, etc.
│
├── staticfiles                    // Collected static files (generated in production)
│   ├── admin/                     // Django admin static assets
│   ├── assets/                    // Shared compiled assets
│   └── user/                      // User-facing static files
│
├── templates                      // HTML templates
│   ├── admin/                     // Custom admin templates and dashboards
│   ├── emails/                    // Email templates (OTP, notifications)
│   ├── plans/                     // Subscription and payment pages
│   ├── siteadmin/                 // Operator/admin interface templates
│   └── user/                      // Public and authenticated user-facing pages
│
├── user                           // User accounts and profile management
│   ├── admin.py                   // Admin configuration for user models
│   ├── context_processors.py      // Global template context helpers
│   ├── email_utils.py             // Email and OTP utilities
│   ├── forms.py                   // Authentication and profile forms
│   ├── models.py                  // Custom user and profile models
│   ├── urls.py                    // User-related routes
│   ├── utils.py                   // Helper utilities
│   └── views.py                   // Authentication, profile, and dashboard views
│
├── requirements.txt               // Python dependencies
├── pyproject.toml                 // Project metadata and tooling configuration
├── railway.json                   // Deployment configuration (Railway)
├── readme.md                     // Project documentation
└── db.sqlite3                     // Local development database (not used in production)
```