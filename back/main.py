from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from database import get_db_conn
from auth import verify_password, hash_password

app = FastAPI(title="Vending API")

# --- Модели данных ---
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    last_name: str
    first_name: str
    middle_name: str = ""

@app.get("/")
def read_root():
    return {"status": "Server is running"}
# --- Эндпоинты: Авторизация ---

@app.post("/register")
def register(data: RegisterRequest):
    print(f"{data.password}")
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        hashed = hash_password(data.password)
        cursor.execute(
            "INSERT INTO Пользователи (email, password, Фамилия, Имя, Отчество, Роль) VALUES (?,?,?,?,?,?)",
            (data.email, hashed, data.last_name, data.first_name, data.middle_name, "Оператор")
        )
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
      #  raise HTTPException(status_code=400, detail="Пользователь уже существует или данные неверны")
    finally:
        conn.close()

@app.post("/login")
def login(data: LoginRequest):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Пользователи WHERE email = ?", (data.email,))
    user = cursor.fetchone()
    conn.close()

    if user and verify_password(data.password, user["password"]):
        # Формируем ФИО для фронтенда: Иванов И. И.
        f = user["Фамилия"]
        i = f"{user['Имя'][0]}." if user["Имя"] else ""
        o = f"{user['Отчество'][0]}." if user["Отчество"] else ""
        return {
            "status": "ok", 
            "fio": f"{f} {i}{o}".strip(), 
            "role": user["Роль"]
        }

    raise HTTPException(status_code=401, detail="Неверный логин или пароль")

# --- Эндпоинты: Статистика ---

@app.get("/stats/total")
def get_total_sales():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(Сумма_продажи) as total, COUNT(*) as count FROM Продажи")
    res = cursor.fetchone()
    conn.close()
    return {"Всё": res["total"] or 0, "Счёт": res["count"] or 0}

@app.get("/stats/daily")
def get_daily_sales():
    conn = get_db_conn()
    cursor = conn.cursor()
    query = """
        SELECT date(Дата) as day, SUM(Сумма_продажи) as total 
        FROM Продажи 
        GROUP BY day 
        ORDER BY day DESC LIMIT 7
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [{"date": r["day"], "total": r["total"]} for r in rows]

@app.get("/stats/efficiency")
def get_efficiency():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Вендинговые_аппараты")
    total = cursor.fetchone()[0] or 1
    # Бизнес-логика: допустим, 2 в сервисе, остальное онлайн
    service = 1
    online = max(0, total - 2)
    conn.close()
    return {
        "efficiency": round((online / total) * 100, 1), 
        "online": online, 
        "total": total, 
        "service": service
    }