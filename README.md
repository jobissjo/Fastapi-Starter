# FastAPI Project Setup Guide

This project is built using FastAPI and provides various ways to run the application along with command-line utilities for managing the database and users.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/jobissjo/Fastapi-Starter.git
cd Fastapi-Starter
```

---

### 2. Set Up Virtual Environment

Make sure you have Python installed (preferably 3.9+).

```bash
python -m venv venv
```

Activate the virtual environment:

- **Windows:**

```bash
venv\Scripts\activate
```

- **Linux/macOS:**

```bash
source venv/bin/activate
```

---

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

### 4. Set Up Environment Variables

Copy the format-env file and create your own `.env` file.

```bash
cp format-env .env
```

Edit the `.env` file and fill in your credentials and environment details.

---

### 5. Optional

If you want to rename the repository, remove git and change the folder name with your project name

## 🛠 Command-Line Utilities

### Initial Development Setup

Use the CLI to setup some initial setup:
```bash
python cli.py initial-setup
```

This do some of the basic setups like
- In database migrations we use alembic tool, that version we do not track, so that folder not include, if we try to initial migrate
that cause a problem, so create a versions folder inside alembic folder

- Same like, if use sqlite db, that db will present inside app/db folder, that will also we do not track, so need to add that folder

- If you needed any additional setup here do that place

### Create a Superuser

Use the CLI to create an admin/superuser:

```bash
python cli.py createsuperuser
```

### Load Initial Data

If you want to preload any data into the database, you can add your logic in:

```bash
app/commands/initial_data.py
```

Then run:

```bash
python cli.py initialdata
```

---

## ⚙️ Run the FastAPI Application

There are three ways to run the app:

### 1. Using FastAPI Dev Server

```bash
fastapi dev
```

---

### 2. Using CLI Command

```bash
python cli.py runserver
```

Optional arguments:
- `--host` (default: `0.0.0.0`)
- `--port` (default: `8000`)
- `--reload` (enabled by default)
- `--no-reload` (disable auto-reload)

Example:

```bash
python cli.py runserver --host 127.0.0.1 --port 8080 --no-reload
```

---

### 3. Using Uvicorn Directly

```bash
uvicorn app.main:app
```

You can also pass `--reload`, `--host`, and `--port` options as needed.

---

## 📁 Project Structure (Simplified)

```
.
├── .vscode/
│   └── launch.json
├── alembic/
├── app/
│   ├── __pycache__/
│   ├── commands/
│   ├── core/
│   ├── db/
│   ├── middlewares/
│   ├── models/
│   ├── routes/
│   │   ├── v1/
│   │   └── v2/
│   ├── schemas/
│   ├── services/
│   ├── templates/
│   ├── utils/
│   ├── __init__.py
│   └── main.py
├── tests/
├── venv/
├── .env
├── .gitignore
├── alembic.ini
├── cli.py
├── format-env
├── local_script.py
└── requirements.txt
```

---

## 📌 Notes

- Make sure your database and other services (e.g., Redis, etc.) mentioned in `.env` are running.
- Keep sensitive credentials out of version control.

