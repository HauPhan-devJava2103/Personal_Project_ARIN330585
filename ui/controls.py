import tkinter as tk
from tkinter import messagebox

class ControlHandler:
    def __init__(self, app):
        self.app = app
        self.is_running = False

    def on_algo_change(self, event=None):
        app = self.app
        self.is_running = False
        app.current_algo_key = app.algo_combo.get()
        AlgoClass = app.algorithms_dict[app.current_algo_key]
        app.algorithm = AlgoClass()
        app.stack_label.config(text="Frontier State (Stack for DFS / Queue for BFS)")
        app.left_canvas.delete("rook")
        app.right_canvas.delete("rook")
        app.stack_text.delete(1.0, tk.END)

        # KHÔNG còn step_button ở đây
        for b in [app.btn_fast_backward, app.btn_back, app.btn_next,
                  app.btn_fast_forward, app.run_button, app.stop_button]:
            b.config(state=tk.DISABLED)
        app.start_button.config(state=tk.NORMAL)

    def start(self):
        app = self.app
        algo = app.algorithm
        self.is_running = False
        algo.steps = []
        algo.solution = None
        app.left_canvas.delete("rook")
        app.right_canvas.delete("rook")
        app.stack_text.delete(1.0, tk.END)

        key = app.current_algo_key.upper()
        if key == "DFS":
            path = algo.set_up_DFS()
        elif key == "BFS":
            path = algo.set_up_BFS()
        elif key == "UCS":
            path = algo.set_up_UCS()
        elif key == "IDS":
            path = algo.set_up_IDS()
        elif key == "IDS*":
            path = algo.set_up_IDSStar()
        elif key == "A*":
            path = algo.set_up_AStar()
        elif key == "GREEDY":
            path = algo.set_up_Greedy()
        elif key == "HC":
            path = algo.set_up_HC(max_iterations=200)
        elif key == "BEAM":
            path = algo.set_up_Beam(beam_size=3)
        elif key == "GA":
            path = algo.set_up_GA()
        elif key == "SA":
            path = algo.set_up_SA(T0=2.5, alpha=0.98, steps=5000)
        elif key == "BATR":
            path = algo.set_up_Backtracking()
        elif key == "BT+FC":
            path = algo.set_up_BacktrackingFC(shuffle_cols=True)
        elif key == "BT+AC3":
            path = algo.set_up_BacktrackingAC3(use_mrv=True, shuffle_cols=True)
        elif key == "PO-DFS":
            hidden = [3, 6, 1, 4, 7, 0, 2, 5]
            app.algorithm = type(app.algorithm)(n=app.algorithm.n, hidden_solution=hidden,
                                                shuffle_values=True, use_mrv=True)
            path = app.algorithm.set_up_PartialDFS(max_sense_per_row=2)

        elif key == "NO-OBS(DFS)":
            path = algo.set_up_NoObsBeliefDFS(use_mrv=True, shuffle_values=True, seed=None)

        elif key == "AND-OR":
            path = algo.set_up_AndOr()

        else:
            messagebox.showerror("Error", f"Unknown algorithm: {app.current_algo_key}")
            return

        # metrics (nếu bạn đã thêm trong BaseAlgorithm)
        m = algo.metrics
        metrics_str = (
            "=== Run Metrics ===\n"
            f"Algorithm         : {self.app.current_algo_key}\n"
            f"Elapsed           : {m['elapsed_s']:.3f} s\n"
            f"Nodes visited     : {m['nodes_visited']}\n"
            f"Max frontier size : {m['max_frontier']}\n"
            f"Max depth reached : {m['max_depth']}\n"
            f"Solution depth    : {m['solution_depth']}\n"
            f"Solution cost     : {m['solution_cost']}\n"   # ← THÊM DÒNG NÀY
            f"Peak memory       : {m['peak_mem_mb']:.3f} MB\n"
        )


        if path:
            algo.solution = path[-1][0]
            app.board.draw_board_state(app.left_canvas, algo.solution)
            app.current_step = 0
            app.show_step(0)

            # BẬT NÚT — KHÔNG có step_button
            app.stop_button.config(state=tk.NORMAL)
            app.run_button.config(state=tk.NORMAL)
            for b in [app.btn_fast_backward, app.btn_back, app.btn_next, app.btn_fast_forward]:
                b.config(state=tk.NORMAL)

            messagebox.showinfo("Run Metrics", metrics_str)
            app.stack_text.insert(tk.END, "\n\n" + metrics_str)
        else:
            messagebox.showinfo("No Solution", "No solution found.\n\n" + metrics_str)
            app.stack_text.insert(tk.END, "\n\n" + metrics_str)

    def run(self):
        app = self.app
        if not hasattr(app, "current_step"):
            return
        self.is_running = True
        app.master.after(0, app.animate)
        app.run_button.config(state=tk.DISABLED)
        app.stop_button.config(state=tk.NORMAL)

    def stop(self):
        self.is_running = False
        self.app.run_button.config(state=tk.NORMAL)

    def animate(self):
        app = self.app
        algo = app.algorithm
        if not self.is_running:
            return
        if app.current_step < len(algo.steps):
            app.show_step(app.current_step)
            app.current_step += 1
            app.master.after(200, app.animate)
        else:
            self.is_running = False
            app.run_button.config(state=tk.NORMAL)

    def show_step(self, step):
        app = self.app
        algo = app.algorithm
        if step < len(algo.steps):
            state, actions, frontier = algo.steps[step]
            app.board.draw_board_state(app.right_canvas, state)
            app.stack_text.delete(1.0, tk.END)

            header = f"Algorithm: {app.current_algo_key}\n"
            action_line = f"Action: {actions[0]}"
            lines = [header, action_line, "-"*30]

            # hiển thị frontier (stack/queue/heap) kèm cost nếu có
            for i, node in enumerate(frontier):
                # ưu tiên đọc node.g; nếu không có thì ước lượng = len(state)
                g = getattr(node, "g", len(node.state))
                lines.append(f"[{i}] g={g}  {node.state}")

            app.stack_text.insert(tk.END, "\n".join(lines))

    def step(self):
        app = self.app
        algo = app.algorithm
        if hasattr(app, "current_step") and app.current_step < len(algo.steps) - 1:
            app.current_step += 1
            app.show_step(app.current_step)

    def step_back(self):
        app = self.app
        if hasattr(app, "current_step") and app.current_step > 0:
            app.current_step -= 1
            app.show_step(app.current_step)

    def fast_backward(self):
        app = self.app
        if hasattr(app, "current_step"):
            app.current_step = 0
            app.show_step(app.current_step)

    def fast_forward(self):
        app = self.app
        algo = app.algorithm
        if hasattr(algo, "steps") and algo.steps:
            app.current_step = len(algo.steps) - 1
            app.show_step(app.current_step)
