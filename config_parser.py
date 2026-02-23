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

    @model_validator(mode="before")
    @classmethod
    def convert_strings(cls, data: Any) -> Any:
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
    maze_config: MazeConfig = MazeConfig.model_validate(cfg)
    return maze_config
