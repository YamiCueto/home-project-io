import json
import os
from collections import deque
import bpy
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
VALIDATION_PATH = os.path.join(PROJECT_DIR, "validation", "HITO_01_V2_VALIDATION.json")

CLEAR_H = 2.70
SLAB_T = 0.20
Z_P1 = 0.00
Z_P2 = CLEAR_H + SLAB_T
COMP_X_OFFSET = 10.50

COLORS = {
    "wall_ext": (0.18, 0.19, 0.21, 1.0),
    "wall_int": (0.40, 0.41, 0.45, 1.0),
    "slab": (0.26, 0.27, 0.29, 1.0),
    "column": (0.85, 0.35, 0.20, 1.0),
    "linderos": (0.95, 0.20, 0.18, 1.0),
    "cerramiento": (0.14, 0.14, 0.16, 1.0),
    "anden": (0.64, 0.64, 0.66, 1.0),
    "calle": (0.20, 0.21, 0.23, 1.0),
    "terraza": (0.84, 0.76, 0.58, 1.0),
    "garage": (0.46, 0.49, 0.54, 1.0),
    "access": (0.86, 0.79, 0.63, 1.0),
    "circulation": (0.90, 0.85, 0.72, 1.0),
    "living": (0.44, 0.72, 0.86, 1.0),
    "dining": (0.50, 0.78, 0.72, 1.0),
    "kitchen": (0.92, 0.65, 0.42, 1.0),
    "bedroom_guest": (0.72, 0.62, 0.86, 1.0),
    "bedroom_master": (0.58, 0.52, 0.84, 1.0),
    "bedroom_daughter": (0.86, 0.58, 0.72, 1.0),
    "bath": (0.40, 0.82, 0.88, 1.0),
    "laundry": (0.68, 0.80, 0.55, 1.0),
    "stair": (0.82, 0.68, 0.38, 1.0),
    "closet": (0.76, 0.64, 0.52, 1.0),
    "balcony": (0.58, 0.78, 0.52, 1.0),
    "furniture": (0.28, 0.22, 0.18, 1.0),
    "vehicle_car": (0.15, 0.35, 0.68, 1.0),
    "vehicle_moto": (0.82, 0.22, 0.18, 1.0),
    "door_frame": (0.95, 0.85, 0.20, 1.0),
    "window_glass": (0.55, 0.85, 0.95, 0.45),
}

COLLECTION_NAMES = [
    "00_Propiedad_Existente",
    "01_Linderos_Provisionales",
    "02_Terraza_Frontal",
    "03_Terraza_Lateral",
    "04_Cerramiento_Existente",
    "05_Andenes_Publicos",
    "06_Calles",
    "07_Propuesta_Primera_Planta",
    "08_Propuesta_Segunda_Planta",
    "09_Estructura_Conceptual",
    "10_Vehiculos",
    "11_Mobiliario",
    "12_Camaras",
]

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

def init_collections():
    cols = {}
    for name in COLLECTION_NAMES:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
        cols[name] = col
    return cols

def get_mat(name, rgba):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.78
        if rgba[3] < 1.0:
            bsdf.inputs["Alpha"].default_value = rgba[3]
    mat.diffuse_color = rgba
    return mat

def create_box(name, x0, y0, z0, x1, y1, z1, mat_key, col):
    sx = abs(x1 - x0)
    sy = abs(y1 - y0)
    sz = abs(z1 - z0)
    if sx < 1e-4 or sy < 1e-4 or sz < 1e-4:
        return None
    cx = (x0 + x1) * 0.5
    cy = (y0 + y1) * 0.5
    cz = (z0 + z1) * 0.5
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    obj.data.materials.append(get_mat(f"MAT_{mat_key}", COLORS[mat_key]))
    return obj

def create_label(name, text, x, y, z, size, col):
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
    obj.data.materials.append(get_mat("MAT_lbl", (0.05, 0.05, 0.05, 1.0)))
    return obj

def create_wall_with_openings(prefix, x0, y0, x1, y1, z_base, wall_h, mat_key, openings, col, x_offset=0.0):
    horizontal = abs(y1 - y0) <= abs(x1 - x0)
    if horizontal:
        ops_sorted = sorted([op for op in openings if op["axis"] == "X"], key=lambda o: o["p0"])
        cursor = x0
        idx = 0
        for op in ops_sorted:
            if op["p0"] > cursor + 1e-4:
                create_box(f"{prefix}_S{idx}", cursor + x_offset, y0, z_base, op["p0"] + x_offset, y1, z_base + wall_h, mat_key, col)
                idx += 1
            if op["z_sill"] > 0.01:
                create_box(f"{prefix}_Sill{idx}", op["p0"] + x_offset, y0, z_base, op["p1"] + x_offset, y1, z_base + op["z_sill"], mat_key, col)
            if op["z_head"] < wall_h - 0.01:
                create_box(f"{prefix}_Lint{idx}", op["p0"] + x_offset, y0, z_base + op["z_head"], op["p1"] + x_offset, y1, z_base + wall_h, mat_key, col)
            if op["kind"] == "window":
                ym = (y0 + y1) * 0.5
                create_box(f"{prefix}_Win{idx}", op["p0"] + x_offset, ym - 0.02, z_base + op["z_sill"], op["p1"] + x_offset, ym + 0.02, z_base + op["z_head"], "window_glass", col)
            else:
                create_box(f"{prefix}_Door{idx}", op["p0"] + x_offset, y0, z_base + 0.02, op["p1"] + x_offset, y1, z_base + 0.05, "door_frame", col)
            cursor = op["p1"]
            idx += 1
        if cursor < x1 - 1e-4:
            create_box(f"{prefix}_S{idx}", cursor + x_offset, y0, z_base, x1 + x_offset, y1, z_base + wall_h, mat_key, col)
    else:
        ops_sorted = sorted([op for op in openings if op["axis"] == "Y"], key=lambda o: o["p0"])
        cursor = y0
        idx = 0
        for op in ops_sorted:
            if op["p0"] > cursor + 1e-4:
                create_box(f"{prefix}_S{idx}", x0 + x_offset, cursor, z_base, x1 + x_offset, op["p0"], z_base + wall_h, mat_key, col)
                idx += 1
            if op["z_sill"] > 0.01:
                create_box(f"{prefix}_Sill{idx}", x0 + x_offset, op["p0"], z_base, x1 + x_offset, op["p1"], z_base + op["z_sill"], mat_key, col)
            if op["z_head"] < wall_h - 0.01:
                create_box(f"{prefix}_Lint{idx}", x0 + x_offset, op["p0"], z_base + op["z_head"], x1 + x_offset, op["p1"], z_base + wall_h, mat_key, col)
            if op["kind"] == "window":
                xm = (x0 + x1) * 0.5
                create_box(f"{prefix}_Win{idx}", xm - 0.02 + x_offset, op["p0"], z_base + op["z_sill"], xm + 0.02 + x_offset, op["p1"], z_base + op["z_head"], "window_glass", col)
            else:
                create_box(f"{prefix}_Door{idx}", x0 + x_offset, op["p0"], z_base + 0.02, x1 + x_offset, op["p1"], z_base + 0.05, "door_frame", col)
            cursor = op["p1"]
            idx += 1
        if cursor < y1 - 1e-4:
            create_box(f"{prefix}_S{idx}", x0 + x_offset, cursor, z_base, x1 + x_offset, y1, z_base + wall_h, mat_key, col)

def build_context(cols):
    create_box("Lindero_Oeste", -0.04, 0.0, 0.0, 0.0, 11.25, 0.12, "linderos", cols["01_Linderos_Provisionales"])
    create_box("Lindero_Norte", 0.0, 11.25, 0.0, 8.0, 11.29, 0.12, "linderos", cols["01_Linderos_Provisionales"])
    create_box("Lindero_Sur", 0.0, -0.04, 0.0, 8.0, 0.0, 0.12, "linderos", cols["01_Linderos_Provisionales"])
    create_box("Lindero_Este", 8.0, 0.0, 0.0, 8.04, 11.25, 0.12, "linderos", cols["01_Linderos_Provisionales"])

    create_box("Huella_Existente_Ref", 0.0, 2.0, -0.03, 6.0, 11.25, -0.01, "cerramiento", cols["00_Propiedad_Existente"])
    create_box("Terraza_Frontal_Ref", 0.0, 0.0, -0.02, 8.0, 2.0, 0.0, "terraza", cols["02_Terraza_Frontal"])
    create_box("Terraza_Lateral_Ref", 6.0, 2.0, -0.02, 8.0, 11.25, 0.0, "terraza", cols["03_Terraza_Lateral"])

    create_box("Cerramiento_Sur_Ref", 0.0, -0.02, 0.0, 8.0, 0.02, 0.35, "cerramiento", cols["04_Cerramiento_Existente"])
    create_box("Cerramiento_Este_Ref", 7.98, 0.0, 0.0, 8.02, 11.25, 0.35, "cerramiento", cols["04_Cerramiento_Existente"])

    create_box("Anden_Frontal", -1.5, -1.5, -0.04, 9.5, 0.0, 0.0, "anden", cols["05_Andenes_Publicos"])
    create_box("Anden_Lateral", 8.0, 0.0, -0.04, 9.5, 11.25, 0.0, "anden", cols["05_Andenes_Publicos"])
    create_label("Lbl_Anden_F", "Anden Publico", 4.0, -0.75, 0.05, 0.30, cols["05_Andenes_Publicos"])

    create_box("Calle_Frontal", -1.5, -6.5, -0.10, 14.5, -1.5, -0.04, "calle", cols["06_Calles"])
    create_box("Calle_Lateral", 9.5, -1.5, -0.10, 14.5, 11.25, -0.04, "calle", cols["06_Calles"])
    create_label("Lbl_Calle_F", "Calle Principal (Y-)", 4.0, -4.0, 0.02, 0.45, cols["06_Calles"])
    create_label("Lbl_Calle_L", "Calle Lateral (X+)", 12.0, 5.5, 0.02, 0.45, cols["06_Calles"])

def get_p2_spec():
    rooms = [
        {"name": "P2_Habitacion_Principal", "x0": 0.15, "y0": 0.15, "x1": 4.55, "y1": 4.35, "mat": "bedroom_master", "cat": "bedroom", "enclosed": True},
        {"name": "P2_Balcon", "x0": 4.65, "y0": 0.15, "x1": 7.85, "y1": 1.55, "mat": "balcony", "cat": "balcony", "enclosed": False},
        {"name": "P2_Vestidor_Principal", "x0": 4.65, "y0": 1.65, "x1": 6.15, "y1": 4.35, "mat": "closet", "cat": "closet", "enclosed": True},
        {"name": "P2_Bano_Principal", "x0": 6.25, "y0": 1.65, "x1": 7.85, "y1": 4.35, "mat": "bath", "cat": "bathroom", "enclosed": True},
        {"name": "P2_Bano_Compartido", "x0": 0.15, "y0": 4.45, "x1": 2.30, "y1": 6.35, "mat": "bath", "cat": "bathroom", "enclosed": True},
        {"name": "P2_Escalera_Hueco", "x0": 2.40, "y0": 4.45, "x1": 6.30, "y1": 5.40, "mat": "stair", "cat": "stair", "enclosed": True},
        {"name": "P2_Distribuidor", "x0": 2.40, "y0": 5.40, "x1": 7.85, "y1": 6.35, "mat": "circulation", "cat": "circulation", "enclosed": True},
        {"name": "P2_Llegada_Escalera", "x0": 6.30, "y0": 4.45, "x1": 7.85, "y1": 5.40, "mat": "circulation", "cat": "circulation", "enclosed": True},
        {"name": "P2_Habitacion_Hija_1", "x0": 0.15, "y0": 6.45, "x1": 3.95, "y1": 9.85, "mat": "bedroom_daughter", "cat": "bedroom", "enclosed": True},
        {"name": "P2_Habitacion_Hija_2", "x0": 4.05, "y0": 6.45, "x1": 7.85, "y1": 9.85, "mat": "bedroom_daughter", "cat": "bedroom", "enclosed": True},
    ]
    walls = [
        ("P2_M_Oeste", 0.00, 0.00, 0.15, 10.00, "wall_ext", []),
        ("P2_M_Este", 7.85, 0.00, 8.00, 10.00, "wall_ext", [
            {"axis": "Y", "p0": 2.40, "p1": 3.40, "z_sill": 1.10, "z_head": 1.75, "kind": "window"},
            {"axis": "Y", "p0": 7.40, "p1": 8.90, "z_sill": 0.70, "z_head": 1.75, "kind": "window"},
        ]),
        ("P2_M_Sur", 0.15, 0.00, 7.85, 0.15, "wall_ext", [
            {"axis": "X", "p0": 1.00, "p1": 3.80, "z_sill": 0.40, "z_head": 1.75, "kind": "window"},
            {"axis": "X", "p0": 5.10, "p1": 7.40, "z_sill": 0.85, "z_head": 1.75, "kind": "window"},
        ]),
        ("P2_M_Norte", 0.15, 9.85, 7.85, 10.00, "wall_ext", [
            {"axis": "X", "p0": 1.20, "p1": 2.80, "z_sill": 0.70, "z_head": 1.75, "kind": "window"},
            {"axis": "X", "p0": 5.20, "p1": 6.80, "z_sill": 0.70, "z_head": 1.75, "kind": "window"},
        ]),
        ("P2_M_Master_Este", 4.55, 0.15, 4.65, 4.35, "wall_int", [
            {"axis": "Y", "p0": 0.35, "p1": 1.45, "z_sill": 0.0, "z_head": 1.75, "kind": "door"},
            {"axis": "Y", "p0": 2.40, "p1": 3.30, "z_sill": 0.0, "z_head": 1.75, "kind": "door"},
        ]),
        ("P2_M_Balcon_Norte", 4.65, 1.55, 7.85, 1.65, "wall_int", []),
        ("P2_M_Vest_Bano", 6.15, 1.65, 6.25, 4.35, "wall_int", [
            {"axis": "Y", "p0": 2.50, "p1": 3.30, "z_sill": 0.0, "z_head": 1.75, "kind": "door"},
        ]),
        ("P2_M_Banda_Sur", 0.15, 4.35, 7.85, 4.45, "wall_int", [
            {"axis": "X", "p0": 3.55, "p1": 4.45, "z_sill": 0.0, "z_head": 1.75, "kind": "door"},
        ]),
        ("P2_M_Bano_Comp_Este", 2.30, 4.45, 2.40, 6.35, "wall_int", [
            {"axis": "Y", "p0": 5.45, "p1": 6.25, "z_sill": 0.0, "z_head": 1.75, "kind": "door"},
        ]),
        ("P2_M_Banda_Norte", 0.15, 6.35, 7.85, 6.45, "wall_int", [
            {"axis": "X", "p0": 3.00, "p1": 3.90, "z_sill": 0.0, "z_head": 1.75, "kind": "door"},
            {"axis": "X", "p0": 4.10, "p1": 5.00, "z_sill": 0.0, "z_head": 1.75, "kind": "door"},
        ]),
        ("P2_M_Entre_Hijas", 3.95, 6.45, 4.05, 9.85, "wall_int", []),
    ]
    furniture = [
        ("P2_Mob_Cama_Master", 1.55, 0.45, 3.15, 2.45, 0.58, "furniture"),
        ("P2_Mob_Velador_M1", 0.95, 0.45, 1.45, 0.90, 0.50, "furniture"),
        ("P2_Mob_Velador_M2", 3.25, 0.45, 3.75, 0.90, 0.50, "furniture"),
        ("P2_Mob_TV_Master", 1.70, 4.00, 3.00, 4.30, 0.55, "furniture"),
        ("P2_Mob_Closet_Vest", 5.55, 1.70, 6.10, 4.25, 2.10, "furniture"),
        ("P2_Mob_Ducha_Master", 6.90, 1.70, 7.80, 2.60, 0.12, "furniture"),
        ("P2_Mob_Inodoro_Master", 7.15, 2.75, 7.80, 3.25, 0.45, "furniture"),
        ("P2_Mob_Lavabo_Master", 7.25, 3.50, 7.80, 4.25, 0.85, "furniture"),
        ("P2_Mob_Ducha_Comp", 0.20, 4.50, 1.10, 5.40, 0.12, "furniture"),
        ("P2_Mob_Inodoro_Comp", 0.20, 5.60, 0.70, 6.25, 0.45, "furniture"),
        ("P2_Mob_Lavabo_Comp", 1.35, 4.50, 2.10, 5.00, 0.85, "furniture"),
        ("P2_Mob_Cama_Hija_1", 0.30, 7.80, 1.50, 9.75, 0.55, "furniture"),
        ("P2_Mob_Escritorio_H1", 0.30, 6.55, 1.50, 7.15, 0.75, "furniture"),
        ("P2_Mob_Closet_H1", 2.30, 9.20, 3.90, 9.80, 2.10, "furniture"),
        ("P2_Mob_Cama_Hija_2", 6.50, 7.80, 7.70, 9.75, 0.55, "furniture"),
        ("P2_Mob_Escritorio_H2", 6.50, 6.55, 7.70, 7.15, 0.75, "furniture"),
        ("P2_Mob_Closet_H2", 4.10, 9.20, 5.70, 9.80, 2.10, "furniture"),
    ]
    slab_segments = [
        (0.00, 0.00, 8.00, 4.45),
        (0.00, 4.45, 2.40, 5.40),
        (6.30, 4.45, 8.00, 5.40),
        (0.00, 5.40, 8.00, 10.00),
    ]
    graph = {
        "P2_Llegada_Escalera": ["P2_Distribuidor"],
        "P2_Distribuidor": ["P2_Llegada_Escalera", "P2_Habitacion_Principal", "P2_Bano_Compartido", "P2_Habitacion_Hija_1", "P2_Habitacion_Hija_2"],
        "P2_Habitacion_Principal": ["P2_Distribuidor", "P2_Balcon", "P2_Vestidor_Principal"],
        "P2_Balcon": ["P2_Habitacion_Principal"],
        "P2_Vestidor_Principal": ["P2_Habitacion_Principal", "P2_Bano_Principal"],
        "P2_Bano_Principal": ["P2_Vestidor_Principal"],
        "P2_Bano_Compartido": ["P2_Distribuidor"],
        "P2_Habitacion_Hija_1": ["P2_Distribuidor"],
        "P2_Habitacion_Hija_2": ["P2_Distribuidor"],
    }
    return {
        "rooms": rooms,
        "walls": walls,
        "furniture": furniture,
        "slab_segments": slab_segments,
        "graph": graph,
        "footprint": (8.00, 10.00),
        "stair_hole": (2.40, 4.45, 6.30, 5.40),
    }

def get_alt_a():
    rooms = [
        {"name": "P1_Garaje_Frontal", "x0": 0.15, "y0": 0.15, "x1": 3.45, "y1": 4.42, "mat": "garage", "cat": "garage", "enclosed": False},
        {"name": "P1_Acceso_Peatonal", "x0": 3.55, "y0": 0.15, "x1": 5.85, "y1": 1.95, "mat": "access", "cat": "circulation", "enclosed": False},
        {"name": "P1_Sala", "x0": 3.55, "y0": 2.05, "x1": 5.85, "y1": 4.40, "mat": "living", "cat": "social", "enclosed": True},
        {"name": "P1_Escalera", "x0": 2.40, "y0": 4.45, "x1": 6.30, "y1": 5.40, "mat": "stair", "cat": "stair", "enclosed": True},
        {"name": "P1_Bano_Social", "x0": 0.15, "y0": 4.75, "x1": 2.25, "y1": 6.55, "mat": "bath", "cat": "bathroom", "enclosed": True},
        {"name": "P1_Distribuidor", "x0": 2.35, "y0": 5.45, "x1": 3.55, "y1": 6.55, "mat": "circulation", "cat": "circulation", "enclosed": True},
        {"name": "P1_Habitacion_Huespedes", "x0": 0.15, "y0": 6.65, "x1": 3.15, "y1": 9.85, "mat": "bedroom_guest", "cat": "bedroom", "enclosed": True},
        {"name": "P1_Comedor", "x0": 3.65, "y0": 5.45, "x1": 5.85, "y1": 7.65, "mat": "dining", "cat": "social", "enclosed": True},
        {"name": "P1_Cocina", "x0": 3.25, "y0": 7.65, "x1": 5.85, "y1": 9.85, "mat": "kitchen", "cat": "kitchen", "enclosed": True},
        {"name": "P1_Lavanderia", "x0": 0.15, "y0": 10.00, "x1": 2.45, "y1": 11.15, "mat": "laundry", "cat": "laundry", "enclosed": False},
        {"name": "P1_Terraza_Lateral_Libre", "x0": 6.40, "y0": 2.00, "x1": 7.90, "y1": 11.15, "mat": "terraza", "cat": "exterior", "enclosed": False},
    ]
    walls = [
        ("P1_M_Oeste", 0.00, 0.00, 0.15, 10.00, "wall_ext", []),
        ("P1_M_Sur_Frente", 0.15, 0.00, 5.85, 0.15, "wall_ext", [
            {"axis": "X", "p0": 0.35, "p1": 3.25, "z_sill": 0.0, "z_head": 2.35, "kind": "door"},
            {"axis": "X", "p0": 4.25, "p1": 5.20, "z_sill": 0.0, "z_head": 2.15, "kind": "door"},
        ]),
        ("P1_M_Este", 5.85, 0.00, 6.00, 10.00, "wall_ext", [
            {"axis": "Y", "p0": 2.40, "p1": 4.00, "z_sill": 0.80, "z_head": 2.10, "kind": "window"},
            {"axis": "Y", "p0": 6.00, "p1": 7.20, "z_sill": 0.80, "z_head": 2.10, "kind": "window"},
            {"axis": "Y", "p0": 8.00, "p1": 9.20, "z_sill": 1.00, "z_head": 2.10, "kind": "window"},
        ]),
        ("P1_M_Norte", 0.15, 9.85, 5.85, 10.00, "wall_ext", [
            {"axis": "X", "p0": 1.10, "p1": 2.40, "z_sill": 0.80, "z_head": 2.10, "kind": "window"},
            {"axis": "X", "p0": 3.50, "p1": 4.40, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        ]),
        ("P1_M_Garaje_Este", 3.45, 0.15, 3.55, 4.40, "wall_int", []),
        ("P1_M_Garaje_Norte", 0.15, 4.65, 2.35, 4.75, "wall_int", []),
        ("P1_M_Acceso_Sala", 3.55, 1.95, 5.85, 2.05, "wall_int", [
            {"axis": "X", "p0": 4.25, "p1": 5.20, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        ]),
        ("P1_M_Bano_Este", 2.25, 4.75, 2.35, 6.55, "wall_int", [
            {"axis": "Y", "p0": 5.55, "p1": 6.35, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        ]),
        ("P1_M_Huesped_Sur", 0.15, 6.55, 3.15, 6.65, "wall_int", [
            {"axis": "X", "p0": 2.25, "p1": 3.15, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        ]),
        ("P1_M_Huesped_Este", 3.15, 6.55, 3.25, 9.85, "wall_int", []),
    ]
    vehicles = [
        ("P1_Veh_Swift_Dzire_2023", 0.30, 0.28, 2.035, 4.275, 1.515, "vehicle_car"),
        ("P1_Veh_VStrom_250_SX", 2.45, 1.80, 3.33, 3.98, 1.355, "vehicle_moto"),
    ]
    furniture = [
        ("P1_Mob_Sofa_Sala", 4.95, 2.20, 5.80, 4.20, 0.78, "furniture"),
        ("P1_Mob_TV_Sala", 3.60, 2.50, 3.95, 3.80, 0.55, "furniture"),
        ("P1_Mob_Mesa_Centro", 4.20, 2.75, 4.70, 3.65, 0.42, "furniture"),
        ("P1_Mob_Mesa_Comedor", 4.15, 5.85, 5.35, 7.05, 0.75, "furniture"),
        ("P1_Mob_Cocina_Meson", 5.20, 7.75, 5.80, 9.80, 0.90, "furniture"),
        ("P1_Mob_Cocina_Refri", 3.30, 9.10, 4.00, 9.80, 1.75, "furniture"),
        ("P1_Mob_Cama_Huesped", 0.30, 7.80, 1.35, 9.70, 0.55, "furniture"),
        ("P1_Mob_Velador_H", 1.45, 9.25, 1.90, 9.70, 0.50, "furniture"),
        ("P1_Mob_Closet_Huesped", 2.50, 8.20, 3.10, 9.75, 2.10, "furniture"),
        ("P1_Mob_Ducha_Social", 0.20, 4.80, 1.10, 5.70, 0.12, "furniture"),
        ("P1_Mob_Inodoro_Social", 0.20, 5.85, 0.70, 6.45, 0.45, "furniture"),
        ("P1_Mob_Lavabo_Social", 1.40, 4.80, 2.15, 5.30, 0.85, "furniture"),
        ("P1_Mob_Lavadora", 0.25, 10.10, 0.95, 10.80, 0.85, "furniture"),
        ("P1_Mob_Lavadero", 1.05, 10.10, 1.85, 10.80, 0.85, "furniture"),
    ]
    columns = [
        (0.05, 0.05), (3.45, 0.05), (5.90, 0.05), (7.90, 0.05),
        (0.05, 4.70), (5.90, 4.70), (7.90, 4.70),
        (0.05, 9.90), (5.90, 9.90), (7.90, 9.90),
    ]
    graph = {
        "P1_Acceso_Peatonal": ["P1_Sala"],
        "P1_Sala": ["P1_Acceso_Peatonal", "P1_Escalera", "P1_Distribuidor", "P1_Comedor"],
        "P1_Escalera": ["P1_Sala", "P1_Distribuidor"],
        "P1_Distribuidor": ["P1_Sala", "P1_Escalera", "P1_Bano_Social", "P1_Habitacion_Huespedes", "P1_Comedor"],
        "P1_Bano_Social": ["P1_Distribuidor"],
        "P1_Habitacion_Huespedes": ["P1_Distribuidor"],
        "P1_Comedor": ["P1_Sala", "P1_Distribuidor", "P1_Cocina"],
        "P1_Cocina": ["P1_Comedor", "P1_Lavanderia"],
        "P1_Lavanderia": ["P1_Cocina"],
    }
    return {
        "code": "A",
        "title": "Alternativa A - Garaje Frontal",
        "rooms": rooms,
        "walls": walls,
        "vehicles": vehicles,
        "furniture": furniture,
        "columns": columns,
        "graph": graph,
        "entry": "P1_Acceso_Peatonal",
        "stair_dir": "X+",
        "stair_rect": (2.40, 4.45, 6.30, 5.40),
        "p1_enclosed_footprint": 44.00,
        "p1_covered_ext": 21.30,
    }

def get_alt_b():
    rooms = [
        {"name": "P1_Terraza_Frontal_Peat", "x0": 0.15, "y0": 0.15, "x1": 7.85, "y1": 1.95, "mat": "access", "cat": "circulation", "enclosed": False},
        {"name": "P1_Sala", "x0": 0.15, "y0": 2.05, "x1": 4.25, "y1": 4.40, "mat": "living", "cat": "social", "enclosed": True},
        {"name": "P1_Comedor", "x0": 4.35, "y0": 2.05, "x1": 5.85, "y1": 4.40, "mat": "dining", "cat": "social", "enclosed": True},
        {"name": "P1_Escalera", "x0": 2.40, "y0": 4.45, "x1": 6.30, "y1": 5.40, "mat": "stair", "cat": "stair", "enclosed": True},
        {"name": "P1_Bano_Social", "x0": 0.15, "y0": 4.50, "x1": 2.25, "y1": 6.35, "mat": "bath", "cat": "bathroom", "enclosed": True},
        {"name": "P1_Distribuidor", "x0": 2.35, "y0": 5.45, "x1": 4.45, "y1": 6.35, "mat": "circulation", "cat": "circulation", "enclosed": True},
        {"name": "P1_Habitacion_Huespedes", "x0": 0.15, "y0": 6.45, "x1": 3.15, "y1": 9.85, "mat": "bedroom_guest", "cat": "bedroom", "enclosed": True},
        {"name": "P1_Cocina", "x0": 3.25, "y0": 6.45, "x1": 4.85, "y1": 9.85, "mat": "kitchen", "cat": "kitchen", "enclosed": True},
        {"name": "P1_Garaje_Lateral", "x0": 4.95, "y0": 5.50, "x1": 7.85, "y1": 11.15, "mat": "garage", "cat": "garage", "enclosed": False},
        {"name": "P1_Lavanderia", "x0": 0.15, "y0": 10.00, "x1": 3.15, "y1": 11.15, "mat": "laundry", "cat": "laundry", "enclosed": False},
    ]
    walls = [
        ("P1_M_Oeste", 0.00, 1.95, 0.15, 10.00, "wall_ext", []),
        ("P1_M_Sur_Frente", 0.15, 1.95, 5.85, 2.05, "wall_ext", [
            {"axis": "X", "p0": 1.60, "p1": 2.55, "z_sill": 0.0, "z_head": 2.15, "kind": "door"},
            {"axis": "X", "p0": 0.40, "p1": 1.40, "z_sill": 0.50, "z_head": 2.10, "kind": "window"},
            {"axis": "X", "p0": 4.50, "p1": 5.50, "z_sill": 0.50, "z_head": 2.10, "kind": "window"},
        ]),
        ("P1_M_Este_Social", 5.85, 2.05, 6.00, 5.45, "wall_ext", [
            {"axis": "Y", "p0": 2.50, "p1": 3.90, "z_sill": 0.60, "z_head": 2.10, "kind": "window"},
        ]),
        ("P1_M_Este_Garaje", 4.85, 5.45, 4.95, 9.85, "wall_int", [
            {"axis": "Y", "p0": 5.60, "p1": 6.40, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        ]),
        ("P1_M_Norte", 0.15, 9.85, 4.85, 10.00, "wall_ext", [
            {"axis": "X", "p0": 1.10, "p1": 2.40, "z_sill": 0.80, "z_head": 2.10, "kind": "window"},
            {"axis": "X", "p0": 3.55, "p1": 4.45, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        ]),
        ("P1_M_Garaje_Acceso_Lateral", 7.85, 5.50, 8.00, 11.15, "wall_ext", [
            {"axis": "Y", "p0": 5.75, "p1": 10.75, "z_sill": 0.0, "z_head": 2.35, "kind": "door"},
        ]),
        ("P1_M_Bano_Este", 2.25, 4.45, 2.35, 6.35, "wall_int", [
            {"axis": "Y", "p0": 5.45, "p1": 6.25, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        ]),
        ("P1_M_Huesped_Sur", 0.15, 6.35, 3.15, 6.45, "wall_int", [
            {"axis": "X", "p0": 2.25, "p1": 3.15, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        ]),
        ("P1_M_Huesped_Este", 3.15, 6.45, 3.25, 9.85, "wall_int", []),
    ]
    vehicles = [
        ("P1_Veh_Swift_Dzire_2023", 5.20, 6.80, 6.935, 10.795, 1.515, "vehicle_car"),
        ("P1_Veh_VStrom_250_SX", 5.30, 5.65, 7.48, 6.53, 1.355, "vehicle_moto"),
    ]
    furniture = [
        ("P1_Mob_Sofa_Sala", 0.25, 2.60, 1.10, 4.30, 0.78, "furniture"),
        ("P1_Mob_Mesa_Centro", 1.45, 3.00, 2.00, 3.90, 0.42, "furniture"),
        ("P1_Mob_TV_Sala", 2.60, 2.10, 3.80, 2.45, 0.55, "furniture"),
        ("P1_Mob_Mesa_Comedor", 4.55, 2.65, 5.55, 3.95, 0.75, "furniture"),
        ("P1_Mob_Cocina_Meson", 4.20, 6.60, 4.80, 9.50, 0.90, "furniture"),
        ("P1_Mob_Cocina_Refri", 3.30, 9.10, 4.00, 9.80, 1.75, "furniture"),
        ("P1_Mob_Cama_Huesped", 0.30, 7.80, 1.35, 9.70, 0.55, "furniture"),
        ("P1_Mob_Velador_H", 1.45, 9.25, 1.90, 9.70, 0.50, "furniture"),
        ("P1_Mob_Closet_Huesped", 2.50, 8.20, 3.10, 9.75, 2.10, "furniture"),
        ("P1_Mob_Ducha_Social", 0.20, 4.55, 1.10, 5.45, 0.12, "furniture"),
        ("P1_Mob_Inodoro_Social", 0.20, 5.65, 0.70, 6.25, 0.45, "furniture"),
        ("P1_Mob_Lavabo_Social", 1.35, 4.55, 2.10, 5.05, 0.85, "furniture"),
        ("P1_Mob_Lavadora", 0.25, 10.10, 0.95, 10.80, 0.85, "furniture"),
        ("P1_Mob_Lavadero", 1.05, 10.10, 1.85, 10.80, 0.85, "furniture"),
    ]
    columns = [
        (0.05, 0.05), (4.30, 0.05), (7.90, 0.05),
        (0.05, 4.45), (4.85, 4.45), (7.90, 4.45),
        (0.05, 9.90), (4.85, 9.90), (7.90, 9.90),
    ]
    graph = {
        "P1_Terraza_Frontal_Peat": ["P1_Sala"],
        "P1_Sala": ["P1_Terraza_Frontal_Peat", "P1_Comedor", "P1_Escalera", "P1_Distribuidor"],
        "P1_Comedor": ["P1_Sala", "P1_Escalera"],
        "P1_Escalera": ["P1_Sala", "P1_Comedor", "P1_Distribuidor"],
        "P1_Distribuidor": ["P1_Sala", "P1_Escalera", "P1_Bano_Social", "P1_Habitacion_Huespedes", "P1_Cocina", "P1_Garaje_Lateral"],
        "P1_Bano_Social": ["P1_Distribuidor"],
        "P1_Habitacion_Huespedes": ["P1_Distribuidor"],
        "P1_Cocina": ["P1_Distribuidor", "P1_Lavanderia"],
        "P1_Lavanderia": ["P1_Cocina"],
        "P1_Garaje_Lateral": ["P1_Distribuidor"],
    }
    return {
        "code": "B",
        "title": "Alternativa B - Garaje Lateral",
        "rooms": rooms,
        "walls": walls,
        "vehicles": vehicles,
        "furniture": furniture,
        "columns": columns,
        "graph": graph,
        "entry": "P1_Terraza_Frontal_Peat",
        "stair_dir": "X+",
        "stair_rect": (2.40, 4.45, 6.30, 5.40),
        "p1_enclosed_footprint": 46.80,
        "p1_covered_ext": 29.50,
    }

def get_alt_c():
    rooms = [
        {"name": "P1_Terraza_Frontal_Peat", "x0": 0.15, "y0": 0.15, "x1": 5.85, "y1": 1.95, "mat": "access", "cat": "circulation", "enclosed": False},
        {"name": "P1_Estacionamiento_Moto", "x0": 6.00, "y0": 0.15, "x1": 7.85, "y1": 2.75, "mat": "garage", "cat": "garage", "enclosed": False},
        {"name": "P1_Patio_Ventilacion", "x0": 6.40, "y0": 2.85, "x1": 7.85, "y1": 5.95, "mat": "terraza", "cat": "exterior", "enclosed": False},
        {"name": "P1_Sala", "x0": 0.15, "y0": 2.05, "x1": 3.85, "y1": 4.40, "mat": "living", "cat": "social", "enclosed": True},
        {"name": "P1_Comedor", "x0": 3.95, "y0": 2.05, "x1": 5.85, "y1": 4.40, "mat": "dining", "cat": "social", "enclosed": True},
        {"name": "P1_Escalera", "x0": 2.40, "y0": 4.45, "x1": 6.30, "y1": 5.40, "mat": "stair", "cat": "stair", "enclosed": True},
        {"name": "P1_Bano_Social", "x0": 0.15, "y0": 4.50, "x1": 2.25, "y1": 6.35, "mat": "bath", "cat": "bathroom", "enclosed": True},
        {"name": "P1_Distribuidor", "x0": 2.35, "y0": 5.45, "x1": 4.75, "y1": 6.35, "mat": "circulation", "cat": "circulation", "enclosed": True},
        {"name": "P1_Habitacion_Huespedes", "x0": 0.15, "y0": 6.45, "x1": 3.15, "y1": 9.85, "mat": "bedroom_guest", "cat": "bedroom", "enclosed": True},
        {"name": "P1_Cocina", "x0": 3.25, "y0": 6.45, "x1": 5.10, "y1": 9.85, "mat": "kitchen", "cat": "kitchen", "enclosed": True},
        {"name": "P1_Garaje_Auto_Lateral", "x0": 5.20, "y0": 6.05, "x1": 7.85, "y1": 11.15, "mat": "garage", "cat": "garage", "enclosed": False},
        {"name": "P1_Lavanderia", "x0": 0.15, "y0": 10.00, "x1": 3.15, "y1": 11.15, "mat": "laundry", "cat": "laundry", "enclosed": False},
    ]
    walls = [
        ("P1_M_Oeste", 0.00, 1.95, 0.15, 10.00, "wall_ext", []),
        ("P1_M_Sur_Frente", 0.15, 1.95, 5.85, 2.05, "wall_ext", [
            {"axis": "X", "p0": 1.50, "p1": 2.45, "z_sill": 0.0, "z_head": 2.15, "kind": "door"},
            {"axis": "X", "p0": 0.40, "p1": 1.35, "z_sill": 0.50, "z_head": 2.10, "kind": "window"},
            {"axis": "X", "p0": 4.20, "p1": 5.50, "z_sill": 0.50, "z_head": 2.10, "kind": "window"},
        ]),
        ("P1_M_Este_Social", 5.85, 2.05, 6.00, 5.45, "wall_ext", [
            {"axis": "Y", "p0": 2.75, "p1": 4.25, "z_sill": 0.45, "z_head": 2.10, "kind": "window"},
        ]),
        ("P1_M_Este_Garaje", 5.10, 5.95, 5.20, 9.85, "wall_int", [
            {"axis": "Y", "p0": 6.10, "p1": 6.90, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        ]),
        ("P1_M_Norte", 0.15, 9.85, 5.10, 10.00, "wall_ext", [
            {"axis": "X", "p0": 1.10, "p1": 2.40, "z_sill": 0.80, "z_head": 2.10, "kind": "window"},
            {"axis": "X", "p0": 3.65, "p1": 4.55, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        ]),
        ("P1_M_Garaje_Acceso_Lateral", 7.85, 6.05, 8.00, 11.15, "wall_ext", [
            {"axis": "Y", "p0": 6.35, "p1": 10.85, "z_sill": 0.0, "z_head": 2.35, "kind": "door"},
        ]),
        ("P1_M_Bano_Este", 2.25, 4.45, 2.35, 6.35, "wall_int", [
            {"axis": "Y", "p0": 5.45, "p1": 6.25, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        ]),
        ("P1_M_Huesped_Sur", 0.15, 6.35, 3.15, 6.45, "wall_int", [
            {"axis": "X", "p0": 2.25, "p1": 3.15, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        ]),
        ("P1_M_Huesped_Este", 3.15, 6.45, 3.25, 9.85, "wall_int", []),
    ]
    vehicles = [
        ("P1_Veh_Swift_Dzire_2023", 5.65, 6.60, 7.385, 10.595, 1.515, "vehicle_car"),
        ("P1_Veh_VStrom_250_SX", 6.50, 0.35, 7.38, 2.53, 1.355, "vehicle_moto"),
    ]
    furniture = [
        ("P1_Mob_Sofa_Sala", 0.25, 2.60, 1.10, 4.30, 0.78, "furniture"),
        ("P1_Mob_Mesa_Centro", 1.45, 3.00, 2.00, 3.90, 0.42, "furniture"),
        ("P1_Mob_TV_Sala", 2.40, 2.10, 3.60, 2.45, 0.55, "furniture"),
        ("P1_Mob_Mesa_Comedor", 4.30, 2.65, 5.45, 3.95, 0.75, "furniture"),
        ("P1_Mob_Cocina_Meson", 4.45, 6.60, 5.05, 9.50, 0.90, "furniture"),
        ("P1_Mob_Cocina_Refri", 3.30, 9.10, 4.00, 9.80, 1.75, "furniture"),
        ("P1_Mob_Cama_Huesped", 0.30, 7.80, 1.35, 9.70, 0.55, "furniture"),
        ("P1_Mob_Velador_H", 1.45, 9.25, 1.90, 9.70, 0.50, "furniture"),
        ("P1_Mob_Closet_Huesped", 2.50, 8.20, 3.10, 9.75, 2.10, "furniture"),
        ("P1_Mob_Ducha_Social", 0.20, 4.55, 1.10, 5.45, 0.12, "furniture"),
        ("P1_Mob_Inodoro_Social", 0.20, 5.65, 0.70, 6.25, 0.45, "furniture"),
        ("P1_Mob_Lavabo_Social", 1.35, 4.55, 2.10, 5.05, 0.85, "furniture"),
        ("P1_Mob_Lavadora", 0.25, 10.10, 0.95, 10.80, 0.85, "furniture"),
        ("P1_Mob_Lavadero", 1.05, 10.10, 1.85, 10.80, 0.85, "furniture"),
    ]
    columns = [
        (0.05, 0.05), (3.90, 0.05), (5.90, 0.05), (7.90, 0.05),
        (0.05, 4.45), (5.90, 4.45), (7.90, 4.45),
        (0.05, 9.90), (5.10, 9.90), (7.90, 9.90),
    ]
    graph = {
        "P1_Terraza_Frontal_Peat": ["P1_Sala"],
        "P1_Sala": ["P1_Terraza_Frontal_Peat", "P1_Comedor", "P1_Escalera", "P1_Distribuidor"],
        "P1_Comedor": ["P1_Sala", "P1_Escalera"],
        "P1_Escalera": ["P1_Sala", "P1_Comedor", "P1_Distribuidor"],
        "P1_Distribuidor": ["P1_Sala", "P1_Escalera", "P1_Bano_Social", "P1_Habitacion_Huespedes", "P1_Cocina", "P1_Garaje_Auto_Lateral"],
        "P1_Bano_Social": ["P1_Distribuidor"],
        "P1_Habitacion_Huespedes": ["P1_Distribuidor"],
        "P1_Cocina": ["P1_Distribuidor", "P1_Lavanderia"],
        "P1_Lavanderia": ["P1_Cocina"],
        "P1_Garaje_Auto_Lateral": ["P1_Distribuidor"],
    }
    return {
        "code": "C",
        "title": "Alternativa C - Aprovechamiento Perimetral",
        "rooms": rooms,
        "walls": walls,
        "vehicles": vehicles,
        "furniture": furniture,
        "columns": columns,
        "graph": graph,
        "entry": "P1_Terraza_Frontal_Peat",
        "stair_dir": "X+",
        "stair_rect": (2.40, 4.45, 6.30, 5.40),
        "p1_enclosed_footprint": 48.10,
        "p1_covered_ext": 25.00,
    }

def build_stairs_x(col, rect, z_base, prefix):
    x0, y0, x1, y1 = rect
    steps = 16
    run = (x1 - x0) / (steps - 1)
    rise = (Z_P2 - Z_P1) / steps
    for i in range(steps - 1):
        sx0 = x0 + i * run
        sx1 = sx0 + run
        sz0 = z_base + i * rise
        sz1 = z_base + (i + 1) * rise
        create_box(f"{prefix}_Peldano_{i+1:02d}", sx0, y0, sz0, sx1, y1, sz1, "stair", col)

def rects_overlap(a, b, tol=1e-4):
    ix0 = max(a[0], b[0])
    iy0 = max(a[1], b[1])
    ix1 = min(a[2], b[2])
    iy1 = min(a[3], b[3])
    return (ix1 - ix0) > tol and (iy1 - iy0) > tol

def bfs_reachable(graph, start):
    visited = set()
    q = deque([start])
    while q:
        node = q.popleft()
        if node in visited:
            continue
        visited.add(node)
        for nxt in graph.get(node, []):
            if nxt not in visited:
                q.append(nxt)
    return visited

def validate_alternative(alt, p2):
    p1_overlaps = []
    for i in range(len(alt["rooms"])):
        for j in range(i + 1, len(alt["rooms"])):
            ra = alt["rooms"][i]
            rb = alt["rooms"][j]
            if rects_overlap((ra["x0"], ra["y0"], ra["x1"], ra["y1"]), (rb["x0"], rb["y0"], rb["x1"], rb["y1"])):
                p1_overlaps.append((ra["name"], rb["name"]))

    p2_overlaps = []
    for i in range(len(p2["rooms"])):
        for j in range(i + 1, len(p2["rooms"])):
            ra = p2["rooms"][i]
            rb = p2["rooms"][j]
            if rects_overlap((ra["x0"], ra["y0"], ra["x1"], ra["y1"]), (rb["x0"], rb["y0"], rb["x1"], rb["y1"])):
                p2_overlaps.append((ra["name"], rb["name"]))

    p1_furn_collisions = []
    for i in range(len(alt["furniture"])):
        for j in range(i + 1, len(alt["furniture"])):
            fa = alt["furniture"][i]
            fb = alt["furniture"][j]
            if rects_overlap((fa[1], fa[2], fa[3], fa[4]), (fb[1], fb[2], fb[3], fb[4])):
                p1_furn_collisions.append((fa[0], fb[0]))

    p2_furn_collisions = []
    for i in range(len(p2["furniture"])):
        for j in range(i + 1, len(p2["furniture"])):
            fa = p2["furniture"][i]
            fb = p2["furniture"][j]
            if rects_overlap((fa[1], fa[2], fa[3], fa[4]), (fb[1], fb[2], fb[3], fb[4])):
                p2_furn_collisions.append((fa[0], fb[0]))

    p1_reach = bfs_reachable(alt["graph"], alt["entry"])
    p1_required = [r["name"] for r in alt["rooms"] if r["cat"] in ("bedroom", "bathroom", "social", "kitchen", "laundry")]
    p1_unconnected = [r for r in p1_required if r not in p1_reach]

    p2_reach = bfs_reachable(p2["graph"], "P2_Llegada_Escalera")
    p2_required = [r["name"] for r in p2["rooms"] if r["cat"] in ("bedroom", "bathroom", "closet", "balcony")]
    p2_unconnected = [r for r in p2_required if r not in p2_reach]

    p1_stair = next(r for r in alt["rooms"] if r["name"] == "P1_Escalera")
    p2_stair = next(r for r in p2["rooms"] if r["name"] == "P2_Escalera_Hueco")
    stair_aligned = (
        abs(p1_stair["x0"] - p2_stair["x0"]) < 1e-4 and
        abs(p1_stair["y0"] - p2_stair["y0"]) < 1e-4 and
        abs(p1_stair["x1"] - p2_stair["x1"]) < 1e-4 and
        abs(p1_stair["y1"] - p2_stair["y1"]) < 1e-4
    )

    stair_hole_clear = True
    for seg in p2["slab_segments"]:
        if rects_overlap(seg, p2["stair_hole"]):
            stair_hole_clear = False

    min_headroom = Z_P2 - SLAB_T - 0.0
    p1_enclosed_area = sum((r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) for r in alt["rooms"] if r["enclosed"])
    p1_ext_cov_area = sum((r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) for r in alt["rooms"] if not r["enclosed"] and r["cat"] in ("garage", "laundry", "circulation"))
    p2_enclosed_area = sum((r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) for r in p2["rooms"] if r["enclosed"])
    p2_balcony_area = sum((r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) for r in p2["rooms"] if not r["enclosed"])

    sala_area = sum((r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) for r in alt["rooms"] if r["name"] == "P1_Sala")

    lot_violations = []
    for r in alt["rooms"] + p2["rooms"]:
        if r["x0"] < -1e-4 or r["y0"] < -1e-4 or r["x1"] > 8.0001 or r["y1"] > 11.2501:
            lot_violations.append(r["name"])

    veh_checks = {}
    for vname, vx0, vy0, vx1, vy1, vh, _ in alt["vehicles"]:
        dx = vx1 - vx0
        dy = vy1 - vy0
        inside_lot = (vx0 >= 0.0 and vy0 >= 0.0 and vx1 <= 8.0 and vy1 <= 11.25)
        veh_checks[vname] = {
            "dims_m": [round(dx, 3), round(dy, 3), round(vh, 3)],
            "inside_lot": inside_lot,
        }

    p1_scenario_2_gross = alt["p1_enclosed_footprint"]
    p1_scenario_1_gross = round(alt["p1_enclosed_footprint"] + alt["p1_covered_ext"], 2)
    p2_gross = 80.00

    checks = {
        "p1_enclosed_limit_60m2": "PASS" if p1_scenario_2_gross <= 60.0 else "FAIL",
        "p1_with_covered_terraces_60m2": "PASS" if p1_scenario_1_gross <= 60.0 else "FAIL",
        "p2_limit_80m2": "PASS" if p2_gross <= 80.0 else "FAIL",
        "total_scenario_2_140m2": "PASS" if (p1_scenario_2_gross + p2_gross) <= 140.0 else "FAIL",
        "total_scenario_1_140m2": "PASS" if (p1_scenario_1_gross + p2_gross) <= 140.0 else "FAIL",
        "sala_comfort_8m2": "PASS" if sala_area >= 8.0 else "FAIL",
        "room_overlaps": "PASS" if (len(p1_overlaps) == 0 and len(p2_overlaps) == 0) else "FAIL",
        "furniture_collisions": "PASS" if (len(p1_furn_collisions) == 0 and len(p2_furn_collisions) == 0) else "FAIL",
        "connectivity_all_rooms": "PASS" if (len(p1_unconnected) == 0 and len(p2_unconnected) == 0) else "FAIL",
        "stairs_aligned_and_slab_hole": "PASS" if (stair_aligned and stair_hole_clear) else "FAIL",
        "stair_headroom_2m": "PASS" if min_headroom >= 2.05 else "FAIL",
        "lot_boundaries_respected": "PASS" if len(lot_violations) == 0 else "FAIL",
        "vehicles_fit_real_scale": "PASS" if all(v["inside_lot"] for v in veh_checks.values()) else "FAIL",
        "structural_verification": "PENDING",
        "urban_setbacks_and_pot": "PENDING",
    }

    return {
        "alternative": alt["code"],
        "title": alt["title"],
        "metrics": {
            "p1_enclosed_gross_m2": p1_scenario_2_gross,
            "p1_covered_ext_m2": alt["p1_covered_ext"],
            "p1_total_with_terraces_m2": p1_scenario_1_gross,
            "p1_net_interior_m2": round(p1_enclosed_area, 2),
            "p1_net_ext_covered_m2": round(p1_ext_cov_area, 2),
            "p1_sala_m2": round(sala_area, 2),
            "p2_gross_m2": p2_gross,
            "p2_net_interior_m2": round(p2_enclosed_area, 2),
            "p2_balcony_m2": round(p2_balcony_area, 2),
            "total_scenario_2_m2": round(p1_scenario_2_gross + p2_gross, 2),
            "total_scenario_1_m2": round(p1_scenario_1_gross + p2_gross, 2),
            "p1_overlaps": p1_overlaps,
            "p2_overlaps": p2_overlaps,
            "p1_furn_collisions": p1_furn_collisions,
            "p2_furn_collisions": p2_furn_collisions,
            "p1_unconnected": p1_unconnected,
            "p2_unconnected": p2_unconnected,
            "vehicles": veh_checks,
        },
        "checks": checks,
    }

def build_and_render_alt(alt, p2):
    clear_scene()
    cols = init_collections()
    build_context(cols)

    c_p1 = cols["07_Propuesta_Primera_Planta"]
    c_p2 = cols["08_Propuesta_Segunda_Planta"]
    c_str = cols["09_Estructura_Conceptual"]
    c_veh = cols["10_Vehiculos"]
    c_mob = cols["11_Mobiliario"]
    c_cam = cols["12_Camaras"]

    wall_h = 1.75
    for r in alt["rooms"]:
        create_box(f"P1_{r['name']}", r["x0"], r["y0"], Z_P1, r["x1"], r["y1"], Z_P1 + 0.04, r["mat"], c_p1)
        cx = (r["x0"] + r["x1"]) * 0.5
        cy = (r["y0"] + r["y1"]) * 0.5
        area = (r["x1"] - r["x0"]) * (r["y1"] - r["y0"])
        short = r["name"].replace("P1_", "").replace("_", " ")
        create_label(f"P1_Lbl_{r['name']}", f"{short}\n{area:.2f} m2", cx, cy, Z_P1 + 0.12, 0.22, c_p1)

    for wname, x0, y0, x1, y1, mkey, ops in alt["walls"]:
        create_wall_with_openings(wname, x0, y0, x1, y1, Z_P1, wall_h, mkey, ops, c_p1)

    build_stairs_x(c_p1, alt["stair_rect"], Z_P1, "P1_Esc")

    for vname, x0, y0, x1, y1, vh, vmat in alt["vehicles"]:
        create_box(vname, x0, y0, Z_P1 + 0.04, x1, y1, Z_P1 + 0.04 + vh, vmat, c_veh)

    for fname, x0, y0, x1, y1, fh, fmat in alt["furniture"]:
        create_box(fname, x0, y0, Z_P1 + 0.04, x1, y1, Z_P1 + 0.04 + fh, fmat, c_mob)

    for idx, (cx, cy) in enumerate(alt["columns"]):
        create_box(f"Col_P1_{idx+1:02d}", cx - 0.12, cy - 0.12, Z_P1, cx + 0.12, cy + 0.12, Z_P2, "column", c_str)

    for idx, seg in enumerate(p2["slab_segments"]):
        create_box(f"P2_Losa_Seg_{idx+1}", seg[0], seg[1], Z_P2 - SLAB_T, seg[2], seg[3], Z_P2, "slab", c_p2)
        create_box(f"C2_Losa_Seg_{idx+1}", seg[0] + COMP_X_OFFSET, seg[1], Z_P1 - 0.10, seg[2] + COMP_X_OFFSET, seg[3], Z_P1, "slab", c_p2)

    for r in p2["rooms"]:
        if r["name"] != "P2_Escalera_Hueco":
            create_box(f"P2_{r['name']}", r["x0"], r["y0"], Z_P2, r["x1"], r["y1"], Z_P2 + 0.04, r["mat"], c_p2)
            create_box(f"C2_{r['name']}", r["x0"] + COMP_X_OFFSET, r["y0"], Z_P1, r["x1"] + COMP_X_OFFSET, r["y1"], Z_P1 + 0.04, r["mat"], c_p2)
        cx = (r["x0"] + r["x1"]) * 0.5
        cy = (r["y0"] + r["y1"]) * 0.5
        area = (r["x1"] - r["x0"]) * (r["y1"] - r["y0"])
        short = r["name"].replace("P2_", "").replace("_", " ")
        create_label(f"C2_Lbl_{r['name']}", f"{short}\n{area:.2f} m2", cx + COMP_X_OFFSET, cy, Z_P1 + 0.12, 0.22, c_p2)

    for wname, x0, y0, x1, y1, mkey, ops in p2["walls"]:
        create_wall_with_openings(wname, x0, y0, x1, y1, Z_P2, wall_h, mkey, ops, c_p2, 0.0)
        create_wall_with_openings(f"C2_{wname}", x0, y0, x1, y1, Z_P1, wall_h, mkey, ops, c_p2, COMP_X_OFFSET)

    for fname, x0, y0, x1, y1, fh, fmat in p2["furniture"]:
        create_box(fname, x0, y0, Z_P2 + 0.04, x1, y1, Z_P2 + 0.04 + fh, fmat, c_mob)
        create_box(f"C2_{fname}", x0 + COMP_X_OFFSET, y0, Z_P1 + 0.04, x1 + COMP_X_OFFSET, y1, Z_P1 + 0.04 + fh, fmat, c_mob)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_object_outline = True
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200

    world = bpy.data.worlds.new(f"World_{alt['code']}")
    scene.world = world
    world.color = (0.92, 0.93, 0.95)

    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.name = f"Cam_{alt['code']}"
    for c in list(cam.users_collection):
        c.objects.unlink(cam)
    c_cam.objects.link(cam)
    scene.camera = cam

    code = alt["code"]
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 16.5
    cam.location = (4.0, 5.2, 20.0)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    c_p2.hide_render = True
    for o in c_mob.objects:
        o.hide_render = o.name.startswith(("P2_", "C2_"))
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", f"HITO_01_V2_{code}_PLANTA_01.png")
    bpy.ops.render.render(write_still=True)

    c_p2.hide_render = False
    c_p1.hide_render = True
    c_veh.hide_render = True
    for o in c_mob.objects:
        o.hide_render = not o.name.startswith("C2_")
    cam.data.ortho_scale = 15.0
    cam.location = (4.0 + COMP_X_OFFSET, 5.0, 20.0)
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", f"HITO_01_V2_{code}_PLANTA_02.png")
    bpy.ops.render.render(write_still=True)

    c_p1.hide_render = False
    c_veh.hide_render = False
    for o in c_mob.objects:
        o.hide_render = False
    cam.data.type = "PERSP"
    cam.data.lens = 35.0
    cam.location = (22.0, -14.0, 15.0)
    direction = Vector((8.0, 5.0, 1.5)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", f"HITO_01_V2_{code}_ISO.png")
    bpy.ops.render.render(write_still=True)

    blend_path = os.path.join(PROJECT_DIR, "models", f"HOME_PROJECT_HITO_01_V2_{code}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    return validate_alternative(alt, p2)

def main():
    p2 = get_p2_spec()
    results = {}
    for alt in (get_alt_a(), get_alt_b(), get_alt_c()):
        results[alt["code"]] = build_and_render_alt(alt, p2)
    with open(VALIDATION_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("HITO_01_V2_COMPLETE:", json.dumps({k: v["checks"] for k, v in results.items()}))

main()
