import numpy as np
import trimesh
from shapely.geometry import Polygon


def _wall_profile(wall_thickness, height, chamfer, lip_height, lip_width):
    """2D wall cross-section in profile-space coordinates.

    Coordinate convention (matches trimesh.creation.sweep_polygon on a CCW path):
      x = 0        : outer surface (where the path runs)
      x > 0        : inward  (toward cookie center)
      x < 0        : outward (away from cookie center, where the lip goes)
      y = 0        : bottom / cutting edge  (path level = world z=0)
      y < 0        : upward in world z      (y=-h maps to world z=+h)
    """
    z1 = min(chamfer,     height * 0.4) if chamfer    > 0 else 0.0
    z2 = max(height - lip_height, height * 0.6) if lip_height > 0 and lip_width > 0 else height
    z3 = height
    w  = wall_thickness
    lw = lip_width if lip_width > 0 and lip_height > 0 else 0.0

    if z1 > 0 and lw > 0:
        verts = [(0, 0), (-w, -z1), (-w, -z2), (-w - lw, -z3), (0, -z3)]
    elif z1 > 0:
        verts = [(0, 0), (-w, -z1), (-w, -z3), (0, -z3)]
    elif lw > 0:
        verts = [(0, 0), (-w, 0), (-w, -z2), (-w - lw, -z3), (0, -z3)]
    else:
        verts = [(0, 0), (-w, 0), (-w, -z3), (0, -z3)]

    return Polygon(verts)


def build_cookie_cutter_mesh(
    contour: Polygon,
    wall_thickness_mm: float = 2.0,
    height_mm: float = 20.0,
    chamfer_mm: float = 3.0,
    lip_height_mm: float = 3.0,
    lip_width_mm: float = 3.0,
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
            "nothing left inside. Try a smaller value or larger output size."
        )

    profile = _wall_profile(wall_thickness_mm, height_mm, chamfer_mm, lip_height_mm, lip_width_mm)

    # Path: outer contour as a closed 3D loop at z=0
    # Shapely's exterior.coords includes the closing point (first == last), which
    # trimesh.sweep_polygon + connect=True uses to close the tube into a watertight mesh.
    pts = np.array([(x, y, 0.0) for x, y in scaled.exterior.coords])
    return trimesh.creation.sweep_polygon(profile, pts, connect=True)
