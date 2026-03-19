# Система управления лицензированием ПО

Backend: **Python (Django + DRF)**  
Frontend: **Angular**  
БД: **PostgreSQL**  
Инфраструктура: **Docker, docker-compose, Jenkins**

## Быстрый старт (локально)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Быстрый старт (Docker)

```bash
docker-compose up --build
```

Backend поднимается на `http://localhost:8000`, frontend (после его добавления) — на `http://localhost:4200` или за Nginx.

