import numpy as np
from typing import Dict, Any, List, Tuple
from enum import Enum

from src.renderer.Renderer import Renderer
from src.renderer.World import World
from src.classes.BuildingConfig import BuildingConfig, Orientation, RoofStyle, TowerConfig, ChurchConfig, ShopConfig
from src.renderer.objects.Building import Building
from src.renderer.objects.Church import Church
from src.renderer.objects.Shop import Shop
from src.renderer.objects.Tower import Tower


class DistrictType(Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    RELIGIOUS = "religious"
    MEDIEVAL = "medieval"
    MIXED = "mixed"


class CityPlanner:
    def __init__(self, world_size: Tuple[int, int, int]):
        self.world = World(world_size=world_size)
        self.world_size = world_size
        self.districts: Dict[DistrictType, List[Tuple[int, int, int, int]]] = {}
        self.building_count = 0

    def create_districts(self, district_size: int = 50):
        """Divide the city into districts"""
        x_districts = self.world_size[0] // district_size
        z_districts = self.world_size[2] // district_size

        # Create district map
        for x in range(x_districts):
            for z in range(z_districts):
                district_type = np.random.choice(list(DistrictType), p=[0.4, 0.3, 0.1, 0.1, 0.1])
                district_bounds = (
                    x * district_size,
                    (x + 1) * district_size,
                    z * district_size,
                    (z + 1) * district_size
                )
                if district_type not in self.districts:
                    self.districts[district_type] = []
                self.districts[district_type].append(district_bounds)

    def get_district_type(self, pos_x: int, pos_z: int) -> DistrictType:
        """Determine which district a position falls into"""
        for district_type, bounds_list in self.districts.items():
            for bounds in bounds_list:
                if (bounds[0] <= pos_x <= bounds[1] and
                        bounds[2] <= pos_z <= bounds[3]):
                    return district_type
        return DistrictType.MIXED

    def generate_building_config(self, district_type: DistrictType, pos: Tuple[int, int, int]) -> Any:
        """Generate appropriate building config based on district type"""
        base_ranges = {
            'width': (4, 12),
            'length': (4, 15),
            'height': (4, 10),
            'roof_height': (2, 4),
            'door_height': (3, 4),
            'window_height': (2, 3),
            'window_size': (1, 4)
        }

        if district_type == DistrictType.MEDIEVAL:
            return TowerConfig(
                width=np.random.randint(5, 8),
                length=np.random.randint(5, 8),
                height=np.random.randint(12, 20),
                num_floors=np.random.randint(3, 5),
                has_battlements=np.random.choice([True, False]),
                position=pos,
                orientation=np.random.choice(list(Orientation)),
                roof_style=RoofStyle.PYRAMID
            )

        elif district_type == DistrictType.RELIGIOUS:
            return ChurchConfig(
                width=np.random.randint(8, 15),
                length=np.random.randint(12, 20),
                height=np.random.randint(8, 12),
                has_steeple=True,
                steeple_height=np.random.randint(6, 10),
                position=pos,
                orientation=np.random.choice(list(Orientation)),
                roof_style=RoofStyle.PITCHED
            )

        elif district_type == DistrictType.COMMERCIAL:
            return ShopConfig(
                width=np.random.randint(6, 10),
                length=np.random.randint(8, 12),
                height=np.random.randint(4, 7),
                has_display_window=True,
                shop_type=np.random.choice(['bakery', 'blacksmith', 'tailor', 'general']),
                position=pos,
                orientation=np.random.choice(list(Orientation)),
                roof_style=np.random.choice([RoofStyle.FLAT, RoofStyle.PITCHED])
            )

        else:  # RESIDENTIAL or MIXED
            return BuildingConfig(
                width=np.random.randint(*base_ranges['width']),
                length=np.random.randint(*base_ranges['length']),
                height=np.random.randint(*base_ranges['height']),
                roof_height=np.random.randint(*base_ranges['roof_height']),
                door_height=np.random.randint(*base_ranges['door_height']),
                window_height=np.random.randint(*base_ranges['window_height']),
                window_size=np.random.randint(*base_ranges['window_size']),
                position=pos,
                orientation=np.random.choice(list(Orientation)),
                roof_style=np.random.choice(list(RoofStyle)),
                roof_overhang=np.random.randint(1, 3),
                roof_steepness=np.random.randint(1, 4)
            )

    def create_building(self, config: Any) -> Building:
        """Create appropriate building type based on config"""
        if isinstance(config, TowerConfig):
            return Tower(config)
        elif isinstance(config, ChurchConfig):
            return Church(config)
        elif isinstance(config, ShopConfig):
            return Shop(config)
        else:
            return Building(config)


def main():
    # Create a world with larger size to accommodate districts
    world_size = (400, 30, 400)
    city = CityPlanner(world_size)

    # Create districts
    city.create_districts(district_size=80)

    # Generate buildings
    num_buildings = 200
    attempts = 0
    max_attempts = 1000
    added_buildings = 0

    np.random.seed(42)  # For reproducible results

    while added_buildings < num_buildings and attempts < max_attempts:
        # Generate random position
        pos_x = np.random.randint(1, world_size[0] - 20)
        pos_z = np.random.randint(1, world_size[2] - 20)

        # Get district type for position
        district_type = city.get_district_type(pos_x, pos_z)

        # Generate appropriate config and building
        config = city.generate_building_config(district_type, (pos_x, 0, pos_z))
        building = city.create_building(config)

        # Try to add building
        if city.world.add_object(f"building_{added_buildings}", building):
            added_buildings += 1
            if added_buildings % 10 == 0:
                print(f"Added {added_buildings} buildings...")

        attempts += 1

    print(f"\nSuccessfully placed {added_buildings} buildings after {attempts} attempts")

    # Create renderer with enhanced color schemes
    renderer = Renderer(scale_factor=0.95)

    # Enhanced color schemes based on building types
    color_schemes = {
        'medieval': {
            'wall': [0.6, 0.6, 0.6],  # Gray stone
            'roof': [0.3, 0.3, 0.3],  # Dark gray
            'floor': [0.5, 0.5, 0.5]
        },
        'religious': {
            'wall': [0.9, 0.9, 0.8],  # Light stone
            'roof': [0.7, 0.2, 0.2],  # Red
            'floor': [0.6, 0.6, 0.6]
        },
        'commercial': {
            'wall': [0.8, 0.6, 0.4],  # Tan
            'roof': [0.4, 0.2, 0.1],  # Brown
            'floor': [0.5, 0.5, 0.5]
        },
        'residential': {
            'wall': [0.75, 0.55, 0.35],  # Wood
            'roof': [0.8, 0.2, 0.2],  # Red clay
            'floor': [0.4, 0.4, 0.4]
        }
    }

    # Set default color scheme
    renderer.set_color_scheme(color_schemes['residential'])

    # Configure and render the world
    print("Rendering world...")
    renderer.render_world(city.world)


if __name__ == "__main__":
    main()