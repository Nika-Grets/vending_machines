from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from front.styles import STYLE_SHEET
from front.widgets.charts import StatusDonutChart, RevenueChart
from front.api import DataFetcher

class MainWindow(QMainWindow):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.setWindowTitle("Система управления ВА")
        self.resize(1200, 800)
        self.setStyleSheet(STYLE_SHEET)

        # Поток для данных
        self.fetcher = DataFetcher()
        self.fetcher.data_received.connect(self.update_ui_with_data)
        self.fetcher.error_occurred.connect(self.handle_error)

        # Основной контейнер (вертикальный: Шапка 1 -> Шапка 2 -> Тело)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        cw = QWidget()
        cw.setLayout(main_layout)
        self.setCentralWidget(cw)

        # --- ШАПКА 1 (Лого + Пользователь) ---
        h1 = QFrame(); h1.setObjectName("Header1"); h1.setFixedHeight(55)
        l1 = QHBoxLayout(h1)
        l1.addWidget(QLabel("<p style='font-size:13px; color:#2C3E50; margin-left:10px;'><b>ЛОГО</b></p>"))
        l1.addStretch()

        # Данные пользователя из БД
        fio = self.user_info.get('fio', 'Иванов И.И.')
        role = self.user_info.get('role', 'Пользователь')
        self.name_lbl = QLabel(f"<p style='text-align:right; color:black;'><b>{fio}</b><br><small>{role}</small></p>")
        l1.addWidget(self.name_lbl)
        main_layout.addWidget(h1)

        # --- ШАПКА 2 (Навигация + Компания) ---
        h2 = QFrame(); h2.setObjectName("Header2"); h2.setFixedHeight(45)
        l2 = QHBoxLayout(h2); l2.setContentsMargins(0, 0, 15, 0); l2.setSpacing(0)

        # Левый блок навигации с кнопкой меню
        self.nav_box = QFrame(); self.nav_box.setFixedWidth(220); self.nav_box.setObjectName("NavBox")
        nl = QHBoxLayout(self.nav_box)
        nl.addWidget(QLabel("<b style='color:white; font-size:11px'>НАВИГАЦИЯ</b>"))

        self.m_btn = QPushButton("≡"); self.m_btn.setObjectName("MenuBtn"); self.m_btn.setFixedSize(30, 25)
        self.m_btn.clicked.connect(self.toggle_sb)
        nl.addWidget(self.m_btn)

        l2.addWidget(self.nav_box)
        l2.addWidget(QLabel("<b style='color:white;'>  ООО ТОРГОВЫЕ АВТОМАТЫ</b>"))
        l2.addStretch()
        main_layout.addWidget(h2)

        # --- ТЕЛО (Сайдбар + Контент) ---
        body = QHBoxLayout(); body.setSpacing(0); body.setContentsMargins(0, 0, 0, 0)

        # Сайдбар
        self.sb = QFrame(); self.sb.setObjectName("Sidebar"); self.sb.setFixedWidth(220)
        sl = QVBoxLayout(self.sb)
        for i in ["Главная", "Монитор ТА", "Отчеты", "Учет ТМЦ", "Администрирование"]:
            btn = QPushButton(i); btn.setObjectName("NavBtn"); sl.addWidget(btn)
        sl.addStretch()
        body.addWidget(self.sb)

        # Контентная область
        cont = QWidget(); cl = QVBoxLayout(cont); cl.setContentsMargins(25, 20, 25, 20)
        cl.addWidget(QLabel("<h2 style='color:#2D3748'>Личный кабинет. Главная</h2>"))

        grid = QGridLayout(); grid.setSpacing(20)
        cl.addLayout(grid)

        # Карточки (плитки)
        # 1. Эффективность
        self.c_eff = self.make_card(grid, "Эффективность сети", 0, 0)
        self.eff_l = QLabel("0%"); self.eff_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.eff_l.setStyleSheet("font-size: 45px; font-weight: bold; color: #27AE60; margin-top: 20px;")
        self.c_eff.layout().addWidget(self.eff_l)

        # 2. Состояние (Бублик)
        self.c_st = self.make_card(grid, "Состояние сети", 0, 1)
        self.chart_st = StatusDonutChart()
        self.c_st.layout().addWidget(self.chart_st)

        # 3. Сводка (с правильным расположением)
        self.c_sum = self.make_card(grid, "Сводка", 0, 2, 2, 1)
        self.sum_l = QLabel("Загрузка данных..."); self.sum_l.setStyleSheet("font-size: 14px; color: #333; line-height:150%;")
        self.sum_l.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.c_sum.layout().addWidget(self.sum_l)

        # 4. График выручки
        self.c_rev = self.make_card(grid, "Динамика выручки", 1, 0, 1, 2)
        self.chart_rev = RevenueChart()
        self.c_rev.layout().addWidget(self.chart_rev)

        body.addWidget(cont)
        main_layout.addLayout(body)

        # Таймер обновления
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(10000)
        self.refresh_data()

    def make_card(self, g, t, r, c, rs=1, cs=1):
        f = QFrame(); f.setObjectName("Card"); f.setLayout(QVBoxLayout())
        tl = QLabel(t.upper()); tl.setObjectName("CardTitle")
        tl.setFixedHeight(25)
        f.layout().addWidget(tl)
        g.addWidget(f, r, c, rs, cs)
        return f

    def toggle_sb(self):
        # Логика сворачивания сайдбара
        hide = not self.sb.isHidden()
        self.sb.setHidden(hide)
        self.nav_box.setFixedWidth(50 if hide else 220)

    def refresh_data(self):
        if not self.fetcher.isRunning():
            self.fetcher.start()

    def update_ui_with_data(self, data):
        # 1. Обновляем Сводку
        total = data['total']
        val = total.get('Всё', 0) or 0
        cnt = total.get('Счёт', 0) or 1
        avg = int(val / max(1, cnt))
        self.sum_l.setText(
            f"<br><b>Выручка:</b> {val:,} ₽<br><br>"
            f"<b>Продаж:</b> {cnt}<br><br>"
            f"<b>Ср. чек:</b> {avg} ₽"
        )

        # 2. Обновляем Эффективность
        eff_data = data['efficiency']
        self.eff_l.setText(f"{eff_data['efficiency']}%")

        # 3. Обновляем Бублик
        on = eff_data['online']
        tot = eff_data['total']
        ser = eff_data['service']
        off = max(0, tot - on - ser)
        self.chart_st.update_data(on, off, ser)

        # 4. Обновляем график выручки
        self.chart_rev.update_data(data['daily'])

    def handle_error(self, err):
        self.sum_l.setText(f"<span style='color:red'>Ошибка связи с сервером</span>")
        print(f"API Error: {err}")