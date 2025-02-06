import json
from enum import Enum
from datetime import datetime
from pathlib import Path

import numpy as np

from src.classes.BuildingConfig import (
    BuildingConfig,
    TowerConfig,
    ChurchConfig,
    ShopConfig,
    Orientation,
    RoofStyle,
)
from src.dataset.utils import ComplexEncoder
from src.renderer.objects.Building import Building
from src.renderer.objects.Church import Church
from src.renderer.objects.Shop import Shop
from src.renderer.objects.Tower import Tower


class BuildingStyle(Enum):
    RESIDENTIAL = "residential"
    TOWER = "tower"
    CHURCH = "church"
    SHOP = "shop"


class BuildingDatasetGenerator:
    def __init__(self, output_path: str = "building_dataset"):
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

    def generate_dataset(self, buildings_per_style: int = 250):
        dataset = []

        for style in BuildingStyle:
            print(f"Generating {style.value} buildings...")
            for i in range(buildings_per_style):
                # Generate building
                config = self._generate_config(style)
                building = self._create_building(config)

                # Store data
                building_data = {
                    "voxels": building.voxels.tolist(),
                    "style": style.value,
                    "prompt": self._generate_prompt(style, config),
                    "config": config.__dict__,
                }
                dataset.append(building_data)

        # Find maximum dimensions
        max_x = max(len(d["voxels"]) for d in dataset)
        max_y = max(len(d["voxels"][0]) if len(d["voxels"]) > 0 else 0 for d in dataset)
        max_z = max(
            (
                len(d["voxels"][0][0])
                if len(d["voxels"]) > 0 and len(d["voxels"][0]) > 0
                else 0
            )
            for d in dataset
        )

        print(f"Maximum dimensions: {max_x}x{max_y}x{max_z}")

        # Pad all voxels to the same size
        padded_voxels = []
        for d in dataset:
            voxels = np.array(d["voxels"])
            padded = np.zeros((max_x, max_y, max_z), dtype=voxels.dtype)
            padded[: voxels.shape[0], : voxels.shape[1], : voxels.shape[2]] = voxels
            padded_voxels.append(padded)

        # Save dataset
        print("Saving dataset...")
        voxels_array = np.array(padded_voxels)
        np.save(self.output_path / "voxels.npy", voxels_array)
        print(f"Dataset voxels shape: {voxels_array.shape}")

        # Save metadata
        metadata = [
            {"style": d["style"], "prompt": d["prompt"], "config": d["config"]}
            for d in dataset
        ]

        with open(self.output_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2, cls=ComplexEncoder)

    def _generate_config(self, style: BuildingStyle) -> BuildingConfig:
        pos = (0, 0, 0)
        orientation = np.random.choice(list(Orientation))

        if style == BuildingStyle.TOWER:
            return TowerConfig(
                width=np.random.randint(5, 8),
                length=np.random.randint(5, 8),
                height=np.random.randint(12, 20),
                num_floors=np.random.randint(3, 5),
                has_battlements=np.random.choice([True, False]),
                position=pos,
                orientation=orientation,
                roof_style=RoofStyle.PYRAMID,
            )

        elif style == BuildingStyle.CHURCH:
            return ChurchConfig(
                width=np.random.randint(8, 15),
                length=np.random.randint(12, 20),
                height=np.random.randint(8, 12),
                has_steeple=True,
                steeple_height=np.random.randint(6, 10),
                position=pos,
                orientation=orientation,
                roof_style=RoofStyle.PITCHED,
            )

        elif style == BuildingStyle.SHOP:
            return ShopConfig(
                width=np.random.randint(6, 10),
                length=np.random.randint(8, 12),
                height=np.random.randint(4, 7),
                has_display_window=True,
                shop_type=np.random.choice(
                    ["bakery", "blacksmith", "tailor", "general"]
                ),
                position=pos,
                orientation=orientation,
                roof_style=np.random.choice([RoofStyle.FLAT, RoofStyle.PITCHED]),
            )

        else:  # RESIDENTIAL
            return BuildingConfig(
                width=np.random.randint(4, 12),
                length=np.random.randint(4, 15),
                height=np.random.randint(4, 10),
                roof_height=np.random.randint(2, 4),
                door_height=np.random.randint(3, 4),
                window_height=np.random.randint(2, 3),
                window_size=np.random.randint(1, 4),
                position=pos,
                orientation=orientation,
                roof_style=np.random.choice(list(RoofStyle)),
            )

    def _create_building(self, config: BuildingConfig) -> Building:
        if isinstance(config, TowerConfig):
            return Tower(config)
        elif isinstance(config, ChurchConfig):
            return Church(config)
        elif isinstance(config, ShopConfig):
            return Shop(config)
        else:
            return Building(config)

    def _generate_prompt(self, style: BuildingStyle, config: BuildingConfig) -> str:
        base = f"A {style.value} style voxel building"

        if style == BuildingStyle.TOWER:
            features = [
                f"{config.height}m tall medieval tower",
                f"{'with' if config.has_battlements else 'without'} battlements",
                f"{config.num_floors} floors",
            ]
        elif style == BuildingStyle.CHURCH:
            features = [
                "gothic church",
                f"with {config.steeple_height}m tall steeple",
                f"{config.width}x{config.length}m footprint",
            ]
        elif style == BuildingStyle.SHOP:
            features = [
                f"{config.shop_type} shop",
                "with display windows",
                f"{config.roof_style.name.lower()} roof",
            ]
        else:
            features = [
                f"{config.width}x{config.length}m footprint",
                f"{config.height}m tall",
                f"{config.roof_style.name.lower()} roof",
            ]

        return f"{base} - {', '.join(features)}"


if __name__ == "__main__":
    dataset_path = Path("training_data")
    current_date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    buildings_per_style = 250
    dataset_path = (
        dataset_path / f"n{buildings_per_style}_training_data_{current_date_str}"
    )

    generator = BuildingDatasetGenerator(dataset_path)
    generator.generate_dataset(buildings_per_style=buildings_per_style)
