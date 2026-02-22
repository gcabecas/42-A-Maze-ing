from maze_gen import Maze
import sys


def neighbors_open_from_maze(
        maze: Maze, x: int, y: int) -> list[tuple[int, int, str]]:
    """Return reachable neighbor cells from (x, y) in the maze.

    A neighbor is considered reachable if there is no wall between the
    current cell and the neighbor cell. The returned move letter is the
    direction taken from (x, y) to reach the neighbor.

    Args:
        maze: Maze instance to query for walls and bounds.
        x: X coordinate of the current cell.
        y: Y coordinate of the current cell.

    Returns:
        A list of tuples (nx, ny, move) where (nx, ny) is a reachable
        neighbor coordinate and move is one of "N", "E", "S", "W".
    """
    cell_value = maze.grid[maze.cell_index(x, y)]
    out: list[tuple[int, int, str]] = []

    if y > 0 and not maze.has_wall_value(cell_value, 1):
        out.append((x, y - 1, "N"))
    if x + 1 < maze.width and not maze.has_wall_value(cell_value, 2):
        out.append((x + 1, y, "E"))
    if y + 1 < maze.height and not maze.has_wall_value(cell_value, 4):
        out.append((x, y + 1, "S"))
    if x > 0 and not maze.has_wall_value(cell_value, 8):
        out.append((x - 1, y, "W"))

    return out


def shortest_path_from_maze(maze: Maze) -> str:
    """Compute the shortest path from entry to exit as direction letters.

    The path is computed with a breadth-first search over open passages.
    Moves are encoded as direction letters: "N", "E", "S", "W".

    Args:
        maze: Maze instance that provides entry/exit and wall data.

    Returns:
        A string of direction letters representing a shortest path.
        Returns an empty string if entry equals exit.

    Raises:
        ValueError: If no path exists from entry to exit.
    """
    start_x, start_y = maze.entry
    goal_x, goal_y = maze.exit

    if maze.entry == maze.exit:
        return ""

    start_i = maze.cell_index(start_x, start_y)
    goal_i = maze.cell_index(goal_x, goal_y)

    prev: list[int] = [-1] * (maze.width * maze.height)
    prev_move: list[str] = [""] * (maze.width * maze.height)

    queue: list[tuple[int, int]] = [(start_x, start_y)]
    head = 0
    prev[start_i] = start_i

    while head < len(queue):
        x, y = queue[head]
        head += 1

        cur_i = maze.cell_index(x, y)
        if cur_i == goal_i:
            break

        for nx, ny, move in neighbors_open_from_maze(maze, x, y):
            next_i = maze.cell_index(nx, ny)
            if prev[next_i] != -1:
                continue
            prev[next_i] = cur_i
            prev_move[next_i] = move
            queue.append((nx, ny))

    if prev[goal_i] == -1:
        raise ValueError("No path found from ENTRY to EXIT")

    moves: list[str] = []
    cur = goal_i
    while cur != start_i:
        moves.append(prev_move[cur])
        cur = prev[cur]
    moves.reverse()
    return "".join(moves)


def write_output_file_from_maze(maze: Maze, filename: str) -> None:
    """Write the maze grid and solution path to an output file.

    The file format is:
      - maze grid as hex digits, one row per line
      - a blank line
      - entry coordinates "x,y"
      - exit coordinates "x,y"
      - shortest path string (direction letters)

    Args:
        maze: Maze instance to serialize and solve.
        filename: Path to the output file to create or overwrite.

    Returns:
        None.

    Side Effects:
        Exits the program with status 1 if the file cannot be written.
    """
    try:
        with open(filename, "w") as f:
            for y in range(maze.height):
                base = y * maze.width
                line = ""
                for x in range(maze.width):
                    line += format(maze.grid[base + x], "X")
                f.write(line + "\n")

            f.write("\n")

            path = shortest_path_from_maze(maze)

            ex, ey = maze.entry
            tx, ty = maze.exit

            f.write(f"{ex},{ey}\n")
            f.write(f"{tx},{ty}\n")
            f.write(path + "\n")

    except OSError as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)
