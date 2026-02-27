import sys
from pydantic import ValidationError
from config_parser import MazeConfig, read_config, verify_config
from mazegen import Maze
from display import display


def main() -> None:
    """Run the maze application from the command line.

        This function parses command-line arguments, loads and validates
        the configuration file, generates the maze, and launches the
        graphical display. It handles all user-facing errors and exits
        the program with a non-zero status code when a failure occurs.

        The expected usage is:
            python3 a_maze_ing.py config.txt

        Returns:
            None

        Raises:
            SystemExit: If an error occurs during argument parsing,
            configuration loading, maze generation, or display.
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
        print(f"Error displaying maze: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
