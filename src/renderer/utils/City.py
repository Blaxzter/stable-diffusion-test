import numpy as np

from src.classes.BuildingConfig import BuildingConfig, Orientation, RoofStyle
from src.renderer.Renderer import Renderer
from src.renderer.World import World
from src.renderer.objects.Building import Building


def main():
    # Create a world with larger size to accommodate more buildings
    world_size = (400, 30, 400)
    world = World(world_size=world_size)

    # Create random buildings
    buildings = []
    num_buildings = 200

    # Random building parameters ranges
    size_ranges = {
        'width': (4, 12),
        'length': (4, 15),
        'height': (4, 10),
        'roof_height': (2, 4),
        'door_height': (3, 4),
        'window_height': (2, 3),
        'window_size': (1, 4)
    }

    # Generate random buildings with retry on collision
    attempts = 0
    max_attempts = 1000
    added_buildings = 0

    np.random.seed(42)  # For reproducible results

    while added_buildings < num_buildings and attempts < max_attempts:
        # Generate random position
        pos_x = np.random.randint(1, world_size[0] - size_ranges['length'][1] - 2)
        pos_z = np.random.randint(1, world_size[2] - size_ranges['width'][1] - 2)

        # Generate random building config
        config = BuildingConfig(
            width=np.random.randint(*size_ranges['width']),
            length=np.random.randint(*size_ranges['length']),
            height=np.random.randint(*size_ranges['height']),
            roof_height=np.random.randint(*size_ranges['roof_height']),
            door_height=np.random.randint(*size_ranges['door_height']),
            window_height=np.random.randint(*size_ranges['window_height']),
            window_size=np.random.randint(*size_ranges['window_size']),
            position=(pos_x, 0, pos_z),
            orientation=np.random.choice(list(Orientation)),  # Random orientation
            roof_style=np.random.choice(list(RoofStyle)),  # Random roof style
            roof_overhang=np.random.randint(1, 3),
            roof_steepness=np.random.randint(1, 4)
        )

        # Try to add building
        building = Building(config)
        if world.add_object(f"house_{added_buildings}", building):
            added_buildings += 1
            if added_buildings % 10 == 0:
                print(f"Added {added_buildings} buildings...")

        attempts += 1

    print(f"\nSuccessfully placed {added_buildings} buildings after {attempts} attempts")

    # Create renderer with custom settings
    renderer = Renderer(scale_factor=0.95)

    # Create a more varied color scheme
    color_variations = [
        # Various wall colors (earth tones)
        {'wall': [0.7, 0.5, 0.3]},  # Brown
        {'wall': [0.8, 0.6, 0.4]},  # Light brown
        {'wall': [0.6, 0.4, 0.2]},  # Dark brown
        {'wall': [0.75, 0.55, 0.35]},  # Medium brown
        {'wall': [0.85, 0.65, 0.45]},  # Tan

        # Various roof colors
        {'roof': [0.9, 0.2, 0.2]},  # Bright red
        {'roof': [0.7, 0.1, 0.1]},  # Dark red
        {'roof': [0.8, 0.3, 0.1]},  # Orange-red
        {'roof': [0.6, 0.2, 0.2]},  # Deep red
        {'roof': [0.85, 0.15, 0.15]}  # Medium red
    ]

    # Combine all color variations into one scheme
    combined_colors = {
        'wall': [0.75, 0.55, 0.35],  # Default wall color
        'roof': [0.8, 0.2, 0.2],  # Default roof color
        'floor': [0.4, 0.4, 0.4]  # Floor color
    }

    renderer.set_color_scheme(combined_colors)

    # Configure and render the world
    print("Rendering world...")
    renderer.render_world(world)


if __name__ == "__main__":
    main()