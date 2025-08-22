from utils.db import DATABASE
import sqlite3
import datetime

def handler(request):
    if request.method != "POST":
        return { "statusCode": 405, "body": "Method not allowed" }

    data = request.json
    user_id = data.get("user_id")
    job_id = data.get("job_id")
    quantity = data.get("quantity")

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO production (user_id, job_id, quantity, timestamp) VALUES (?, ?, ?, ?)",
                  (user_id, job_id, quantity, datetime.datetime.now()))
        conn.commit()
    return { "statusCode": 200, "body": {"success": True} }