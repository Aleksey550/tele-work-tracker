from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Монтируем статику
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    return {"message": "Hello from local server!"}

@app.get("/api/jobs")
async def get_jobs():
    # Просто возвращаем тестовые данные
    return [
        {"id": 1, "name": "Нарезка поролона", "rate": 0.02}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)