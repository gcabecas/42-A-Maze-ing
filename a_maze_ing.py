import sys
from pydantic import ValidationError
from config_parser import MazeConfig, read_config, verify_config
from maze_gen import Maze
from maze_output import write_output_file_from_maze


def main() -> None:
    """Entry point of the program.

    Reads a config file passed as argument, validates it, and prints the parsed
    configuration. Exits with status code 1 on error.

    Returns:
        None
    """
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

    print_config(maze_data)

    if maze_data.PERFECT:
        maze = Maze(
            maze_data.WIDTH,
            maze_data.HEIGHT,
            maze_data.SEED,
            maze_data.ENTRY,
            maze_data.EXIT)
        maze.generate_with_42()
        write_output_file_from_maze(maze, maze_data.OUTPUT_FILE)
        print_maze(maze)


def print_config(cfg: MazeConfig) -> None:
    """Print the validated configuration to stdout.

    Args:
        cfg: Validated maze configuration.

    Returns:
        None
    """
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

    line = "+"
    for x in range(w):
        c = maze.cell(x, 0)
        line += "---+" if (c & 1) else "   +"
    print(line)

    for y in range(h):
        line = ""
        for x in range(w):
            c = maze.cell(x, y)

            if x == 0:
                line += "|" if (c & 8) else " "

            if c == 15:
                line += "## "
            else:
                line += "   "

            line += "|" if (c & 2) else " "
        print(line)

        line = "+"
        for x in range(w):
            c = maze.cell(x, y)
            line += "---+" if (c & 4) else "   +"
        print(line)


if __name__ == "__main__":
    main()
