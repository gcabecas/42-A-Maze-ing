from typing import Any, Optional
from pydantic import BaseModel, Field, model_validator


class MazeConfig(BaseModel):
    WIDTH: int = Field(gt=0)
    HEIGHT: int = Field(gt=0)
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str = Field(min_length=1)
    PERFECT: bool
    SEED: Optional[int] = None
    """Configuration model for maze generation.

    This model validates and stores all parameters required to generate
    a maze. It ensures dimensions are positive integers, coordinates are
    valid tuples, and optional parameters such as the random seed are
    properly typed.

    Attributes:
        WIDTH (int): Width of the maze. Must be greater than 0.
        HEIGHT (int): Height of the maze. Must be greater than 0.
        ENTRY (tuple[int, int]): Entry coordinates as (x, y).
        EXIT (tuple[int, int]): Exit coordinates as (x, y).
        OUTPUT_FILE (str): Path to the output file.
        PERFECT (bool): Whether the maze is perfect (no loops).
        SEED (Optional[int]): Optional random seed.
    """
    @model_validator(mode="before")
    @classmethod
    def convert_strings(cls, data: Any) -> Any:
        """Convert raw configuration values before validation.

        This method runs before Pydantic validation and converts
        string-based inputs into the expected Python types. It is useful
        when loading configuration values from environment variables or
        configuration files.

        Supported conversions:
            - WIDTH and HEIGHT to int
            - SEED to int if provided
            - ENTRY and EXIT from "x,y" to tuple[int, int]
            - PERFECT from "true"/"false" to bool

        Args:
            cls (type[MazeConfig]): The model class.
            data (Any): Raw input data, usually a dictionary.

        Returns:
            Any: The transformed data dictionary or the original value
            if it is not a dictionary.

        Raises:
            ValueError: If a field cannot be converted to the expected
            type or does not match the required format.
        """
        if not isinstance(data, dict):
            return data

        if "WIDTH" in data:
            try:
                data["WIDTH"] = int(data["WIDTH"])
            except (ValueError, TypeError):
                raise ValueError(f"WIDTH must be an int (got {data['WIDTH']})")

        if "HEIGHT" in data:
            try:
                data["HEIGHT"] = int(data["HEIGHT"])
            except (ValueError, TypeError):
                raise ValueError(f"HEIGHT must be an int (got "
                                 f"{data['HEIGHT']})")

        if "SEED" in data and data["SEED"] not in ("", None):
            try:
                data["SEED"] = int(data["SEED"])
            except (ValueError, TypeError):
                raise ValueError(f"SEED must be an int (got {data['SEED']})")

        if "ENTRY" in data:
            try:
                a, b = str(data["ENTRY"]).split(",", 1)
                data["ENTRY"] = (int(a.strip()), int(b.strip()))
            except (ValueError, TypeError):
                raise ValueError(f"ENTRY must be 'x,y' with 2 ints (got "
                                 f"{data['ENTRY']})")

        if "EXIT" in data:
            try:
                a, b = str(data["EXIT"]).split(",", 1)
                data["EXIT"] = (int(a.strip()), int(b.strip()))
            except (ValueError, TypeError):
                raise ValueError(f"EXIT must be 'x,y' with 2 ints (got "
                                 f"{data['EXIT']})")

        if "PERFECT" in data:
            v: str = str(data["PERFECT"]).strip().lower()
            if v == "true":
                data["PERFECT"] = True
            elif v == "false":
                data["PERFECT"] = False
            else:
                raise ValueError(f"PERFECT must be True or False (got "
                                 f"{data['PERFECT']})")

        return data


def read_config(filename: str) -> dict[str, str]:
    """Read a configuration file into a dictionary.

    The configuration file must contain one key-value pair per line,
    separated by "=". Empty lines and lines starting with "#" are
    ignored.

    Args:
        filename (str): Path to the configuration file.

    Returns:
        dict[str, str]: A dictionary mapping configuration keys to
        their corresponding string values.

    Raises:
        ValueError: If a non-empty, non-comment line does not contain
        the "=" separator.
        OSError: If the file cannot be opened or read.
    """
    cfg: dict[str, str] = {}
    with open(filename, "r") as f:
        for lineno, line in enumerate(f, start=1):
            s: str = line.strip()
            if not s or s.startswith("#"):
                continue
            if "=" not in s:
                raise ValueError(f"invalid line {lineno} (missing '=')")
            k, v = s.split("=", 1)
            cfg[k.strip()] = v.strip()
    return cfg


def verify_config(cfg: dict[str, str]) -> MazeConfig:
    """Validate a configuration dictionary using MazeConfig.

    This function validates and converts the raw configuration
    dictionary into a strongly typed ``MazeConfig`` instance using
    Pydantic model validation.

    Args:
        cfg (dict[str, str]): Raw configuration dictionary.

    Returns:
        MazeConfig: A validated and fully typed configuration object.

    Raises:
        ValidationError: If the configuration does not satisfy
        MazeConfig constraints.
    """
    maze_config: MazeConfig = MazeConfig.model_validate(cfg)
    return maze_config
