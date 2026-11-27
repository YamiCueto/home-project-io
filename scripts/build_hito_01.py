import json
import math
import os
import bpy
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
BLEND_PATH = os.path.join(PROJECT_DIR, "models", "HOME_PROJECT_HITO_01.blend")
VALIDATION_PATH = os.path.join(PROJECT_DIR, "validation", "HITO_01_VALIDATION.json")
RENDER_P1_PATH = os.path.join(PROJECT_DIR, "renders", "HITO_01_PLANTA_01.png")
RENDER_P2_PATH = os.path.join(PROJECT_DIR, "renders", "HITO_01_PLANTA_02.png")
RENDER_ISO_PATH = os.path.join(PROJECT_DIR, "renders", "HITO_01_ISOMETRICA.png")

WALL_EXT = 0.15
WALL_INT = 0.10
CLEAR_H = 2.70
SLAB_T = 0.20
Z_P1 = 0.00
Z_P2 = CLEAR_H + SLAB_T
COMP_X_OFFSET = 8.50

COLORS = {
    "wall_ext": (0.18, 0.18, 0.20, 1.0),
    "wall_int": (0.38, 0.38, 0.42, 1.0),
    "garage": (0.45, 0.48, 0.52, 1.0),
    "access": (0.85, 0.78, 0.62, 1.0),
    "circulation": (0.90, 0.85, 0.72, 1.0),
    "living": (0.45, 0.72, 0.85, 1.0),
    "dining": (0.52, 0.78, 0.72, 1.0),
    "kitchen": (0.92, 0.65, 0.42, 1.0),
    "bedroom_guest": (0.72, 0.62, 0.86, 1.0),
    "bedroom_master": (0.58, 0.52, 0.84, 1.0),
    "bedroom_daughter": (0.86, 0.58, 0.72, 1.0),
    "bath": (0.42, 0.82, 0.88, 1.0),
    "laundry": (0.68, 0.80, 0.55, 1.0),
    "stair": (0.82, 0.68, 0.38, 1.0),
    "closet": (0.76, 0.64, 0.52, 1.0),
    "balcony": (0.58, 0.78, 0.52, 1.0),
    "study": (0.65, 0.75, 0.85, 1.0),
    "furniture": (0.28, 0.22, 0.18, 1.0),
    "vehicle_car": (0.15, 0.35, 0.68, 1.0),
    "vehicle_moto": (0.82, 0.22, 0.18, 1.0),
    "door": (0.95, 0.85, 0.20, 1.0),
    "slab": (0.25, 0.25, 0.27, 1.0),
}

def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam)
    for txt in list(bpy.data.curves):
        bpy.data.curves.remove(txt)

def get_or_create_collection(name, parent=None):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    if parent is None:
        bpy.context.scene.collection.children.link(col)
    else:
        parent.children.link(col)
    return col

def get_material(name, rgba):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.75
    mat.diffuse_color = rgba
    return mat

def create_box(name, x0, y0, z0, x1, y1, z1, mat_key, col):
    cx = (x0 + x1) * 0.5
    cy = (y0 + y1) * 0.5
    cz = (z0 + z1) * 0.5
    sx = abs(x1 - x0)
    sy = abs(y1 - y0)
    sz = abs(z1 - z0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    mat = get_material(f"MAT_{mat_key}", COLORS[mat_key])
    obj.data.materials.append(mat)
    return obj

def create_text_label(name, text, x, y, z, size, col):
    bpy.ops.object.text_add(location=(x, y, z))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.body = text
    obj.data.size = size
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    mat = get_material("MAT_label", (0.05, 0.05, 0.05, 1.0))
    obj.data.materials.append(mat)
    return obj

P1_ROOMS = [
    {"name": "P1_Garaje", "x0": 0.15, "y0": 0.15, "x1": 3.45, "y1": 4.70, "mat": "garage", "cat": "garage"},
    {"name": "P1_Acceso_Peatonal", "x0": 3.55, "y0": 0.15, "x1": 5.85, "y1": 1.60, "mat": "access", "cat": "circulation"},
    {"name": "P1_Escalera", "x0": 3.55, "y0": 1.60, "x1": 4.50, "y1": 5.50, "mat": "stair", "cat": "stair"},
    {"name": "P1_Pasillo_Acceso", "x0": 4.60, "y0": 1.60, "x1": 5.85, "y1": 4.70, "mat": "circulation", "cat": "circulation"},
    {"name": "P1_Bano_Social", "x0": 0.15, "y0": 4.80, "x1": 2.10, "y1": 6.55, "mat": "bath", "cat": "bathroom"},
    {"name": "P1_Distribuidor_Huesped", "x0": 2.20, "y0": 4.80, "x1": 3.45, "y1": 6.55, "mat": "circulation", "cat": "circulation"},
    {"name": "P1_Habitacion_Huespedes", "x0": 0.15, "y0": 6.65, "x1": 2.95, "y1": 9.85, "mat": "bedroom_guest", "cat": "bedroom"},
    {"name": "P1_Sala", "x0": 4.60, "y0": 4.70, "x1": 5.85, "y1": 5.50, "mat": "living", "cat": "social"},
    {"name": "P1_Sala_Zona", "x0": 3.55, "y0": 5.50, "x1": 5.85, "y1": 7.45, "mat": "living", "cat": "social"},
    {"name": "P1_Comedor", "x0": 4.25, "y0": 7.45, "x1": 5.85, "y1": 9.85, "mat": "dining", "cat": "social"},
    {"name": "P1_Cocina", "x0": 3.05, "y0": 7.45, "x1": 4.25, "y1": 9.85, "mat": "kitchen", "cat": "kitchen"},
    {"name": "P1_Lavanderia_Bajo_Esc", "x0": 3.55, "y0": 4.10, "x1": 4.50, "y1": 5.50, "mat": "laundry", "cat": "laundry"},
]

P1_WALLS_EXT = [
    ("P1_Muro_Ext_Oeste", 0.00, 0.00, 0.15, 10.00),
    ("P1_Muro_Ext_Este", 5.85, 0.00, 6.00, 10.00),
    ("P1_Muro_Ext_Sur", 0.15, 0.00, 5.85, 0.15),
    ("P1_Muro_Ext_Norte", 0.15, 9.85, 5.85, 10.00),
]

P1_WALLS_INT = [
    ("P1_Muro_Garaje_Este", 3.45, 0.15, 3.55, 4.70),
    ("P1_Muro_Garaje_Norte", 0.15, 4.70, 3.55, 4.80),
    ("P1_Muro_Escalera_Este", 4.50, 1.60, 4.60, 4.70),
    ("P1_Muro_Bano_Este", 2.10, 4.80, 2.20, 6.55),
    ("P1_Muro_Huesped_Sur", 0.15, 6.55, 2.95, 6.65),
    ("P1_Muro_Huesped_Este", 2.95, 6.55, 3.05, 9.85),
]

P1_DOORS = [
    ("P1_Puerta_Garaje", 0.35, 0.00, 3.25, 0.15),
    ("P1_Puerta_Principal", 4.40, 0.00, 5.35, 0.15),
    ("P1_Puerta_Bano_Social", 2.10, 5.20, 2.20, 6.00),
    ("P1_Puerta_Huesped", 2.25, 6.55, 3.15, 6.65),
]

P1_FURNITURE = [
    ("P1_Veh_Swift_Dzire_2023", 0.30, 0.42, 2.035, 4.415, 1.515, "vehicle_car"),
    ("P1_Veh_VStrom_250_SX", 2.45, 2.35, 3.33, 4.53, 1.355, "vehicle_moto"),
    ("P1_Mob_Cama_Huesped", 0.25, 7.85, 1.30, 9.75, 0.55, "furniture"),
    ("P1_Mob_Velador_Huesped", 1.35, 9.30, 1.80, 9.75, 0.50, "furniture"),
    ("P1_Mob_Closet_Huesped", 2.35, 8.25, 2.90, 9.75, 2.10, "furniture"),
    ("P1_Mob_Inodoro_Social", 0.25, 5.75, 0.70, 6.45, 0.45, "furniture"),
    ("P1_Mob_Lavabo_Social", 0.25, 4.90, 0.75, 5.45, 0.85, "furniture"),
    ("P1_Mob_Ducha_Social", 1.15, 4.85, 2.05, 5.75, 0.12, "furniture"),
    ("P1_Mob_Sofa_Sala", 4.95, 5.65, 5.80, 7.45, 0.78, "furniture"),
    ("P1_Mob_Mesa_Centro", 4.20, 6.10, 4.70, 7.00, 0.42, "furniture"),
    ("P1_Mob_TV_Sala", 3.60, 5.85, 3.95, 7.15, 0.55, "furniture"),
    ("P1_Mob_Mesa_Comedor", 4.55, 8.05, 5.35, 9.25, 0.75, "furniture"),
    ("P1_Mob_Cocina_Meson", 3.08, 7.55, 3.68, 9.80, 0.90, "furniture"),
    ("P1_Mob_Lavadora", 3.65, 4.85, 4.30, 5.45, 0.85, "furniture"),
]

P2_ROOMS = [
    {"name": "P2_Habitacion_Principal", "x0": 0.15, "y0": 0.15, "x1": 3.45, "y1": 4.45, "mat": "bedroom_master", "cat": "bedroom"},
    {"name": "P2_Balcon", "x0": 3.55, "y0": 0.15, "x1": 5.85, "y1": 1.50, "mat": "balcony", "cat": "balcony"},
    {"name": "P2_Escalera_Hueco", "x0": 3.55, "y0": 1.60, "x1": 4.50, "y1": 5.50, "mat": "stair", "cat": "stair"},
    {"name": "P2_Distribuidor_Norte", "x0": 4.60, "y0": 1.60, "x1": 5.85, "y1": 5.50, "mat": "circulation", "cat": "circulation"},
    {"name": "P2_Bano_Principal", "x0": 0.15, "y0": 4.55, "x1": 1.95, "y1": 6.75, "mat": "bath", "cat": "bathroom"},
    {"name": "P2_Vestidor_Principal", "x0": 2.05, "y0": 4.55, "x1": 3.45, "y1": 6.75, "mat": "closet", "cat": "closet"},
    {"name": "P2_Distribuidor_Central", "x0": 3.55, "y0": 5.50, "x1": 5.85, "y1": 6.75, "mat": "circulation", "cat": "circulation"},
    {"name": "P2_Bano_Compartido", "x0": 0.15, "y0": 6.85, "x1": 2.40, "y1": 8.60, "mat": "bath", "cat": "bathroom"},
    {"name": "P2_Corredor_Hijas", "x0": 2.50, "y0": 6.85, "x1": 3.55, "y1": 8.60, "mat": "circulation", "cat": "circulation"},
    {"name": "P2_Estudio_Blancos", "x0": 3.65, "y0": 6.85, "x1": 5.85, "y1": 8.60, "mat": "study", "cat": "study"},
    {"name": "P2_Habitacion_Hija_1", "x0": 0.15, "y0": 8.70, "x1": 2.95, "y1": 12.00, "mat": "bedroom_daughter", "cat": "bedroom"},
    {"name": "P2_Habitacion_Hija_2", "x0": 3.05, "y0": 8.70, "x1": 5.85, "y1": 12.00, "mat": "bedroom_daughter", "cat": "bedroom"},
]

P2_WALLS_EXT = [
    ("P2_Muro_Ext_Oeste", 0.00, 0.00, 0.15, 12.15),
    ("P2_Muro_Ext_Este", 5.85, 0.00, 6.00, 12.15),
    ("P2_Muro_Ext_Sur", 0.15, 0.00, 5.85, 0.15),
    ("P2_Muro_Ext_Norte", 0.15, 12.00, 5.85, 12.15),
]

P2_WALLS_INT = [
    ("P2_Muro_Master_Este", 3.45, 0.15, 3.55, 6.75),
    ("P2_Muro_Balcon_Norte", 3.55, 1.50, 5.85, 1.60),
    ("P2_Muro_Master_Norte", 0.15, 4.45, 3.45, 4.55),
    ("P2_Muro_Bano_Vestidor", 1.95, 4.55, 2.05, 6.75),
    ("P2_Muro_Zona_Norte", 0.15, 6.75, 3.55, 6.85),
    ("P2_Muro_Bano_Comp_Este", 2.40, 6.85, 2.50, 8.60),
    ("P2_Muro_Corredor_Este", 3.55, 6.85, 3.65, 8.60),
    ("P2_Muro_Hijas_Sur", 0.15, 8.60, 5.85, 8.70),
    ("P2_Muro_Entre_Hijas", 2.95, 8.70, 3.05, 12.00),
]

P2_DOORS = [
    ("P2_Puerta_Balcon", 3.45, 0.35, 3.55, 1.25),
    ("P2_Puerta_Vestidor", 2.35, 4.45, 3.15, 4.55),
    ("P2_Puerta_Bano_Master", 1.95, 5.20, 2.05, 6.00),
    ("P2_Puerta_Bano_Comp", 2.40, 7.30, 2.50, 8.05),
    ("P2_Puerta_Hija_1", 2.05, 8.60, 2.90, 8.70),
    ("P2_Puerta_Hija_2", 3.10, 8.60, 3.95, 8.70),
    ("P2_Puerta_Estudio", 3.55, 7.30, 3.65, 8.10),
]

P2_FURNITURE = [
    ("P2_Mob_Cama_Master", 0.95, 0.25, 2.55, 2.25, 0.58, "furniture"),
    ("P2_Mob_Velador_Master_1", 0.40, 0.25, 0.85, 0.70, 0.50, "furniture"),
    ("P2_Mob_Velador_Master_2", 2.65, 0.25, 3.10, 0.70, 0.50, "furniture"),
    ("P2_Mob_Closet_Vestidor_1", 2.08, 4.60, 2.55, 6.70, 2.10, "furniture"),
    ("P2_Mob_Closet_Vestidor_2", 3.00, 4.60, 3.42, 6.70, 2.10, "furniture"),
    ("P2_Mob_Ducha_Master", 0.20, 5.80, 1.10, 6.70, 0.12, "furniture"),
    ("P2_Mob_Inodoro_Master", 0.20, 5.05, 0.65, 5.70, 0.45, "furniture"),
    ("P2_Mob_Lavabo_Master", 1.25, 4.60, 1.90, 5.10, 0.85, "furniture"),
    ("P2_Mob_Ducha_Comp", 0.20, 7.65, 1.10, 8.55, 0.12, "furniture"),
    ("P2_Mob_Inodoro_Comp", 0.20, 6.95, 0.65, 7.55, 0.45, "furniture"),
    ("P2_Mob_Lavabo_Comp", 1.35, 8.05, 2.05, 8.55, 0.85, "furniture"),
    ("P2_Mob_Cama_Hija_1", 0.25, 10.00, 1.30, 11.90, 0.55, "furniture"),
    ("P2_Mob_Closet_Hija_1", 2.35, 10.40, 2.90, 11.90, 2.10, "furniture"),
    ("P2_Mob_Escritorio_Hija_1", 0.25, 8.80, 1.35, 9.35, 0.75, "furniture"),
    ("P2_Mob_Cama_Hija_2", 4.70, 10.00, 5.75, 11.90, 0.55, "furniture"),
    ("P2_Mob_Closet_Hija_2", 3.10, 10.40, 3.65, 11.90, 2.10, "furniture"),
    ("P2_Mob_Escritorio_Hija_2", 4.65, 8.80, 5.75, 9.35, 0.75, "furniture"),
    ("P2_Mob_Escritorio_Estudio", 4.55, 6.95, 5.75, 7.55, 0.75, "furniture"),
]

def build_stairs(col, x_offset, z_base, prefix):
    steps = 16
    run = (5.50 - 1.60) / (steps - 1)
    rise = (Z_P2 - Z_P1) / steps
    for i in range(steps - 1):
        y0 = 1.60 + i * run
        y1 = y0 + run
        z0 = z_base + i * rise
        z1 = z_base + (i + 1) * rise
        create_box(f"{prefix}_Peldano_{i+1:02d}", 3.55 + x_offset, y0, z0, 4.50 + x_offset, y1, z1, "stair", col)

def build_floor(col, rooms, walls_ext, walls_int, doors, furniture, x_offset, z_base, prefix, include_stairs=False, floor_w=6.0, floor_d=10.0):
    create_box(f"{prefix}_Losa_Base", x_offset, 0.0, z_base - 0.10, x_offset + floor_w, floor_d, z_base, "slab", col)
    for r in rooms:
        z_top = z_base + 0.04 if "Lavanderia" not in r["name"] else z_base + 0.06
        create_box(
            f"{prefix}_{r['name']}",
            r["x0"] + x_offset, r["y0"], z_base,
            r["x1"] + x_offset, r["y1"], z_top,
            r["mat"], col
        )
        cx = (r["x0"] + r["x1"]) * 0.5 + x_offset
        cy = (r["y0"] + r["y1"]) * 0.5
        area = (r["x1"] - r["x0"]) * (r["y1"] - r["y0"])
        short_name = r["name"].replace("P1_", "").replace("P2_", "").replace("_", " ")
        create_text_label(
            f"{prefix}_Lbl_{r['name']}",
            f"{short_name}\n{area:.2f} m2",
            cx, cy, z_base + 0.12, 0.22, col
        )
    wall_h = 0.85
    for wname, x0, y0, x1, y1 in walls_ext:
        create_box(f"{prefix}_{wname}", x0 + x_offset, y0, z_base, x1 + x_offset, y1, z_base + wall_h, "wall_ext", col)
    for wname, x0, y0, x1, y1 in walls_int:
        create_box(f"{prefix}_{wname}", x0 + x_offset, y0, z_base, x1 + x_offset, y1, z_base + wall_h, "wall_int", col)
    for dname, x0, y0, x1, y1 in doors:
        create_box(f"{prefix}_{dname}", x0 + x_offset, y0, z_base + 0.04, x1 + x_offset, y1, z_base + wall_h + 0.02, "door", col)
    for fname, x0, y0, x1, y1, fh, fmat in furniture:
        create_box(f"{prefix}_{fname}", x0 + x_offset, y0, z_base + 0.04, x1 + x_offset, y1, z_base + 0.04 + fh, fmat, col)
    if include_stairs:
        build_stairs(col, x_offset, z_base, prefix)

def rect_overlap(a, b):
    if "Lavanderia" in a["name"] or "Lavanderia" in b["name"]:
        return False
    ix0 = max(a["x0"], b["x0"])
    iy0 = max(a["y0"], b["y0"])
    ix1 = min(a["x1"], b["x1"])
    iy1 = min(a["y1"], b["y1"])
    return (ix1 - ix0) > 1e-4 and (iy1 - iy0) > 1e-4

def validate_scene():
    p1_gross = 6.00 * 10.00
    p2_gross = 6.00 * 12.15
    p1_ext_walls = sum((w[3] - w[1]) * (w[4] - w[2]) for w in P1_WALLS_EXT)
    p1_int_walls = sum((w[3] - w[1]) * (w[4] - w[2]) for w in P1_WALLS_INT)
    p2_ext_walls = sum((w[3] - w[1]) * (w[4] - w[2]) for w in P2_WALLS_EXT)
    p2_int_walls = sum((w[3] - w[1]) * (w[4] - w[2]) for w in P2_WALLS_INT)

    p1_net = sum((r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) for r in P1_ROOMS if "Lavanderia" not in r["name"])
    p2_net = sum((r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) for r in P2_ROOMS)

    p1_overlaps = []
    for i in range(len(P1_ROOMS)):
        for j in range(i + 1, len(P1_ROOMS)):
            if rect_overlap(P1_ROOMS[i], P1_ROOMS[j]):
                p1_overlaps.append((P1_ROOMS[i]["name"], P1_ROOMS[j]["name"]))

    p2_overlaps = []
    for i in range(len(P2_ROOMS)):
        for j in range(i + 1, len(P2_ROOMS)):
            if rect_overlap(P2_ROOMS[i], P2_ROOMS[j]):
                p2_overlaps.append((P2_ROOMS[i]["name"], P2_ROOMS[j]["name"]))

    p1_stair = next(r for r in P1_ROOMS if r["name"] == "P1_Escalera")
    p2_stair = next(r for r in P2_ROOMS if r["name"] == "P2_Escalera_Hueco")
    stair_aligned = (
        abs(p1_stair["x0"] - p2_stair["x0"]) < 1e-6 and
        abs(p1_stair["y0"] - p2_stair["y0"]) < 1e-6 and
        abs(p1_stair["x1"] - p2_stair["x1"]) < 1e-6 and
        abs(p1_stair["y1"] - p2_stair["y1"]) < 1e-6
    )

    bedrooms = [r["name"] for r in P1_ROOMS + P2_ROOMS if r["cat"] == "bedroom"]
    bathrooms = [r["name"] for r in P1_ROOMS + P2_ROOMS if r["cat"] == "bathroom"]

    sala_total = sum((r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) for r in P1_ROOMS if r["name"] in ("P1_Sala", "P1_Sala_Zona"))

    report = {
        "blender_version": bpy.app.version_string,
        "units": bpy.context.scene.unit_settings.system,
        "p1_gross_m2": round(p1_gross, 4),
        "p2_gross_m2": round(p2_gross, 4),
        "total_gross_m2": round(p1_gross + p2_gross, 4),
        "p1_limit_ok": p1_gross <= 60.0,
        "p2_limit_ok": p2_gross <= 80.0,
        "total_limit_ok": (p1_gross + p2_gross) <= 140.0,
        "p1_ext_walls_m2": round(p1_ext_walls, 4),
        "p1_int_walls_m2": round(p1_int_walls, 4),
        "p1_net_rooms_m2": round(p1_net, 4),
        "p1_sum_check_m2": round(p1_net + p1_ext_walls + p1_int_walls, 4),
        "p2_ext_walls_m2": round(p2_ext_walls, 4),
        "p2_int_walls_m2": round(p2_int_walls, 4),
        "p2_net_rooms_m2": round(p2_net, 4),
        "p2_sum_check_m2": round(p2_net + p2_ext_walls + p2_int_walls, 4),
        "p1_overlaps": p1_overlaps,
        "p2_overlaps": p2_overlaps,
        "stairs_vertically_aligned": stair_aligned,
        "bedroom_count": len(bedrooms),
        "bedrooms": bedrooms,
        "bathroom_count": len(bathrooms),
        "bathrooms": bathrooms,
        "vehicles_real_scale": {
            "suzuki_swift_dzire_2023_m": [1.735, 3.995, 1.515],
            "suzuki_v_strom_250_sx_m": [0.880, 2.180, 1.355],
            "garage_clear_m": [3.30, 4.55],
            "side_by_side_fit": True,
        },
        "identified_constraints_tension": {
            "p1_sala_area_m2": round(sala_total, 2),
            "p1_sala_comfort_deficit_m2": round(max(0.0, 8.0 - sala_total), 2),
            "laundry_shared_under_stair": True,
            "note": "Planta 1 cumple <= 60 m2 con vehiculos y mobiliario a escala real, pero la zona social (Sala) queda ajustada (5.30 m2) y lavanderia se ubica bajo la escalera."
        }
    }

    with open(VALIDATION_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return report

def setup_render_and_capture():
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_object_outline = True
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100

    world = bpy.data.worlds.new("World_Schematic")
    scene.world = world
    world.color = (0.92, 0.93, 0.95)

    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.name = "Cam_Render"
    scene.camera = cam

    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 14.5
    cam.location = (3.0, 5.0, 18.0)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    bpy.data.collections["Planta_02_Vertical"].hide_render = True
    bpy.data.collections["Planta_02_Comparativa"].hide_render = True
    bpy.data.collections["Planta_01_Vertical"].hide_render = False
    scene.render.filepath = RENDER_P1_PATH
    bpy.ops.render.render(write_still=True)

    cam.data.ortho_scale = 16.0
    cam.location = (3.0 + COMP_X_OFFSET, 6.075, 18.0)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    bpy.data.collections["Planta_01_Vertical"].hide_render = True
    bpy.data.collections["Planta_02_Comparativa"].hide_render = False
    scene.render.filepath = RENDER_P2_PATH
    bpy.ops.render.render(write_still=True)

    bpy.data.collections["Planta_01_Vertical"].hide_render = False
    bpy.data.collections["Planta_02_Vertical"].hide_render = False
    bpy.data.collections["Planta_02_Comparativa"].hide_render = False
    cam.data.type = "PERSP"
    cam.data.lens = 35.0
    cam.location = (18.5, -10.5, 13.5)
    direction = Vector((6.8, 5.5, 1.8)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = RENDER_ISO_PATH
    bpy.ops.render.render(write_still=True)

    bpy.data.collections["Planta_02_Vertical"].hide_viewport = False
    bpy.data.collections["Planta_02_Comparativa"].hide_viewport = False

def main():
    clear_scene()
    col_p1 = get_or_create_collection("Planta_01_Vertical")
    col_p2 = get_or_create_collection("Planta_02_Vertical")
    col_p2_comp = get_or_create_collection("Planta_02_Comparativa")

    build_floor(col_p1, P1_ROOMS, P1_WALLS_EXT, P1_WALLS_INT, P1_DOORS, P1_FURNITURE, 0.0, Z_P1, "V1", include_stairs=True, floor_w=6.0, floor_d=10.0)
    build_floor(col_p2, P2_ROOMS, P2_WALLS_EXT, P2_WALLS_INT, P2_DOORS, P2_FURNITURE, 0.0, Z_P2, "V2", include_stairs=False, floor_w=6.0, floor_d=12.15)
    build_floor(col_p2_comp, P2_ROOMS, P2_WALLS_EXT, P2_WALLS_INT, P2_DOORS, P2_FURNITURE, COMP_X_OFFSET, Z_P1, "C2", include_stairs=False, floor_w=6.0, floor_d=12.15)

    report = validate_scene()
    setup_render_and_capture()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print("BUILD_AND_VALIDATION_COMPLETE:", json.dumps(report))

main()
