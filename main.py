from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3
from typing import List


app = FastAPI(title="Vending API")

class LoginRequest(BaseModel):
    email: str
    password: str
    
class SaleInfo(BaseModel):
    ID: int
    ID_товара: str
    Количество: int
    Сумма_продажи: float
    Дата: str
    Метод_оплаты: str

def get_db_conn():
    conn = sqlite3.connect('grt.db')
    conn.row_factory = sqlite3.Row
    return conn

# Endpoints

@app.get("/")
def read_root():
    return {"status": "Server is running"}

@app.post("/login")
def login (data: LoginRequest):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Пользователи WHERE email = ?", (data.email,))
    user = cursor.fetchone()
    conn.close()

    if user and data.password == "admin":
        return {"message": "Успех", "ID": user["ID"], "Роль": user["Роль"]}
    
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")

@app.get("/sales", response_model=List[SaleInfo])
def get_sales():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Продажи ORDER BY Дата DESC LIMIT 100")
    rows = cursor.fetchall()
    conn.close()

    return JSONResponse(content=[dict(row) for row in rows], headers={"Content-Type": "application/json; charset=utf-8"}) 

@app.get("/stats/total")
def get_total_sales():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(Сумма_продажи) AS total, COUNT(*) as count FROM Продажи")
    result = cursor.fetchone()
    conn.close()
    return {"Всё": result["total"], "Счёт": result["count"]}

@app.get("/stats/daily")
def get_daily_sales():
    conn = get_db_conn()
    cursor = conn.cursor()
    # Группируем продажи по датам за последние 7 дней
    query = """
        SELECT date(Дата) as day, SUM(Сумма_продажи) as total 
        FROM Продажи 
        GROUP BY day 
        ORDER BY day DESC LIMIT 7
    """
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return [{"date": r["day"], "total": r["total"]} for r in result]

@app.get("/stats/efficiency")
def get_efficiency():
    conn = get_db_conn()
    cursor = conn.cursor()
    # имитация, считаем процент аппаратов без критических ошибок в логах
    cursor.execute("SELECT COUNT(*) FROM Вендинговые_аппараты")
    total = cursor.fetchone()[0] or 1
    # допустим, что 2 аппарата требуют обслуживания (по ТЗ)
    online = max(0, total - 2) 
    conn.close()
    return {"efficiency": round((online / total) * 100, 1), "online": online, "total": total, "service": 1}

@app.get("/notifications")
def get_notifications():
    # по ТЗ система должна уведомлять о событиях
    return [
        {"time": "10:15", "msg": "ТА №4: Низкий уровень запаса (Кофе)", "type": "warning"},
        {"time": "09:40", "msg": "ТА №1: Инкассация проведена", "type": "info"},
        {"time": "08:20", "msg": "ТА №7: Ошибка купюроприемника", "type": "critical"},
    ]
