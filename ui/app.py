import tkinter as tk
from .layout import LayoutBuilder
from .board_view import BoardView
from .controls import ControlHandler

class EightRooksApp:
    def __init__(self, master, algorithms_dict, default_algo="DFS"):
        self.master = master
        self.master.title("Eight Rooks Puzzle")

        self.algorithms_dict = algorithms_dict
        self.current_algo_key = default_algo
        self.algorithm = self.algorithms_dict[self.current_algo_key]()
        self.n = 8
        self.cell_size = 50

        # Gắn các module con
        self.layout = LayoutBuilder(self)
        self.board = BoardView(self)
        self.controls = ControlHandler(self)

        # Tạo giao diện
        self.layout.create_layout()
        self.board.draw_boards()

    # Ủy quyền cho lớp Controls
    def start(self): self.controls.start()
    def stop(self): self.controls.stop()
    def run(self): self.controls.run()
    def animate(self): self.controls.animate()
    def step(self): self.controls.step()
    def step_back(self): self.controls.step_back()
    def fast_backward(self): self.controls.fast_backward()
    def fast_forward(self): self.controls.fast_forward()
    def show_step(self, step): self.controls.show_step(step)
