from dataclasses import dataclass, asdict
from typing import Callable

import numpy as np


@dataclass
class Param:
    name: str
    label: str
    type: str                  # "int" | "float" | "select" | "bool"
    default: object
    min: float | None = None
    max: float | None = None
    step: float | None = None
    options: list[str] | None = None


@dataclass
class Tool:
    id: str
    name: str
    description: str
    params: list[Param]
    func: Callable[..., np.ndarray]

    def schema(self) -> dict:
        return {"id": self.id, "name": self.name, "description": self.description,
                "params": [asdict(p) for p in self.params]}


TOOLS: dict[str, Tool] = {}


def register(tool: Tool) -> Tool:
    TOOLS[tool.id] = tool
    return tool


def resolve_params(tool: Tool, raw: dict) -> dict:
    out = {}
    for p in tool.params:
        v = raw.get(p.name, p.default)
        try:
            if p.type in ("int", "float"):
                v = int(v) if p.type == "int" else float(v)
                if not p.min <= v <= p.max:
                    raise ValueError(f"{p.name} must be between {p.min} and {p.max}")
            elif p.type == "select":
                if v not in p.options:
                    raise ValueError(f"{p.name} must be one of {p.options}")
            elif p.type == "bool":
                v = bool(v)
        except TypeError:
            raise ValueError(f"Invalid value for {p.name}")
        out[p.name] = v
    return out