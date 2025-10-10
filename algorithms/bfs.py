from collections import deque
from .base import BaseAlgorithm, Node

class BFSAlgorithm(BaseAlgorithm):
    def set_up_BFS(self):
        
        self.begin_run()
        open_queue = deque()
        root = self.make_root_node()
        open_queue.append(root)

        self.update_frontier_peak(len(open_queue))
        self.update_depth_peak(len(root.state) - 1)
        self.steps.append((root.state, [root.action], list(open_queue)))

        while open_queue:
            
            n = open_queue.popleft()
            self.metrics["nodes_visited"] += 1
            self.steps.append((n.state, [f"Dequeued state: {n.state}"], list(open_queue)))

            if self.is_goal(n.state):
                self.end_run(solution_node=n)
                return self.extract_path(n)

            for action, new_state in self.succ(n.state):
                new_node = Node(state=new_state, parent=n, action=action)
                open_queue.append(new_node)
                self.update_frontier_peak(len(open_queue))
                self.update_depth_peak(len(new_state) - 1)
                self.steps.append((new_node.state, [f"Enqueued state: {new_state}"], list(open_queue)))

        self.end_run(solution_node=None)
        return None
