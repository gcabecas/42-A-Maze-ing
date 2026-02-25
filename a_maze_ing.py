import sys
from pydantic import ValidationError
from config_parser import MazeConfig, read_config, verify_config
from maze import Maze
from mytest import display


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

    # print_config(maze_data)

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
        print_maze(maze)
        print(f"{maze.solver}")
    except ValueError as e:
        print(f"Error generating maze: {e}", file=sys.stderr)
        sys.exit(1)

# jsam test
    try:
        display(maze)
    except Exception as e:
        print(f"{e}")


def print_config(cfg: MazeConfig) -> None:
    print("Config:")
    print(f"  WIDTH: {cfg.WIDTH}")
    print(f"  HEIGHT: {cfg.HEIGHT}")
    print(f"  ENTRY: {cfg.ENTRY}")
    print(f"  EXIT: {cfg.EXIT}")
    print(f"  OUTPUT_FILE: {cfg.OUTPUT_FILE}")
    print(f"  PERFECT: {cfg.PERFECT}")
    print(f"  SEED: {cfg.SEED}")


def print_maze(maze: Maze) -> None:
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
    print(line)

    for y in range(h):
        line = ""
        for x in range(w):
            c = g[idx(x, y)]
            if x == 0:
                line += "|" if (c & W) else " "
            line += "## " if c == maze.ALL else "   "
            line += "|" if (c & E) else " "
        print(line)

        line = "+"
        for x in range(w):
            c = g[idx(x, y)]
            line += "---+" if (c & S) else "   +"
        print(line)


if __name__ == "__main__":
    main()
