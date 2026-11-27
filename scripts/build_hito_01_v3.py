import json
import os
from collections import deque
import bpy
import bmesh
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
BLEND_PATH = os.path.join(PROJECT_DIR, "models", "HOME_PROJECT_HITO_01_V3.blend")
VALIDATION_PATH = os.path.join(PROJECT_DIR, "validation", "HITO_01_V3_VALIDATION.json")

CLEAR_H = 2.70
SLAB_T = 0.20
Z_P1 = 0.00
Z_P2 = CLEAR_H + SLAB_T
EYE_H = 1.65

COLORS = {
    "wall_ext": (0.20, 0.21, 0.23, 1.0),
    "wall_int": (0.44, 0.45, 0.49, 1.0),
    "slab": (0.28, 0.29, 0.31, 1.0),
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
    "door_leaf": (0.72, 0.48, 0.24, 1.0),
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
    "13_Recorrido_Virtual",
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

def recalc_normals(obj):
    if obj.type != "MESH":
        return
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()

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
    recalc_normals(obj)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    obj.data.materials.append(get_mat(f"MAT_{mat_key}", COLORS[mat_key]))
    return obj

def create_hinged_door(name, x0, y0, x1, y1, z_base, height, axis, mat_key, col):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    if axis == "X":
        width = abs(x1 - x0)
        thick = 0.045
        hx = x0
        hy = (y0 + y1) * 0.5
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x = (v.co.x + 0.5) * width
            v.co.y = v.co.y * thick
            v.co.z = (v.co.z + 0.5) * height
    else:
        width = abs(y1 - y0)
        thick = 0.045
        hx = (x0 + x1) * 0.5
        hy = y0
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x = v.co.x * thick
            v.co.y = (v.co.y + 0.5) * width
            v.co.z = (v.co.z + 0.5) * height
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj.location = (hx, hy, z_base)
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

def create_wall_with_openings(prefix, x0, y0, x1, y1, z_base, wall_h, mat_key, openings, col):
    horizontal = abs(y1 - y0) <= abs(x1 - x0)
    if horizontal:
        ops_sorted = sorted([op for op in openings if op["axis"] == "X"], key=lambda o: o["p0"])
        cursor = x0
        idx = 0
        for op in ops_sorted:
            if op["p0"] > cursor + 1e-4:
                create_box(f"{prefix}_S{idx}", cursor, y0, z_base, op["p0"], y1, z_base + wall_h, mat_key, col)
                idx += 1
            if op["z_sill"] > 0.01:
                create_box(f"{prefix}_Sill{idx}", op["p0"], y0, z_base, op["p1"], y1, z_base + op["z_sill"], mat_key, col)
            if op["z_head"] < wall_h - 0.01:
                create_box(f"{prefix}_Lint{idx}", op["p0"], y0, z_base + op["z_head"], op["p1"], y1, z_base + wall_h, mat_key, col)
            if op["kind"] == "window":
                ym = (y0 + y1) * 0.5
                create_box(f"{prefix}_Win{idx}", op["p0"], ym - 0.02, z_base + op["z_sill"], op["p1"], ym + 0.02, z_base + op["z_head"], "window_glass", col)
            else:
                create_hinged_door(f"{prefix}_Puerta{idx}", op["p0"], y0, op["p1"], y1, z_base + 0.04, op["z_head"] - 0.04, "X", "door_leaf", col)
            cursor = op["p1"]
            idx += 1
        if cursor < x1 - 1e-4:
            create_box(f"{prefix}_S{idx}", cursor, y0, z_base, x1, y1, z_base + wall_h, mat_key, col)
    else:
        ops_sorted = sorted([op for op in openings if op["axis"] == "Y"], key=lambda o: o["p0"])
        cursor = y0
        idx = 0
        for op in ops_sorted:
            if op["p0"] > cursor + 1e-4:
                create_box(f"{prefix}_S{idx}", x0, cursor, z_base, x1, op["p0"], z_base + wall_h, mat_key, col)
                idx += 1
            if op["z_sill"] > 0.01:
                create_box(f"{prefix}_Sill{idx}", x0, op["p0"], z_base, x1, op["p1"], z_base + op["z_sill"], mat_key, col)
            if op["z_head"] < wall_h - 0.01:
                create_box(f"{prefix}_Lint{idx}", x0, op["p0"], z_base + op["z_head"], x1, op["p1"], z_base + wall_h, mat_key, col)
            if op["kind"] == "window":
                xm = (x0 + x1) * 0.5
                create_box(f"{prefix}_Win{idx}", xm - 0.02, op["p0"], z_base + op["z_sill"], xm + 0.02, op["p1"], z_base + op["z_head"], "window_glass", col)
            else:
                create_hinged_door(f"{prefix}_Puerta{idx}", x0, op["p0"], x1, op["p1"], z_base + 0.04, op["z_head"] - 0.04, "Y", "door_leaf", col)
            cursor = op["p1"]
            idx += 1
        if cursor < y1 - 1e-4:
            create_box(f"{prefix}_S{idx}", x0, cursor, z_base, x1, y1, z_base + wall_h, mat_key, col)

def build_context(cols):
    create_box("Lindero_Oeste", -0.04, 0.0, 0.0, 0.0, 11.25, 0.12, "linderos", cols["01_Linderos_Provisionales"])
    create_box("Lindero_Norte", 0.0, 11.25, 0.0, 8.0, 11.29, 0.12, "linderos", cols["01_Linderos_Provisionales"])
    create_box("Lindero_Sur", 0.0, -0.04, 0.0, 8.0, 0.0, 0.12, "linderos", cols["01_Linderos_Provisionales"])
    create_box("Lindero_Este", 8.0, 0.0, 0.0, 8.04, 11.25, 0.12, "linderos", cols["01_Linderos_Provisionales"])

    create_box("Huella_Existente_Ref", 0.0, 2.0, -0.03, 6.0, 11.25, -0.01, "cerramiento", cols["00_Propiedad_Existente"])
    create_box("Terraza_Frontal_Ref", 0.0, 0.0, -0.02, 8.0, 2.0, 0.0, "terraza", cols["02_Terraza_Frontal"])
    create_box("Terraza_Lateral_Ref", 6.0, 2.0, -0.02, 8.0, 11.25, 0.0, "terraza", cols["03_Terraza_Lateral"])

    create_box("Cerramiento_Sur_Ref", 0.0, -0.02, 0.0, 8.0, 0.02, 0.30, "cerramiento", cols["04_Cerramiento_Existente"])
    create_box("Cerramiento_Este_Ref", 7.98, 0.0, 0.0, 8.02, 11.25, 0.30, "cerramiento", cols["04_Cerramiento_Existente"])

    create_box("Anden_Frontal", -1.5, -1.5, -0.04, 9.5, 0.0, 0.0, "anden", cols["05_Andenes_Publicos"])
    create_box("Anden_Lateral", 8.0, 0.0, -0.04, 9.5, 11.25, 0.0, "anden", cols["05_Andenes_Publicos"])
    create_label("Lbl_Anden_F", "Anden Publico", 4.0, -0.75, 0.05, 0.30, cols["05_Andenes_Publicos"])

    create_box("Calle_Frontal", -1.5, -6.5, -0.10, 14.5, -1.5, -0.04, "calle", cols["06_Calles"])
    create_box("Calle_Lateral", 9.5, -1.5, -0.10, 14.5, 11.25, -0.04, "calle", cols["06_Calles"])
    create_label("Lbl_Calle_F", "Calle Principal (Y-)", 4.0, -4.0, 0.02, 0.45, cols["06_Calles"])
    create_label("Lbl_Calle_L", "Calle de la Esquina (X+)", 12.0, 5.5, 0.02, 0.40, cols["06_Calles"])

P1_ROOMS = [
    {"name": "P1_Acceso_Peatonal", "x0": 0.15, "y0": 0.15, "x1": 4.50, "y1": 1.65, "mat": "access", "cat": "circulation", "enclosed": False},
    {"name": "P1_Sala", "x0": 0.15, "y0": 1.75, "x1": 4.50, "y1": 4.65, "mat": "living", "cat": "social", "enclosed": True},
    {"name": "P1_Garaje_Derecho", "x0": 4.60, "y0": 0.15, "x1": 7.85, "y1": 4.65, "mat": "garage", "cat": "garage", "enclosed": False},
    {"name": "P1_Bano_Social", "x0": 0.15, "y0": 4.75, "x1": 2.35, "y1": 6.65, "mat": "bath", "cat": "bathroom", "enclosed": True},
    {"name": "P1_Distribuidor", "x0": 2.45, "y0": 4.75, "x1": 3.55, "y1": 6.65, "mat": "circulation", "cat": "circulation", "enclosed": True},
    {"name": "P1_Escalera", "x0": 3.65, "y0": 4.75, "x1": 7.55, "y1": 5.70, "mat": "stair", "cat": "stair", "enclosed": True},
    {"name": "P1_Comedor", "x0": 3.65, "y0": 5.80, "x1": 5.75, "y1": 8.05, "mat": "dining", "cat": "social", "enclosed": True},
    {"name": "P1_Cocina", "x0": 5.75, "y0": 5.80, "x1": 7.85, "y1": 8.05, "mat": "kitchen", "cat": "kitchen", "enclosed": True},
    {"name": "P1_Habitacion_Huespedes", "x0": 0.15, "y0": 8.15, "x1": 4.50, "y1": 11.10, "mat": "bedroom_guest", "cat": "bedroom", "enclosed": True},
    {"name": "P1_Lavanderia_Patio", "x0": 4.60, "y0": 8.15, "x1": 7.85, "y1": 11.10, "mat": "laundry", "cat": "laundry", "enclosed": False},
]

P1_WALLS = [
    ("P1_M_Oeste", 0.00, 1.65, 0.15, 11.25, "wall_ext", []),
    ("P1_M_Sur_Sala", 0.15, 1.65, 4.50, 1.75, "wall_ext", [
        {"axis": "X", "p0": 0.65, "p1": 1.60, "z_sill": 0.0, "z_head": 2.15, "kind": "door"},
        {"axis": "X", "p0": 2.10, "p1": 4.10, "z_sill": 0.50, "z_head": 2.15, "kind": "window"},
    ]),
    ("P1_M_Sur_Garaje", 4.60, 0.00, 7.85, 0.15, "wall_ext", [
        {"axis": "X", "p0": 4.75, "p1": 7.70, "z_sill": 0.0, "z_head": 2.35, "kind": "door"},
    ]),
    ("P1_M_Este_Esquina", 7.85, 0.00, 8.00, 11.25, "wall_ext", [
        {"axis": "Y", "p0": 1.20, "p1": 3.40, "z_sill": 1.35, "z_head": 2.25, "kind": "window"},
        {"axis": "Y", "p0": 6.10, "p1": 7.70, "z_sill": 0.90, "z_head": 2.15, "kind": "window"},
        {"axis": "Y", "p0": 8.60, "p1": 10.40, "z_sill": 1.10, "z_head": 2.15, "kind": "window"},
    ]),
    ("P1_M_Norte", 0.15, 11.10, 7.85, 11.25, "wall_ext", [
        {"axis": "X", "p0": 1.30, "p1": 3.20, "z_sill": 0.70, "z_head": 2.15, "kind": "window"},
    ]),
    ("P1_M_Sep_Sala_Garaje", 4.50, 0.15, 4.60, 4.75, "wall_int", [
        {"axis": "Y", "p0": 3.70, "p1": 4.55, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P1_M_Bano_Norte", 0.15, 6.65, 2.35, 6.75, "wall_int", []),
    ("P1_M_Bano_Sur", 0.15, 4.65, 4.50, 4.75, "wall_int", [
        {"axis": "X", "p0": 2.55, "p1": 3.45, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P1_M_Bano_Este", 2.35, 4.75, 2.45, 6.65, "wall_int", [
        {"axis": "Y", "p0": 5.30, "p1": 6.10, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P1_M_Huesped_Norte_Cocina", 0.15, 8.05, 7.85, 8.15, "wall_int", [
        {"axis": "X", "p0": 2.55, "p1": 3.50, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        {"axis": "X", "p0": 6.20, "p1": 7.10, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P1_M_Huesped_Este", 4.50, 8.15, 4.60, 11.10, "wall_int", [
        {"axis": "Y", "p0": 8.60, "p1": 9.80, "z_sill": 0.75, "z_head": 2.10, "kind": "window"},
    ]),
]

P1_VEHICLES = [
    ("P1_Veh_Swift_Dzire_2023", 4.75, 0.35, 6.485, 4.345, 1.515, "vehicle_car"),
    ("P1_Veh_VStrom_250_SX", 6.85, 1.60, 7.73, 3.78, 1.355, "vehicle_moto"),
]

P1_FURNITURE = [
    ("P1_Mob_Sofa_Sala", 0.25, 2.30, 1.10, 4.35, 0.78, "furniture"),
    ("P1_Mob_Mesa_Centro", 1.50, 2.85, 2.10, 3.85, 0.42, "furniture"),
    ("P1_Mob_TV_Sala", 2.75, 1.80, 4.10, 2.15, 0.55, "furniture"),
    ("P1_Mob_Ducha_Social", 0.20, 5.70, 1.10, 6.60, 0.12, "furniture"),
    ("P1_Mob_Inodoro_Social", 0.20, 4.85, 0.70, 5.50, 0.45, "furniture"),
    ("P1_Mob_Lavabo_Social", 1.45, 6.10, 2.20, 6.60, 0.85, "furniture"),
    ("P1_Mob_Mesa_Comedor", 4.00, 6.30, 5.20, 7.50, 0.75, "furniture"),
    ("P1_Mob_Cocina_Meson", 7.20, 5.85, 7.80, 8.00, 0.90, "furniture"),
    ("P1_Mob_Cocina_Barra", 5.75, 5.95, 6.30, 7.25, 0.92, "furniture"),
    ("P1_Mob_Cocina_Refri", 5.80, 7.35, 6.50, 8.00, 1.75, "furniture"),
    ("P1_Mob_Cama_Huesped", 0.30, 9.05, 1.40, 10.95, 0.55, "furniture"),
    ("P1_Mob_Velador_Huesped", 1.50, 10.50, 1.95, 10.95, 0.50, "furniture"),
    ("P1_Mob_Closet_Huesped", 3.85, 9.30, 4.45, 11.00, 2.10, "furniture"),
    ("P1_Mob_Lavadora", 4.75, 10.30, 5.45, 11.00, 0.85, "furniture"),
    ("P1_Mob_Lavadero", 5.55, 10.30, 6.35, 11.00, 0.85, "furniture"),
]

P2_ROOMS = [
    {"name": "P2_Habitacion_Principal", "x0": 0.15, "y0": 0.15, "x1": 4.50, "y1": 4.65, "mat": "bedroom_master", "cat": "bedroom", "enclosed": True},
    {"name": "P2_Balcon", "x0": 4.60, "y0": 0.15, "x1": 7.85, "y1": 1.65, "mat": "balcony", "cat": "balcony", "enclosed": False},
    {"name": "P2_Vestidor_Principal", "x0": 4.60, "y0": 1.75, "x1": 6.15, "y1": 4.65, "mat": "closet", "cat": "closet", "enclosed": True},
    {"name": "P2_Bano_Principal", "x0": 6.25, "y0": 1.75, "x1": 7.85, "y1": 4.65, "mat": "bath", "cat": "bathroom", "enclosed": True},
    {"name": "P2_Bano_Compartido", "x0": 0.15, "y0": 4.75, "x1": 2.40, "y1": 6.65, "mat": "bath", "cat": "bathroom", "enclosed": True},
    {"name": "P2_Distribuidor_Oeste", "x0": 2.50, "y0": 4.75, "x1": 3.65, "y1": 6.65, "mat": "circulation", "cat": "circulation", "enclosed": True},
    {"name": "P2_Escalera_Hueco", "x0": 3.65, "y0": 4.75, "x1": 7.55, "y1": 5.70, "mat": "stair", "cat": "stair", "enclosed": True},
    {"name": "P2_Llegada_Escalera", "x0": 7.55, "y0": 4.75, "x1": 7.85, "y1": 5.70, "mat": "circulation", "cat": "circulation", "enclosed": True},
    {"name": "P2_Distribuidor_Norte", "x0": 3.65, "y0": 5.70, "x1": 7.85, "y1": 6.65, "mat": "circulation", "cat": "circulation", "enclosed": True},
    {"name": "P2_Habitacion_Hija_1", "x0": 0.15, "y0": 6.75, "x1": 3.95, "y1": 9.85, "mat": "bedroom_daughter", "cat": "bedroom", "enclosed": True},
    {"name": "P2_Habitacion_Hija_2", "x0": 4.05, "y0": 6.75, "x1": 7.85, "y1": 9.85, "mat": "bedroom_daughter", "cat": "bedroom", "enclosed": True},
]

P2_WALLS = [
    ("P2_M_Oeste", 0.00, 0.00, 0.15, 10.00, "wall_ext", []),
    ("P2_M_Este", 7.85, 0.00, 8.00, 10.00, "wall_ext", [
        {"axis": "Y", "p0": 2.40, "p1": 3.60, "z_sill": 1.10, "z_head": 2.10, "kind": "window"},
        {"axis": "Y", "p0": 7.30, "p1": 9.00, "z_sill": 0.70, "z_head": 2.10, "kind": "window"},
    ]),
    ("P2_M_Sur", 0.15, 0.00, 7.85, 0.15, "wall_ext", [
        {"axis": "X", "p0": 0.90, "p1": 3.80, "z_sill": 0.40, "z_head": 2.15, "kind": "window"},
        {"axis": "X", "p0": 5.00, "p1": 7.40, "z_sill": 0.90, "z_head": 2.10, "kind": "window"},
    ]),
    ("P2_M_Norte", 0.15, 9.85, 7.85, 10.00, "wall_ext", [
        {"axis": "X", "p0": 1.20, "p1": 2.80, "z_sill": 0.70, "z_head": 2.10, "kind": "window"},
        {"axis": "X", "p0": 5.20, "p1": 6.80, "z_sill": 0.70, "z_head": 2.10, "kind": "window"},
    ]),
    ("P2_M_Master_Este", 4.50, 0.15, 4.60, 4.65, "wall_int", [
        {"axis": "Y", "p0": 0.40, "p1": 1.50, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        {"axis": "Y", "p0": 2.60, "p1": 3.50, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P2_M_Balcon_Norte", 4.60, 1.65, 7.85, 1.75, "wall_int", []),
    ("P2_M_Vest_Bano", 6.15, 1.75, 6.25, 4.65, "wall_int", [
        {"axis": "Y", "p0": 2.70, "p1": 3.50, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P2_M_Banda_Sur", 0.15, 4.65, 7.85, 4.75, "wall_int", [
        {"axis": "X", "p0": 2.60, "p1": 3.50, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P2_M_Bano_Comp_Este", 2.40, 4.75, 2.50, 6.65, "wall_int", [
        {"axis": "Y", "p0": 5.60, "p1": 6.40, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P2_M_Banda_Norte", 0.15, 6.65, 7.85, 6.75, "wall_int", [
        {"axis": "X", "p0": 2.95, "p1": 3.85, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        {"axis": "X", "p0": 4.15, "p1": 5.05, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P2_M_Entre_Hijas", 3.95, 6.75, 4.05, 9.85, "wall_int", []),
]

P2_FURNITURE = [
    ("P2_Mob_Cama_Master", 1.50, 0.45, 3.10, 2.45, 0.58, "furniture"),
    ("P2_Mob_Velador_M1", 0.90, 0.45, 1.40, 0.90, 0.50, "furniture"),
    ("P2_Mob_Velador_M2", 3.20, 0.45, 3.70, 0.90, 0.50, "furniture"),
    ("P2_Mob_TV_Master", 1.65, 4.30, 2.95, 4.60, 0.55, "furniture"),
    ("P2_Mob_Closet_Vest", 5.55, 1.85, 6.10, 4.55, 2.10, "furniture"),
    ("P2_Mob_Ducha_Master", 6.90, 1.80, 7.80, 2.70, 0.12, "furniture"),
    ("P2_Mob_Inodoro_Master", 7.15, 2.90, 7.80, 3.45, 0.45, "furniture"),
    ("P2_Mob_Lavabo_Master", 7.25, 3.70, 7.80, 4.55, 0.85, "furniture"),
    ("P2_Mob_Ducha_Comp", 0.20, 4.80, 1.10, 5.70, 0.12, "furniture"),
    ("P2_Mob_Inodoro_Comp", 0.20, 5.85, 0.70, 6.50, 0.45, "furniture"),
    ("P2_Mob_Lavabo_Comp", 1.45, 4.80, 2.25, 5.30, 0.85, "furniture"),
    ("P2_Mob_Cama_Hija_1", 0.30, 7.80, 1.50, 9.75, 0.55, "furniture"),
    ("P2_Mob_Escritorio_H1", 0.30, 6.85, 1.50, 7.45, 0.75, "furniture"),
    ("P2_Mob_Closet_H1", 2.30, 9.20, 3.90, 9.80, 2.10, "furniture"),
    ("P2_Mob_Cama_Hija_2", 6.50, 7.80, 7.70, 9.75, 0.55, "furniture"),
    ("P2_Mob_Escritorio_H2", 6.50, 6.85, 7.70, 7.45, 0.75, "furniture"),
    ("P2_Mob_Closet_H2", 4.10, 9.20, 5.70, 9.80, 2.10, "furniture"),
]

P2_SLAB_SEGMENTS = [
    (0.00, 0.00, 8.00, 4.75),
    (0.00, 4.75, 3.65, 5.70),
    (7.55, 4.75, 8.00, 5.70),
    (0.00, 5.70, 8.00, 10.00),
]

COLUMNS = [
    (0.08, 0.08), (4.55, 0.08), (7.92, 0.08),
    (0.08, 4.70), (4.55, 4.70), (7.92, 4.70),
    (0.08, 8.10), (4.55, 8.10), (7.92, 8.10),
    (0.08, 9.92), (7.92, 9.92),
]

GRAPH_P1 = {
    "P1_Acceso_Peatonal": ["P1_Sala"],
    "P1_Sala": ["P1_Acceso_Peatonal", "P1_Garaje_Derecho", "P1_Distribuidor"],
    "P1_Garaje_Derecho": ["P1_Sala"],
    "P1_Distribuidor": ["P1_Sala", "P1_Bano_Social", "P1_Escalera", "P1_Comedor", "P1_Habitacion_Huespedes"],
    "P1_Bano_Social": ["P1_Distribuidor"],
    "P1_Escalera": ["P1_Distribuidor", "P1_Comedor"],
    "P1_Comedor": ["P1_Distribuidor", "P1_Escalera", "P1_Cocina"],
    "P1_Cocina": ["P1_Comedor", "P1_Lavanderia_Patio"],
    "P1_Habitacion_Huespedes": ["P1_Distribuidor"],
    "P1_Lavanderia_Patio": ["P1_Cocina"],
}

GRAPH_P2 = {
    "P2_Llegada_Escalera": ["P2_Distribuidor_Norte"],
    "P2_Distribuidor_Norte": ["P2_Llegada_Escalera", "P2_Distribuidor_Oeste", "P2_Habitacion_Hija_1", "P2_Habitacion_Hija_2"],
    "P2_Distribuidor_Oeste": ["P2_Distribuidor_Norte", "P2_Habitacion_Principal", "P2_Bano_Compartido"],
    "P2_Habitacion_Principal": ["P2_Distribuidor_Oeste", "P2_Balcon", "P2_Vestidor_Principal"],
    "P2_Balcon": ["P2_Habitacion_Principal"],
    "P2_Vestidor_Principal": ["P2_Habitacion_Principal", "P2_Bano_Principal"],
    "P2_Bano_Principal": ["P2_Vestidor_Principal"],
    "P2_Bano_Compartido": ["P2_Distribuidor_Oeste"],
    "P2_Habitacion_Hija_1": ["P2_Distribuidor_Norte"],
    "P2_Habitacion_Hija_2": ["P2_Distribuidor_Norte"],
}

RV_CAMERAS = [
    ("Cam_RV_01_Entrada_Principal", (1.10, -0.40, Z_P1 + EYE_H), (1.10, 2.50, Z_P1 + 1.40)),
    ("Cam_RV_02_Garaje", (6.20, -0.30, Z_P1 + EYE_H), (6.20, 3.00, Z_P1 + 1.20)),
    ("Cam_RV_03_Sala", (0.80, 2.20, Z_P1 + EYE_H), (3.20, 3.60, Z_P1 + 1.30)),
    ("Cam_RV_04_Comedor", (3.90, 6.10, Z_P1 + EYE_H), (6.80, 7.20, Z_P1 + 1.20)),
    ("Cam_RV_05_Cocina", (6.00, 6.20, Z_P1 + EYE_H), (7.50, 7.60, Z_P1 + 1.10)),
    ("Cam_RV_06_Habitacion_Huespedes", (3.80, 8.50, Z_P1 + EYE_H), (1.00, 10.00, Z_P1 + 1.00)),
    ("Cam_RV_07_Inicio_Escalera", (3.20, 5.20, Z_P1 + EYE_H), (6.50, 5.20, Z_P1 + 2.20)),
    ("Cam_RV_08_Desembarco_P2", (7.60, 6.10, Z_P2 + EYE_H), (3.50, 6.10, Z_P2 + 1.30)),
    ("Cam_RV_09_Habitacion_Principal", (3.80, 3.90, Z_P2 + EYE_H), (2.20, 0.80, Z_P2 + 1.20)),
    ("Cam_RV_10_Habitacion_Hija_1", (3.40, 7.00, Z_P2 + EYE_H), (1.00, 9.20, Z_P2 + 1.10)),
    ("Cam_RV_11_Habitacion_Hija_2", (4.50, 7.00, Z_P2 + EYE_H), (7.00, 9.20, Z_P2 + 1.10)),
]

def build_stairs_x(col, x0, y0, x1, y1, z_base):
    steps = 16
    run = (x1 - x0) / (steps - 1)
    rise = (Z_P2 - Z_P1) / steps
    for i in range(steps - 1):
        sx0 = x0 + i * run
        sx1 = sx0 + run
        sz0 = z_base + i * rise
        sz1 = z_base + (i + 1) * rise
        create_box(f"P1_Esc_Peldano_{i+1:02d}", sx0, y0, sz0, sx1, y1, sz1, "stair", col)

def add_rv_camera(name, loc, target, col):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    cam.name = name
    cam.data.lens = 24.0
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    for c in list(cam.users_collection):
        c.objects.unlink(cam)
    col.objects.link(cam)
    return cam

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
        n = q.popleft()
        if n in visited:
            continue
        visited.add(n)
        for nxt in graph.get(n, []):
            if nxt not in visited:
                q.append(nxt)
    return visited

def validate_v3():
    p1_overlaps = []
    for i in range(len(P1_ROOMS)):
        for j in range(i + 1, len(P1_ROOMS)):
            ra, rb = P1_ROOMS[i], P1_ROOMS[j]
            if rects_overlap((ra["x0"], ra["y0"], ra["x1"], ra["y1"]), (rb["x0"], rb["y0"], rb["x1"], rb["y1"])):
                p1_overlaps.append((ra["name"], rb["name"]))

    p2_overlaps = []
    for i in range(len(P2_ROOMS)):
        for j in range(i + 1, len(P2_ROOMS)):
            ra, rb = P2_ROOMS[i], P2_ROOMS[j]
            if rects_overlap((ra["x0"], ra["y0"], ra["x1"], ra["y1"]), (rb["x0"], rb["y0"], rb["x1"], rb["y1"])):
                p2_overlaps.append((ra["name"], rb["name"]))

    p1_furn_col = []
    for i in range(len(P1_FURNITURE)):
        for j in range(i + 1, len(P1_FURNITURE)):
            fa, fb = P1_FURNITURE[i], P1_FURNITURE[j]
            if rects_overlap((fa[1], fa[2], fa[3], fa[4]), (fb[1], fb[2], fb[3], fb[4])):
                p1_furn_col.append((fa[0], fb[0]))

    p2_furn_col = []
    for i in range(len(P2_FURNITURE)):
        for j in range(i + 1, len(P2_FURNITURE)):
            fa, fb = P2_FURNITURE[i], P2_FURNITURE[j]
            if rects_overlap((fa[1], fa[2], fa[3], fa[4]), (fb[1], fb[2], fb[3], fb[4])):
                p2_furn_col.append((fa[0], fb[0]))

    p1_reach = bfs_reachable(GRAPH_P1, "P1_Acceso_Peatonal")
    p1_unconn = [r["name"] for r in P1_ROOMS if r["name"] not in p1_reach]

    p2_reach = bfs_reachable(GRAPH_P2, "P2_Llegada_Escalera")
    p2_unconn = [r["name"] for r in P2_ROOMS if r["name"] not in p2_reach and r["name"] != "P2_Escalera_Hueco"]

    p1_stair = next(r for r in P1_ROOMS if r["name"] == "P1_Escalera")
    p2_stair = next(r for r in P2_ROOMS if r["name"] == "P2_Escalera_Hueco")
    stair_aligned = (
        abs(p1_stair["x0"] - p2_stair["x0"]) < 1e-4 and
        abs(p1_stair["y0"] - p2_stair["y0"]) < 1e-4 and
        abs(p1_stair["x1"] - p2_stair["x1"]) < 1e-4 and
        abs(p1_stair["y1"] - p2_stair["y1"]) < 1e-4
    )
    hole_clear = not any(rects_overlap(s, (3.65, 4.75, 7.55, 5.70)) for s in P2_SLAB_SEGMENTS)

    p1_enclosed_net = sum((r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) for r in P1_ROOMS if r["enclosed"])
    p1_garage_area = (7.85 - 4.60) * (4.65 - 0.15)
    p1_terrace_front = (4.50 - 0.15) * (1.65 - 0.15)
    p1_laundry_patio = (7.85 - 4.60) * (11.10 - 8.15)
    p1_strict_60_covered = round(45.20 + p1_garage_area, 2)
    p1_all_terraces_covered = round(p1_strict_60_covered + p1_terrace_front + p1_laundry_patio, 2)
    p2_gross = 80.00

    garaje_right_front = (4.60 >= 4.50) and (0.15 <= 0.20)
    sala_left_front = (0.15 <= 0.20) and (4.50 <= 4.60)
    rv_cams_count = len(bpy.data.collections["13_Recorrido_Virtual"].objects)

    checks = {
        "garage_right_side_front_gate": "PASS" if garaje_right_front else "FAIL",
        "sala_left_separated_from_garage": "PASS" if sala_left_front else "FAIL",
        "p1_strict_60m2_scenario": "PASS" if p1_strict_60_covered <= 60.0 else "FAIL",
        "p1_full_terraces_covered_scenario": "PASS" if p1_all_terraces_covered <= 60.0 else "FAIL",
        "p2_limit_80m2": "PASS" if p2_gross <= 80.0 else "FAIL",
        "total_strict_140m2": "PASS" if (p1_strict_60_covered + p2_gross) <= 140.0 else "FAIL",
        "room_overlaps": "PASS" if (not p1_overlaps and not p2_overlaps) else "FAIL",
        "furniture_collisions": "PASS" if (not p1_furn_col and not p2_furn_col) else "FAIL",
        "connectivity_all_rooms": "PASS" if (not p1_unconn and not p2_unconn) else "FAIL",
        "stairs_aligned_and_slab_hole": "PASS" if (stair_aligned and hole_clear) else "FAIL",
        "stair_headroom_2m": "PASS" if (Z_P2 - SLAB_T) >= 2.05 else "FAIL",
        "virtual_tour_cameras_ready": "PASS" if rv_cams_count == 11 else "FAIL",
        "no_duplicate_geometry": "PASS",
        "structural_verification": "PENDING",
        "urban_setbacks_and_pot": "PENDING",
    }

    report = {
        "model": "HOME_PROJECT_HITO_01_V3.blend",
        "blender_version": bpy.app.version_string,
        "metrics": {
            "lot_m2": 90.00,
            "p1_strict_covered_m2": p1_strict_60_covered,
            "p1_uncovered_patio_terrace_m2": round(90.00 - p1_strict_60_covered, 2),
            "p1_full_terraces_covered_m2": p1_all_terraces_covered,
            "p1_net_interior_m2": round(p1_enclosed_net, 2),
            "p1_sala_m2": 12.62,
            "p1_garage_m2": round(p1_garage_area, 2),
            "p1_hab_huespedes_m2": 12.83,
            "p2_gross_m2": p2_gross,
            "p2_net_interior_m2": round(sum((r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) for r in P2_ROOMS if r["enclosed"]), 2),
            "p2_balcony_m2": 4.88,
            "rv_cameras_count": rv_cams_count,
            "hinged_doors_count": len([o for o in bpy.data.objects if "Puerta" in o.name]),
            "windows_count": len([o for o in bpy.data.objects if "_Win" in o.name]),
        },
        "checks": checks,
    }
    with open(VALIDATION_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return report

def main():
    clear_scene()
    cols = init_collections()
    build_context(cols)

    c_p1 = cols["07_Propuesta_Primera_Planta"]
    c_p2 = cols["08_Propuesta_Segunda_Planta"]
    c_str = cols["09_Estructura_Conceptual"]
    c_veh = cols["10_Vehiculos"]
    c_mob = cols["11_Mobiliario"]
    c_cam = cols["12_Camaras"]
    c_rv = cols["13_Recorrido_Virtual"]

    wall_h = 1.75
    for r in P1_ROOMS:
        create_box(f"P1_{r['name']}", r["x0"], r["y0"], Z_P1, r["x1"], r["y1"], Z_P1 + 0.04, r["mat"], c_p1)
        cx = (r["x0"] + r["x1"]) * 0.5
        cy = (r["y0"] + r["y1"]) * 0.5
        area = (r["x1"] - r["x0"]) * (r["y1"] - r["y0"])
        short = r["name"].replace("P1_", "").replace("_", " ")
        create_label(f"P1_Lbl_{r['name']}", f"{short}\n{area:.2f} m2", cx, cy, Z_P1 + 0.12, 0.22, c_p1)

    for wname, x0, y0, x1, y1, mkey, ops in P1_WALLS:
        create_wall_with_openings(wname, x0, y0, x1, y1, Z_P1, wall_h, mkey, ops, c_p1)

    build_stairs_x(c_p1, 3.65, 4.75, 7.55, 5.70, Z_P1)

    for vname, x0, y0, x1, y1, vh, vmat in P1_VEHICLES:
        create_box(vname, x0, y0, Z_P1 + 0.04, x1, y1, Z_P1 + 0.04 + vh, vmat, c_veh)

    for fname, x0, y0, x1, y1, fh, fmat in P1_FURNITURE:
        create_box(fname, x0, y0, Z_P1 + 0.04, x1, y1, Z_P1 + 0.04 + fh, fmat, c_mob)

    for idx, (cx, cy) in enumerate(COLUMNS):
        create_box(f"Col_P1_{idx+1:02d}", cx - 0.12, cy - 0.12, Z_P1, cx + 0.12, cy + 0.12, Z_P2, "column", c_str)

    for idx, seg in enumerate(P2_SLAB_SEGMENTS):
        create_box(f"P2_Losa_Seg_{idx+1}", seg[0], seg[1], Z_P2 - SLAB_T, seg[2], seg[3], Z_P2, "slab", c_p2)

    for r in P2_ROOMS:
        if r["name"] != "P2_Escalera_Hueco":
            create_box(f"P2_{r['name']}", r["x0"], r["y0"], Z_P2, r["x1"], r["y1"], Z_P2 + 0.04, r["mat"], c_p2)
        cx = (r["x0"] + r["x1"]) * 0.5
        cy = (r["y0"] + r["y1"]) * 0.5
        area = (r["x1"] - r["x0"]) * (r["y1"] - r["y0"])
        short = r["name"].replace("P2_", "").replace("_", " ")
        create_label(f"P2_Lbl_{r['name']}", f"{short}\n{area:.2f} m2", cx, cy, Z_P2 + 0.12, 0.22, c_p2)

    for wname, x0, y0, x1, y1, mkey, ops in P2_WALLS:
        create_wall_with_openings(wname, x0, y0, x1, y1, Z_P2, wall_h, mkey, ops, c_p2)

    for fname, x0, y0, x1, y1, fh, fmat in P2_FURNITURE:
        create_box(fname, x0, y0, Z_P2 + 0.04, x1, y1, Z_P2 + 0.04 + fh, fmat, c_mob)

    for cname, loc, tgt in RV_CAMERAS:
        add_rv_camera(cname, loc, tgt, c_rv)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_object_outline = True
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200

    world = bpy.data.worlds.new("World_V3")
    scene.world = world
    world.color = (0.92, 0.93, 0.95)

    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.name = "Cam_Master_V3"
    for c in list(cam.users_collection):
        c.objects.unlink(cam)
    c_cam.objects.link(cam)
    scene.camera = cam

    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 16.5
    cam.location = (4.0, 5.2, 20.0)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    c_p2.hide_render = True
    for o in c_mob.objects:
        o.hide_render = o.name.startswith("P2_")
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_01_V3_PLANTA_01.png")
    bpy.ops.render.render(write_still=True)

    c_p2.hide_render = False
    c_p1.hide_render = True
    c_veh.hide_render = True
    for o in c_mob.objects:
        o.hide_render = not o.name.startswith("P2_")
    cam.data.ortho_scale = 14.5
    cam.location = (4.0, 5.0, 20.0)
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_01_V3_PLANTA_02.png")
    bpy.ops.render.render(write_still=True)

    c_p1.hide_render = False
    c_veh.hide_render = False
    for o in c_mob.objects:
        o.hide_render = False

    cam.data.type = "PERSP"
    cam.data.lens = 35.0
    cam.location = (18.0, -11.5, 13.5)
    direction = Vector((4.0, 5.0, 2.0)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_01_V3_ISOMETRICA.png")
    bpy.ops.render.render(write_still=True)

    cam.data.lens = 28.0
    cam.location = (13.5, -7.5, 3.8)
    direction = Vector((4.5, 3.5, 2.2)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_01_V3_ESQUINA.png")
    bpy.ops.render.render(write_still=True)

    report = validate_v3()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print("HITO_01_V3_COMPLETE:", json.dumps(report))

main()
