import trimesh
import numpy as np
from shapely.geometry import Polygon
from shapely.affinity import scale as shapely_scale


def build_cookie_cutter_mesh(
    contour: Polygon,
    wall_thickness_mm: float = 2.0,
    height_mm: float = 20.0,
    image_size: tuple = (512, 512),
    output_size_mm: float = 80.0,
) -> trimesh.Trimesh:
    img_w, img_h = image_size
    scale = output_size_mm / max(img_w, img_h)

    scaled = Polygon([(x * scale, y * scale) for x, y in contour.exterior.coords])

    inner = scaled.buffer(-wall_thickness_mm)

    if inner.is_empty or inner.area < 1.0:
        raise ValueError(
            f"Wall thickness {wall_thickness_mm}mm is too large for this shape — "
            "nothing left inside. Try a smaller wall thickness or larger output size."
        )

    wall_polygon = scaled.difference(inner)

    mesh = trimesh.creation.extrude_polygon(wall_polygon, height=height_mm)

    if not mesh.is_watertight:
        trimesh.repair.fix_normals(mesh)
        trimesh.repair.fill_holes(mesh)

    return mesh
