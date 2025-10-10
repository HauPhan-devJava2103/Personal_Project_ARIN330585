import random
from copy import deepcopy
from collections import deque
from .base import BaseAlgorithm, Node

class PartiallyObservableSearchAlgorithm(BaseAlgorithm):
    '''
    Belief State Search cho 8 quân xe ở môi trường qs 1 phần
    Belief = domains: list[ set[int] ] — miền cột có thể cho từng hàng
    Cung cấp hidden_solution (list[int] độ dài n), ta có "sensor" để quan sát:
        observe_equal(r, c) -> True/False
    '''

    def __init__(self,n=8, hidden_solution = None, shuffle_values = True, use_mrv = True):
        super().__init__(n=n)
        self.hidden_solution = hidden_solution      # list[int] | None
        self.shuffle_values = shuffle_values        # xáo trộn thứ tự thử cột
        self.use_mrv = use_mrv                      # chọn biến bằng MRV

    # Tạo Belief ban đầu
    def _init_domains(self):
        return [set(range(self.n)) for _ in range(self.n)]
    
    def _apply_commits(self, domains, state):
        """Khóa các hàng đã gán và loại nhanh cột đã dùng khỏi hàng chưa gán."""
        assigned = {r: c for (r, c) in state}
        used = set(assigned.values())
        for r in range(self.n):
            if r in assigned:
                domains[r] = {assigned[r]}
            elif len(domains[r]) > 1:
                domains[r] -= used

    # ===== Sensor =====
    def _observe_equal(self, row, col):
        """Nếu có đáp án ẩn, trả True/False; nếu không, trả None (không quan sát được)."""
        if self.hidden_solution is None:
            return None
        return int(self.hidden_solution[row]) == int(col)

    def _select_row(self, state, domains):
            assigned_rows = {r for r, _ in state}
            if self.use_mrv:
                best_row, best_size = None, float("inf")
                for r in range(self.n):
                    if r in assigned_rows:
                        continue
                    size = len(domains[r])
                    if size < best_size:
                        best_size, best_row = size, r
                return best_row
            else:
                # hàng đầu tiên chưa gán
                for r in range(self.n):
                    if r not in assigned_rows:
                        return r
                return None

    def _forward_check(self, domains, row, col):
        """
        Tạo bản sao miền; khóa row={col}, xóa 'col' khỏi hàng khác.
        Trả về new_domains hoặc None nếu sinh miền rỗng.
        """
        new_domains = deepcopy(domains)
        new_domains[row] = {col}
        for r in range(self.n):
            if r == row:
                continue
            if len(new_domains[r]) > 1 and col in new_domains[r]:
                new_domains[r].remove(col)
                if not new_domains[r]:
                    return None
        return new_domains
    
    def set_up_PartialDFS(self, max_sense_per_row=2):
            """
            DFS trên belief:
            - Nếu có sensor: trước khi gán row=col, hỏi observe_equal(row,col).
            - Nếu sensor trả False, bỏ giá trị; True thì gán và đi sâu.
            - Nếu không sensor: thử tất cả giá trị trong miền theo DFS.
            """
            self.begin_run()

            root = Node(state=[], parent=None, action="Start (empty)")
            self.update_depth_peak(-1)
            self.update_frontier_peak(1)
            self.steps.append((root.state, ["Init PO-DFS (no AC-3)"], [root]))

            # Miền ban đầu + áp state
            domains0 = self._init_domains()
            self._apply_commits(domains0, root.state)

            solution_node = None
            stack_nodes = [root]

            def dfs(parent_node, domains):
                nonlocal solution_node, stack_nodes
                if solution_node is not None:
                    return True

                # Goal
                if len(parent_node.state) == self.n:
                    solution_node = parent_node
                    return True

                # chọn hàng
                row = self._select_row(parent_node.state, domains)
                if row is None:
                    return False

                values = list(domains[row])
                if self.shuffle_values:
                    random.shuffle(values)
                else:
                    values.sort()

                sensed = 0
                for col in values:
                    # Nếu có sensor, hỏi trước
                    ans = None
                    if self.hidden_solution is not None and sensed < max_sense_per_row:
                        ans = self._observe_equal(row, col)
                        sensed += 1
                        if ans is False:
                            # log: bị loại bởi quan sát
                            self.steps.append((parent_node.state, [f"SENSE: row {row} == {col} → False (prune)"], list(stack_nodes)))
                            continue
                        elif ans is True:
                            self.steps.append((parent_node.state, [f"SENSE: row {row} == {col} → True"], list(stack_nodes)))

                    # Forward-check tối thiểu
                    new_domains = self._forward_check(domains, row, col)
                    if new_domains is None:
                        # miền rỗng sau khi gán → prune
                        self.steps.append((parent_node.state, [f"FC prune ({row},{col})"], list(stack_nodes)))
                        continue

                    # Tạo child & đi sâu
                    new_state = list(parent_node.state) + [(row, col)]
                    child = Node(state=new_state, parent=parent_node, action=f"Assign ({row},{col})")
                    stack_nodes.append(child)
                    self.metrics["nodes_visited"] += 1
                    self.update_depth_peak(len(new_state) - 1)
                    self.update_frontier_peak(len(stack_nodes))
                    self.steps.append((new_state, [f"Push: ({row},{col})"], list(stack_nodes)))

                    if dfs(child, new_domains):
                        return True

                    # Quay lui
                    stack_nodes.pop()
                    self.steps.append((parent_node.state, [f"Backtrack from ({row},{col})"], list(stack_nodes)))

                return False

            found = dfs(root, domains0)

            if found and solution_node is not None:
                self.end_run(solution_node=solution_node)
                self.solution = solution_node.state
                return self.extract_path(solution_node)

            self.end_run(solution_node=None)
            self.solution = None
            return None