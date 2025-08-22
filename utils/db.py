import sqlite3
import os

DATABASE = "data.db"

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

        # Пользователи
        try:
            c.execute("INSERT OR IGNORE INTO users (name, pin, is_admin) VALUES (?, ?, ?)", ("Иван", "1234", 0))
            c.execute("INSERT OR IGNORE INTO users (name, pin, is_admin) VALUES (?, ?, ?)", ("Админ", "0000", 1))
        except:
            pass

        # Работы
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