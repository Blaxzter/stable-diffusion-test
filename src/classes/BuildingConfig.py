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

@dataclass
class TowerConfig(BuildingConfig):
    num_floors: int = 3
    has_battlements: bool = True
    window_style: str = "arrow_slit"
    tower_cap_style: RoofStyle = RoofStyle.PYRAMID

@dataclass
class ChurchConfig(BuildingConfig):
    has_steeple: bool = True
    # filter voxels by material 

    steeple_height: int = 8
    window_style: str = "stained_glass"
    has_bell_tower: bool = True
    bell_tower_height: int = 18  # Taller than the main building
    bell_tower_width: int = 4    # Width of the tower
    bell_tower_position: str = "left"  # 'left' or 'right' side of the church

@dataclass
class ShopConfig(BuildingConfig):
    shop_type: str = "general"
    has_display_window: bool = True
    awning_style: str = "stripe"
    storage_room: bool = True