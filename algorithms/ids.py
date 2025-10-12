# algorithms/ids.py
from .base import BaseAlgorithm, Node

class IDSAlgorithm(BaseAlgorithm):
    """
    IDDFS (Iterative Deepening DFS) cho Eight Rooks.
    Hiển thị được trên giao diện (GUI) vì có self.steps tương tự BFS.
    """

    def set_up_IDS(self, max_depth=None):
        if max_depth is None:
            max_depth = self.n - 1

        self.begin_run()

        # Gốc: bắt đầu từ hàng 0, không ngẫu nhiên
        root = self.make_root_node()
        self.update_frontier_peak(1)
        self.update_depth_peak(len(root.state) - 1)
        self.steps.append((root.state, ["Init root"], [root]))

        for limit in range(0, max_depth + 1):
            # Log vòng lặp mới
            self.steps.append((root.state, [f"=== Depth limit = {limit} ==="], [root]))
            found = self._dls(root, limit)
            if found is not None:
                self.end_run(solution_node=found)
                self.metrics["solution_cost"] = len(found.state)
                return self.extract_path(found)

        self.end_run(solution_node=None)
        return None

    def _dls(self, node: Node, limit: int):
        """Hàm DLS: đệ quy theo chiều sâu có chặn."""
        self.metrics["nodes_visited"] += 1
        self.steps.append((node.state, [f"Visit depth={len(node.state)-1}, limit={limit}"], [node]))

        if self.is_goal(node.state):
            self.steps.append((node.state, [f"Goal found! {node.state}"], [node]))
            return node

        if limit == 0:
            self.steps.append((node.state, [f"Limit reached at {node.state}"], [node]))
            return None

        for action, new_state in self.succ(node.state):
            child = Node(state=new_state, parent=node, action=action)
            self.update_depth_peak(len(new_state) - 1)
            self.steps.append((new_state, [f"Push {action}"], [child]))
            got = self._dls(child, limit - 1)
            if got is not None:
                return got
            self.steps.append((node.state, [f"Backtrack from {new_state}"], [node]))

        return None
