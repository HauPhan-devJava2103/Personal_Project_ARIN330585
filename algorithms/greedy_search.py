# algorithms/greedy.py
import heapq
import itertools
from .base import BaseAlgorithm, Node

class GreedyBestFirstAlgorithm(BaseAlgorithm):
    """Greedy Best-First: chọn node có h(state) nhỏ nhất để mở rộng."""

    # Heuristic: tổng k cột rẻ nhất còn trống (admissible)
    def heuristic(self, state) -> float:
        k = self.n - len(state)
        if k <= 0:
            return 0.0
        used = {c for _, c in state}
        r = len(state)
        costs = [self.move_cost(r, c) for c in range(self.n) if c not in used]
        costs.sort()
        return float(sum(costs[:k]))

    def _key(self, state):
        # khóa để chống lặp: tuple các cột theo thứ tự hàng
        return tuple(c for _, c in state)

    def set_up_Greedy(self):
        """Chạy Greedy Best-First, ưu tiên h nhỏ nhất (min-heap theo h)."""
        self.begin_run()

        # 1) root
        root = self.make_root_node()
        root.g = self.move_cost(*root.state[0])
        h0 = self.heuristic(root.state)

        # 2) hàng đợi ưu tiên theo h
        counter = itertools.count()           # tie-breaker ổn định
        open_heap = []                        # (h, tie, Node)
        heapq.heappush(open_heap, (h0, next(counter), root))

        visited = set()

        # log/metrics
        self.update_frontier_peak(1)
        self.update_depth_peak(len(root.state) - 1)
        self.steps.append((root.state, [f"Push root: h={h0:.2f}"], [root]))

        # 3) vòng lặp Greedy
        while open_heap:
            hcur, _, node = heapq.heappop(open_heap)
            self.metrics["nodes_visited"] += 1

            key = self._key(node.state)
            if key in visited:
                continue
            visited.add(key)

            self.steps.append((node.state, [f"Pop: h={hcur:.2f}"], [t[2] for t in open_heap]))

            if self.is_goal(node.state):
                self.end_run(solution_node=node)
                self.metrics["solution_cost"] = float(getattr(node, "g", 0.0))
                return self.extract_path(node)

            for action, new_state in self.succ(node.state):
                r_new, c_new = new_state[-1]
                step = self.move_cost(r_new, c_new)

                child = Node(state=new_state, parent=node, action=action)
                child.g = getattr(node, "g", 0.0) + step
                h_new = self.heuristic(new_state)

                heapq.heappush(open_heap, (h_new, next(counter), child))

                self.update_frontier_peak(len(open_heap))
                self.update_depth_peak(len(new_state) - 1)
                self.steps.append(
                    (new_state, [f"Push: h={h_new:.2f}"], [t[2] for t in open_heap])
                )

        self.end_run(solution_node=None)
        return None
