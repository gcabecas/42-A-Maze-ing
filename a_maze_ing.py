import sys
from pydantic import ValidationError
from config_parser import MazeConfig, read_config, verify_config


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


if __name__ == "__main__":
    main()
