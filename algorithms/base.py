import random
import time
import tracemalloc

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action


class BaseAlgorithm:
    def __init__(self, n=8):
        self.n = n
        self.steps = []      # [(state, [action_str], frontier_snapshot)]
        self.solution = None
        # ======= metrics =======
        self.metrics = {
            "nodes_visited": 0,
            "max_frontier": 0,
            "max_depth": 0,
            "solution_depth": 0,
            "elapsed_s": 0.0,
            "peak_mem_mb": 0.0,
            "solution_cost": 0,     
        }
    def begin_run(self):
        self.metrics.update({
            "nodes_visited": 0,
            "max_frontier": 0,
            "max_depth": 0,
            "solution_depth": 0,
            "elapsed_s": 0.0,
            "peak_mem_mb": 0.0,
            "solution_cost": 0,
        })
        self._t0 = time.perf_counter()
        tracemalloc.start()

    def update_frontier_peak(self, frontier_len):
        if frontier_len > self.metrics["max_frontier"]:
            self.metrics["max_frontier"] = frontier_len

    def update_depth_peak(self, depth_now):
        # depth_now = len(state)-1 (đặt quân ở hàng 0 là depth 0)
        if depth_now > self.metrics["max_depth"]:
            self.metrics["max_depth"] = depth_now

    def end_run(self, solution_node=None):
        # thời gian
        t1 = time.perf_counter()
        self.metrics["elapsed_s"] = (t1 - self._t0) if self._t0 else 0.0
        # peak memory (current, peak) in bytes
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.metrics["peak_mem_mb"] = peak / (1024.0 * 1024.0)
        # độ sâu lời giải (n-1 nếu đủ n quân)
        if solution_node is not None:
            self.metrics["solution_depth"] = max(0, len(solution_node.state) - 1)

    # ======= logic chung =======
    def is_goal(self, state):
        if len(state) != self.n:
            return False
        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                if state[i][0] == state[j][0] or state[i][1] == state[j][1]:
                    return False
        return True

    def succ(self, state):
        successors = []
        current_row = len(state)
        if current_row >= self.n:
            return successors
        used_cols = {col for _, col in state}
        for col in range(self.n):
            if col not in used_cols:
                new_state = state + [(current_row, col)]
                action = f"Place rook at ({current_row}, {col})"
                successors.append((action, new_state))
        return successors

    def make_root_node(self):
        col = random.randint(0, self.n - 1)
        state = [(0, col)]
        return Node(state=state, action=f"Place first rook at (0, {col})")

    def extract_path(self, node):
        path = []
        while node:
            path.append((node.state, node.action))
            node = node.parent
        return path[::-1]
    
    # Khởi tạo trạng thái bđ
    def random_initial_state(self):
        '''Sinh ra đủ 8 quân xe có thể trùng cột'''
        return [(r, random.randint(0, self.n - 1)) for r in range(self.n)]
    
     # ===== Chi phí mỗi bước: phạt cột phải =====
    def move_cost(self, row: int, col: int) -> float:
        """
        Cost đặt 1 quân tại (row, col).
        Mặc định: 1 + col  (col càng lớn càng đắt).
        """
        return 1.0 + col
    
        # Sinh láng giềng
    def generate_neighbors(self, state):
        '''Đổi cột cột sang cột khác'''
        neighbors = []
        for r in range(self.n):
            cur_col = state[r][1]
            for new_col in range(self.n):
                if cur_col == new_col:
                    continue
                new_state = list(state)
                new_state[r] = (r,new_col)
                action = f"Move row {r}: {cur_col} → {new_col}"
                neighbors.append((action,new_state))
        return neighbors
    
        # Đánh giá chất lượng
    def fitness(self,state):
        '''Điểm = số cột khác nhau'''
        return ({c for _, c in state})

    
    # Kiểm tra mục tiêu
    def is_goal_full(self,state):
        return len(state) == self.n and self.fitness(state) == self.n
