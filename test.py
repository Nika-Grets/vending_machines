import sys, requests
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

# --- 1. ГРАФИК-БУБЛИК ---
class StatusDonutChart(FigureCanvas):
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(3, 3), dpi=100)
        super().__init__(self.fig)
        self.data = [0, 0, 0] # [on, off, service]
        self.labels = ["Работает", "Оффлайн", "Обслуживание"]
        self.colors = ['#2ECC71', '#E74C3C', '#F1C40F']
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def update_data(self, on, off, ser):
        self.data = [on, off, ser]
        self.draw_donut(f"Всего\n{sum(self.data)} шт")

    def draw_donut(self, text, color="#333"):
        self.ax.clear()
        vals = self.data if sum(self.data) > 0 else [1, 0, 0]
        self.ax.pie(vals, colors=self.colors, startangle=90, counterclock=False, wedgeprops={'width': 0.4, 'edgecolor': 'w'})
        self.ax.text(0, 0, text, ha='center', va='center', fontsize=10, fontweight='bold', color=color)
        self.draw()

    def on_click(self, event):
        if event.inaxes != self.ax or sum(self.data) == 0: return
        x, y = event.xdata, event.ydata
        angle = (90 - np.degrees(np.arctan2(y, x))) % 360
        total, current_angle = sum(self.data), 0
        for i, val in enumerate(self.data):
            if val == 0: continue
            step = (val / total) * 360
            if current_angle <= angle <= current_angle + step:
                self.draw_donut(f"{self.labels[i]}\n{val} шт", self.colors[i])
                QTimer.singleShot(2000, lambda: self.draw_donut(f"Всего\n{sum(self.data)} шт"))
                break
            current_angle += step

# --- 2. ГРАФИК ВЫРУЧКИ ---
class RevenueChart(FigureCanvas):
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(4, 3), dpi=90)
        super().__init__(self.fig)

    def update_data(self, data):
        self.ax.clear()
        if data:
            self.ax.bar([str(d['date'])[-5:] for d in data], [d['total'] for d in data], color='#3498DB')
            self.ax.tick_params(axis='both', labelsize=8)
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
        self.fig.tight_layout()
        self.draw()

# --- 3. ГЛАВНОЕ ОКНО ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vending Control Panel")
        self.resize(1200, 800)
        self.setStyleSheet("""
            QMainWindow { background: #F4F7F6; }
            #Header1 { background: white; border-bottom: 1px #DDD; }
            #Header2 { background: #1C232D; border-bottom: 1px solid #DDD; }
            #Sidebar { background: #1C232D; border: none; }
            #Card { background: white; border-radius: 10px; border: 1px solid #D1D9E0; }
            #CardTitle { color: #1C232D; font-size: 11px; font-weight: bold; border-bottom: 1px solid #EEE; padding-bottom: 5px; }
            QPushButton#MenuBtn { background: #2D3748; color: white; border: none; font-size: 18px; border-radius: 3px; }
            QPushButton#NavBtn { color: #A0AEC0; text-align: left; border: none; padding: 12px; font-size: 13px; }
            QPushButton#NavBtn:hover { background: #2D3748; color: white; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        cw = QWidget(); cw.setLayout(layout); self.setCentralWidget(cw)

        # шапка 1
        h1 = QFrame(); h1.setObjectName("Header1"); h1.setFixedHeight(55)
        l1 = QHBoxLayout(h1); l1.addWidget(QLabel("<p style='font-size:13px; color:#2C3E50'>Лого</p>"))
        l1.addStretch(); l1.addWidget(QLabel("<p style='font-size:13px; color:#1C232D'> Иванов И.И. </p>"))
        layout.addWidget(h1)

        # шапка 2
        h2 = QFrame(); h2.setObjectName("Header2"); h2.setFixedHeight(45)
        l2 = QHBoxLayout(h2); l2.setContentsMargins(0,0,15,0); l2.setSpacing(0)
        self.nav_box = QFrame(); self.nav_box.setFixedWidth(220); self.nav_box.setStyleSheet("background:#1C232D")
        nl = QHBoxLayout(self.nav_box); nl.addWidget(QLabel("<b style='color:white; font-size:11px'>НАВИГАЦИЯ</b>"))
        self.m_btn = QPushButton("≡"); self.m_btn.setObjectName("MenuBtn"); self.m_btn.setFixedSize(30,25)
        self.m_btn.clicked.connect(self.toggle_sb); nl.addWidget(self.m_btn)
        l2.addWidget(self.nav_box); l2.addWidget(QLabel("  <b>ООО ТОРГОВЫЕ АВТОМАТЫ</b>")); l2.addStretch()
        layout.addWidget(h2)

        # тело (Сайдбар + Контент)
        body = QHBoxLayout(); body.setSpacing(0); body.setContentsMargins(0,0,0,0)
        self.sb = QFrame(); self.sb.setObjectName("Sidebar"); self.sb.setFixedWidth(220)
        sl = QVBoxLayout(self.sb)
        for i in ["Главная", "Монитор ТА", "Отчеты", "Учет ТМЦ", "Администрирование"]:
            btn = QPushButton(i); btn.setObjectName("NavBtn"); sl.addWidget(btn)
        sl.addStretch(); body.addWidget(self.sb)

        cont = QWidget(); cl = QVBoxLayout(cont); cl.setContentsMargins(25,20,25,20)
        cl.addWidget(QLabel("<h2 style='color:#2D3748'>Личный кабинет. Главная</h2>"))
        grid = QGridLayout(); grid.setSpacing(20); cl.addLayout(grid)

        # плитки
        self.c_eff = self.make_card(grid, "Эффективность сети", 0, 0)
        self.eff_l = QLabel("0%"); self.eff_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.eff_l.setStyleSheet("font-size: 45px; font-weight: bold; color: #27AE60; margin-top: 20px;")
        self.c_eff.layout().addWidget(self.eff_l)

        self.c_st = self.make_card(grid, "Состояние сети", 0, 1)
        self.chart_st = StatusDonutChart(); self.c_st.layout().addWidget(self.chart_st)

        self.c_sum = self.make_card(grid, "Сводка", 0, 2, 2, 1)
        self.sum_l = QLabel("Загрузка..."); self.sum_l.setStyleSheet("font-size: 13px; color: #555;")
        self.sum_l.setAlignment(Qt.AlignmentFlag.AlignTop); self.c_sum.layout().addWidget(self.sum_l)

        self.c_rev = self.make_card(grid, "Динамика выручки", 1, 0, 1, 2)
        self.chart_rev = RevenueChart(); self.c_rev.layout().addWidget(self.chart_rev)

        body.addWidget(cont); layout.addLayout(body)
        self.timer = QTimer(); self.timer.timeout.connect(self.load); self.timer.start(10000); self.load()

    def make_card(self, g, t, r, c, rs=1, cs=1):
        f = QFrame(); f.setObjectName("Card"); f.setLayout(QVBoxLayout())
        # контейнер для заголовка с фиксированной высотой
        t_area = QFrame(); t_area.setObjectName("TitleArea"); t_area.setFixedHeight(35)
        t_lay = QHBoxLayout(t_area); t_lay.setContentsMargins(0,0,0,5)
        tl = QLabel(t.upper()); tl.setObjectName("CardTitle")
        t_lay.addWidget(tl)
        f.layout().addWidget(t_area)
        g.addWidget(f, r, c, rs, cs); return f

    def toggle_sb(self):
        hide = not self.sb.isHidden()
        self.sb.setHidden(hide); self.nav_box.setFixedWidth(50 if hide else 220)

    def load(self):
        U = "http://127.0.0.1:8000"
        try:
            r1 = requests.get(f"{U}/stats/total", timeout=2).json()
            self.sum_l.setText(f"Выручка: {r1['Всё']:,} ₽<br><br>Продаж: {r1['Счёт']}<br><br>Ср. чек: {int(r1['Всё']/max(1,r1['Счёт']))} ₽")

            r2 = requests.get(f"{U}/stats/efficiency", timeout=2).json()
            self.eff_l.setText(f"{r2['efficiency']}%")
            # оффлайн для бублика (тестово)
            on, tot, ser = r2['online'], r2['total'], r2.get('service', 1)
            self.chart_st.update_data(on, max(0, tot-on-ser), ser)

            r3 = requests.get(f"{U}/stats/daily", timeout=2).json()
            self.chart_rev.update_data(r3)
        except: self.sum_l.setText("<span style='color:red'>Ошибка API</span>")

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setFont(QFont("Segoe UI", 9))
    w = MainWindow(); w.show(); sys.exit(app.exec())