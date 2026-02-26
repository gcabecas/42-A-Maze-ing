import os
import sys
from pydantic import ValidationError
from config_parser import MazeConfig, read_config, verify_config
from maze import Maze
from display import display


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)

    try:
        raw_cfg: dict[str, str] = read_config(sys.argv[1])
        maze_data: MazeConfig = verify_config(raw_cfg)
    except OSError as e:
        print(f"Error reading config file: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error parsing config file: {e}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as e:
        print("Error: invalid config values:", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)

    try:
        maze = Maze(
            maze_data.WIDTH,
            maze_data.HEIGHT,
            maze_data.SEED,
            maze_data.ENTRY,
            maze_data.EXIT,
            maze_data.OUTPUT_FILE,
            maze_data.PERFECT)
        maze.generate()
    except ValueError as e:
        print(f"Error generating maze: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        display(maze)
    except Exception as e:
        print(f"{e}")
    #loop_termiale(maze)


def loop_termiale(maze: Maze) -> None:
    colors = [
        "\x1b[31m",
        "\x1b[32m",
        "\x1b[33m",
        "\x1b[34m",
        "\x1b[35m",
        "\x1b[36m",
        "\x1b[37m",
    ]
    color_idx = 0
    show_path = False

    while True:
        print_maze(maze, colors[color_idx], show_path)
        choice = input("Choice? (1-4): ").strip()

        if choice == "3":
            color_idx = (color_idx + 1) % len(colors)
        elif choice == "4":
            return
        elif choice == "1":
            maze = Maze(
                maze.width,
                maze.height,
                None,
                maze.entry,
                maze.exit,
                maze.output_file,
                maze.perfect
            )
            maze.generate()
        elif choice == "2":
            show_path = not show_path


def print_maze(maze: Maze, color: str, show_path: bool) -> None:
    os.system("cls" if os.name == "nt" else "clear")

    reset = "\x1b[0m"

    def p(line: str) -> None:
        print(f"{color}{line}{reset}")

    path_cells = set()
    if show_path and getattr(maze, "solver", ""):
        x, y = maze.entry
        path_cells.add((x, y))
        for d in maze.solver:
            if d == "N":
                y -= 1
            elif d == "S":
                y += 1
            elif d == "E":
                x += 1
            elif d == "W":
                x -= 1
            else:
                continue
            if 0 <= x < maze.width and 0 <= y < maze.height:
                path_cells.add((x, y))
            else:
                break

    w = maze.width
    h = maze.height
    g = maze.grid
    idx = maze.cell_index

    N = int(Maze.N)
    E = int(Maze.E)
    S = int(Maze.S)
    W = int(Maze.W)

    line = "+"
    for x in range(w):
        c = g[idx(x, 0)]
        line += "---+" if (c & N) else "   +"
    p(line)

    for y in range(h):
        line = ""
        for x in range(w):
            c = g[idx(x, y)]
            if x == 0:
                line += "|" if (c & W) else " "

            if show_path and (x, y) in path_cells:
                cell = ".. "
            else:
                cell = "## " if c == maze.ALL else "   "

            if (x, y) == maze.entry:
                cell = "E  "
            elif (x, y) == maze.exit:
                cell = "X  "

            line += cell
            line += "|" if (c & E) else " "
        p(line)

        line = "+"
        for x in range(w):
            c = g[idx(x, y)]
            line += "---+" if (c & S) else "   +"
        p(line)

    p("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show/hide path from entry to exit")
    print("3. Rotate maze colors")
    print("4. Quit")


if __name__ == "__main__":
    main()
