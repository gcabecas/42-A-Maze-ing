from typing import Any, Optional
from pydantic import BaseModel, Field, model_validator


class MazeConfig(BaseModel):
    """Maze configuration validated by Pydantic.

    Attributes:
        WIDTH: Maze width (must be > 0).
        HEIGHT: Maze height (must be > 0).
        ENTRY: Entry coordinates as (x, y).
        EXIT: Exit coordinates as (x, y).
        OUTPUT_FILE: Output filename (non-empty).
        PERFECT: Whether the maze must be perfect (single path).
        SEED: Optional random seed for reproducibility.
    """

    WIDTH: int = Field(gt=0)
    HEIGHT: int = Field(gt=0)
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str = Field(min_length=1)
    PERFECT: bool
    SEED: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def convert_strings(cls, data: Any) -> Any:
        """Convert raw string values from the config dict into proper types.

        Args:
            data: Raw config data (usually a dict[str, str]).

        Returns:
            The same dict after conversion.

        Raises:
            ValueError: If a value has a wrong format.
            TypeError: If a value has an unexpected type.
        """
        if not isinstance(data, dict):
            return data

        if "WIDTH" in data:
            try:
                data["WIDTH"] = int(data["WIDTH"])
            except (ValueError, TypeError):
                raise ValueError(
                    f"WIDTH must be an int (got {
                        data['WIDTH']})")

        if "HEIGHT" in data:
            try:
                data["HEIGHT"] = int(data["HEIGHT"])
            except (ValueError, TypeError):
                raise ValueError(
                    f"HEIGHT must be an int (got {
                        data['HEIGHT']})")

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
                raise ValueError(
                    f"ENTRY must be 'x,y' with 2 ints (got {
                        data['ENTRY']})")

        if "EXIT" in data:
            try:
                a, b = str(data["EXIT"]).split(",", 1)
                data["EXIT"] = (int(a.strip()), int(b.strip()))
            except (ValueError, TypeError):
                raise ValueError(
                    f"EXIT must be 'x,y' with 2 ints (got {
                        data['EXIT']})")

        if "PERFECT" in data:
            v: str = str(data["PERFECT"]).strip().lower()
            if v == "true":
                data["PERFECT"] = True
            elif v == "false":
                data["PERFECT"] = False
            else:
                raise ValueError(
                    f"PERFECT must be True or False (got {
                        data['PERFECT']})")

        return data


def read_config(filename: str) -> dict[str, str]:
    """Read a KEY=VALUE configuration file and return its content as a dict.

    Notes:
        - Empty lines are ignored.
        - Lines starting with '#' are ignored.
        - Every non-comment line must contain '='.

    Args:
        filename: Path to the config file.

    Returns:
        A dictionary mapping keys to raw string values.

    Raises:
        OSError: If the file cannot be opened.
        ValueError: If a non-comment line does not contain '='.
    """
    cfg: dict[str, str] = {}
    with open(filename, "r", encoding="utf-8") as f:
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
    """Validate and convert the raw config dict into a MazeConfig instance.

    Args:
        cfg: Raw config dictionary (values are usually strings).

    Returns:
        A validated MazeConfig object.

    Raises:
        pydantic.ValidationError: If validation fails.
    """
    return MazeConfig.model_validate(cfg)
