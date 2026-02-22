import random


class Maze:
    """Grid maze generator with optional embedded "42" blocked pattern.

    The maze is stored as a flat list of integers (self.grid). Each cell
    value encodes walls using bit-like weights (1, 2, 4, 8). Helper
    methods carve or close walls between neighboring cells.

    The generator can embed a visible "42" pattern as blocked cells, while
    ensuring a path still exists from entry to exit.
    """

    def __init__(self, width: int, height: int, seed: int,
                 entry: tuple[int, int], exit: tuple[int, int]) -> None:
        """Initialize maze parameters and default grid/wall configuration.

        Args:
            width: Maze width in cells.
            height: Maze height in cells.
            seed: Seed used to drive deterministic random choices.
            entry: (x, y) start cell coordinates.
            exit: (x, y) goal cell coordinates.

        Returns:
            None.
        """
        self.width = width
        self.height = height
        self.seed = seed
        self.entry = entry
        self.exit = exit

        self.grid = [15] * (width * height)
        # self.pattern = [
        #    "1000111",
        #    "1000001",
        #    "1110111",
        #    "0010100",
        #    "0010111",
        # ]
        self.pattern = [
            "000111000",
            "001111100",
            "000111000",
            "000111000",
            "000111000",
            "000111000",
            "001111100",
            "011111110",
            "001101100"
        ]
        self.DIRS = (
            (0, -1, 1, 4),
            (1, 0, 2, 8),
            (0, 1, 4, 1),
            (-1, 0, 8, 2),
        )

    def cell_index(self, x: int, y: int) -> int:
        """Return the flat index in self.grid for cell coordinates (x, y).

        Args:
            x: X coordinate of the cell.
            y: Y coordinate of the cell.

        Returns:
            The index into the 1D grid list.
        """
        return y * self.width + x

    def in_bounds(self, x: int, y: int) -> bool:
        """Check whether (x, y) is inside the maze boundaries.

        Args:
            x: X coordinate to test.
            y: Y coordinate to test.

        Returns:
            True if coordinates are within the maze, else False.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def cell(self, x: int, y: int) -> int:
        """Return the encoded wall value for the cell at (x, y).

        Args:
            x: X coordinate of the cell.
            y: Y coordinate of the cell.

        Returns:
            The integer encoding the cell's walls.
        """
        return self.grid[self.cell_index(x, y)]

    def has_wall_value(self, value: int, wall: int) -> bool:
        """Return True if a wall is present in an encoded cell value.

        The encoding uses weights in {1, 2, 4, 8}. A wall is present when
        the corresponding bit-like weight is set.

        Args:
            value: Encoded cell value to inspect.
            wall: Wall weight to test (1, 2, 4, or 8).

        Returns:
            True if the wall is present, else False.
        """
        return (value // wall) % 2 == 1

    def has_wall(self, x: int, y: int, wall: int) -> bool:
        """Return True if cell (x, y) contains the specified wall.

        Args:
            x: X coordinate of the cell.
            y: Y coordinate of the cell.
            wall: Wall weight to test (1, 2, 4, or 8).

        Returns:
            True if the wall is present, else False.
        """
        return self.has_wall_value(self.cell(x, y), wall)

    def remove_wall_at_index(self, i: int, wall: int) -> None:
        """Remove a wall from the cell at flat index i, if present.

        Args:
            i: Index in the 1D grid list.
            wall: Wall weight to remove (1, 2, 4, or 8).

        Returns:
            None.
        """
        if (self.grid[i] // wall) % 2 == 1:
            self.grid[i] -= wall

    def add_wall_at_index(self, i: int, wall: int) -> None:
        """Add a wall to the cell at flat index i, if missing.

        Args:
            i: Index in the 1D grid list.
            wall: Wall weight to add (1, 2, 4, or 8).

        Returns:
            None.
        """
        if (self.grid[i] // wall) % 2 == 0:
            self.grid[i] += wall

    def carve_between(self, x: int, y: int, nx: int, ny: int) -> None:
        """Open the passage between (x, y) and its neighbor (nx, ny).

        This removes the appropriate wall in the current cell and the
        opposite wall in the neighbor cell, based on movement direction.

        Args:
            x: X coordinate of the current cell.
            y: Y coordinate of the current cell.
            nx: X coordinate of the neighbor cell.
            ny: Y coordinate of the neighbor cell.

        Returns:
            None.
        """
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
        """Close the passage between (x, y) and its neighbor (nx, ny).

        This adds the appropriate wall in the current cell and the
        opposite wall in the neighbor cell, based on movement direction.

        Args:
            x: X coordinate of the current cell.
            y: Y coordinate of the current cell.
            nx: X coordinate of the neighbor cell.
            ny: Y coordinate of the neighbor cell.

        Returns:
            None.
        """
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
        """Build a blocked-cells mask by placing the "42" pattern at origin.

        Cells corresponding to '1' characters in self.pattern are marked
        as blocked. The origin (ox, oy) is the top-left placement point.

        Args:
            ox: X coordinate of the pattern origin (top-left).
            oy: Y coordinate of the pattern origin (top-left).

        Returns:
            A boolean list of length width * height, where True means the
            cell is blocked by the pattern.
        """
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
        """Apply a blocked mask to the maze by closing walls around blocks.

        Blocked cells are reset to full walls (value 15), and all edges
        between a blocked cell and any in-bounds neighbor are closed.

        Args:
            blocked: Boolean mask where True marks blocked cells.

        Returns:
            None.
        """
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
        """Check if a path exists from entry to exit while avoiding blocks.

        This performs a breadth-first search that only traverses open
        passages and never enters a blocked cell.

        Args:
            blocked: Boolean mask where True marks blocked cells.

        Returns:
            True if a valid path exists, else False.
        """
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
        """Generate a perfect maze while never carving into blocked cells.

        A "perfect" maze is a spanning tree over reachable cells (no loops
        and exactly one path between any two reachable cells). This uses a
        randomized depth-first search with a stack.

        Args:
            blocked: Boolean mask where True marks blocked cells.

        Returns:
            None.

        Raises:
            ValueError: If the entry cell is blocked by the pattern.
        """
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

    def generate_with_42(self) -> None:
        """Generate a maze embedding a visible "42" pattern when possible.

        The method tries candidate placements for the pattern (center
        first, then random origins). For each placement, it generates a
        perfect maze avoiding the blocked cells, applies the blocked
        cells, and verifies that a path still exists from entry to exit.

        Returns:
            None.

        Raises:
            ValueError: If the maze is too small for the pattern.
            ValueError: If no placement keeps a valid entry-to-exit path.
        """
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

        raise ValueError(
            "Could not place a visible 42 without blocking the path")
