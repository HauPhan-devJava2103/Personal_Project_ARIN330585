from collections import deque
from .base import BaseAlgorithm, Node

class DFSAlgorithm(BaseAlgorithm):
    def set_up_DFS(self):
        '''DFS - duyệt theo chiều sâu bằng Stack (LIFO)'''

        # Khởi động bộ đếm
        self.begin_run()

        # Khởi tạo stack và node gốc
        root = self.make_root_node()
        stack = deque([root])

        # Thống kê bước đầu
        self.update_frontier_peak(len(stack)) 
        self.update_depth_peak(len(root.state) - 1)         # độ sâu hiện tại
        self.steps.append((root.state, [root.action], list(stack)))

        while stack:
            node = stack.pop()
            self.metrics["nodes_visited"] += 1
            self.steps.append((node.state,                  # log: vừa POP
                               [f"Popped state: {node.state}"],list(stack)))
            
            # Kiểm tra mục tiêu
            if self.is_goal(node.state):
                self.end_run(solution_node=node)            # dừng đo & ghi depth nghiệm
                return self.extract_path(node)

            for action, new_state in self.succ(node.state):
                child = Node(state=new_state, parent=node, action=action)
                stack.append(child)

                self.update_frontier_peak(len(stack))
                self.update_depth_peak(len(new_state) - 1)
                self.steps.append((new_state,
                                   [f"Pushed state: {new_state}"],
                                   list(stack)))
                
        # 5) Không tìm thấy nghiệm
        self.end_run(solution_node=None)
        return None