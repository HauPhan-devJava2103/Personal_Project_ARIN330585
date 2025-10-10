# algorithms/beam.py
from .base import BaseAlgorithm, Node

class BeamSearchAlgorithm(BaseAlgorithm):
    """
    Beam Search theo tầng cho Eight Rooks.
    - Mỗi tầng (mỗi hàng) chỉ giữ lại tối đa beam_size trạng thái tốt nhất.
    - score(state): ưu tiên số cột khác nhau, sau đó ưu tiên sâu hơn.
    """

    def score(self, state):
        distinct_cols = len({c for _, c in state})
        depth = len(state)  # số quân đã đặt
        return (distinct_cols, depth)  # sort giảm dần theo tuple này

    def _complete_last_rook_if_possible(self, node: Node):
        """
        Fallback an toàn:
        Nếu node đang ở độ sâu n-1 (thiếu đúng 1 hàng),
        tự điền cột còn lại để thành đủ 8 quân.
        """
        r = len(node.state)
        if r != self.n - 1:
            return None

        used = {c for _, c in node.state}
        remain = [c for c in range(self.n) if c not in used]
        if len(remain) != 1:
            return None

        c = remain[0]
        new_state = node.state + [(r, c)]
        child = Node(state=new_state, parent=node, action=f"Place ({r},{c})")
        return child

    def set_up_Beam(self, beam_size=3):
        k = max(1, int(beam_size))

        # Bắt đầu đo thời gian/bộ nhớ
        self.begin_run()

        # Root: đặt 1 quân ở hàng 0 (ngẫu nhiên cột)
        root = self.make_root_node()
        beam = [root]

        # Log/metrics ban đầu
        self.update_frontier_peak(len(beam))
        self.update_depth_peak(len(root.state) - 1)
        self.steps.append((root.state, [f"Init beam (k={k})"], list(beam)))

        # Nếu root đã là nghiệm (n=1)
        if self.is_goal(root.state):
            self.steps.append((root.state, ["Goal at root"], list(beam)))
            self.end_run(solution_node=root)
            self.metrics["solution_cost"] = len(root.state)
            return self.extract_path(root)

        # Vòng lặp theo TẦNG
        while beam:
            # (1) Kiểm tra goal trong beam hiện tại
            for n in beam:
                if self.is_goal(n.state):
                    self.steps.append((n.state, ["Goal found in beam"], list(beam)))
                    self.end_run(solution_node=n)
                    self.metrics["solution_cost"] = len(n.state)
                    return self.extract_path(n)

            # (2) Mở rộng cả beam
            self.metrics["nodes_visited"] += len(beam)
            children = []
            seen_keys = set()  # tránh trùng trong cùng tầng

            for parent in beam:
                # Fallback: nếu đang ở n-1 quân, tự hoàn tất quân thứ 8
                maybe_done = self._complete_last_rook_if_possible(parent)
                if maybe_done is not None:
                    self.steps.append((maybe_done.state, ["Auto-complete last rook"], [maybe_done]))
                    self.end_run(solution_node=maybe_done)
                    self.metrics["solution_cost"] = len(maybe_done.state)
                    return self.extract_path(maybe_done)

                # Sinh hậu duệ bình thường
                for action, new_state in self.succ(parent.state):
                    key = tuple(new_state)
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)

                    child = Node(state=new_state, parent=parent, action=action)
                    children.append(child)
                    self.update_depth_peak(len(new_state) - 1)

            # Log children tầng kế
            self.update_frontier_peak(len(children))
            self.steps.append((
                beam[-1].state if beam else [],
                [f"Generated {len(children)} children"],
                list(children)
            ))

            # (3) Không còn child → thất bại (nhưng với rooks hiếm khi xảy ra)
            if not children:
                # Thử một nhát fallback trên cả beam (phòng trường hợp succ() lỗi)
                for parent in beam:
                    maybe_done = self._complete_last_rook_if_possible(parent)
                    if maybe_done is not None:
                        self.steps.append((maybe_done.state, ["Auto-complete last rook (no children)"], [maybe_done]))
                        self.end_run(solution_node=maybe_done)
                        self.metrics["solution_cost"] = len(maybe_done.state)
                        return self.extract_path(maybe_done)

                self.steps.append(([], ["No children; search failed"], []))
                self.end_run(solution_node=None)
                return None

            # (4) Goal trong children?
            for c in children:
                if self.is_goal(c.state):
                    self.steps.append((c.state, ["Goal found in children"], [c]))
                    self.end_run(solution_node=c)
                    self.metrics["solution_cost"] = len(c.state)
                    return self.extract_path(c)

            # (5) Cắt còn top-k theo score giảm dần
            children.sort(key=lambda nd: self.score(nd.state), reverse=True)
            new_beam = children[:k]
            self.steps.append((new_beam[0].state, [f"Pruned to top-{k} beam"], list(new_beam)))

            beam = new_beam

        # Hết beam mà không có nghiệm
        self.end_run(solution_node=None)
        return None
