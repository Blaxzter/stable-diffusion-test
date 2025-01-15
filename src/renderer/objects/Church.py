from src.classes.BuildingConfig import ChurchConfig, Orientation
from src.renderer.materials import Material
from src.renderer.objects.Building import Building


class Church(Building):
    """Class for generating church structures with bell tower"""

    def __init__(self, config: ChurchConfig):
        self.church_config = config
        super().__init__(config)

    def create_bell_tower(self):
        p = self.padding
        base_height = self.config.height
        tower_width = self.church_config.bell_tower_width

        # add tower base

        # Determine tower position based on orientation and preference
        if self.config.orientation in [Orientation.NORTH, Orientation.SOUTH]:
            if self.church_config.bell_tower_position == "left":
                tower_x = p - tower_width  # Place tower outside the left wall
            else:
                tower_x = p + self.config.length + 1  # Place tower outside the right wall
            tower_z = p + (self.config.width // 3)  # Place along the length
            tower_depth = tower_width
        else:  # EAST or WEST
            if self.church_config.bell_tower_position == "left":
                tower_z = p - tower_width  # Place tower outside the left wall
            else:
                tower_z = p + self.config.width + 1  # Place tower outside the right wall
            tower_x = p + (self.config.length // 3)  # Place along the length
            tower_depth = tower_width

        # Create tower base
        self.voxels[tower_x:tower_x + tower_width,
        1:self.church_config.bell_tower_height,
        tower_z:tower_z + tower_depth] = Material.STONE

        # Add windows to the tower
        window_levels = range(3, self.church_config.bell_tower_height - 3, 3)
        for y in window_levels:
            # Add windows on all four sides of the tower
            # Front
            self.voxels[tower_x + 1:tower_x + tower_width - 1,
            y:y + 2,
            tower_z:tower_z + 1] = Material.STAINED_GLASS
            # Back
            self.voxels[tower_x + 1:tower_x + tower_width - 1,
            y:y + 2,
            tower_z + tower_depth - 1:tower_z + tower_depth] = Material.STAINED_GLASS
            # Left
            self.voxels[tower_x:tower_x + 1,
            y:y + 2,
            tower_z + 1:tower_z + tower_depth - 1] = Material.STAINED_GLASS
            # Right
            self.voxels[tower_x + tower_width - 1:tower_x + tower_width,
            y:y + 2,
            tower_z + 1:tower_z + tower_depth - 1] = Material.STAINED_GLASS

        # Create tower roof (pyramid style)
        tower_top = self.church_config.bell_tower_height
        for i in range(3):  # 3 layers for the pyramid roof
            offset = i
            size = tower_width - (offset * 2)
            if size > 0:
                self.voxels[tower_x + offset:tower_x + tower_width - offset,
                tower_top + i:tower_top + i + 1,
                tower_z + offset:tower_z + tower_depth - offset] = Material.ROOF

        # Add small cross on top of the tower
        cross_x = tower_x + (tower_width // 2)
        cross_z = tower_z + (tower_depth // 2)
        # Vertical part
        self.voxels[cross_x:cross_x + 1,
        tower_top + 2:tower_top + 5,
        cross_z:cross_z + 1] = Material.STONE
        # Horizontal part
        self.voxels[cross_x - 1:cross_x + 2,
        tower_top + 3:tower_top + 4,
        cross_z:cross_z + 1] = Material.STONE

    def create_steeple(self):
        p = self.padding
        base_height = self.config.height
        # add roof height to base height
        roof_height = self.config.roof_height + 1
        base_height += roof_height

        # Adjust center based on bell tower position to balance the church
        if self.church_config.bell_tower_position == "left":
            center_x = self.config.length // 2 + p + 1  # Shift slightly right
        else:
            center_x = self.config.length // 2 + p - 1  # Shift slightly left
        center_z = self.config.width // 2 + p

        # Create wider steeple base (4x4)
        steeple_base_width = 4
        steeple_base_height = 3
        for y in range(base_height, base_height + steeple_base_height):
            offset = (steeple_base_width) // 2
            self.voxels[center_x - offset:center_x + offset,
            y:y + 1,
            center_z - offset:center_z + offset] = Material.STONE

        # Create tapering spire
        spire_height = self.church_config.steeple_height - steeple_base_height
        for y in range(base_height + steeple_base_height, base_height + self.church_config.steeple_height):
            progress = (y - (base_height + steeple_base_height)) / spire_height
            width = max(1, int(3 * (1 - progress)))
            offset = width // 2
            self.voxels[center_x - offset:center_x + width - offset,
            y:y + 1,
            center_z - offset:center_z + width - offset] = Material.STONE

        # Add cross at the top
        top_y = base_height + self.church_config.steeple_height
        self.voxels[center_x:center_x + 1,
        top_y:top_y + 3,
        center_z:center_z + 1] = Material.STONE
        self.voxels[center_x - 1:center_x + 2,
        top_y + 1:top_y + 2,
        center_z:center_z + 1] = Material.STONE

    def create_stained_glass(self):
        p = self.padding
        # Replace regular windows with stained glass and make them taller
        window_mask = self.voxels == Material.WINDOW
        self.voxels[window_mask] = Material.STAINED_GLASS

        # Create larger stained glass window at the front
        if self.config.orientation == Orientation.NORTH:
            self.voxels[p + self.config.length // 2 - 1:p + self.config.length // 2 + 2,
            2:self.config.height - 1,
            p:p + 1] = Material.STAINED_GLASS
        elif self.config.orientation == Orientation.SOUTH:
            self.voxels[p + self.config.length // 2 - 1:p + self.config.length // 2 + 2,
            2:self.config.height - 1,
            -p - 1:-p] = Material.STAINED_GLASS
        elif self.config.orientation == Orientation.EAST:
            self.voxels[-p - 1:-p,
            2:self.config.height - 1,
            p + self.config.width // 2 - 1:p + self.config.width // 2 + 2] = Material.STAINED_GLASS
        elif self.config.orientation == Orientation.WEST:
            self.voxels[p:p + 1,
            2:self.config.height - 1,
            p + self.config.width // 2 - 1:p + self.config.width // 2 + 2] = Material.STAINED_GLASS

    def generate(self):
        super().generate()
        if self.church_config.has_bell_tower:
            self.create_bell_tower()
        if self.church_config.has_steeple:
            self.create_steeple()
        if self.church_config.window_style == "stained_glass":
            self.create_stained_glass()