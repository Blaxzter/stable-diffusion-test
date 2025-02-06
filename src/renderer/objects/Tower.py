from src.classes.BuildingConfig import TowerConfig
from src.renderer.materials import Material
from src.renderer.objects.Building import Building


class Tower(Building):
    """Class for generating tower structures"""

    def __init__(self, config: TowerConfig):
        self.tower_config = config
        super().__init__(config)

    def create_battlements(self):
        p = self.padding
        height = self.config.height

        # Create merlon pattern (raised sections)
        for i in range(p, self.voxels.shape[0] - p, 2):
            self.voxels[i : i + 1, height : height + 2, p:-p] = Material.STONE
            self.voxels[p:-p, height : height + 2, i : i + 1] = Material.STONE

    def create_floor_markers(self):
        p = self.padding
        for floor in range(1, self.tower_config.num_floors + 1):
            height = (self.config.height // self.tower_config.num_floors) * floor
            self.voxels[p:-p, height : height + 1, p:-p] = Material.FLOOR

    def generate(self):
        super().generate()
        if self.tower_config.has_battlements:
            # remove roof
            self.voxels[self.voxels == Material.ROOF] = Material.AIR
            self.create_battlements()
        self.create_floor_markers()
