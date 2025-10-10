# algorithms/and_or_search.py
from .base import BaseAlgorithm, Node

class AndOrSearchAlgorithm(BaseAlgorithm):
    """
    AND–OR Search cho Eight Rooks (deterministic, không sensing).
    - OR-node: chọn một hành động (đặt 1 quân ở hàng kế tiếp vào 1 cột hợp lệ).
    - AND-node: tập các kết quả của 1 hành động. Với bài rooks (deterministic),
    - Trả về: path (list[(state, action)]) 
    """

    def set_up_AndOr(self):
        """
        Khởi chạy AND–OR Search từ trạng thái gốc (make_root_node) cho tới khi đủ n quân.
        """
        self.begin_run()

        # Gốc: đặt sẵn 1 quân ngẫu nhiên ở hàng 0
        root = self.make_root_node()
        self.update_frontier_peak(1)
        self.update_depth_peak(len(root.state) - 1)
        self.steps.append((root.state, ["Init AND-OR with root"], [root]))

        # Tập phát hiện vòng lặp theo khóa trạng thái (tuple các cột)
        visited_keys = set()

        # Chạy OR từ gốc
        goal_node = self._or_search(root, visited_keys)

        # Kết thúc
        if goal_node is not None:
            self.end_run(solution_node=goal_node)
            self.solution = goal_node.state
            # Ở đây solution_cost = số quân đã đặt
            self.metrics["solution_cost"] = len(goal_node.state)
            return self.extract_path(goal_node)

        self.end_run(solution_node=None)
        self.solution = None
        return None

    def _state_key(self, state):
        """Khóa vòng lặp: tuple các cột theo thứ tự hàng."""
        return tuple(c for _, c in state)

    def _or_search(self, node: Node, history: set) -> Node | None:
        """
        OR-node: nhận một Node, chọn 1 hành động để đi tiếp.
        Trả về Node lời giải nếu tìm được, None nếu thất bại.
        """
        self.metrics["nodes_visited"] += 1

        # Log pop OR
        self.steps.append((node.state, [f"OR: visit {node.state}"], []))

        # Đạt mục tiêu
        if self.is_goal(node.state):
            return node

        key = self._state_key(node.state)
        if key in history:
            # vòng lặp → thất bại nhánh này
            self.steps.append((node.state, [f"OR: loop detected → backtrack"], []))
            return None

        # Thêm vào history
        history.add(key)

        # Thử các hành động kế tiếp (đặt quân ở hàng kế)
        for action, new_state in self.succ(node.state):
            child = Node(state=new_state, parent=node, action=action)

            # Log push
            self.update_depth_peak(len(new_state) - 1)
            self.steps.append((new_state, [f"Try action: {action}"], [child]))

            # AND-node: trong deterministic rooks, hành động này có đúng 1 kết quả là new_state
            plan_node = self._and_search([child], history)
            if plan_node is not None:
                return plan_node  # tìm được nghiệm theo nhánh này

        # Tháo khỏi history khi backtrack
        history.remove(key)
        self.steps.append((node.state, [f"OR: all actions failed → backtrack"], []))
        return None

    def _and_search(self, children: list[Node], history: set) -> Node | None:
        """
        AND-node: yêu cầu TẤT CẢ kết quả của một hành động phải thành công.
        Với rooks (deterministic), chỉ có 1 child → chỉ cần OR trên child đó.
        Để giữ cấu trúc chuẩn, code vẫn hỗ trợ nhiều child nếu bạn mở rộng.
        """
        # Nếu rỗng → trivially success (không xảy ra ở đây)
        if not children:
            return None

        # Với rooks: chỉ 1 child
        if len(children) == 1:
            return self._or_search(children[0], history)

        # Nếu sau này có sensing sinh ra nhiều child:
        last_solution = None
        for ch in children:
            sol = self._or_search(ch, history)
            if sol is None:
                return None  # chỉ cần 1 thất bại → AND thất bại
            last_solution = sol
        return last_solution
