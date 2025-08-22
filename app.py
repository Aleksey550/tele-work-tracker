from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import datetime

app = Flask(__name__, static_folder='static')
CORS(app)  # Разрешаем запросы с фронтенда

DATABASE = 'data.db'

# Создаем базу данных и таблицы при запуске
def init_db():
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

        # Добавим тестовых пользователей
        try:
            c.execute("INSERT INTO users (name, pin, is_admin) VALUES (?, ?, ?)",
                      ("Иван", "1234", 0))
            c.execute("INSERT INTO users (name, pin, is_admin) VALUES (?, ?, ?)",
                      ("Админ", "0000", 1))
        except:
            pass  # Уже есть

        # Добавим виды работ
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
                c.execute("INSERT INTO jobs (name, rate) VALUES (?, ?)", (name, rate))
            except:
                pass  # Уже есть

        conn.commit()

# Запускаем базу при старте
init_db()

# === API маршруты ===

# Вход пользователя
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    name = data.get('name')
    pin = data.get('pin')

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, is_admin FROM users WHERE name = ? AND pin = ?", (name, pin))
        user = c.fetchone()

    if user:
        return jsonify({"success": True, "user": {"id": user[0], "name": user[1], "is_admin": bool(user[2])}})
    else:
        return jsonify({"success": False, "message": "Неверное имя или пин-код"})

# Получить все виды работ
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, rate FROM jobs")
        jobs = [{"id": row[0], "name": row[1], "rate": row[2]} for row in c.fetchall()]
    return jsonify(jobs)

# Записать выработку
@app.route('/api/record', methods=['POST'])
def record_production():
    data = request.json
    user_id = data.get('user_id')
    job_id = data.get('job_id')
    quantity = data.get('quantity')

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO production (user_id, job_id, quantity, timestamp) VALUES (?, ?, ?, ?)",
                  (user_id, job_id, quantity, datetime.datetime.now()))
        conn.commit()
    return jsonify({"success": True})

# Получить статистику
@app.route('/api/stats', methods=['GET'])
def get_stats():
    user_id = request.args.get('user_id')
    start = request.args.get('start')
    end = request.args.get('end')

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
        params.append(start)
    if end:
        query += " AND p.timestamp <= ?"
        params.append(end)

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
    return jsonify(stats)

# Получить всех пользователей (для админа)
@app.route('/api/users', methods=['GET'])
def get_users():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, is_admin FROM users")
        users = [{"id": u[0], "name": u[1], "is_admin": bool(u[2])} for u in c.fetchall()]
    return jsonify(users)

# Добавить работу (только для админа)
@app.route('/api/add_job', methods=['POST'])
def add_job():
    data = request.json
    name = data.get('name')
    rate = data.get('rate')

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO jobs (name, rate) VALUES (?, ?)", (name, rate))
            conn.commit()
            return jsonify({"success": True})
        except sqlite3.IntegrityError:
            return jsonify({"success": False, "message": "Работа с таким названием уже есть"})

# Удалить работу
@app.route('/api/delete_job/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        if c.rowcount == 0:
            return jsonify({"success": False, "message": "Работа не найдена"})
        conn.commit()
        return jsonify({"success": True})

# Главная страница (Telegram Web App)
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)