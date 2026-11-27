import os
import bpy
import bmesh
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
BLEND_PATH = os.path.join(PROJECT_DIR, "models", "HOME_PROJECT_HITO_02.blend")

CLEAR_H = 2.70
SLAB_T = 0.20
Z_P1 = 0.00
Z_P2 = CLEAR_H + SLAB_T
Z_ROOF = Z_P2 + CLEAR_H
EYE_H = 1.65

COLORS = {
    "wall_ext": (0.86, 0.85, 0.83, 1.0),
    "wall_int": (0.90, 0.89, 0.87, 1.0),
    "slab": (0.62, 0.63, 0.65, 1.0),
    "roof": (0.72, 0.73, 0.75, 1.0),
    "column": (0.78, 0.42, 0.28, 1.0),
    "beam": (0.68, 0.38, 0.26, 1.0),
    "linderos": (0.92, 0.22, 0.18, 1.0),
    "cerramiento": (0.20, 0.21, 0.23, 1.0),
    "anden": (0.66, 0.66, 0.68, 1.0),
    "calle": (0.22, 0.23, 0.25, 1.0),
    "terraza": (0.84, 0.78, 0.64, 1.0),
    "garage": (0.50, 0.53, 0.57, 1.0),
    "access": (0.86, 0.80, 0.66, 1.0),
    "circulation": (0.88, 0.84, 0.74, 1.0),
    "living": (0.52, 0.74, 0.86, 1.0),
    "dining": (0.56, 0.78, 0.72, 1.0),
    "kitchen": (0.90, 0.68, 0.46, 1.0),
    "bedroom_guest": (0.74, 0.66, 0.86, 1.0),
    "bedroom_master": (0.62, 0.56, 0.84, 1.0),
    "bedroom_daughter": (0.86, 0.62, 0.74, 1.0),
    "bath": (0.46, 0.80, 0.86, 1.0),
    "laundry": (0.68, 0.80, 0.58, 1.0),
    "stair": (0.80, 0.68, 0.42, 1.0),
    "railing": (0.18, 0.19, 0.21, 1.0),
    "closet": (0.76, 0.66, 0.54, 1.0),
    "balcony": (0.60, 0.78, 0.54, 1.0),
    "furniture": (0.34, 0.26, 0.20, 1.0),
    "vehicle_car": (0.16, 0.36, 0.68, 1.0),
    "vehicle_moto": (0.82, 0.22, 0.18, 1.0),
    "door_leaf": (0.58, 0.38, 0.20, 1.0),
    "garage_door": (0.32, 0.34, 0.38, 1.0),
    "window_glass": (0.55, 0.82, 0.92, 0.45),
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
        bsdf.inputs["Roughness"].default_value = 0.72
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

def create_sectional_garage_door(name, x0, y0, x1, y1, z_base, height, col):
    panels = 4
    ph = height / panels
    for i in range(panels):
        create_box(f"{name}_Panel_{i+1}", x0, y0 + 0.03, z_base + i * ph + 0.01, x1, y1 - 0.03, z_base + (i + 1) * ph - 0.01, "garage_door", col)

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
            elif op["kind"] == "sectional":
                create_sectional_garage_door(f"{prefix}_Porton{idx}", op["p0"], y0, op["p1"], y1, z_base + 0.04, op["z_head"] - 0.04, col)
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
    create_box("Lindero_Oeste", -0.04, 0.0, 0.0, 0.0, 11.25, 0.10, "linderos", cols["01_Linderos_Provisionales"])
    create_box("Lindero_Norte", 0.0, 11.25, 0.0, 8.0, 11.29, 0.10, "linderos", cols["01_Linderos_Provisionales"])
    create_box("Lindero_Sur", 0.0, -0.04, 0.0, 8.0, 0.0, 0.10, "linderos", cols["01_Linderos_Provisionales"])
    create_box("Lindero_Este", 8.0, 0.0, 0.0, 8.04, 11.25, 0.10, "linderos", cols["01_Linderos_Provisionales"])

    create_box("Huella_Existente_Ref", 0.0, 2.0, -0.03, 6.0, 11.25, -0.01, "cerramiento", cols["00_Propiedad_Existente"])
    create_box("Terraza_Frontal_Ref", 0.0, 0.0, -0.02, 8.0, 2.0, 0.0, "terraza", cols["02_Terraza_Frontal"])
    create_box("Terraza_Lateral_Ref", 6.0, 2.0, -0.02, 8.0, 11.25, 0.0, "terraza", cols["03_Terraza_Lateral"])

    create_box("Cerramiento_Sur_Ref", 0.0, 0.0, 0.0, 4.55, 0.08, 1.10, "cerramiento", cols["04_Cerramiento_Existente"])

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
    {"name": "P1_Bano_Social", "x0": 0.15, "y0": 4.75, "x1": 2.05, "y1": 6.65, "mat": "bath", "cat": "bathroom", "enclosed": True},
    {"name": "P1_Distribuidor", "x0": 2.15, "y0": 4.75, "x1": 3.10, "y1": 6.65, "mat": "circulation", "cat": "circulation", "enclosed": True},
    {"name": "P1_Escalera", "x0": 3.10, "y0": 4.75, "x1": 6.85, "y1": 5.70, "mat": "stair", "cat": "stair", "enclosed": True},
    {"name": "P1_Comedor", "x0": 3.10, "y0": 5.80, "x1": 5.65, "y1": 8.05, "mat": "dining", "cat": "social", "enclosed": True},
    {"name": "P1_Cocina", "x0": 5.65, "y0": 5.80, "x1": 7.85, "y1": 8.05, "mat": "kitchen", "cat": "kitchen", "enclosed": True},
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
        {"axis": "X", "p0": 4.75, "p1": 7.70, "z_sill": 0.0, "z_head": 2.35, "kind": "sectional"},
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
    ("P1_M_Bano_Norte", 0.15, 6.65, 2.05, 6.75, "wall_int", []),
    ("P1_M_Bano_Sur", 0.15, 4.65, 4.50, 4.75, "wall_int", [
        {"axis": "X", "p0": 2.15, "p1": 3.05, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P1_M_Bano_Este", 2.05, 4.75, 2.15, 6.65, "wall_int", [
        {"axis": "Y", "p0": 5.30, "p1": 6.10, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P1_M_Huesped_Norte_Cocina", 0.15, 8.05, 7.85, 8.15, "wall_int", [
        {"axis": "X", "p0": 2.15, "p1": 3.10, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
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
    ("P1_Mob_Lavabo_Social", 1.25, 6.10, 2.00, 6.60, 0.85, "furniture"),
    ("P1_Mob_Mesa_Comedor", 3.60, 6.30, 4.80, 7.50, 0.75, "furniture"),
    ("P1_Mob_Cocina_Meson", 7.20, 5.85, 7.80, 8.00, 0.90, "furniture"),
    ("P1_Mob_Cocina_Barra", 5.65, 5.95, 6.20, 7.25, 0.92, "furniture"),
    ("P1_Mob_Cocina_Refri", 5.70, 7.35, 6.40, 8.00, 1.75, "furniture"),
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
    {"name": "P2_Bano_Compartido", "x0": 0.15, "y0": 4.75, "x1": 2.05, "y1": 6.65, "mat": "bath", "cat": "bathroom", "enclosed": True},
    {"name": "P2_Distribuidor_Oeste", "x0": 2.15, "y0": 4.75, "x1": 3.10, "y1": 6.65, "mat": "circulation", "cat": "circulation", "enclosed": True},
    {"name": "P2_Escalera_Hueco", "x0": 3.10, "y0": 4.75, "x1": 6.85, "y1": 5.70, "mat": "stair", "cat": "stair", "enclosed": True},
    {"name": "P2_Llegada_Escalera", "x0": 6.85, "y0": 4.75, "x1": 7.85, "y1": 5.70, "mat": "circulation", "cat": "circulation", "enclosed": True},
    {"name": "P2_Distribuidor_Norte", "x0": 3.10, "y0": 5.70, "x1": 7.85, "y1": 6.65, "mat": "circulation", "cat": "circulation", "enclosed": True},
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
        {"axis": "X", "p0": 2.15, "p1": 3.05, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P2_M_Bano_Comp_Este", 2.05, 4.75, 2.15, 6.65, "wall_int", [
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
    ("P2_Mob_Lavabo_Comp", 1.25, 4.80, 1.95, 5.30, 0.85, "furniture"),
    ("P2_Mob_Cama_Hija_1", 0.30, 7.80, 1.50, 9.75, 0.55, "furniture"),
    ("P2_Mob_Escritorio_H1", 0.30, 6.85, 1.50, 7.45, 0.75, "furniture"),
    ("P2_Mob_Closet_H1", 2.30, 9.20, 3.90, 9.80, 2.10, "furniture"),
    ("P2_Mob_Cama_Hija_2", 6.50, 7.80, 7.70, 9.75, 0.55, "furniture"),
    ("P2_Mob_Escritorio_H2", 6.50, 6.85, 7.70, 7.45, 0.75, "furniture"),
    ("P2_Mob_Closet_H2", 4.10, 9.20, 5.70, 9.80, 2.10, "furniture"),
]

P2_SLAB_SEGMENTS = [
    (0.00, 0.00, 8.00, 4.75),
    (0.00, 4.75, 3.10, 5.70),
    (6.85, 4.75, 8.00, 5.70),
    (0.00, 5.70, 8.00, 10.00),
]

COLUMNS = [
    (0.125, 0.125), (4.55, 0.125), (7.875, 0.125),
    (0.125, 4.70), (4.55, 4.70), (7.875, 4.70),
    (0.125, 8.10), (4.55, 8.10), (7.875, 8.10),
    (0.125, 9.875), (7.875, 9.875),
]

BEAMS = [
    (0.00, 0.00, 8.00, 0.25),
    (0.00, 4.575, 8.00, 4.825),
    (0.00, 7.975, 8.00, 8.225),
    (0.00, 9.75, 8.00, 10.00),
    (0.00, 0.25, 0.25, 9.75),
    (4.425, 0.25, 4.675, 8.00),
    (7.75, 0.25, 8.00, 9.75),
]

RV_CAMERAS = [
    ("Cam_RV_01_Entrada_Principal", (1.10, -0.80, Z_P1 + EYE_H), (1.10, 2.50, Z_P1 + 1.40)),
    ("Cam_RV_02_Garaje", (6.20, -0.50, Z_P1 + EYE_H), (6.20, 3.00, Z_P1 + 1.20)),
    ("Cam_RV_03_Sala", (0.80, 2.20, Z_P1 + EYE_H), (3.20, 3.60, Z_P1 + 1.30)),
    ("Cam_RV_04_Comedor", (3.50, 6.20, Z_P1 + EYE_H), (6.80, 7.20, Z_P1 + 1.20)),
    ("Cam_RV_05_Cocina", (5.90, 6.20, Z_P1 + EYE_H), (7.50, 7.60, Z_P1 + 1.10)),
    ("Cam_RV_06_Habitacion_Huespedes", (3.80, 8.50, Z_P1 + EYE_H), (1.00, 10.00, Z_P1 + 1.00)),
    ("Cam_RV_07_Inicio_Escalera", (2.60, 5.22, Z_P1 + EYE_H), (6.50, 5.22, Z_P1 + 2.20)),
    ("Cam_RV_08_Desembarco_P2", (7.35, 5.22, Z_P2 + EYE_H), (4.00, 6.10, Z_P2 + 1.30)),
    ("Cam_RV_09_Habitacion_Principal", (3.80, 3.90, Z_P2 + EYE_H), (2.20, 0.80, Z_P2 + 1.20)),
    ("Cam_RV_10_Habitacion_Hija_1", (3.40, 7.00, Z_P2 + EYE_H), (1.00, 9.20, Z_P2 + 1.10)),
    ("Cam_RV_11_Habitacion_Hija_2", (4.50, 7.00, Z_P2 + EYE_H), (7.00, 9.20, Z_P2 + 1.10)),
]

WALKTHROUGH_WAYPOINTS = [
    (0, (9.0, -5.5, Z_P1 + 2.2), (4.0, 2.5, Z_P1 + 1.6)),
    (96, (1.12, -1.0, Z_P1 + EYE_H), (1.12, 2.5, Z_P1 + 1.5)),
    (192, (1.12, 2.5, Z_P1 + EYE_H), (2.60, 4.2, Z_P1 + 1.4)),
    (288, (2.60, 4.2, Z_P1 + EYE_H), (2.60, 6.8, Z_P1 + 1.4)),
    (384, (2.60, 7.2, Z_P1 + EYE_H), (1.80, 9.5, Z_P1 + 1.2)),
    (480, (2.60, 7.2, Z_P1 + EYE_H), (5.50, 7.0, Z_P1 + 1.3)),
    (576, (2.60, 5.22, Z_P1 + EYE_H), (6.80, 5.22, Z_P2 + 0.8)),
    (720, (7.35, 5.22, Z_P2 + EYE_H), (7.35, 6.20, Z_P2 + 1.5)),
    (816, (5.50, 6.20, Z_P2 + EYE_H), (2.60, 6.20, Z_P2 + 1.5)),
    (912, (2.60, 4.00, Z_P2 + EYE_H), (2.20, 0.80, Z_P2 + 1.2)),
    (1008, (3.40, 6.20, Z_P2 + EYE_H), (1.20, 8.80, Z_P2 + 1.2)),
    (1152, (4.60, 6.20, Z_P2 + EYE_H), (6.80, 8.80, Z_P2 + 1.2)),
]

def build_stairs_and_railings(col, x0, y0, x1, y1, z_base):
    steps = 16
    run = (x1 - x0) / (steps - 1)
    rise = (Z_P2 - Z_P1) / steps
    for i in range(steps - 1):
        sx0 = x0 + i * run
        sx1 = sx0 + run
        sz0 = z_base + i * rise
        sz1 = z_base + (i + 1) * rise
        create_box(f"P1_Esc_Peldano_{i+1:02d}", sx0, y0, sz0, sx1, y1, sz1, "stair", col)
    create_box("P2_Baranda_Hueco_Norte", x0, y1 - 0.05, Z_P2, x1, y1, Z_P2 + 0.95, "railing", col)
    create_box("P2_Baranda_Hueco_Oeste", x0, y0, Z_P2, x0 + 0.05, y1, Z_P2 + 0.95, "railing", col)

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

    for r in P1_ROOMS:
        create_box(f"P1_Piso_{r['name']}", r["x0"], r["y0"], Z_P1, r["x1"], r["y1"], Z_P1 + 0.04, r["mat"], c_p1)

    for wname, x0, y0, x1, y1, mkey, ops in P1_WALLS:
        create_wall_with_openings(wname, x0, y0, x1, y1, Z_P1, CLEAR_H, mkey, ops, c_p1)

    build_stairs_and_railings(c_p1, 3.10, 4.75, 6.85, 5.70, Z_P1)

    for vname, x0, y0, x1, y1, vh, vmat in P1_VEHICLES:
        create_box(vname, x0, y0, Z_P1 + 0.04, x1, y1, Z_P1 + 0.04 + vh, vmat, c_veh)

    for fname, x0, y0, x1, y1, fh, fmat in P1_FURNITURE:
        create_box(fname, x0, y0, Z_P1 + 0.04, x1, y1, Z_P1 + 0.04 + fh, fmat, c_mob)

    for idx, (cx, cy) in enumerate(COLUMNS):
        create_box(f"Col_P1_{idx+1:02d}", cx - 0.125, cy - 0.125, Z_P1, cx + 0.125, cy + 0.125, Z_P2, "column", c_str)
        create_box(f"Col_P2_{idx+1:02d}", cx - 0.125, cy - 0.125, Z_P2, cx + 0.125, cy + 0.125, Z_ROOF, "column", c_str)

    for idx, b in enumerate(BEAMS):
        create_box(f"Viga_P1_{idx+1:02d}", b[0], b[1], Z_P2 - SLAB_T - 0.25, b[2], b[3], Z_P2 - SLAB_T, "beam", c_str)
        create_box(f"Viga_P2_{idx+1:02d}", b[0], b[1], Z_ROOF - 0.25, b[2], b[3], Z_ROOF, "beam", c_str)

    for idx, seg in enumerate(P2_SLAB_SEGMENTS):
        create_box(f"P2_Losa_Seg_{idx+1}", seg[0], seg[1], Z_P2 - SLAB_T, seg[2], seg[3], Z_P2, "slab", c_str)

    create_box("Cubierta_Plana_Superior", 0.00, 0.00, Z_ROOF, 8.00, 10.00, Z_ROOF + SLAB_T, "roof", c_p2)
    create_box("Pretil_Sur", 0.00, 0.00, Z_ROOF + SLAB_T, 8.00, 0.15, Z_ROOF + SLAB_T + 0.55, "wall_ext", c_p2)
    create_box("Pretil_Este", 7.85, 0.15, Z_ROOF + SLAB_T, 8.00, 10.00, Z_ROOF + SLAB_T + 0.55, "wall_ext", c_p2)
    create_box("Pretil_Norte", 0.00, 9.85, Z_ROOF + SLAB_T, 7.85, 10.00, Z_ROOF + SLAB_T + 0.55, "wall_ext", c_p2)
    create_box("Pretil_Oeste", 0.00, 0.15, Z_ROOF + SLAB_T, 0.15, 9.85, Z_ROOF + SLAB_T + 0.55, "wall_ext", c_p2)

    for r in P2_ROOMS:
        if r["name"] != "P2_Escalera_Hueco":
            create_box(f"P2_Piso_{r['name']}", r["x0"], r["y0"], Z_P2, r["x1"], r["y1"], Z_P2 + 0.04, r["mat"], c_p2)

    for wname, x0, y0, x1, y1, mkey, ops in P2_WALLS:
        create_wall_with_openings(wname, x0, y0, x1, y1, Z_P2, CLEAR_H, mkey, ops, c_p2)

    for fname, x0, y0, x1, y1, fh, fmat in P2_FURNITURE:
        create_box(fname, x0, y0, Z_P2 + 0.04, x1, y1, Z_P2 + 0.04 + fh, fmat, c_mob)

    for cname, loc, tgt in RV_CAMERAS:
        add_rv_camera(cname, loc, tgt, c_rv)

    bpy.ops.object.camera_add()
    anim_cam = bpy.context.active_object
    anim_cam.name = "Cam_Recorrido_Anim"
    anim_cam.data.lens = 24.0
    for c in list(anim_cam.users_collection):
        c.objects.unlink(anim_cam)
    c_rv.objects.link(anim_cam)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_object_outline = True
    scene.render.fps = 24
    scene.frame_start = 0
    scene.frame_end = 1152

    for frame, loc, tgt in WALKTHROUGH_WAYPOINTS:
        anim_cam.location = loc
        direction = Vector(tgt) - Vector(loc)
        anim_cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        anim_cam.keyframe_insert(data_path="location", frame=frame)
        anim_cam.keyframe_insert(data_path="rotation_euler", frame=frame)

    world = bpy.data.worlds.new("World_Hito2")
    scene.world = world
    world.color = (0.90, 0.92, 0.94)

    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.name = "Cam_Presentacion"
    for c in list(cam.users_collection):
        c.objects.unlink(cam)
    c_cam.objects.link(cam)
    scene.camera = cam

    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"

    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 12.5
    cam.location = (4.0, -10.0, 3.2)
    cam.rotation_euler = (1.5708, 0.0, 0.0)
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_02_FACHADA_FRONTAL.png")
    bpy.ops.render.render(write_still=True)

    cam.data.ortho_scale = 14.0
    cam.location = (18.0, 5.5, 3.2)
    cam.rotation_euler = (1.5708, 0.0, 1.5708)
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_02_FACHADA_LATERAL.png")
    bpy.ops.render.render(write_still=True)

    cam.data.type = "PERSP"
    cam.data.lens = 28.0
    cam.location = (14.5, -8.5, 4.5)
    cam.rotation_euler = (Vector((4.0, 4.5, 2.5)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_02_ESQUINA.png")
    bpy.ops.render.render(write_still=True)

    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 14.5
    cam.location = (4.0, 5.2, 18.0)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    cam.data.clip_start = 16.4
    c_p2.hide_render = True
    for o in c_str.objects:
        if o.name.startswith(("P2_Losa", "Viga_", "Col_P2")):
            o.hide_render = True
    for o in c_mob.objects:
        o.hide_render = o.name.startswith("P2_")
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_02_PLANTA_01.png")
    bpy.ops.render.render(write_still=True)

    c_p2.hide_render = False
    c_p1.hide_render = True
    c_veh.hide_render = True
    cam.data.clip_start = 13.4
    for o in c_p2.objects:
        if o.name.startswith(("Cubierta_", "Pretil_")):
            o.hide_render = True
    for o in c_str.objects:
        if o.name.startswith(("Viga_P2", "Col_P1")):
            o.hide_render = True
    for o in c_mob.objects:
        o.hide_render = not o.name.startswith("P2_")
    cam.location = (4.0, 5.0, 18.0)
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_02_PLANTA_02.png")
    bpy.ops.render.render(write_still=True)

    c_p1.hide_render = False
    c_veh.hide_render = False
    for o in c_p2.objects:
        o.hide_render = False
    for o in c_str.objects:
        o.hide_render = False
    for o in c_mob.objects:
        o.hide_render = False
    cam.data.clip_start = 0.1

    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 10.5
    cam.location = (4.8, -5.0, 3.0)
    cam.rotation_euler = (1.5708, 0.0, 0.0)
    cam.data.clip_start = 9.75
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_02_CORTE_ESCALERA.png")
    bpy.ops.render.render(write_still=True)
    cam.data.clip_start = 0.1

    scene.camera = anim_cam
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.image_settings.media_type = "VIDEO"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_02_RECORRIDO_PRELIMINAR.mp4")
    bpy.ops.render.render(animation=True)

    scene.camera = cam
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print("HITO_02_BUILD_COMPLETE")

main()
