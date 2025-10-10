# algorithms/sim_anneal.py
import math
import random
from .base import BaseAlgorithm, Node

class SimulatedAnnealingAlgorithm(BaseAlgorithm):
    """
    Simulated Annealing cho Eight Rooks (đặt 1 quân mỗi hàng).
    - Trạng thái: list[(row, col)] đủ n (có thể trùng cột).
    - Energy: n - số cột khác nhau (0 là tối ưu).
    - Láng giềng: chọn ngẫu nhiên 1 hàng, đổi sang 1 cột khác.
    - Lịch nhiệt: T_k = T0 * alpha^k (alpha < 1).
    """

    # ====== Tham số dễ chỉnh ======
    T0 = 2.5               # nhiệt độ ban đầu
    ALPHA = 0.98           # hệ số làm nguội (0.9..0.995)
    STEPS = 5000           # số bước tối đa
    LOG_EVERY = 200        # log định kỳ để theo dõi (không ảnh hưởng hiển thị chuyển động)

    # Hàm đánh giá
    def energy(self, state):
        """Energy = số xung đột cột = n - số cột khác nhau (0 là tốt nhất)."""
        distinct = len({c for _, c in state})
        return self.n - distinct

    def is_goal_full(self, state):
        """Nghiệm: không trùng cột."""
        return self.energy(state) == 0

    # ====== SA chính ======
    def set_up_SA(self, T0: float = None, alpha: float = None, steps: int = None):
        """
        Chạy SA, trả về path (list[(state, action)]) để GUI phát lại.
        - T0: nhiệt độ đầu, alpha: hệ số nguội (0<alpha<1), steps: số bước.
        """
        T0 = float(T0 if T0 is not None else self.T0)
        alpha = float(alpha if alpha is not None else self.ALPHA)
        steps = int(steps if steps is not None else self.STEPS)

        # bắt đầu đo
        self.begin_run()

        # trạng thái khởi đầu
        cur = self.random_initial_state()
        E_cur = self.energy(cur)
        best = cur
        E_best = E_cur

        path = [(cur, f"Start: energy={E_cur}")]
        self.update_depth_peak(self.n - 1)
        self.update_frontier_peak(1)
        self.steps.append((cur, [f"Init SA: T0={T0:.3f}, alpha={alpha}, steps={steps}, E={E_cur}"], [Node(state=cur)]))

        if self.is_goal_full(cur):
            self.end_run(solution_node=Node(state=cur))
            self.solution = cur
            return path

        T = T0
        for k in range(1, steps + 1):
            # đề xuất láng giềng
            neighbors = self.generate_neighbors(cur)
            if not neighbors:
                break
            action, nxt = random.choice(neighbors)
            
            E_nxt = self.energy(nxt)
            dE = E_nxt - E_cur

            # quyết định chấp nhận
            accept = (dE <= 0) or (random.random() < math.exp(-dE / max(T, 1e-9)))

            # thống kê
            self.metrics["nodes_visited"] += 1

            # log định kỳ (thông tin)
            if k % self.LOG_EVERY == 0:
                frontier = [Node(state=cur), Node(state=nxt)]
                msg = f"Iter {k}: T={T:.3f}, E_cur={E_cur}, E_nxt={E_nxt}, dE={dE}, accept={accept}"
                self.steps.append((cur, [msg], frontier))

            # cập nhật nếu chấp nhận —> QUAN TRỌNG: append steps để GUI thấy chuyển động
            if accept:
                cur, E_cur = nxt, E_nxt
                path.append((cur, f"{action} (E={E_cur})"))

                # push một snapshot ngắn để UI animate
                self.steps.append((cur, [f"{action} | E={E_cur}, T={T:.3f}"], [Node(state=cur)]))

                # cập nhật best
                if E_cur < E_best:
                    best, E_best = cur, E_cur

                # nghiệm?
                if self.is_goal_full(cur):
                    self.end_run(solution_node=Node(state=cur))
                    self.solution = cur
                    return path

            # làm nguội
            T *= alpha

        # hết bước: trả về best tìm được
        solved = self.is_goal_full(best)
        self.end_run(solution_node=Node(state=best) if solved else None)
        if solved:
            self.solution = best
        path.append((best, f"Stop: best_energy={E_best}"))
        return path
