*This project has been created as part of the 42 curriculum by gcabecas, jsam.*

## Description

**A‑Maze‑ing** generates a 2D maze and displays it via MiniLibX. The program reads
a simple configuration, builds a perfect (or imperfect) maze, places the “42”
pattern at the center when possible, computes the shortest path, then exports
the result to a text file. An MLX interface lets you regenerate the maze, change
the color, and display the path.

## Instructions

### Prerequisites

- Python $\ge 3.10$
- MiniLibX (via `mlx-2.2-py3-none-any.whl`)

### Installation

```bash
make venv
make install
```

### Run

```bash
make run
```

By default, `make run` uses `config.txt`. For another file:

```bash
make run CONFIG=mon_config.txt
```

## Full config file format

The file is a set of `KEY=VALUE` pairs, one per line.

| Key | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| `WIDTH` | int | Maze width | `20` | Yes |
| `HEIGHT` | int | Maze height | `15` | Yes |
| `ENTRY` | `x,y` | Entry coordinates | `0,0` | Yes |
| `EXIT` | `x,y` | Exit coordinates | `19,14` | Yes |
| `OUTPUT_FILE` | str | Export file | `maze.txt` | Yes |
| `PERFECT` | bool | `True` for perfect, `False` for imperfect | `True` | Yes |
| `SEED` | int | Random seed (optional) | `42` | No |

### Example

```ini
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

## Generation algorithm

### Choices

- **Perfect maze**: DFS/backtracking (stack) starting from the entry.
- **Imperfect maze**: random wall openings after generationating perfect or imperfect .
- **“42” pattern**: a blocked area is attempted in the center (or elsewhere if
	needed) as long as a valid path between entry and exit exists.

### Why this choice

DFS/backtracking is **simple to implement**, fast, and guarantees a perfect
maze (a single path between two cells). Controlled wall openings **double the
usefulness** of the algorithm: generating perfect or imperfect mazes with the
same core code.

## Reusable parts

- **`mazegen package`**: the `Maze` class encapsulates generation, solving
	(shortest path), and file export.
- **`generator`**: take width, heigth, entry, exit, outputfile, perfect and optionnaly a seed and generate a maze

## Features

- Perfect / imperfect generation (`PERFECT`)
- Deterministic seed (`SEED`)
- Text export (walls + entry/exit + solution)
- MiniLibX UI: regenerate, change color, display the path

## Team & project management

### Roles

- **gcabecas**: generation algorithm, configuration parsing
- **jsam**: main program, text file export, MLX display

### Planning & evolution

- **Planned**: 3 days learning tech, 3 days coding, 1 day cleanup.
- **Actual**: schedule mostly respected, with +- 2 days.

### Retrospective

- **What worked well**: teamwork.

- **To improve**: github management.

### Tools used

- GitHub, Discord

## Resources

- Maze generation (DFS/backtracking) : https://en.wikipedia.org/wiki/Maze_generation_algorithm
- Pydantic : https://docs.pydantic.dev/
- MiniLibX (42) : https://harm-smits.github.io/42docs/libs/minilibx

### Use of AI

- **README**: structure and writing.
- **Docstrings**: clarification and summary of some functions.
- **Explanations**: help understanding the topic and concepts.
