# algorithms/idsstar.py
import math
from .base import BaseAlgorithm, Node

class IDSStarAlgorithm(BaseAlgorithm):
    """
    IDA* (Iterative Deepening A*), còn được gọi là IDS*:
    - f(n) = g(n) + h(n)
    - Duyệt theo chiều sâu nhưng BỊ CHẶN bởi ngưỡng f (threshold)
    - Lặp tăng threshold = min(f vượt ngưỡng) ở lần trước cho tới khi tìm được lời giải
    - Ở bài Eight Rooks, g là tổng chi phí các bước đặt quân; h là ước lượng tối ưu còn lại (admissible)
    """

    # ====== HEURISTIC: tổng k cột rẻ nhất còn trống ======
    def heuristic(self, state) -> float:
        """
        h(state) = tổng chi phí nhỏ nhất có thể cho k quân còn lại,
        với k = số hàng chưa đặt = self.n - len(state).
        Tính bằng cách lấy k cột RẺ NHẤT trong số các cột chưa dùng (admissible).
        """
        remaining = self.n - len(state)
        if remaining <= 0:
            return 0.0

        used_cols = {c for _, c in state}
        r = len(state)  # hàng kế tiếp (cost hiện tại chỉ phụ thuộc col)
        candidates = []
        for c in range(self.n):
            if c not in used_cols:
                candidates.append(self.move_cost(r, c))
        candidates.sort()
        # nếu số cột trống < remaining (hiếm), cứ cộng hết
        return float(sum(candidates[:remaining]))

    # ====== HÀM CHÍNH: chạy IDA* ======
    def set_up_IDSStar(self):
        """
        Trả về path (list[(state, action), ...]) như các thuật toán khác.
        GUI của bạn đang dùng path[-1][0] làm self.algorithm.solution để vẽ.
        """
        # Khởi động đo thời gian/bộ nhớ
        self.begin_run()

        # Node gốc (đã có 1 quân tại hàng 0, cột ngẫu nhiên theo make_root_node)
        root = self.make_root_node()
        r0, c0 = root.state[0]
        g0 = self.move_cost(r0, c0)   # chi phí của nước đầu tiên (đã đặt sẵn trong root)
        root.g = g0

        # Log và thống kê ban đầu
        self.update_depth_peak(len(root.state) - 1)
        self.update_frontier_peak(1)
        self.steps.append((root.state, [f"Root at {(r0, c0)} g={g0:.2f}"], [root]))

        # threshold khởi đầu = f(root) = g0 + h(root)
        threshold = g0 + self.heuristic(root.state)
        self.steps.append((root.state, [f"Start IDS* with threshold={threshold:.2f}"], [root]))

        # DFS bị chặn theo f ≤ threshold
        def dfs_idastar(node: Node, g: float, bound: float, path_stack: list[Node]):
            """
            Trả về:
              - (goal_node, goal_g) nếu tìm thấy nghiệm trong bound
              - (None, min_excess) nếu không thấy; min_excess = f nhỏ nhất vượt bound
            """
            # Đếm node đã thăm
            self.metrics["nodes_visited"] += 1

            # Tính f = g + h để kiểm soát ngưỡng
            h = self.heuristic(node.state)
            f = g + h

            # Log thăm node
            self.steps.append((node.state, [f"Visit: g={g:.2f}, h={h:.2f}, f={f:.2f}"], list(path_stack)))

            # Vượt ngưỡng -> trả về f để lần sau nâng threshold tới gần hơn
            if f > bound:
                return None, f

            # Kiểm tra goal (đủ n quân, không xung đột)
            if self.is_goal(node.state):
                return node, g

            min_excess = math.inf

            # Mở rộng
            for action, new_state in self.succ(node.state):
                r_new, c_new = new_state[-1]
                step = self.move_cost(r_new, c_new)
                new_g = g + step

                child = Node(state=new_state, parent=node, action=action)
                child.g = new_g

                path_stack.append(child)
                self.update_frontier_peak(len(path_stack))
                self.update_depth_peak(len(new_state) - 1)
                self.steps.append((new_state, [f"Push: step={step:.2f} → g={new_g:.2f}"], list(path_stack)))

                got, val = dfs_idastar(child, new_g, bound, path_stack)
                if got is not None:
                    return got, val  # Tìm thấy nghiệm

                # Backtrack
                path_stack.pop()
                self.steps.append((node.state, [f"Backtrack to depth={len(node.state)-1}"], list(path_stack)))

                # Lấy f vượt ngưỡng nhỏ nhất
                if val < min_excess:
                    min_excess = val

            return None, min_excess

        # Vòng lặp tăng threshold theo min f vượt ngưỡng
        path_stack = [root]
        goal_node = None
        goal_cost = None

        while True:
            got, next_bound = dfs_idastar(root, g0, threshold, path_stack)
            if got is not None:
                goal_node = got
                goal_cost = next_bound  # tại nghiệm, next_bound chính là g(goal)
                break
            if next_bound == math.inf:
                # Không còn mở rộng được
                self.end_run(solution_node=None)
                return None
            threshold = next_bound
            self.steps.append((root.state, [f"Increase threshold → {threshold:.2f}"], [root]))

        # Kết thúc: ghi metrics và trả về path
        self.end_run(solution_node=goal_node)
        self.metrics["solution_cost"] = float(goal_cost)
        return self.extract_path(goal_node)
