from utils.db import DATABASE
import sqlite3

def handler(request):
    if request.method != "POST":
        return { "statusCode": 405, "body": "Method not allowed" }

    data = request.json
    name = data.get("name")
    pin = data.get("pin")

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, is_admin FROM users WHERE name = ? AND pin = ?", (name, pin))
        user = c.fetchone()

    if user:
        return {
            "statusCode": 200,
            "body": {
                "success": True,
                "user": {"id": user[0], "name": user[1], "is_admin": bool(user[2])}
            }
        }
    else:
        return {
            "statusCode": 401,
            "body": {"success": False, "message": "Неверное имя или пин-код"}
        }