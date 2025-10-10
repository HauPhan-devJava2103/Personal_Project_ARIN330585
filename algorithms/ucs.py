import heapq
import itertools
from .base import BaseAlgorithm, Node

class UCSAlgorithm(BaseAlgorithm):

    def set_up_UCS(self):
        # Bắt đầu đo thời gian + tracemalloc
        self.begin_run()

        counter = itertools.count()           # tie-breaker để heap ổn định
        open_heap = []                        # mỗi phần tử: (g_cost, tie, Node)

        # Root: đã có 1 quân ở hàng 0 (do make_root_node())
        root = self.make_root_node()
        r0, c0 = root.state[0]
        g0 = self.move_cost(r0, c0)           # TÍNH COST cho quân đầu
        root.g = g0
        heapq.heappush(open_heap, (g0, next(counter), root))

        self.update_frontier_peak(len(open_heap))
        self.update_depth_peak(len(root.state) - 1)
        self.steps.append(
            (root.state, [f"Push root g={g0:.2f} at {(r0, c0)}"],
             [t[2] for t in open_heap])
        )

        # best_cost: g tốt nhất đã thấy cho một "mẫu cột"
        best_cost = {}  # key = tuple(cols), value = g

        while open_heap:
            g, _, n = heapq.heappop(open_heap)
            self.metrics["nodes_visited"] += 1

            if not hasattr(n, "g"):
                n.g = g

            self.steps.append(
                (n.state, [f"Popped g={g:.2f}: {n.state}"],
                 [t[2] for t in open_heap])
            )

            cols_key = tuple(c for _, c in n.state)
            # Nếu đã có đường rẻ hơn tới cùng trạng thái -> bỏ qua
            if cols_key in best_cost and g > best_cost[cols_key]:
                continue
            best_cost[cols_key] = g

            # Goal?
            if self.is_goal(n.state):
                self.end_run(solution_node=n)
                self.metrics["solution_cost"] = g
                return self.extract_path(n)

            # Mở rộng: đặt thêm 1 quân ở hàng tiếp theo
            for action, new_state in self.succ(n.state):
                r_new, c_new = new_state[-1]          # nước mới vừa thêm
                step_cost = self.move_cost(r_new, c_new)
                new_g = g + step_cost

                new_node = Node(state=new_state, parent=n, action=action)
                new_node.g = new_g

                heapq.heappush(open_heap, (new_g, next(counter), new_node))
                self.update_frontier_peak(len(open_heap))
                self.update_depth_peak(len(new_state) - 1)

                self.steps.append(
                    (new_state,
                     [f"Pushed g={new_g:.2f} (step={step_cost:.2f}) at {(r_new, c_new)}"],
                     [t[2] for t in open_heap])
                )

        # Không tìm thấy nghiệm
        self.end_run(solution_node=None)
        return None