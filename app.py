from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
import datetime

app = FastAPI()

# Монтируем статику: /static → папка static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Указываем путь к базе
DATABASE = "data.db"

def init_db():
    """Создаёт таблицы и заполняет начальные данные"""
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        
        # Пользователи
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            pin TEXT,
            is_admin INTEGER DEFAULT 0
        )''')

        # Виды работ
        c.execute('''CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            rate REAL
        )''')

        # Выработка
        c.execute('''CREATE TABLE IF NOT EXISTS production (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            job_id INTEGER,
            quantity INTEGER,
            timestamp DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (job_id) REFERENCES jobs (id)
        )''')

        # Добавляем тестовых пользователей (если ещё нет)
        try:
            c.execute("INSERT OR IGNORE INTO users (name, pin, is_admin) VALUES (?, ?, ?)", ("Иван", "1234", 0))
            c.execute("INSERT OR IGNORE INTO users (name, pin, is_admin) VALUES (?, ?, ?)", ("Админ", "0000", 1))
        except:
            pass

        # Виды работ
        jobs = [
            ("Нарезка поролона для планок подголовника", 0.02),
            ("Нарезка поролона для декоративных планок подголовника", 0.02),
            ("Нарезка поролона для царг", 0.05),
            ("Оклейка поролоном планок подголовника", 0.34),
            ("Оклейка поролоном декоративных планок", 0.34),
            ("Оклейка поролоном царг", 0.34),
            ("Пристрел ткани на планку подголовника", 0.66),
            ("Пристрел торцов на планку подголовника", 0.33),
            ("Пристрел ткани на декоративную планку", 0.67),
            ("Пристрел ткани на торец декоративной планки", 0.67),
            ("Пристрел ткани на царгу", 1.75),
            ("Пристрел спанбонда к нижней части подголовника", 0.5),
            ("Пристрел усовой гайки к короткой декоративной планке", 1),
            ("Пристрел усовой гайки к длинной декоративной планке", 0.5),
            ("Пристрел усовой гайки к нижней части подголовника", 0.67),
            ("Пристрел усовой гайки к длинной царге", 0.5),
            ("Пристрел усовой гайки к короткой царге", 0.33),
            ("Сборка рамки подголовника", 1.5),
            ("Сборка подголовника", 1.5),
            ("Упаковка велюровых частей в пленку", 0.75),
            ("Упаковка ножек в пакет", 0.5),
            ("Упаковка кровати", 9),
        ]
        for name, rate in jobs:
            try:
                c.execute("INSERT OR IGNORE INTO jobs (name, rate) VALUES (?, ?)", (name, rate))
            except:
                pass
        conn.commit()

# === API маршруты ===

@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    name = data.get("name")
    pin = data.get("pin")

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, is_admin FROM users WHERE name = ? AND pin = ?", (name, pin))
        user = c.fetchone()

    if user:
        return {"success": True, "user": {"id": user[0], "name": user[1], "is_admin": bool(user[2])}}
    else:
        raise HTTPException(status_code=401, detail="Неверное имя или пин-код")

@app.get("/api/jobs")
async def get_jobs():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, rate FROM jobs")
        jobs = [{"id": row[0], "name": row[1], "rate": row[2]} for row in c.fetchall()]
    return jobs

@app.post("/api/record")
async def record_production(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    job_id = data.get("job_id")
    quantity = data.get("quantity")

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO production (user_id, job_id, quantity, timestamp) VALUES (?, ?, ?, ?)",
                  (user_id, job_id, quantity, datetime.datetime.now()))
        conn.commit()
    return {"success": True}

@app.get("/api/stats")
async def get_stats(user_id: int = None, start: str = None, end: str = None):
    query = '''SELECT u.name, j.name, j.rate, p.quantity, p.timestamp
               FROM production p
               JOIN users u ON p.user_id = u.id
               JOIN jobs j ON p.job_id = j.id
               WHERE 1=1'''
    params = []
    if user_id:
        query += " AND p.user_id = ?"
        params.append(user_id)
    if start:
        query += " AND p.timestamp >= ?"
        params.append(f"{start}T00:00:00")
    if end:
        query += " AND p.timestamp <= ?"
        params.append(f"{end}T23:59:59")

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute(query, params)
        rows = c.fetchall()

    stats = []
    for row in rows:
        stats.append({
            "worker": row[0],
            "job": row[1],
            "rate": row[2],
            "quantity": row[3],
            "timestamp": row[4]
        })
    return stats

@app.get("/api/users")
async def get_users():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, is_admin FROM users")
        users = [{"id": u[0], "name": u[1], "is_admin": bool(u[2])} for u in c.fetchall()]
    return users

@app.get("/")
async def index():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Ошибка: index.html не найден</h1>", status_code=404)

# Запуск приложения
if __name__ == "__main__":
    init_db()  # Вызывается только при запуске через `python app.py`
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)