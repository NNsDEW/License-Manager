# License-Manager
Ипо 31 23 Наминов Наиль

Backend: **Python (Django + DRF)**  
Frontend: **Angular**  
БД: **SQLite (db.sqlite3)**  

## Быстрый старт (локально)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend поднимается на `http://localhost:8000`.

## Запуск через Docker

Убедитесь, что запущен Docker Desktop, затем из корня проекта выполните:

```bash
docker compose up --build
```

После запуска:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:4200`

Остановка:

```bash
docker compose down
```
