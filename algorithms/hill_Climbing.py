import random
from .base import BaseAlgorithm, Node

class HillClimbingAlgorithm(BaseAlgorithm):

    '''
    Trạng thái ban đầu: list[(row, col)] mỗi hàng 1 quân có thể trùng cột
    Fitness: số cột khác nhau(0..n)
    Láng giềng: đổi cột sang một cột khác. nếu tốt thì nhảy sang
    '''
    
    # Hill-Climbing
    def set_up_HC(self, max_iterations = 200):
        '''
        1. Trạng thái ban đầu ngẫu nhiên
        2. Sinh ra các trạng thái láng giềng -> chọn láng giềng tốt nhất
        3. Nếu tốt nhảy
        '''

        self.begin_run()

        current = self.random_initial_state()
        current_fit = self.fitness(current)
        path = [(current, "Start with random full state")]

        root_node = Node(state=current, action="Start")
        self.steps.append((current, [f"Start fitness = {current_fit}"], [root_node]))
        self.update_frontier_peak(1)
        self.update_depth_peak(self.n - 1)

        # Kiểm tra đạt nghiệm
        if self.is_goal_full(current):
            self.end_run(solution_node=root_node)
            self.metrics["solution_cost"] = 0
            self.solution = current
            return path

        # -- 2) vòng lặp cải thiện --
        for it in range(1, max_iterations + 1):
            neighbors = self.generate_neighbors(current)
            frontier_nodes = [Node(state=s, action=a) for (a, s) in neighbors]
            self.update_frontier_peak(len(frontier_nodes))

            # Đánh giá các láng giềng
            best_idx = None
            best_fit = current_fit
            for i, (_,s) in enumerate(neighbors):
                f = self.fitness(s)
                self.metrics["nodes_visited"] += 1
                if f > best_fit:
                    best_fit = f
                    best_idx = i

            self.steps.append(
                (current, [f"Iter {it}: fitness={current_fit}, neighbors={len(neighbors)}"],
                 frontier_nodes)
            )

            # Không láng giềng nào phù hợp
            if best_idx is None:
                self.steps.append(
                    (current, [f"No better neighbor. Converged at fitness={current_fit}"], [])
                )
                break
            # Di chuyển sang láng giềng tốt
            best_action, best_state = neighbors[best_idx]
            current = best_state
            current_fit = best_fit
            path.append((current, f"{best_action} (fitness→{current_fit})"))
            self.steps.append(
                (current, [f"Move: {best_action} → fitness={current_fit}"], [Node(state=current)])
            )

            # đạt nghiệm?
            if self.is_goal_full(current):
                sol_node = Node(state=current, action="Goal")
                self.end_run(solution_node=sol_node)
                self.metrics["solution_cost"] = len(path) - 1  # số lần cải thiện
                self.solution = current
                return path
            
        # Nếu k có solution
        self.end_run(solution_node=Node(state=current))
        if self.is_goal_full(current):
            self.solution = current
        return path


