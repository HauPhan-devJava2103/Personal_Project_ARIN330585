import tkinter as tk
from tkinter import ttk
import os

class LayoutBuilder:
    def __init__(self, app):
        self.app = app

    def create_layout(self):
        app = self.app

        # --- Combobox chọn thuật toán ---
        topbar = tk.Frame(app.master)
        topbar.pack(side=tk.TOP, fill=tk.X, pady=6)

        tk.Label(topbar, text="Algorithm:").pack(side=tk.LEFT, padx=(10,4))
        app.algo_combo = ttk.Combobox(topbar, state="readonly",
                                      values=list(app.algorithms_dict.keys()))
        app.algo_combo.set(app.current_algo_key)
        app.algo_combo.pack(side=tk.LEFT)
        app.algo_combo.bind("<<ComboboxSelected>>", app.controls.on_algo_change)

        # --- Final Result ---
        app.left_frame = tk.Frame(app.master)
        app.left_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(app.left_frame, text="Final Result").pack()
        app.left_canvas = tk.Canvas(app.left_frame, width=app.n*app.cell_size, height=app.n*app.cell_size)
        app.left_canvas.pack()

        # --- Step-by-step ---
        app.right_frame = tk.Frame(app.master)
        app.right_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(app.right_frame, text="Step-by-Step").pack()
        app.right_canvas = tk.Canvas(app.right_frame, width=app.n*app.cell_size, height=app.n*app.cell_size)
        app.right_canvas.pack()

        # --- Stack/Queue ---
        app.stack_frame = tk.Frame(app.master)
        app.stack_frame.pack(side=tk.LEFT, padx=10)
        app.stack_label = tk.Label(app.stack_frame, text="Frontier State")
        app.stack_label.pack()
        app.stack_text = tk.Text(app.stack_frame, width=36, height=22)
        app.stack_text.pack()

        # --- Khu vực Nút điều khiển ---
        app.control_frame = tk.Frame(app.master)
        app.control_frame.pack(side=tk.BOTTOM, pady=10)

        # Hàng 1: Start - Dừng - Run
        bar = tk.Frame(app.control_frame)
        bar.pack(side=tk.TOP, pady=5)
        app.start_button = tk.Button(bar, text="Start", command=app.start)
        app.start_button.pack(side=tk.LEFT, padx=6)
        app.stop_button = tk.Button(bar, text="Dừng", command=app.stop, state=tk.DISABLED)
        app.stop_button.pack(side=tk.LEFT, padx=6)
        app.run_button = tk.Button(bar, text="Run", command=app.run, state=tk.DISABLED)
        app.run_button.pack(side=tk.LEFT, padx=6)

        # Hàng 2: 4 nút icon
        nav_frame = tk.Frame(app.control_frame)
        nav_frame.pack(side=tk.TOP, pady=5)
        asset_path = os.path.join(os.path.dirname(__file__), "..", "assets")

        def load_icon(name):
            path = os.path.join(asset_path, name)
            if os.path.exists(path):
                return tk.PhotoImage(file=path)
            return None

        app.icon_fast_backward = load_icon("fast-backward-icon.png")
        app.icon_back = load_icon("back-icon.png")
        app.icon_next = load_icon("next-icon.png")
        app.icon_fast_forward = load_icon("fast-forward-icon.png")

        app.btn_fast_backward = tk.Button(nav_frame, image=app.icon_fast_backward,
                                          command=app.fast_backward, state=tk.DISABLED)
        app.btn_back = tk.Button(nav_frame, image=app.icon_back,
                                 command=app.step_back, state=tk.DISABLED)
        app.btn_next = tk.Button(nav_frame, image=app.icon_next,
                                 command=app.step, state=tk.DISABLED)
        app.btn_fast_forward = tk.Button(nav_frame, image=app.icon_fast_forward,
                                         command=app.fast_forward, state=tk.DISABLED)

        for b in [app.btn_fast_backward, app.btn_back, app.btn_next, app.btn_fast_forward]:
            b.pack(side=tk.LEFT, padx=4)
