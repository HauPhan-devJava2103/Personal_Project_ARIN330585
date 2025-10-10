from .base import BaseAlgorithm, Node

class IDSAlgorithm(BaseAlgorithm):
    """
    IDDFS cơ bản cho bài Eight Rooks.
    - Lặp limit = 0..max_depth
    - Mỗi vòng gọi DLS (đệ quy) với giới hạn độ sâu 'limit'
    - Trả về đường đi ngay khi gặp nghiệm
    """

    def set_up_IDS(self, max_depth=None):
        """
        Hàm "IDDFS" theo mã giả:
          for limit in 0..max_depth:
              if DLS(root, limit): return path
          return None
        """
        # thiết lập max_depth mặc định: n-1 (độ sâu lời giải tối đa)
        if max_depth is None:
            max_depth = self.n - 1

        # bắt đầu đo thời gian/bộ nhớ (metrics)
        self.begin_run()

        # node gốc (đặt quân ở hàng 0)
        root = self.make_root_node()

        # lặp tăng dần giới hạn độ sâu
        for limit in range(0, max_depth + 1):
            found = self._dls(root, limit)     # gọi DLS
            if found is not None:
                # kết thúc đo và trả về đường đi root→goal
                self.end_run(solution_node=found)
                # nếu cần, coi cost = số bước (mỗi bước đặt 1 quân)
                self.metrics["solution_cost"] = len(found.state)
                return self.extract_path(found)

        # không tìm thấy nghiệm
        self.end_run(solution_node=None)
        return None

    def _dls(self, node: Node, limit: int):
        """
        Hàm DLS theo mã giả:
          if goal(node): return node
          if limit == 0: return None
          for child in children(node):
              r = DLS(child, limit-1)
              if r: return r
          return None
        """
        # đếm số node đã thăm (mỗi lần "thăm" 1 node)
        self.metrics["nodes_visited"] += 1

        # goal?
        if self.is_goal(node.state):
            return node

        # hết giới hạn độ sâu → dừng mở rộng
        if limit == 0:
            return None

        # sinh các trạng thái con (đặt thêm 1 quân ở hàng kế, cột chưa dùng)
        for action, new_state in self.succ(node.state):
            child = Node(state=new_state, parent=node, action=action)

            # (tuỳ chọn) cập nhật độ sâu tối đa đạt được
            depth_now = len(new_state) - 1
            if depth_now > self.metrics["max_depth"]:
                self.metrics["max_depth"] = depth_now

            # đệ quy xuống với limit-1
            got = self._dls(child, limit - 1)
            if got is not None:
                return got

        # không thấy nghiệm ở nhánh này
        return None
