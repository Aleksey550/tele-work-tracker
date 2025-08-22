from utils.db import DATABASE
import sqlite3

def handler(request):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, is_admin FROM users")
        users = [{"id": u[0], "name": u[1], "is_admin": bool(u[2])} for u in c.fetchall()]
    return { "statusCode": 200, "body": users }