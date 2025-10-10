# algorithms/astar.py
import heapq
import itertools
from .base import BaseAlgorithm, Node

class AStarAlgorithm(BaseAlgorithm):
    """
    A* cho bài Eight Rooks.
    - f(n) = g(n) + h(n)
    - g(n): tổng chi phí đã đi (mỗi bước đặt quân).
    - h(n): ước lượng chi phí ít nhất còn lại (admissible).
    """

    # ===== Heuristic: tổng k cột rẻ nhất còn trống =====
    def heuristic(self, state) -> float:
        """
        h(state) = tổng chi phí nhỏ nhất cho k quân còn lại,
        k = self.n - len(state).
        Lấy k cột rẻ nhất trong số cột chưa dùng (admissible & consistent).
        """
        remaining = self.n - len(state)
        if remaining <= 0:
            return 0.0

        used_cols = {c for _, c in state}
        r = len(state)  # hàng kế tiếp (ở đây cost chỉ phụ thuộc col)
        costs = []
        for c in range(self.n):
            if c not in used_cols:
                costs.append(self.move_cost(r, c))
        costs.sort()
        return float(sum(costs[:remaining]))

    def set_up_AStar(self):
        """
        Chạy A* và trả về path (list[(state, action), ...])
        """
        # 1) Khởi động đo thời gian/bộ nhớ
        self.begin_run()

        # 2) Khởi tạo root
        root = self.make_root_node()          
        r0, c0 = root.state[0]
        g0 = self.move_cost(r0, c0)    
        h0 = self.heuristic(root.state)
        f0 = g0 + h0
        root.g = g0
        root.f = f0

        # 3) Hàng đợi ưu tiên theo f
        counter = itertools.count()             # tie-breaker
        open_heap = []                          # (f, tie, node)
        heapq.heappush(open_heap, (f0, next(counter), root))

        # 4) Bảng best_g: chi phí tốt nhất đã thấy cho 1 trạng thái (khóa = tuple(cột))
        best_g = {}  # key: tuple(cols) -> g

        # 5) Log/metrics ban đầu
        self.update_frontier_peak(len(open_heap))
        self.update_depth_peak(len(root.state) - 1)
        self.steps.append(
            (root.state, [f"Push root: g={g0:.2f}, h={h0:.2f}, f={f0:.2f}"],
             [t[2] for t in open_heap])
        )

        while open_heap:
            f, _, node = heapq.heappop(open_heap)
            self.metrics["nodes_visited"] += 1
            # đảm bảo node có g/f để GUI hiển thị
            if not hasattr(node, "f"): node.f = f
            if not hasattr(node, "g"): node.g = (f - self.heuristic(node.state))

            # Log pop
            self.steps.append(
                (node.state, [f"Pop: g={node.g:.2f}, h={self.heuristic(node.state):.2f}, f={f:.2f}"],
                 [t[2] for t in open_heap])
            )

            # Prune theo best_g
            key = tuple(c for _, c in node.state)
            if key in best_g and node.g > best_g[key]:
                # đã có đường rẻ hơn đến cùng trạng thái
                continue
            best_g[key] = node.g

            # Goal
            if self.is_goal(node.state):
                self.end_run(solution_node=node)
                self.metrics["solution_cost"] = float(node.g)
                return self.extract_path(node)

            # Mở rộng
            for action, new_state in self.succ(node.state):
                r_new, c_new = new_state[-1]
                step = self.move_cost(r_new, c_new)
                g_new = node.g + step
                h_new = self.heuristic(new_state)
                f_new = g_new + h_new

                # prune sớm nếu đã có g tốt hơn
                key_new = tuple(c for _, c in new_state)
                if key_new in best_g and g_new >= best_g[key_new]:
                    continue

                child = Node(state=new_state, parent=node, action=action)
                child.g = g_new
                child.f = f_new

                heapq.heappush(open_heap, (f_new, next(counter), child))

                # cập nhật metrics + log
                self.update_frontier_peak(len(open_heap))
                self.update_depth_peak(len(new_state) - 1)
                self.steps.append(
                    (new_state, [f"Push: step={step:.2f} → g={g_new:.2f}, h={h_new:.2f}, f={f_new:.2f}"],
                     [t[2] for t in open_heap])
                )

        # 7) Không tìm thấy nghiệm
        self.end_run(solution_node=None)
        return None
