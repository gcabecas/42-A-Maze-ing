import random
import sys
from typing import Optional


class Maze:
    """Represent and generate a maze with optional embedded pattern.

        This class handles maze generation (perfect or imperfect),
        shortest-path solving, pattern blocking, and output file writing.
        The maze is internally represented as a grid of bitmasks encoding
        walls in the four cardinal directions.
    """
    N = 1
    E = 2
    S = 4
    W = 8
    ALL = N | E | S | W

    DIRS = ((0, -1, 1, 4, "N"),
            (1, 0, 2, 8, "E"),
            (0, 1, 4, 1, "S"),
            (-1, 0, 8, 2, "W"))

    def __init__(self, width: int, height: int, seed: Optional[int],
                 entry: tuple[int, int], exit: tuple[int, int],
                 output_file: str, perfect: bool) -> None:
        """Initialize a Maze instance.

            Args:
                width: Width of the maze in cells.
                height: Height of the maze in cells.
                seed: Optional random seed for deterministic generation.
                entry: (x, y) coordinates of the maze entry.
                exit: (x, y) coordinates of the maze exit.
                output_file: Path to the output file.
                perfect: Whether the maze must be perfect (acyclic).

            Returns:
                None
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.perfect = perfect
        self.solver: str = ""

        if seed is None:
            seed = random.getrandbits(32)
        self.seed = seed
        self.rng = random.Random(self.seed)

        self.grid = [self.ALL] * (width * height)

        self.pattern = ["1000111", "1000001", "1110111", "0010100", "0010111"]

        self.step_to_walls = {
            (dx, dy): (w1, w2) for dx, dy, w1, w2, _ in self.DIRS}

        self.pattern_ones = [(x, y) for y, row in enumerate(self.pattern)
                             for x, ch in enumerate(row) if ch == "1"]

    def cell_index(self, x: int, y: int) -> int:
        """Return the linear index of a cell.

            Args:
                x: X-coordinate of the cell.
                y: Y-coordinate of the cell.

            Returns:
                The index in the internal grid list.
        """
        return y * self.width + x

    def in_bounds(self, x: int, y: int) -> bool:
        """Check whether a cell is inside maze bounds.

            Args:
                x: X-coordinate.
                y: Y-coordinate.

            Returns:
                True if the coordinates are valid, False otherwise.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def carve_between(self, x: int, y: int, nx: int, ny: int) -> None:
        """Remove the wall between two adjacent cells.

            Args:
                x: X-coordinate of the first cell.
                y: Y-coordinate of the first cell.
                nx: X-coordinate of the neighboring cell.
                ny: Y-coordinate of the neighboring cell.

            Returns:
                None
            """
        wall_a, wall_b = self.step_to_walls[(nx - x, ny - y)]
        self.grid[self.cell_index(x, y)] &= ~wall_a
        self.grid[self.cell_index(nx, ny)] &= ~wall_b

    def close_between(self, x: int, y: int, nx: int, ny: int) -> None:
        """Add a wall between two adjacent cells.

            Args:
                x: X-coordinate of the first cell.
                y: Y-coordinate of the first cell.
                nx: X-coordinate of the neighboring cell.
                ny: Y-coordinate of the neighboring cell.

            Returns:
                None
        """
        wall_a, wall_b = self.step_to_walls[(nx - x, ny - y)]
        self.grid[self.cell_index(x, y)] |= wall_a
        self.grid[self.cell_index(nx, ny)] |= wall_b

    def make_blocked(self, ox: int, oy: int) -> \
            tuple[list[bool], list[tuple[int, int, int]]]:
        """Create a blocked mask for a pattern placed at a position.

            Args:
                ox: X-origin of the pattern.
                oy: Y-origin of the pattern.

            Returns:
                A tuple containing:
                    - A boolean list marking blocked cells.
                    - A list of blocked cell coordinates and indices.
        """
        idx = self.cell_index
        cells = [(x, y, idx(x, y)) for x, y in
                 ((ox + rx, oy + ry) for rx, ry in self.pattern_ones)]
        blocked = [False] * (self.width * self.height)
        for _, _, i in cells:
            blocked[i] = True
        return blocked, cells

    def apply_blocked_cells(
            self, blocked_cells: list[tuple[int, int, int]]) -> None:
        """Apply wall closures to blocked cells.

            Args:
                blocked_cells: List of blocked cell tuples
                    (x, y, index).

            Returns:
                None
        """
        inb = self.in_bounds
        for x, y, i in blocked_cells:
            self.grid[i] = self.ALL
            for dx, dy, *_ in self.DIRS:
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    self.close_between(x, y, nx, ny)

    def find_path(self, blocked: list[bool], want_path: bool) -> \
            tuple[bool, Optional[list[int]], Optional[list[str]]]:
        """Perform BFS to determine if a path exists.

            Args:
                blocked: Boolean list marking blocked cells.
                want_path: Whether to reconstruct the path.

            Returns:
                A tuple containing:
                    - True if a path exists, False otherwise.
                    - Parent index list if requested.
                    - Move direction list if requested.
        """
        idx = self.cell_index
        inb = self.in_bounds
        grid = self.grid
        dirs = self.DIRS

        start = idx(*self.entry)
        goal = idx(*self.exit)
        if blocked[start] or blocked[goal]:
            return False, None, None

        n = self.width * self.height
        visited = [False] * n
        parent: Optional[list[int]] = [-1] * n if want_path else None
        move: Optional[list[str]] = [""] * n if want_path else None

        q = [self.entry]
        head = 0
        visited[start] = True

        while head < len(q):
            x, y = q[head]
            head += 1
            cur = idx(x, y)
            if cur == goal:
                return True, parent, move

            cellv = grid[cur]
            for dx, dy, wall, _, letter in dirs:
                if cellv & wall:
                    continue
                nx, ny = x + dx, y + dy
                if not inb(nx, ny):
                    continue
                ni = idx(nx, ny)
                if blocked[ni] or visited[ni]:
                    continue

                visited[ni] = True
                if want_path:
                    assert parent is not None and move is not None
                    parent[ni] = cur
                    move[ni] = letter
                q.append((nx, ny))

        return False, parent, move

    def shortest_path_indices(self, blocked: list[bool]) -> list[int]:
        """Return the shortest path as cell indices.

            Args:
                blocked: Boolean list marking blocked cells.

            Returns:
                A list of cell indices forming the shortest path.
                Returns an empty list if no path exists.
        """
        ok, parent, _ = self.find_path(blocked, want_path=True)
        if not ok or parent is None:
            return []

        idx = self.cell_index
        start = idx(*self.entry)
        cur = idx(*self.exit)

        path: list[int] = []
        while cur != start:
            path.append(cur)
            cur = parent[cur]
            if cur == -1:
                return []
        path.append(start)
        return path[::-1]

    def solve_shortest(self, blocked: list[bool]) -> None:
        """Compute and store the shortest path as directions.

            Args:
                blocked: Boolean list marking blocked cells.

            Returns:
                None

            Raises:
                ValueError: If no path exists from entry to exit.
        """
        if self.entry == self.exit:
            self.solver = ""
            return

        ok, parent, move = self.find_path(blocked, want_path=True)
        if not ok or parent is None or move is None:
            raise ValueError("No path found from entry to exit")

        idx = self.cell_index
        start = idx(*self.entry)
        cur = idx(*self.exit)

        out: list[str] = []
        while cur != start:
            out.append(move[cur])
            cur = parent[cur]
        self.solver = "".join(reversed(out))

    def generate_perfect_avoiding(self, blocked: list[bool]) -> int:
        """Generate a perfect maze avoiding blocked cells.

            Args:
                blocked: Boolean list marking blocked cells.

            Returns:
                The number of reachable carved cells.

            Raises:
                ValueError: If the entry is inside a blocked cell.
        """
        w, h = self.width, self.height
        rng = self.rng
        dirs = self.DIRS

        sx, sy = self.entry
        start = sy * w + sx
        if blocked[start]:
            raise ValueError("ENTRY is inside the 42 pattern")

        n = w * h
        self.grid = [self.ALL] * n

        visited = [False] * n
        visited[start] = True
        count = 1
        stack = [(sx, sy)]

        while stack:
            x, y = stack[-1]
            cand = []
            for dx, dy, *_ in dirs:
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h:
                    continue
                ni = ny * w + nx
                if blocked[ni] or visited[ni]:
                    continue
                cand.append((nx, ny, ni))

            if not cand:
                stack.pop()
                continue

            nx, ny, ni = rng.choice(cand)
            self.carve_between(x, y, nx, ny)
            visited[ni] = True
            count += 1
            stack.append((nx, ny))

        return count

    def make_imperfect(self, blocked: list[bool]) -> None:
        """Introduce cycles to make the maze imperfect.

            This method opens a small, sampled set of walls to create
            additional loops while avoiding fully open 3x3 areas. It
            respects the blocked-cell mask so no walls are removed
            between blocked cells or across blocked boundaries.

            Args:
                blocked: Boolean list marking blocked cells.

            Returns:
                None
        """
        w, h = self.width, self.height
        n = w * h
        g = self.grid
        rng = self.rng

        def block_is_open(tx: int, ty: int) -> bool:
            """Check whether a 3x3 block at (tx, ty) is fully open.

                Args:
                    tx: Top-left x-coordinate of the 3x3 block.
                    ty: Top-left y-coordinate of the 3x3 block.

                Returns:
                    True if all internal walls in the 3x3 block are open,
                    False otherwise or if the block is out of bounds.
            """
            if tx < 0 or ty < 0 or tx + 2 >= w or ty + 2 >= h:
                return False
            for yy in range(ty, ty + 3):
                base = yy * w
                for xx in range(tx, tx + 3):
                    i = base + xx
                    if xx < tx + 2 and (g[i] & self.E):
                        return False
                    if yy < ty + 2 and (g[i] & self.S):
                        return False
            return True

        def creates_open_block(x: int, y: int) -> bool:
            """Check all 3x3 blocks that include the cell (x, y).

                Args:
                    x: X-coordinate of the cell to test.
                    y: Y-coordinate of the cell to test.

                Returns:
                    True if any 3x3 block containing (x, y) is fully open,
                    False otherwise.
            """
            for ty in range(y - 2, y + 1):
                for tx in range(x - 2, x + 1):
                    if block_is_open(tx, ty):
                        return True
            return False

        open_cells = n - int(sum(blocked))
        k = max(1, int(open_cells ** 0.5))

        sample: list[tuple[int, int]] = []
        seen = 0

        for i in range(n):
            if blocked[i]:
                continue

            x = i % w

            if x + 1 < w:
                ni = i + 1
                if (not blocked[ni]) and (g[i] & self.E):
                    seen += 1
                    if len(sample) < k:
                        sample.append((i, 0))
                    else:
                        j = rng.randrange(seen)
                        if j < k:
                            sample[j] = (i, 0)

            if i + w < n:
                ni = i + w
                if (not blocked[ni]) and (g[i] & self.S):
                    seen += 1
                    if len(sample) < k:
                        sample.append((i, 1))
                    else:
                        j = rng.randrange(seen)
                        if j < k:
                            sample[j] = (i, 1)

        for i, d in sample:
            if d == 0:
                ni = i + 1
                g[i] &= ~self.E
                g[ni] &= ~self.W
                if (creates_open_block(i % w, i // w)
                        or creates_open_block((i + 1) % w, (i + 1) // w)):
                    g[i] |= self.E
                    g[ni] |= self.W
            else:
                ni = i + w
                g[i] &= ~self.S
                g[ni] &= ~self.N
                if (creates_open_block(i % w, i // w)
                        or creates_open_block((i + w) % w, (i + w) // w)):
                    g[i] |= self.S
                    g[ni] |= self.N

    def write_output_file_from_maze(self) -> None:
        """Write the maze and solution to the output file.

            The file contains:
                - The maze grid encoded in hexadecimal.
                - Entry coordinates.
                - Exit coordinates.
                - The shortest path solution.

            Returns:
                None

            Raises:
                SystemExit: If the file cannot be written.
        """
        try:
            with open(self.output_file, "w") as f:
                f.write("\n".join("".join(f"{self.grid[y * self.width + x]:X}"
                                          for x in range(self.width))for y in
                                  range(self.height)))
                f.write(f"\n\n{self.entry[0]},{self.entry[1]}\n{self.exit[0]},"
                        f"{self.exit[1]}\n{self.solver}")
        except OSError as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)

    def generate(self) -> None:
        """Generate the maze with optional pattern placement.

            This method:
                - Validates entry and exit positions.
                - Attempts to place a visible pattern.
                - Generates a perfect or imperfect maze.
                - Ensures a valid path exists.
                - Solves the maze.
                - Writes the output file.

            Returns:
                None

            Raises:
                ValueError: If generation fails or constraints are invalid.
        """
        ph, pw = len(self.pattern), len(self.pattern[0])

        if self.entry[0] >= self.width or self.entry[1] >= self.height \
                or self.exit[0] >= self.width or self.exit[1] >= self.height:
            raise ValueError("ENTRY or EXIT is out of maze bounds")

        if self.entry == self.exit:
            raise ValueError("ENTRY and EXIT cannot be the same")

        if pw > self.width or ph > self.height:
            print(
                "Error: maze too small to place the pattern.",
                file=sys.stderr,
            )
            blocked = [False] * (self.width * self.height)

            self.generate_perfect_avoiding(blocked)
            if not self.perfect:
                self.make_imperfect(blocked)

            if not self.find_path(blocked, want_path=False)[0]:
                raise ValueError("No path found from entry to exit")

            self.solve_shortest(blocked)
            self.write_output_file_from_maze()
            return

        center = ((self.width - pw) // 2, (self.height - ph) // 2)
        origins = [(x, y) for y in range(self.height - ph + 1) for x in
                   range(self.width - pw + 1) if (x, y) != center]
        self.rng.shuffle(origins)
        origins.insert(0, center)

        total_open = self.width * self.height - len(self.pattern_ones)

        for ox, oy in origins:
            if any(ox <= x < ox + pw and oy <= y < oy + ph for x,
                   y in (self.entry, self.exit)):
                continue

            blocked, cells = self.make_blocked(ox, oy)
            if self.generate_perfect_avoiding(blocked) != total_open:
                continue
            if not self.perfect:
                self.make_imperfect(blocked)

            self.apply_blocked_cells(cells)
            if not self.find_path(blocked, want_path=False)[0]:
                continue

            self.solve_shortest(blocked)
            self.write_output_file_from_maze()
            return

        raise ValueError("Could not place a visible pattern")
