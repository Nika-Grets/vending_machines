import requests
from PyQt6.QtCore import QThread, pyqtSignal

BASE_URL = "http://127.0.0.1:8000"

class DataFetcher(QThread):
    """Поток для фонового обновления данных"""
    data_received = pyqtSignal(dict)  # Сигнал передаст словарь с результатами
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            # Собираем данные со всех нужных эндпоинтов
            total = requests.get(f"{BASE_URL}/stats/total", timeout=3).json()
            eff = requests.get(f"{BASE_URL}/stats/efficiency", timeout=3).json()
            daily = requests.get(f"{BASE_URL}/stats/daily", timeout=3).json()

            combined_data = {
                "total": total,
                "efficiency": eff,
                "daily": daily
            }
            self.data_received.emit(combined_data)
        except Exception as e:
            self.error_occurred.emit(str(e))

class ApiClient:
    """Простой синхронный клиент для авторизации (используется в окнах входа)"""
    @staticmethod
    def login(email, password):
        return requests.post(f"{BASE_URL}/login", json={"email": email, "password": password}, timeout=3)

    @staticmethod
    def register(data):
        return requests.post(f"{BASE_URL}/register", json=data, timeout=3)