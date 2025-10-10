# algorithms/no_observation_belief_dfs.py
from copy import deepcopy
import random
from .base import BaseAlgorithm, Node

class NoObservationSearchWithBeliefDFS(BaseAlgorithm):
    """
    DFS (backtracking) cho Eight Rooks trong chế độ No-Observation:
    - Belief = domains[r] ⊆ {0..n-1} (miền cột có thể cho từng hàng).
    - Không sensor; chỉ thu hẹp miền theo hành động gán + ràng buộc all-different.
    - Forward-checking tối thiểu: gán row=col → xóa col khỏi miền các hàng còn lại.
    - Tùy chọn: MRV (chọn hàng có miền nhỏ nhất) và shuffle thứ tự giá trị.
    - steps chỉ chứa state đã CHỐT (không có None) để tránh ảnh hưởng các thuật toán khác/GUI.
    """

    # ---------- BELIEF / DOMAINS ----------
    def _init_domains(self):
        """Ban đầu, mỗi hàng có thể dùng tất cả các cột."""
        return [set(range(self.n)) for _ in range(self.n)]

    def _apply_state_to_domains(self, domains, state):
        """
        - domains[row] = {col} nếu (row,col) đã chốt
        - Xóa nhanh các cột đã dùng khỏi miền các hàng chưa gán
        """
        assigned = {r: c for (r, c) in state}
        used = set(assigned.values())
        for r in range(self.n):
            if r in assigned:
                domains[r] = {assigned[r]}
            elif len(domains[r]) > 1:
                domains[r] -= used

    def _forward_assign(self, domains, row, col):
        """
        Tạo miền
        - domains'[row] = {col}
        - xóa col khỏi miền các hàng khác
        - nếu có miền rỗng → None (prune)
        """
        nd = deepcopy(domains)
        nd[row] = {col}
        for r in range(self.n):
            if r == row:
                continue
            if len(nd[r]) > 1 and col in nd[r]:
                nd[r].remove(col)
                if not nd[r]:
                    return None
        return nd

    # Chọn biến
    def _select_row(self, state, domains, use_mrv=True):
        """
        Trả về hàng chưa gán:
        - use_mrv=True: hàng có miền nhỏ nhất (MRV)
        - use_mrv=False: hàng đầu tiên chưa gán
        """
        assigned = {r for r, _ in state}
        if use_mrv:
            best_row, best_sz = None, float("inf")
            for r in range(self.n):
                if r in assigned:
                    continue
                sz = len(domains[r])
                if sz < best_sz:
                    best_sz, best_row = sz, r
            return best_row
        else:
            for r in range(self.n):
                if r not in assigned:
                    return r
            return None

    def _committed_only(self, domains):
        """Trích các (row,col) đã đơn trị để vẽ lên canvas (không có None)."""
        out = []
        for r in range(self.n):
            if len(domains[r]) == 1:
                out.append((r, next(iter(domains[r]))))
        return out

    def _belief_str(self, domains):
        """Chuỗi tóm tắt miền cho message (actions)."""
        parts = []
        for r in range(self.n):
            s = sorted(domains[r])
            if len(s) == 1:
                parts.append(f"{r}:{{{s[0]}}}")
            else:
                parts.append(f"{r}:{{{','.join(map(str, s))}}}")
        return " | ".join(parts)

    def set_up_NoObsBeliefDFS(self, use_mrv=True, shuffle_values=True, seed=None):
        """
        - use_mrv: dùng MRV chọn biến
        - shuffle_values: xáo trộn thứ tự thử cột
        - seed: cố định RNG (tuỳ chọn)
        """
        if seed is not None:
            random.seed(seed)

        self.begin_run()

        # Gốc rỗng
        root = Node(state=[], parent=None, action="Start (empty)")
        domains0 = self._init_domains()
        self._apply_state_to_domains(domains0, root.state)

        # Log init
        self.update_frontier_peak(1)
        self.update_depth_peak(-1)
        init_msg = "Init No-Obs Belief DFS\n" + self._belief_str(domains0)
        self.steps.append((self._committed_only(domains0), [init_msg], [root]))

        solution_node = None
        stack_nodes = [root]

        def dfs(parent, domains):
            nonlocal solution_node, stack_nodes
            if solution_node is not None:
                return True

            # Goal: mọi hàng đã gán
            if len(parent.state) == self.n:
                solution_node = parent
                return True

            # Chọn hàng
            row = self._select_row(parent.state, domains, use_mrv=use_mrv)
            if row is None:
                return False

            # Giá trị (cột) trong miền
            values = list(domains[row])
            if shuffle_values:
                random.shuffle(values)
            else:
                values.sort()

            for col in values:
                # forward-check
                nd = self._forward_assign(domains, row, col)
                if nd is None:
                    # prune
                    msg = f"FC prune ({row},{col})\n" + self._belief_str(domains)
                    self.steps.append((self._committed_only(domains), [msg], list(stack_nodes)))
                    continue

                # child
                new_state = list(parent.state) + [(row, col)]
                child = Node(state=new_state, parent=parent, action=f"Assign ({row},{col})")

                # log + metrics
                stack_nodes.append(child)
                self.metrics["nodes_visited"] += 1
                self.update_depth_peak(len(new_state) - 1)
                self.update_frontier_peak(len(stack_nodes))
                msg = f"Push: ({row},{col})\n" + self._belief_str(nd)
                self.steps.append((self._committed_only(nd), [msg], list(stack_nodes)))

                # đi sâu
                if dfs(child, nd):
                    return True

                # backtrack
                stack_nodes.pop()
                msg = f"Backtrack from ({row},{col})\n" + self._belief_str(domains)
                self.steps.append((self._committed_only(domains), [msg], list(stack_nodes)))

            return False

        # Chạy DFS
        found = dfs(root, domains0)

        # Kết thúc
        if found and solution_node is not None:
            self.end_run(solution_node=solution_node)
            self.solution = solution_node.state
            self.metrics["solution_cost"] = len(solution_node.state)
            return self.extract_path(solution_node)

        self.end_run(solution_node=None)
        self.solution = None
        return None
