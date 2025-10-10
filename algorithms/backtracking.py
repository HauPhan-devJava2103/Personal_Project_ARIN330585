from .base import BaseAlgorithm, Node

class BacktrackingAlgorithm(BaseAlgorithm):
    """
    Backtracking cho Eight Rooks:
    - Ở mỗi hàng, thử lần lượt các cột CHƯA dùng; nếu đi vào ngõ cụt thì quay lui.
    """

    def set_up_Backtracking(self):
        """
        metrics:
          - nodes_visited: số nút được thăm (mỗi lần đặt thử 1 quân).
          - max_depth: độ sâu lớn nhất (len(state)-1).
          - max_frontier: kỷ lục chiều dài ngăn xếp đệ quy (stack).
          - solution_depth: cập nhật khi gặp nghiệm.
        """
        self.begin_run()

        root = self.make_root_node()
        stack_nodes = [root]  # dùng để chụp snapshot frontier
        self.update_depth_peak(-1)            # depth = len(state)-1, rỗng ⇒ -1
        self.update_frontier_peak(len(stack_nodes))
        self.steps.append((root.state, ["Init backtracking"], list(stack_nodes)))

        solution_node = None

        def backtrack(parent: Node):
            nonlocal solution_node, stack_nodes
            # Nếu đã có lời giải thì dừng (để lấy NGHIỆM ĐẦU TIÊN)
            if solution_node is not None:
                return True

            row = len(parent.state)
            # Kiểm tra Goal
            if row == self.n:
                solution_node = parent
                return True

            # Tập cột đã dùng
            used_cols = {c for _, c in parent.state}

            # Thử từng cột chưa dùng cho hàng 'row'
            for col in range(self.n):
                if col in used_cols:
                    continue

                # Tạo state mới
                new_state = parent.state + [(row, col)]
                action = f"Place rook at ({row}, {col})"
                child = Node(state=new_state, parent=parent, action=action)

                # Log/push
                stack_nodes.append(child)
                self.metrics["nodes_visited"] += 1
                self.update_depth_peak(len(new_state) - 1)
                self.update_frontier_peak(len(stack_nodes))
                self.steps.append((new_state, [f"Push: {action}"], list(stack_nodes)))

                # Tiến sâu
                if backtrack(child):
                    return True

                # Quay lui
                stack_nodes.pop()
                self.steps.append((parent.state, [f"Backtrack from ({row}, {col})"], list(stack_nodes)))

            # Không có cột hợp lệ → ngõ cụt
            return False

        # Chạy
        found = backtrack(root)

        if found and solution_node is not None:
            self.end_run(solution_node=solution_node)
            self.solution = solution_node.state
            return self.extract_path(solution_node)

        # Không tìm thấy 
        self.end_run(solution_node=None)
        self.solution = None
        return None
