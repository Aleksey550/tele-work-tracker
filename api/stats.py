from utils.db import DATABASE
import sqlite3

def handler(request):
    user_id = request.args.get("user_id")
    start = request.args.get("start")
    end = request.args.get("end")

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
    return { "statusCode": 200, "body": stats }