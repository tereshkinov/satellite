import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle

# Параметры задачи
gamma = 6.67e-11  # Гравитационная постоянная
M = 5.99e24  # Масса Земли
R_earth = 6.38e6  # Радиус Земли
r_c = 1e7  # Радиус круговой орбиты

# Скорость на круговой орбите
v_c = np.sqrt(gamma * M / r_c)


class SatelliteSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Симулятор движения спутника")
        self.root.geometry("800x700")

        # Инициализация атрибутов
        self.is_animating = False
        self.animation = None
        self.current_u = 0
        self.time_step = 0
        self.max_time_steps = 1000
        self.current_state = np.array([r_c, 0, 0, v_c])
        self.trajectory_x = []
        self.trajectory_y = []

        # Создаем элементы интерфейса
        self.create_widgets()
        self.init_plot()

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Главный контейнер
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Фрейм для графика
        graph_frame = tk.Frame(main_frame, height=500)
        graph_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        graph_frame.pack_propagate(False)

        # Создаем график
        self.figure, self.ax = plt.subplots(figsize=(6, 4.5))
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Фрейм для управления
        control_frame = tk.Frame(main_frame, height=150)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X)
        control_frame.pack_propagate(False)

        # Ползунок для управления u
        slider_frame = tk.Frame(control_frame)
        slider_frame.pack(fill=tk.X, pady=5, padx=10)

        self.u_label = tk.Label(slider_frame, text="Скорость торможения (м/с): 0")
        self.u_label.pack(side=tk.LEFT, anchor='w')

        self.u_slider = ttk.Scale(slider_frame, from_=0, to=7000, orient=tk.HORIZONTAL,
                                  command=self.update_u)
        self.u_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # Кнопки управления
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.start_btn = tk.Button(btn_frame, text="Старт", width=8, command=self.start_animation)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(btn_frame, text="Стоп", width=8, command=self.stop_animation)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = tk.Button(btn_frame, text="Сброс", width=8, command=self.reset_simulation)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # Информационная метка
        self.status_label = tk.Label(control_frame, text="Готов к запуску", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, padx=10, pady=5)

    def init_plot(self):
        """Инициализация графика"""
        self.ax.clear()
        scale = 3
        self.ax.set_xlim(-scale * r_c, scale * r_c)
        self.ax.set_ylim(-scale * r_c, scale * r_c)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title("Движение спутника вокруг Земли")

        # Форматирование осей
        ticks = np.linspace(-scale * r_c, scale * r_c, 7)
        self.ax.set_xticks(ticks)
        self.ax.set_yticks(ticks)
        self.ax.set_xticklabels([f"{x / 1e7:.0f}" for x in ticks])
        self.ax.set_yticklabels([f"{y / 1e7:.0f}" for y in ticks])
        self.ax.set_xlabel("x (тыс. км)")
        self.ax.set_ylabel("y (тыс. км)")

        # Земля
        earth = Circle((0, 0), R_earth, color='blue', alpha=0.3)
        self.ax.add_patch(earth)

        # Круговая орбита
        theta = np.linspace(0, 2 * np.pi, 100)
        self.orbit, = self.ax.plot(r_c * np.cos(theta), r_c * np.sin(theta), 'k--', alpha=0.3)

        # Спутник и траектория
        self.satellite, = self.ax.plot([], [], 'ro', markersize=6)
        self.trajectory, = self.ax.plot([], [], 'r-', linewidth=0.6, alpha=0.7)

        self.canvas.draw()

    def update_u(self, val):
        """Обновление скорости торможения"""
        self.current_u = float(val)
        self.u_label.config(text=f"Скорость торможения (м/с): {self.current_u:.0f}")
        self.status_label.config(text=f"Установлено торможение: {self.current_u:.0f} м/с")

        if not self.is_animating:
            self.reset_simulation()

    def start_animation(self):
        """Запуск анимации"""
        if not self.is_animating:
            self.is_animating = True
            self.status_label.config(text="Анимация запущена")
            self.animation = FuncAnimation(self.figure, self.update_plot,
                                           frames=self.max_time_steps,
                                           interval=30, blit=False)
            self.canvas.draw()

    def stop_animation(self):
        """Остановка анимации"""
        if self.is_animating:
            if self.animation:
                self.animation.event_source.stop()
            self.is_animating = False
            self.status_label.config(text="Анимация остановлена")

    def reset_simulation(self):
        """Сброс симуляции"""
        self.time_step = 0
        self.trajectory_x = [r_c]
        self.trajectory_y = [0]
        self.current_state = np.array([r_c, 0, 0, v_c - self.current_u])
        self.init_plot()
        self.status_label.config(text=f"Сброс. Торможение: {self.current_u:.0f} м/с")

    def equations_of_motion(self, state):
        """Уравнения движения спутника"""
        x, y, vx, vy = state
        r = np.sqrt(x ** 2 + y ** 2)
        r3 = r ** 3
        ax = -gamma * M * x / r3
        ay = -gamma * M * y / r3
        return np.array([vx, vy, ax, ay])

    def runge_kutta_4(self, state, dt):
        """Метод Рунге-Кутты 4-го порядка"""
        k1 = self.equations_of_motion(state)
        k2 = self.equations_of_motion(state + 0.5 * dt * k1)
        k3 = self.equations_of_motion(state + 0.5 * dt * k2)
        k4 = self.equations_of_motion(state + dt * k3)
        return state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

    def update_plot(self, frame):
        """Обновление графика на каждом кадре анимации"""
        if not self.is_animating:
            return

        self.time_step += 1
        dt = 10  # Шаг времени (секунды)

        # Используем метод Рунге-Кутты 4-го порядка
        self.current_state = self.runge_kutta_4(self.current_state, dt)

        # Обновление позиции
        x, y = self.current_state[0], self.current_state[1]
        self.trajectory_x.append(x)
        self.trajectory_y.append(y)

        # Обновление графиков
        self.satellite.set_data([x], [y])
        self.trajectory.set_data(self.trajectory_x, self.trajectory_y)

        # Обновление информации
        r = np.sqrt(x ** 2 + y ** 2)
        v = np.sqrt(self.current_state[2] ** 2 + self.current_state[3] ** 2)
        total_seconds = self.time_step * dt
        minutes, seconds = divmod(total_seconds, 60)
        time_str = f"{int(minutes)} мин {int(seconds)} сек"

        self.status_label.config(
            text=f"Время: {time_str} | Расстояние: {r / 1000:.1f} км | Скорость: {v:.1f} м/с"
        )

        # Проверка столкновения
        if r <= R_earth * 1.0:
            self.status_label.config(text=f"СПУТНИК УПАЛ! Время: {time_str}")
            self.stop_animation()

        return self.satellite, self.trajectory


if __name__ == "__main__":
    root = tk.Tk()
    app = SatelliteSimulator(root)
    root.mainloop()