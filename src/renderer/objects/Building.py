import numpy as np
from enum import Enum
from src.renderer.materials import Material
from src.classes.BuildingConfig import BuildingConfig, Orientation, RoofStyle
from src.renderer.objects.parts.Roof import Roof


class Building:
    """Class for generating building structures"""

    def __init__(self, config: BuildingConfig):
        self.config = config
        # Create expanded voxel space with padding for overhangs
        padding = max(self.config.roof_overhang, 20)  # minimum padding of 2 for windows
        self.padding = padding
        self.voxels = np.zeros(
            (
                config.length + 1 + (padding * 2),
                config.height + config.roof_height + 1 + padding,
                config.width + 1 + (padding * 2),
            ),
            dtype=np.int8,
        )
        self.generate()
        self.trim_to_size()

    def get_used_bounds(self):
        """Calculate the actual used space bounds"""
        # Find non-zero elements
        non_zero = np.nonzero(self.voxels)
        if len(non_zero[0]) == 0:  # If array is empty
            return (0, 0), (0, 0), (0, 0)

        # Get min and max for each dimension
        x_min, x_max = np.min(non_zero[0]), np.max(non_zero[0])
        y_min, y_max = np.min(non_zero[1]), np.max(non_zero[1])
        z_min, z_max = np.min(non_zero[2]), np.max(non_zero[2])

        return (x_min, x_max), (y_min, y_max), (z_min, z_max)

    def trim_to_size(self):
        """Trim the voxel space to the actually used space"""
        (x_min, x_max), (y_min, y_max), (z_min, z_max) = self.get_used_bounds()
        self.voxels = self.voxels[
            x_min : x_max + 1, y_min : y_max + 1, z_min : z_max + 1
        ]

    def create_floor(self):
        # Offset by padding
        p = self.padding
        self.voxels[p:-p, 0:1, p:-p] = Material.FLOOR

    def create_walls(self):
        p = self.padding
        # Front and back walls
        self.voxels[p:-p, 1 : self.config.height + 1, p : p + 1] = Material.STONE
        self.voxels[p:-p, 1 : self.config.height + 1, -p - 1 : -p] = Material.STONE
        # Side walls
        self.voxels[p : p + 1, 1 : self.config.height + 1, p:-p] = Material.STONE
        self.voxels[-p - 1 : -p, 1 : self.config.height + 1, p:-p] = Material.STONE

    def create_door(self):
        p = self.padding
        # Create door based on orientation
        if self.config.orientation == Orientation.NORTH:
            door_pos = self.config.length // 2 + p
            self.voxels[
                door_pos - 1 : door_pos + 1, 1 : self.config.door_height + 1, p : p + 1
            ] = Material.DOOR
        elif self.config.orientation == Orientation.SOUTH:
            door_pos = self.config.length // 2 + p
            self.voxels[
                door_pos - 1 : door_pos + 1,
                1 : self.config.door_height + 1,
                -p - 1 : -p,
            ] = Material.DOOR
        elif self.config.orientation == Orientation.EAST:
            door_pos = self.config.width // 2 + p
            self.voxels[
                -p - 1 : -p,
                1 : self.config.door_height + 1,
                door_pos - 1 : door_pos + 1,
            ] = Material.DOOR
        elif self.config.orientation == Orientation.WEST:
            door_pos = self.config.width // 2 + p
            self.voxels[
                p : p + 1, 1 : self.config.door_height + 1, door_pos - 1 : door_pos + 1
            ] = Material.DOOR

    def create_windows(self):
        p = self.padding
        window_spacing = 3

        def create_window_row(
            start_idx, end_idx, height_range, wall_idx, is_length_wall=True
        ):
            """Helper function to create a row of windows"""
            window_positions = np.arange(
                start_idx + window_spacing, end_idx - window_spacing, window_spacing * 2
            )
            for pos in window_positions:
                if is_length_wall:
                    self.voxels[
                        pos + p : pos + p + self.config.window_size,
                        height_range[0] : height_range[1],
                        wall_idx,
                    ] = Material.WINDOW
                else:
                    self.voxels[
                        wall_idx,
                        height_range[0] : height_range[1],
                        pos + p : pos + p + self.config.window_size,
                    ] = Material.WINDOW

        # Window height range
        height_range = (
            self.config.window_height,
            self.config.window_height + self.config.window_size,
        )

        # Front windows (North)
        create_window_row(0, self.config.length, height_range, self.padding, True)

        # Back windows (South)
        create_window_row(0, self.config.length, height_range, -self.padding - 1, True)

        # Left windows (West)
        create_window_row(0, self.config.width, height_range, self.padding, False)

        # Right windows (East)
        create_window_row(0, self.config.width, height_range, -self.padding - 1, False)

        # Add second row of windows if building is tall enough
        if self.config.height >= 7:
            second_height_range = (self.config.height - 2, self.config.height - 1)

            create_window_row(
                0, self.config.length, second_height_range, self.padding, True
            )
            create_window_row(
                0, self.config.length, second_height_range, -self.padding - 1, True
            )
            create_window_row(
                0, self.config.width, second_height_range, self.padding, False
            )
            create_window_row(
                0, self.config.width, second_height_range, -self.padding - 1, False
            )

    def create_roof(self):
        roof = Roof(self.voxels, self)
        roof.create_roof()

    def generate(self):
        """Generate the complete building structure"""
        self.create_floor()
        self.create_walls()
        self.create_windows()
        self.create_door()
        self.create_roof()

    def rotate(self, new_orientation: Orientation):
        """Rotate the building to a new orientation"""
        # Store current state
        current_voxels = self.voxels.copy()

        # If rotating 90° or 270°, swap length and width
        if abs(new_orientation.value - self.config.orientation.value) % 2 == 1:
            self.voxels = np.zeros(
                (
                    self.config.width + 1 + (self.padding * 2),
                    self.config.height + self.config.roof_height + 1 + self.padding,
                    self.config.length + 1 + (self.padding * 2),
                ),
                dtype=np.int8,
            )
            # Swap length and width in config
            self.config.length, self.config.width = (
                self.config.width,
                self.config.length,
            )

        # Perform rotation
        rotations = (new_orientation.value - self.config.orientation.value) % 4
        self.voxels = np.rot90(current_voxels, k=rotations, axes=(0, 2))

        # Update orientation
        self.config.orientation = new_orientation
        self.trim_to_size()
