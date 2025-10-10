
import random
from .base import BaseAlgorithm, Node

class GeneticAlgorithm(BaseAlgorithm):
    """
    Genetic Algorithm cho Eight Rooks.
    - Chromosome: list[int] length n, gene[i] = column của quân ở hàng i.
    - Fitness (mặc định): số cột khác nhau (0..n), maximize. Khi == n là nghiệm.
      (Tùy chọn) thêm mục tiêu phụ: giảm tổng chi phí cột (nếu bật USE_COST_OBJECTIVE).
    - Crossover: uniform (trộn gene từng vị trí).
    - Parent selection: chọn từ top p% (tournament/roulette có thể thay dễ dàng).
    """

    # Tham số GA - Genetic
    POP_SIZE = 200
    MAX_GENERATIONS = 1000
    ELITISM_RATE = 0.02         # giữ top k% cá thể tốt nhất qua thế hệ kế.
    PARENT_POOL_RATE = 0.50     # chọn bố/mẹ từ top 50%
    MUTATION_RATE = 0.25
    LOG_EVERY = 1               # log mỗi thế hệ -> Tăng đỡ dày

    # Mục tiêu phụ (tùy chọn): nếu True, khuyến khích cột nhỏ (phạt cột phải)
    USE_COST_OBJECTIVE = False
    COST_WEIGHT = 0.05          # trọng số rất nhỏ để không lấn át mục tiêu chính


    def chromosome_to_state(self, chrom):
        """Chuyển chromosome -> state dạng [(row, col), ...] cho GUI."""
        return [(r, chrom[r]) for r in range(self.n)]

    # Fitness
    def fitness(self, chrom):
        """
        Fitness chính: số cột khác nhau (maximize).
        Tùy chọn: trừ nhẹ theo tổng chi phí cột để ưu tiên cột nhỏ (nếu bật).
        """
        distinct = len(set(chrom))  # 0..n
        if not self.USE_COST_OBJECTIVE:
            return float(distinct)

        # thêm mục tiêu phụ: tổng cost nhỏ (cột trái tốt hơn)
        base = float(distinct)
        total_cost = sum(self.move_cost(r, c) for r, c in enumerate(chrom))
        # distinct ưu tiên tuyệt đối; cost chỉ “tinh chỉnh” khi distinct bằng nhau
        return base - self.COST_WEIGHT * total_cost

    def is_goal_full(self, chrom):
        """Nghiệm: không trùng cột (distinct == n)."""
        return len(set(chrom)) == self.n

    # Khởi tạo quần thể ban đầu
    def random_chromosome(self):
        """Chromosome ngẫu nhiên: mỗi hàng chọn 1 cột (0..n-1)."""
        return [random.randint(0, self.n - 1) for _ in range(self.n)]

    def init_population(self):
        return [self.random_chromosome() for _ in range(self.POP_SIZE)]

    # Toán tử di chuyền
    def crossover(self, p1, p2):
        """
        Uniform crossover: tại mỗi gene, lấy từ p1 hoặc p2 theo xác suất 0.5.
        """
        child = []
        for a, b in zip(p1, p2):
            child.append(a if random.random() < 0.5 else b)
        return child
    
    def mutate(self, chrom):
        '''SWAP 2 GEN'''
        if random.random() < self.MUTATION_RATE and self.n > 1:
            i, j = random.sample(range(self.n), 2)
            chrom[i], chrom[j] = chrom[j], chrom[i]
        return chrom

    # Vòng lặp thuật toán
    def set_up_GA(self):

        # Bắt đầu đo
        self.begin_run()

        # Khởi tạo quần thể
        population = self.init_population()
        self.update_frontier_peak(len(population))
        self.update_depth_peak(self.n - 1)

        # Log ban đầu
        best = max(population, key=self.fitness)
        best_fit = self.fitness(best)
        self.metrics["nodes_visited"] += len(population)

        init_state = self.chromosome_to_state(best)
        self.steps.append((init_state, [f"Init population: best_fitness={best_fit:.3f}"], 
                           [Node(state=self.chromosome_to_state(ch)) for ch in population[:min(10, len(population))]]))

        path = [(init_state, "Start GA with random population")]

        # Nếu đã nghiệm
        if self.is_goal_full(best):
            sol_state = self.chromosome_to_state(best)
            self.end_run(solution_node=Node(state=sol_state))
            self.solution = sol_state
            self.metrics["solution_cost"] = 0.0
            return path + [(sol_state, "Goal reached in initial population")]

        # Số lượng elitism/parent pool
        elite_k = max(1, int(self.ELITISM_RATE * self.POP_SIZE))
        pool_k  = max(2, int(self.PARENT_POOL_RATE * self.POP_SIZE))

        gen = 1
        while gen <= self.MAX_GENERATIONS:
            # Sắp xếp theo fitness giảm dần
            population.sort(key=self.fitness, reverse=True)

            elites = population[:elite_k]
            parent_pool = population[:pool_k]

            # Tạo thế hệ mới
            new_gen = elites[:]  # elitism
            while len(new_gen) < self.POP_SIZE:
                p1 = random.choice(parent_pool)
                p2 = random.choice(parent_pool)
                child = self.crossover(p1, p2)
                child = self.mutate(child)
                new_gen.append(child)

            population = new_gen
            self.metrics["nodes_visited"] += len(population)
            self.update_frontier_peak(len(population))

            # Ghi log mỗi LOG_EVERY thế hệ
            if gen % self.LOG_EVERY == 0:
                best = max(population, key=self.fitness)
                best_fit = self.fitness(best)
                best_state = self.chromosome_to_state(best)
                # snapshot một ít cá thể (tránh log quá nặng)
                snapshot = [Node(state=self.chromosome_to_state(ch)) for ch in population[:min(10, len(population))]]
                self.steps.append((best_state, [f"Gen {gen}: best_fitness={best_fit:.3f}"], snapshot))

            # Kiểm tra nghiệm
            if self.is_goal_full(best):
                sol_state = self.chromosome_to_state(best)
                self.end_run(solution_node=Node(state=sol_state))
                self.solution = sol_state
                # (tùy chọn) báo cáo tổng cost cột nếu bật USE_COST_OBJECTIVE
                if self.USE_COST_OBJECTIVE:
                    total_cost = sum(self.move_cost(r, c) for r, c in sol_state)
                    self.metrics["solution_cost"] = float(total_cost)
                else:
                    self.metrics["solution_cost"] = 0.0
                path.append((sol_state, f"Goal found at generation {gen}"))
                return path

            gen += 1

        # Không tìm thấy nghiệm trong MAX_GENERATIONS
        # Trả về best hiện có (có thể chưa đủ n cột khác nhau)
        best = max(population, key=self.fitness)
        best_state = self.chromosome_to_state(best)
        self.end_run(solution_node=None)
        path.append((best_state, "Stopped: max generations reached"))
        return path
