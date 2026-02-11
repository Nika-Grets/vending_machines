from PyQt6.QtWidgets import * 
from PyQt6.QtCore import Qt
from front.styles import STYLE_SHEET
from front.api import ApiClient

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.user_data = None
        self.setWindowTitle("Вход")
        self.setFixedSize(350, 400)
        self.setStyleSheet(STYLE_SHEET)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.email = QLineEdit(placeholderText="Email")
        self.password = QLineEdit(placeholderText="Пароль", echoMode=QLineEdit.EchoMode.Password)

        btn_login = QPushButton("ВОЙТИ", objectName="Primary")
        btn_login.clicked.connect(self.handle_login)

        btn_reg = QPushButton("Регистрация")
        btn_reg.setStyleSheet("border:none; color:#3498DB;")
        btn_reg.clicked.connect(self.open_reg)

        self.err = QLabel("")
        self.err.setObjectName("ErrorMsg")

        self.logo = QLabel("<h2>ЛОГО</h2>")
        self.logo.setObjectName("NamingLog")
        layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addWidget(btn_login)
        layout.addWidget(btn_reg)
        layout.addWidget(self.err)


    def handle_login(self):
        try:
            r = ApiClient.login(self.email.text(), self.password.text())
            if r.status_code == 200:
                self.user_data = r.json()
                self.accept()
            else:
                self.err.setText("Неверный логин или пароль")
        except:
            self.err.setText("Сервер недоступен")

    def open_reg(self):
        reg = RegisterWindow()
        reg.exec()

class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setStyleSheet(STYLE_SHEET)
        layout = QVBoxLayout(self)

        self.inputs = {
            "email": QLineEdit(placeholderText="Email"),
            "password": QLineEdit(placeholderText="Пароль", echoMode=QLineEdit.EchoMode.Password),
            "last_name": QLineEdit(placeholderText="Фамилия"),
            "first_name": QLineEdit(placeholderText="Имя"),
            "middle_name": QLineEdit(placeholderText="Отчество")
        }
        for w in self.inputs.values(): layout.addWidget(w)

        btn = QPushButton("СОЗДАТЬ АККАУНТ", objectName="Primary")
        btn.clicked.connect(self.handle_reg)
        layout.addWidget(btn)

    def handle_reg(self):
        data = {k: v.text() for k, v in self.inputs.items()}
        try:
            r = ApiClient.register(data)
            if r.status_code == 200:
                QMessageBox.information(self, "Успех", "Регистрация завершена!")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", r.json().get('detail', 'Ошибка регистрации'))
        except:
            QMessageBox.critical(self, "Ошибка", "Сервер оффлайн")
