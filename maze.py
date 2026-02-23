import random
from typing import Optional
import sys


class Maze:
    def __init__(self,
                 width: int,
                 height: int,
                 seed: Optional[int],
                 entry: tuple[int,
                              int],
                 exit: tuple[int,
                             int],
                 output_file: str) -> None:

        self.width = width
        self.height = height
        self.seed = seed
        self.entry = entry
        self.exit = exit
        self.solver: str = ""
        self.output_file = output_file

        if seed is None:
            self.rng = random.Random()
            self.seed = self.rng.getrandbits(32)

        self.grid = [15] * (width * height)
        self.pattern = [
            "1000111",
            "1000001",
            "1110111",
            "0010100",
            "0010111",
        ]
        self.DIRS = (
            (0, -1, 1, 4),
            (1, 0, 2, 8),
            (0, 1, 4, 1),
            (-1, 0, 8, 2),
        )

    def cell_index(self, x: int, y: int) -> int:
        return y * self.width + x

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def cell(self, x: int, y: int) -> int:
        return self.grid[self.cell_index(x, y)]

    def has_wall_value(self, value: int, wall: int) -> bool:
        return (value // wall) % 2 == 1

    def has_wall(self, x: int, y: int, wall: int) -> bool:
        return self.has_wall_value(self.cell(x, y), wall)

    def remove_wall_at_index(self, i: int, wall: int) -> None:
        if (self.grid[i] // wall) % 2 == 1:
            self.grid[i] -= wall

    def add_wall_at_index(self, i: int, wall: int) -> None:
        if (self.grid[i] // wall) % 2 == 0:
            self.grid[i] += wall

    def carve_between(self, x: int, y: int, nx: int, ny: int) -> None:
        dx = nx - x
        dy = ny - y

        for test_dx, test_dy, a, b in self.DIRS:
            if dx == test_dx and dy == test_dy:
                current = self.cell_index(x, y)
                neighbor = self.cell_index(nx, ny)

                self.remove_wall_at_index(current, a)
                self.remove_wall_at_index(neighbor, b)
                return

    def close_between(self, x: int, y: int, nx: int, ny: int) -> None:
        dx = nx - x
        dy = ny - y

        for test_dx, test_dy, a, b in self.DIRS:
            if dx == test_dx and dy == test_dy:
                current = self.cell_index(x, y)
                neighbor = self.cell_index(nx, ny)

                self.add_wall_at_index(current, a)
                self.add_wall_at_index(neighbor, b)
                return

    def make_blocked(self, ox: int, oy: int) -> list[bool]:
        blocked = [False] * (self.width * self.height)

        pattern_height = len(self.pattern)
        pattern_width = len(self.pattern[0])

        for row in range(pattern_height):
            for col in range(pattern_width):
                if self.pattern[row][col] == "1":
                    x = ox + col
                    y = oy + row
                    blocked[self.cell_index(x, y)] = True

        return blocked

    def apply_blocked_cells(self, blocked: list[bool]) -> None:
        for row in range(self.height):
            for col in range(self.width):
                cell_i = self.cell_index(col, row)
                if not blocked[cell_i]:
                    continue

                self.grid[cell_i] = 15

                for step_x, step_y, _, _ in self.DIRS:
                    neighbor_x = col + step_x
                    neighbor_y = row + step_y
                    if self.in_bounds(neighbor_x, neighbor_y):
                        self.close_between(col, row, neighbor_x, neighbor_y)

    def path_exists_avoiding(self, blocked: list[bool]) -> bool:
        start_x, start_y = self.entry
        goal_x, goal_y = self.exit

        if blocked[self.cell_index(start_x, start_y)]:
            return False
        if blocked[self.cell_index(goal_x, goal_y)]:
            return False

        visited = [False] * (self.width * self.height)

        queue: list[tuple[int, int]] = [(start_x, start_y)]
        queue_head = 0

        visited[self.cell_index(start_x, start_y)] = True

        while queue_head < len(queue):
            x, y = queue[queue_head]
            queue_head += 1

            if (x, y) == (goal_x, goal_y):
                return True

            cell_value = self.cell(x, y)

            for step_x, step_y, wall_here, _ in self.DIRS:
                if self.has_wall_value(cell_value, wall_here):
                    continue

                next_x = x + step_x
                next_y = y + step_y

                if not self.in_bounds(next_x, next_y):
                    continue

                next_i = self.cell_index(next_x, next_y)
                if blocked[next_i] or visited[next_i]:
                    continue

                visited[next_i] = True
                queue.append((next_x, next_y))

        return False

    def generate_perfect_avoiding(self, blocked: list[bool]) -> None:
        rng = random.Random(self.seed)

        start_x, start_y = self.entry

        self.grid = [15] * (self.width * self.height)

        if blocked[self.cell_index(start_x, start_y)]:
            raise ValueError("ENTRY is inside the 42 pattern")

        visited = [False] * (self.width * self.height)
        stack: list[tuple[int, int]] = [(start_x, start_y)]
        visited[self.cell_index(start_x, start_y)] = True

        while stack:
            current_x, current_y = stack[-1]

            unvisited_neighbors: list[tuple[int, int]] = []
            for step_x, step_y, _, _ in self.DIRS:
                neighbor_x = current_x + step_x
                neighbor_y = current_y + step_y

                if not self.in_bounds(neighbor_x, neighbor_y):
                    continue

                neighbor_i = self.cell_index(neighbor_x, neighbor_y)
                if blocked[neighbor_i] or visited[neighbor_i]:
                    continue

                unvisited_neighbors.append((neighbor_x, neighbor_y))

            if not unvisited_neighbors:
                stack.pop()
                continue

            next_x, next_y = rng.choice(unvisited_neighbors)
            self.carve_between(current_x, current_y, next_x, next_y)
            visited[self.cell_index(next_x, next_y)] = True
            stack.append((next_x, next_y))

    def solve_shortest(self, blocked: list[bool]) -> None:
        start_x, start_y = self.entry
        goal_x, goal_y = self.exit

        if (start_x, start_y) == (goal_x, goal_y):
            self.solver = ""
            return

        start_i = self.cell_index(start_x, start_y)
        goal_i = self.cell_index(goal_x, goal_y)

        if blocked[start_i] or blocked[goal_i]:
            raise ValueError("No path: entry or exit is blocked")

        visited = [False] * (self.width * self.height)
        parent = [-1] * (self.width * self.height)
        move_to = [""] * (self.width * self.height)

        queue: list[tuple[int, int]] = [(start_x, start_y)]
        head = 0
        visited[start_i] = True

        letters = ("N", "E", "S", "W")

        while head < len(queue):
            x, y = queue[head]
            head += 1

            cur_i = self.cell_index(x, y)
            if cur_i == goal_i:
                break

            cell_value = self.cell(x, y)

            for k, (step_x, step_y, wall_here, _) in enumerate(self.DIRS):
                if self.has_wall_value(cell_value, wall_here):
                    continue

                nx = x + step_x
                ny = y + step_y
                if not self.in_bounds(nx, ny):
                    continue

                ni = self.cell_index(nx, ny)
                if blocked[ni] or visited[ni]:
                    continue

                visited[ni] = True
                parent[ni] = cur_i
                move_to[ni] = letters[k]
                queue.append((nx, ny))

        if not visited[goal_i]:
            raise ValueError("No path found from entry to exit")

        path_rev: list[str] = []
        cur = goal_i
        while cur != start_i:
            path_rev.append(move_to[cur])
            cur = parent[cur]

        path_rev.reverse()
        self.solver = "".join(path_rev)

    def write_output_file_from_maze(self) -> None:
        try:
            with open(f"{self.output_file}", "w") as f:
                for y in range(self.height):
                    base = y * self.width
                    line = ""
                    for x in range(self.width):
                        line += format(self.grid[base + x], "X")
                    f.write(line + "\n")

                f.write("\n")

                ex, ey = self.entry
                tx, ty = self.exit

                f.write(f"{ex},{ey}\n")
                f.write(f"{tx},{ty}\n")
                f.write(self.solver + "\n")

        except OSError as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)

    def generate(self) -> None:
        pattern_height = len(self.pattern)
        pattern_width = len(self.pattern[0])

        if pattern_width > self.width or pattern_height > self.height:
            raise ValueError("Maze too small to place the 42 pattern")

        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit

        rng = random.Random(self.seed)

        placement_candidates: list[tuple[int, int]] = []

        center_x = (self.width - pattern_width) // 2
        center_y = (self.height - pattern_height) // 2
        placement_candidates.append((center_x, center_y))

        for _ in range(self.width * self.height):
            origin_x = rng.randrange(0, self.width - pattern_width + 1)
            origin_y = rng.randrange(0, self.height - pattern_height + 1)
            placement_candidates.append((origin_x, origin_y))

        for origin_x, origin_y in placement_candidates:

            if origin_x <= entry_x < origin_x + \
                pattern_width and origin_y <= entry_y < origin_y \
                    + pattern_height:
                continue
            if origin_x <= exit_x < origin_x + \
                pattern_width and origin_y <= exit_y < origin_y \
                    + pattern_height:
                continue

            blocked = self.make_blocked(origin_x, origin_y)

            self.generate_perfect_avoiding(blocked)
            self.apply_blocked_cells(blocked)

            if self.path_exists_avoiding(blocked):
                return

            self.solve_shortest(blocked)
            self.write_output_file_from_maze()
        raise ValueError(
            "Could not place a visible 42 without blocking the path")
