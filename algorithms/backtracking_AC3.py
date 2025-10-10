# algorithms/backtracking_ac3.py
import random
from copy import deepcopy
from collections import deque
from .base import BaseAlgorithm, Node

class BacktrackingAC3Algorithm(BaseAlgorithm):
    """
    Backtracking + AC-3 (MAC) cho Eight Rooks:
    - Biến: mỗi hàng (row) phải gán một cột (0..n-1).
    - Ràng buộc: All-Different theo cột => Xi != Xj.
    - Khi gán row->col, chạy AC-3 để duy trì arc consistency rồi mới đệ quy.
    - Tuỳ chọn: MRV (chọn hàng có miền nhỏ nhất), shuffle cột để kiểm thử.
    """

    # Thiết lập
    def _init_domains(self):
        """Ban đầu, mỗi hàng có thể dùng mọi cột."""
        return [set(range(self.n)) for _ in range(self.n)]

    def _apply_state_to_domains(self, domains, state):
        """
        Áp trạng thái hiện có vào miền:
        - Nếu row đã gán col trong state: khóa domains[row] = {col}
        """
        assigned = {r: c for (r, c) in state}
        for r in range(self.n):
            if r in assigned:
                domains[r] = {assigned[r]}
        used_cols = set(assigned.values())
        for r in range(self.n):
            if len(domains[r]) > 1:  # chưa gán
                domains[r] -= used_cols

    # AC3
    def _ac3(self, domains):
        """
        AC-3 cơ bản cho ràng buộc Xi != Xj trên mọi cặp (i,j), i!=j.
        Trả về True nếu arc-consistent; False nếu có miền rỗng.
        """
        q = deque((i, j) for i in range(self.n) for j in range(self.n) if i != j)

        while q:
            xi, xj = q.popleft()
            if self._revise(domains, xi, xj):
                if not domains[xi]:
                    return False
                # Nếu xi đổi miền, cần xét lại các cung (xk, xi) với k ≠ xj
                for xk in range(self.n):
                    if xk != xi and xk != xj:
                        q.append((xk, xi))
        return True

    def _revise(self, domains, xi, xj):
        """
        REVISION cho Xi != Xj:
        - Nếu D(Xj) là singleton {v}, thì xoá v khỏi D(Xi).
        - Nếu D(Xj) có >=2 giá trị, luôn có hỗ trợ khác v => không xoá gì.
        """
        di = domains[xi]
        dj = domains[xj]
        if len(dj) != 1:
            return False

        vj = next(iter(dj))
        if vj in di:
            di.remove(vj)
            return True
        return False

    # Chọn biến
    def _select_row(self, state, domains, use_mrv=True):
        """
        Trả về index hàng chưa gán:
        - MRV: hàng có miền nhỏ nhất.
        - Nếu không MRV: hàng đầu tiên chưa gán (len(state)).
        """
        assigned_rows = {r for r, _ in state}
        if not use_mrv:
            for r in range(self.n):
                if r not in assigned_rows:
                    return r

        best_row, best_size = None, float("inf")
        for r in range(self.n):
            if r in assigned_rows:
                continue
            size = len(domains[r])
            if size < best_size:
                best_size, best_row = size, r
        return best_row

    # ================== Thuật toán chính ==================
    def set_up_BacktrackingAC3(self, use_mrv=True, shuffle_cols=False):
        """
        Backtracking + AC-3:
        - Khởi tạo miền từ trạng thái rỗng; (có thể thay bằng state gốc nếu muốn).
        - Mỗi bước: chọn hàng chưa gán (MRV), thử từng cột trong miền;
          gán tạm row={col}, chạy AC-3; nếu miền còn arc-consistent thì đệ quy.
        """
        self.begin_run()

        # Bắt đầu từ trạng thái rỗng để AC-3 phát huy tác dụng ngay từ đầu.
        root = Node(state=[], parent=None, action="Start (empty)")
        stack_nodes = [root]
        path = [(root.state, "Start")]

        # Miền khởi đầu + áp state (rỗng)
        domains = self._init_domains()
        self._apply_state_to_domains(domains, root.state)

        # Log init
        self.update_depth_peak(-1)
        self.update_frontier_peak(len(stack_nodes))
        self.steps.append((root.state, ["Init BT+AC3"], list(stack_nodes)))

        solution_node = None

        def bt_ac3(parent_node, domains):
            nonlocal solution_node, stack_nodes, path

            # Nếu đã có nghiệm ở nhánh khác
            if solution_node is not None:
                return True

            # Goal?
            if len(parent_node.state) == self.n:
                solution_node = parent_node
                return True

            # Chọn hàng để gán
            row = self._select_row(parent_node.state, domains, use_mrv=use_mrv)
            if row is None:
                return False  # phòng thủ

            # Thứ tự giá trị trong miền
            cols = list(domains[row])
            if shuffle_cols:
                random.shuffle(cols)
            else:
                cols.sort()

            for col in cols:
                # Tạo child + miền mới
                new_state = list(parent_node.state) + [(row, col)]
                child = Node(state=new_state, parent=parent_node, action=f"Place ({row},{col})")

                new_domains = deepcopy(domains)
                # Khoá row = {col}
                new_domains[row] = {col}

                # Loại nhanh col khỏi các hàng chưa gán
                for r in range(self.n):
                    if r == row:
                        continue
                    if len(new_domains[r]) > 1 and col in new_domains[r]:
                        new_domains[r].remove(col)

                # Chạy AC-3
                ac_ok = self._ac3(new_domains)

                # Log & tiếp tục
                if ac_ok:
                    stack_nodes.append(child)
                    self.metrics["nodes_visited"] += 1
                    self.update_depth_peak(len(child.state) - 1)
                    self.update_frontier_peak(len(stack_nodes))
                    self.steps.append((child.state, [f"Push ({row},{col}) | AC-3 OK"], list(stack_nodes)))
                    path.append((child.state, f"Assign ({row},{col})"))

                    if bt_ac3(child, new_domains):
                        return True

                    # Quay lui
                    stack_nodes.pop()
                    self.steps.append((parent_node.state, [f"Backtrack from ({row},{col})"], list(stack_nodes)))
                else:
                    self.steps.append((parent_node.state, [f"AC-3 prunes ({row},{col})"], list(stack_nodes)))

            return False

        found = bt_ac3(root, domains)

        if found and solution_node is not None:
            self.end_run(solution_node=solution_node)
            self.solution = solution_node.state
            return self.extract_path(solution_node)

        self.end_run(solution_node=None)
        self.solution = None
        return None
