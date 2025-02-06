from typing import Tuple

import numpy as np

from src.renderer.objects.Building import Building
from src.renderer.materials import Material


class World:
    """Class to manage multiple objects in a shared world space"""

    def __init__(self, world_size: Tuple[int, int, int] = (50, 20, 50)):
        self.world_size = world_size
        self.voxels = np.zeros(world_size, dtype=np.int8)  # Changed to int8
        self.objects = {}  # Dictionary to store objects and their configurations

    def add_object(self, name: str, building: Building) -> bool:
        """Add an object to the world if space is available"""
        x, y, z = building.config.position
        obj_shape = building.voxels.shape

        # Check if the object fits within world bounds
        if (
            x + obj_shape[0] > self.world_size[0]
            or y + obj_shape[1] > self.world_size[1]
            or z + obj_shape[2] > self.world_size[2]
        ):
            print(
                f"Object {name} doesn't fit in the world at position {building.config.position}"
            )
            return False

        # Check if space is already occupied
        if np.any(
            self.voxels[
                x : x + obj_shape[0], y : y + obj_shape[1], z : z + obj_shape[2]
            ]
            != Material.AIR
        ):
            print(f"Space for object {name} is already occupied")
            return False

        # Add object to world
        self.voxels[
            x : x + obj_shape[0], y : y + obj_shape[1], z : z + obj_shape[2]
        ] = building.voxels
        self.objects[name] = building
        return True

    def remove_object(self, name: str):
        """Remove an object from the world"""
        if name in self.objects:
            building = self.objects[name]
            x, y, z = building.config.position
            obj_shape = building.voxels.shape

            # Clear voxels for this object
            self.voxels[
                x : x + obj_shape[0], y : y + obj_shape[1], z : z + obj_shape[2]
            ] = Material.AIR

            del self.objects[name]
