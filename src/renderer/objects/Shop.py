from src.classes.BuildingConfig import ShopConfig, Orientation
from src.renderer.materials import Material
from src.renderer.objects.Building import Building


class Shop(Building):
    """Class for generating shop structures"""

    def __init__(self, config: ShopConfig):
        self.shop_config = config
        super().__init__(config)

    def create_display_window(self):
        p = self.padding
        # Create larger window at front based on orientation
        if self.config.orientation == Orientation.NORTH:
            self.voxels[p + 2:-p - 2, 1:4, p:p + 1] = Material.WINDOW
        elif self.config.orientation == Orientation.SOUTH:
            self.voxels[p + 2:-p - 2, 1:4, -p - 1:-p] = Material.WINDOW
        elif self.config.orientation == Orientation.EAST:
            self.voxels[-p - 1:-p, 1:4, p + 2:-p - 2] = Material.WINDOW
        elif self.config.orientation == Orientation.WEST:
            self.voxels[p:p + 1, 1:4, p + 2:-p - 2] = Material.WINDOW

    def create_awning(self):
        p = self.padding
        height = 4  # Above display window

        # Create awning based on orientation
        if self.config.orientation == Orientation.NORTH:
            self.voxels[p + 1:-p - 1, height:height + 1, p - 1:p + 2] = Material.WOOL
        elif self.config.orientation == Orientation.SOUTH:
            self.voxels[p + 1:-p - 1, height:height + 1, -p - 2:-p + 1] = Material.WOOL
        elif self.config.orientation == Orientation.EAST:
            self.voxels[-p - 2:-p + 1, height:height + 1, p + 1:-p - 1] = Material.WOOL
        elif self.config.orientation == Orientation.WEST:
            self.voxels[p - 1:p + 2, height:height + 1, p + 1:-p - 1] = Material.WOOL

    def generate(self):
        super().generate()
        if self.shop_config.has_display_window:
            self.create_display_window()
        self.create_awning()