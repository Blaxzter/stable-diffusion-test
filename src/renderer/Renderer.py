from typing import List, Dict

import numpy as np
import open3d as o3d

from src.renderer.World import World
from src.renderer.materials import Material
from src.renderer.objects.Building import Building


class Renderer:
    """Class for rendering voxel structures using Open3D"""

    def __init__(self, scale_factor: float = 0.95):
        self.scale_factor = scale_factor
        self.color_map = {
            Material.AIR: [0, 0, 0],  # Transparent/black
            Material.FLOOR: [0.4, 0.4, 0.4],  # Gray
            Material.STONE: [0.8, 0.6, 0.4],  # Brown
            Material.ROOF: [0.8, 0.2, 0.2],  # Red
            Material.WINDOW: [0.3, 0.7, 0.9],  # Light blue
            Material.DOOR: [0.4, 0.2, 0.1],  # Dark brown
            Material.WOOL: [0.9, 0.9, 0.9],  # White
            Material.STAINED_GLASS: [0.3, 0.3, 0.3],  #
        }

    def _create_cube_mesh(
        self, center: np.ndarray, color: List[float]
    ) -> o3d.geometry.TriangleMesh:
        """Create a single cube mesh with the specified color"""
        vertices = (
            np.array(
                [
                    [-0.5, -0.5, -0.5],
                    [0.5, -0.5, -0.5],
                    [-0.5, 0.5, -0.5],
                    [0.5, 0.5, -0.5],
                    [-0.5, -0.5, 0.5],
                    [0.5, -0.5, 0.5],
                    [-0.5, 0.5, 0.5],
                    [0.5, 0.5, 0.5],
                ]
            )
            + center
        )

        triangles = np.array(
            [
                [0, 2, 1],
                [1, 2, 3],  # front
                [1, 3, 5],
                [5, 3, 7],  # right
                [5, 7, 4],
                [4, 7, 6],  # back
                [4, 6, 0],
                [0, 6, 2],  # left
                [2, 6, 3],
                [3, 6, 7],  # top
                [0, 1, 4],
                [4, 1, 5],  # bottom
            ]
        )

        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(vertices)
        mesh.triangles = o3d.utility.Vector3iVector(triangles)
        mesh.paint_uniform_color(color)
        mesh.compute_vertex_normals()
        return mesh

    def _get_color_for_material(self, material_id: int) -> List[float]:
        """Get color for a specific material ID"""
        return self.color_map.get(material_id, self.color_map[Material.STONE])

    def render_world(self, world: World):
        """Render the complete world with all objects"""
        meshes = []

        # Create meshes for all non-air voxels
        for position in np.argwhere(world.voxels != Material.AIR):
            material_id = world.voxels[tuple(position)]
            color = self._get_color_for_material(material_id)
            mesh = self._create_cube_mesh(position, color)
            mesh.scale(self.scale_factor, center=mesh.get_center())
            meshes.append(mesh)

        if meshes:
            # Combine all meshes
            combined_mesh = meshes[0]
            for mesh in meshes[1:]:
                combined_mesh += mesh

            # Configure visualization
            vis = o3d.visualization.Visualizer()
            vis.create_window()

            # Add the mesh
            vis.add_geometry(combined_mesh)

            # Configure render options
            render_option = vis.get_render_option()
            render_option.background_color = np.array(
                [0.7, 0.7, 0.7]
            )  # Light gray background
            render_option.point_size = 1
            render_option.show_coordinate_frame = True

            # Configure camera
            ctr = vis.get_view_control()
            ctr.set_zoom(0.8)
            ctr.set_lookat([world.world_size[0] / 2, 0, world.world_size[2] / 2])

            # Run visualization
            vis.run()
            vis.destroy_window()

    def set_color_scheme(self, color_map: Dict[str, List[float]]):
        """Update the color scheme for different materials"""
        # Convert string keys to Material enum values
        material_colors = {
            Material.FLOOR: color_map.get("floor", self.color_map[Material.FLOOR]),
            Material.STONE: color_map.get("wall", self.color_map[Material.STONE]),
            Material.ROOF: color_map.get("roof", self.color_map[Material.ROOF]),
        }
        self.color_map.update(material_colors)
