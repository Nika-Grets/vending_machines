import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import QTimer

# === Бублик
class StatusDonutChart(FigureCanvas):
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(3, 3), dpi=100)
        super().__init__(self.fig)
        self.data = [0, 0, 0]
        self.labels = ["Работает", "Оффлайн", "Обслуживание"]
        self.colors = ['#2ECC71', '#E74C3C', '#F1C40F']
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def update_data(self, on, off, ser):
        self.data = [on, off, ser]
        self.draw_donut(f"Всего\n{sum(self.data)} шт")

    def draw_donut(self, text, color="#333"):
        self.ax.clear()
        vals = self.data if sum(self.data) > 0 else [1, 0, 0]
        self.ax.pie(vals, colors=self.colors, startangle=90, counterclock=False, 
                    wedgeprops={'width': 0.4, 'edgecolor': 'w'})
        self.ax.text(0, 0, text, ha='center', va='center', fontsize=10, fontweight='bold', color=color)
        self.draw()

    def on_click(self, event):
        if event.inaxes != self.ax or sum(self.data) == 0: return
        # Логика определения сегмента при клике
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

# === График
class RevenueChart(FigureCanvas):
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(4, 3), dpi=90)
        super().__init__(self.fig)

    def update_data(self, data):
        self.ax.clear()
        if data:
            self.ax.bar([str(d['date'])[-7:] for d in data], [d['total'] for d in data], color='#3498DB')
            self.ax.tick_params(axis='both', labelsize=8)
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
        self.fig.tight_layout()
        self.draw()