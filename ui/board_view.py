class BoardView:
    def __init__(self, app):
        self.app = app

    def draw_boards(self):
        app = self.app
        for canvas in [app.left_canvas, app.right_canvas]:
            canvas.delete("all")
            for i in range(app.n):
                for j in range(app.n):
                    color = "white" if (i + j) % 2 == 0 else "gray"
                    canvas.create_rectangle(j*app.cell_size, i*app.cell_size,
                                            (j+1)*app.cell_size, (i+1)*app.cell_size,
                                            fill=color)

    def place_rook(self, canvas, row, col, color="black"):
        app = self.app
        x = col * app.cell_size + app.cell_size // 2
        y = row * app.cell_size + app.cell_size // 2
        canvas.create_oval(x-20, y-20, x+20, y+20, fill=color, tags="rook")

    def draw_board_state(self, canvas, state):
        canvas.delete("rook")
        for row, col in state:
            self.place_rook(canvas, row, col)
