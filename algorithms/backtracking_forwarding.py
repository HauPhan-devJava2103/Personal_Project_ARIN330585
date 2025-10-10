# algorithms/backtracking_forward_simple.py
import random
from copy import deepcopy
from .base import BaseAlgorithm, Node

class BacktrackingForwardAlgorithm(BaseAlgorithm):
    """
    Backtracking + Forward Checking TỐI THIỂU:
    - Khi gán row→col: xoá col khỏi miền các hàng còn lại.
    - Nếu miền nào trống → quay lui ngay.
    """

    def set_up_BacktrackingFC(self, shuffle_cols: bool = False):
        self.begin_run()

        root = Node(state=[], parent=None, action="Start (empty)")
        stack_nodes = [root]

        # Miền khởi đầu: hàng nào cũng có thể chọn mọi cột
        domains = [set(range(self.n)) for _ in range(self.n)]

        # Log init
        self.update_depth_peak(-1)
        self.update_frontier_peak(len(stack_nodes))
        self.steps.append((root.state, ["Init BT+FC (simple)"], list(stack_nodes)))

        solution_node = None
        path = [(root.state, "Start")]

        def assign_and_propagate_simple(state, parent_node, domains, row, col):
            """
            Gán row→col, forward-check: xoá col khỏi miền các hàng sau.
            Nếu BẤT KỲ miền nào trống → thất bại ngay.
            """
            new_state = list(state) + [(row, col)]
            child = Node(state=new_state, parent=parent_node, action=f"Place ({row},{col})")

            new_domains = deepcopy(domains)
            # khoá hàng hiện tại = {col}
            new_domains[row] = {col}

            # FC: xoá col khỏi miền các hàng CHƯA gán
            for r in range(row + 1, self.n):
                if col in new_domains[r]:
                    new_domains[r].remove(col)

            # CHỈ kiểm tra miền trống (minimal forward check)
            for r in range(len(new_state), self.n):
                if not new_domains[r]:      # miền rỗng ⇒ ngõ cụt
                    return None, None

            return child, new_domains

        def btfc_simple(parent_node, domains):
            nonlocal solution_node, stack_nodes, path

            if solution_node is not None:
                return True

            row = len(parent_node.state)
            # Goal
            if row == self.n:
                solution_node = parent_node
                return True

            # Hàng kế tiếp ⇒ thử các cột trong miền (có thể xáo trộn cho ngẫu nhiên)
            cols = list(domains[row])
            if shuffle_cols:
                random.shuffle(cols)
            else:
                cols.sort()

            for col in cols:
                child, new_domains = assign_and_propagate_simple(parent_node.state, parent_node, domains, row, col)
                if child is None:
                    # bị FC cắt ngay
                    self.steps.append((parent_node.state, [f"FC prunes ({row},{col})"], list(stack_nodes)))
                    continue

                # push + log
                stack_nodes.append(child)
                self.metrics["nodes_visited"] += 1
                self.update_depth_peak(len(child.state) - 1)
                self.update_frontier_peak(len(stack_nodes))
                self.steps.append((child.state, [f"Push: ({row},{col})"], list(stack_nodes)))
                path.append((child.state, f"Assign ({row},{col})"))

                # đi sâu
                if btfc_simple(child, new_domains):
                    return True

                # quay lui
                stack_nodes.pop()
                self.steps.append((parent_node.state, [f"Backtrack from ({row},{col})"], list(stack_nodes)))

            return False

        found = btfc_simple(root, domains)

        if found and solution_node is not None:
            self.end_run(solution_node=solution_node)
            self.solution = solution_node.state
            return self.extract_path(solution_node)

        self.end_run(solution_node=None)
        self.solution = None
        return None
