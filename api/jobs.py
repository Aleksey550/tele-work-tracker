from utils.db import DATABASE
import sqlite3

def handler(request):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, rate FROM jobs")
        jobs = [{"id": row[0], "name": row[1], "rate": row[2]} for row in c.fetchall()]
    return { "statusCode": 200, "body": jobs }