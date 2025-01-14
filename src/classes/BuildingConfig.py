from dataclasses import dataclass
from enum import Enum
from typing import Tuple

class Orientation(Enum):
    NORTH = 0  # Default - door faces north
    EAST = 1   # Rotated 90° clockwise
    SOUTH = 2  # Rotated 180°
    WEST = 3   # Rotated 270° clockwise

class RoofStyle(Enum):
    FLAT = 0
    PITCHED = 1
    PYRAMID = 2
    MANSARD = 3

@dataclass
class BuildingConfig:
    width: int
    length: int
    height: int
    door_height: int = 4
    door_width: int = 2
    window_size: int = 2
    window_height: int = 3
    roof_height: int = 3
    position: Tuple[int, int, int] = (0, 0, 0)
    orientation: Orientation = Orientation.NORTH  # Added orientation
    roof_style: RoofStyle = RoofStyle.PITCHED
    roof_overhang: int = 1  # Number of blocks to overhang
    roof_steepness: int = 2  # Higher number = steeper roof