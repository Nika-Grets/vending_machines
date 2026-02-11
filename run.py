import sys
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtGui import QFont

# Импортируем наши окна из новой структуры
from front.windows.auth_win import LoginWindow
from front.windows.main_win import MainWindow

def main():
    app = QApplication(sys.argv)

    # Устанавливаем глобальный шрифт для всего приложения
    app.setFont(QFont("Segoe UI", 9))

    # 1. Показываем окно входа
    login = LoginWindow()

    # login.exec() блокирует выполнение дальше, пока окно не закроется
    if login.exec() == QDialog.DialogCode.Accepted:

        # 2. Если пользователь вошел, создаем главное окно
        # Передаем в него user_data (fio, role), полученные от API
        window = MainWindow(login.user_data)
        window.show()

        # Запускаем основной цикл событий приложения
        sys.exit(app.exec())
    else:
        # Если пользователь просто закрыл окно входа — выходим
        sys.exit(0)

if __name__ == "__main__":
    main()