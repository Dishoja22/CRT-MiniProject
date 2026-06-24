# Deployment & Configuration Guide

This document describes how to deploy, configure, and initialize the Multi-Role Learning Management System (MRLMS) in local development and production environments, including SQLite, MySQL, and Supabase PostgreSQL.

---

## 💻 1. Local Development (SQLite)
By default, the application is pre-configured to run out-of-the-box using **SQLite** for development. This requires zero setup.

1. **Install Python 3.9+**:
   Ensure Python is installed and added to your system PATH.

2. **Clone and Enter Directory**:
   ```bash
   git clone <repository-url>
   cd MRLMS
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch Application**:
   ```bash
   python app.py
   ```
   - **Database Auto-Seeding**: During startup, the app checks if `mrlms.db` exists. If not, it executes `db.create_all()` and seeds the database with admin, faculty, and student sample accounts.

---

## 🛢️ 2. Production Database (MySQL)
To migrate from SQLite to MySQL:

1. **Create MySQL Database**:
   Log into your MySQL server and run:
   ```sql
   CREATE DATABASE mrlms_db;
   ```

2. **Execute Schema SQL**:
   Import the tables and seeding details by running the `database.sql` script:
   ```bash
   mysql -u root -p mrlms_db < database.sql
   ```

3. **Configure Environment Variables**:
   Set the following variables before running `app.py`:
   - `USE_MYSQL` = `True`
   - `MYSQL_USER` = `your_mysql_username` (e.g. `root`)
   - `MYSQL_PASSWORD` = `your_mysql_password`
   - `MYSQL_HOST` = `localhost`
   - `MYSQL_DB` = `mrlms_db`

4. **Run Server**:
   ```bash
   python app.py
   ```

---

## ⚡ 3. Supabase PostgreSQL Integration
Since Supabase runs on PostgreSQL, you can use Supabase as your database server for this Flask application. Flask-SQLAlchemy integrates natively with PostgreSQL.

### Prerequisites
- Install `psycopg2-binary` (PostgreSQL adapter for Python):
  ```bash
  pip install psycopg2-binary
  ```

### Step 1: Obtain Connection String
1. Go to your **Supabase Dashboard** -> Project -> **Project Settings** -> **Database**.
2. Copy the **URI** connection string. It will look like:
   `postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres`

### Step 2: Bind in `config.py`
To support this connection, we can set the `DATABASE_URL` environment variable. The app checks for `DATABASE_URL` in `config.py`:
```python
db_uri = os.environ.get('DATABASE_URL')
```
Simply set the `DATABASE_URL` environment variable to your Supabase connection string.
*Note: Python's SQLAlchemy requires the prefix `postgresql://` (or `postgresql+psycopg2://`) rather than `postgres://` which Supabase sometimes defaults. Ensure it starts with `postgresql://`.*

```bash
# On Windows PowerShell:
$env:DATABASE_URL="postgresql://postgres.vlxyxlrrvmdhploulsps:[YOUR_PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
python app.py
```

---

## 🚀 4. Production WSGI Web Servers
In production environments (like AWS EC2, DigitalOcean, or Heroku), do not run using the built-in Flask debugger server. Instead, use a WSGI server:

### Gunicorn (Linux/macOS)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Waitress (Windows)
```bash
pip install waitress
python -c "from waitress import serve; from app import app; serve(app, host='0.0.0.0', port=5000)"
```
