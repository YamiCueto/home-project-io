import math
import os
import bpy
import bmesh
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
BLEND_PATH = os.path.join(PROJECT_DIR, "models", "HOME_PROJECT_HITO_03.blend")

CLEAR_H = 2.70
SLAB_T = 0.20
Z_P1 = 0.00
Z_P2 = CLEAR_H + SLAB_T
Z_ROOF = Z_P2 + CLEAR_H
EYE_H = 1.65

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
    "14_Fachadas_Y_Vegetacion",
    "15_Iluminacion",
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
    for lgt in list(bpy.data.lights):
        bpy.data.lights.remove(lgt)
    for txt in list(bpy.data.curves):
        bpy.data.curves.remove(txt)

def init_collections():
    cols = {}
    for name in COLLECTION_NAMES:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
        cols[name] = col
    return cols

def build_procedural_pbr_materials():
    mats = {}

    def new_mat(name, base_col, rough=0.6, metal=0.0, trans=0.0, bump_scale=0.0, brick=False, wave=False, c2=None):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nt = mat.node_tree
        nodes = nt.nodes
        links = nt.links
        bsdf = nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = base_col
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if trans > 0.0:
            bsdf.inputs["Transmission Weight"].default_value = trans
            bsdf.inputs["IOR"].default_value = 1.52
        mat.diffuse_color = base_col
        if bump_scale > 0.0 or brick or wave:
            tex_coord = nodes.new("ShaderNodeTexCoord")
            if brick:
                brk = nodes.new("ShaderNodeTexBrick")
                brk.inputs["Scale"].default_value = 4.5
                brk.inputs["Color1"].default_value = base_col
                brk.inputs["Color2"].default_value = c2 if c2 else base_col
                brk.inputs["Mortar"].default_value = (0.18, 0.18, 0.18, 1.0)
                brk.inputs["Mortar Size"].default_value = 0.025
                links.new(tex_coord.outputs["Object"], brk.inputs["Vector"])
                links.new(brk.outputs["Color"], bsdf.inputs["Base Color"])
                bmp = nodes.new("ShaderNodeBump")
                bmp.inputs["Strength"].default_value = bump_scale
                links.new(brk.outputs["Fac"], bmp.inputs["Height"])
                links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
            elif wave:
                wv = nodes.new("ShaderNodeTexWave")
                wv.wave_type = "BANDS"
                wv.inputs["Scale"].default_value = 6.0
                wv.inputs["Distortion"].default_value = 6.5
                wv.inputs["Detail"].default_value = 4.0
                ramp = nodes.new("ShaderNodeValToRGB")
                ramp.color_ramp.elements[0].color = base_col
                ramp.color_ramp.elements[1].color = c2 if c2 else base_col
                links.new(tex_coord.outputs["Object"], wv.inputs["Vector"])
                links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
                links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
                bmp = nodes.new("ShaderNodeBump")
                bmp.inputs["Strength"].default_value = bump_scale
                links.new(wv.outputs["Fac"], bmp.inputs["Height"])
                links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
            else:
                ns = nodes.new("ShaderNodeTexNoise")
                ns.inputs["Scale"].default_value = 28.0
                ns.inputs["Detail"].default_value = 6.0
                links.new(tex_coord.outputs["Object"], ns.inputs["Vector"])
                bmp = nodes.new("ShaderNodeBump")
                bmp.inputs["Strength"].default_value = bump_scale
                links.new(ns.outputs["Fac"], bmp.inputs["Height"])
                links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
        mats[name] = mat
        return mat

    new_mat("MAT_estuco_blanco", (0.91, 0.90, 0.87, 1.0), rough=0.78, bump_scale=0.06)
    new_mat("MAT_concreto_arq", (0.48, 0.49, 0.50, 1.0), rough=0.72, bump_scale=0.14)
    new_mat("MAT_piedra_natural", (0.42, 0.39, 0.35, 1.0), rough=0.85, bump_scale=0.30, brick=True, c2=(0.30, 0.28, 0.25, 1.0))
    new_mat("MAT_madera_ext", (0.38, 0.22, 0.11, 1.0), rough=0.45, bump_scale=0.12, wave=True, c2=(0.24, 0.13, 0.06, 1.0))
    new_mat("MAT_aluminio_negro", (0.05, 0.05, 0.06, 1.0), rough=0.28, metal=0.88)
    new_mat("MAT_antracita", (0.14, 0.15, 0.17, 1.0), rough=0.38, metal=0.45, bump_scale=0.05)
    new_mat("MAT_vidrio_arq", (0.86, 0.94, 0.97, 1.0), rough=0.03, trans=0.92)
    new_mat("MAT_porcelanato_ext", (0.72, 0.70, 0.66, 1.0), rough=0.35, bump_scale=0.05, brick=True, c2=(0.68, 0.66, 0.62, 1.0))
    new_mat("MAT_wall_int", (0.88, 0.87, 0.85, 1.0), rough=0.80)
    new_mat("MAT_slab", (0.55, 0.56, 0.58, 1.0), rough=0.75)
    new_mat("MAT_linderos", (0.90, 0.20, 0.18, 1.0), rough=0.6)
    new_mat("MAT_anden", (0.62, 0.62, 0.64, 1.0), rough=0.88, bump_scale=0.10)
    new_mat("MAT_calle", (0.13, 0.14, 0.15, 1.0), rough=0.92, bump_scale=0.15)
    new_mat("MAT_follaje_tropical", (0.12, 0.34, 0.11, 1.0), rough=0.55, bump_scale=0.08)
    new_mat("MAT_tierra", (0.18, 0.12, 0.08, 1.0), rough=0.95)
    new_mat("MAT_vehicle_car", (0.12, 0.30, 0.62, 1.0), rough=0.20, metal=0.65)
    new_mat("MAT_vehicle_moto", (0.78, 0.18, 0.12, 1.0), rough=0.25, metal=0.55)
    new_mat("MAT_furniture", (0.34, 0.26, 0.20, 1.0), rough=0.65)
    new_mat("MAT_stair", (0.74, 0.62, 0.44, 1.0), rough=0.55)
    new_mat("MAT_solar_panel", (0.06, 0.10, 0.22, 1.0), rough=0.15, metal=0.35)
    new_mat("MAT_luz_calida", (1.0, 0.84, 0.58, 1.0), rough=0.2)
    bsdf_l = mats["MAT_luz_calida"].node_tree.nodes.get("Principled BSDF")
    bsdf_l.inputs["Emission Color"].default_value = (1.0, 0.82, 0.55, 1.0)
    bsdf_l.inputs["Emission Strength"].default_value = 6.0
    return mats

def recalc_normals(obj):
    if obj.type != "MESH":
        return
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()

def create_box(name, x0, y0, z0, x1, y1, z1, mat, col):
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
    obj.data.materials.append(mat)
    return obj

def create_hinged_door(name, x0, y0, x1, y1, z_base, height, axis, mat, col):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    if axis == "X":
        width = abs(x1 - x0)
        thick = 0.05
        hx = x0
        hy = (y0 + y1) * 0.5
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x = (v.co.x + 0.5) * width
            v.co.y = v.co.y * thick
            v.co.z = (v.co.z + 0.5) * height
    else:
        width = abs(y1 - y0)
        thick = 0.05
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
    obj.data.materials.append(mat)
    return obj

def create_window_unit(prefix, x0, y0, z0, x1, y1, z1, axis, mats, col):
    ft = 0.045
    if axis == "X":
        ym = (y0 + y1) * 0.5
        create_box(f"{prefix}_Glass", x0 + ft, ym - 0.015, z0 + ft, x1 - ft, ym + 0.015, z1 - ft, mats["MAT_vidrio_arq"], col)
        create_box(f"{prefix}_FrameB", x0, y0, z0, x1, y1, z0 + ft, mats["MAT_aluminio_negro"], col)
        create_box(f"{prefix}_FrameT", x0, y0, z1 - ft, x1, y1, z1, mats["MAT_aluminio_negro"], col)
        create_box(f"{prefix}_FrameL", x0, y0, z0 + ft, x0 + ft, y1, z1 - ft, mats["MAT_aluminio_negro"], col)
        create_box(f"{prefix}_FrameR", x1 - ft, y0, z0 + ft, x1, y1, z1 - ft, mats["MAT_aluminio_negro"], col)
    else:
        xm = (x0 + x1) * 0.5
        create_box(f"{prefix}_Glass", xm - 0.015, y0 + ft, z0 + ft, xm + 0.015, y1 - ft, z1 - ft, mats["MAT_vidrio_arq"], col)
        create_box(f"{prefix}_FrameB", x0, y0, z0, x1, y1, z0 + ft, mats["MAT_aluminio_negro"], col)
        create_box(f"{prefix}_FrameT", x0, y0, z1 - ft, x1, y1, z1, mats["MAT_aluminio_negro"], col)
        create_box(f"{prefix}_FrameL", x0, y0, z0 + ft, x1, y0 + ft, z1 - ft, mats["MAT_aluminio_negro"], col)
        create_box(f"{prefix}_FrameR", x0, y1 - ft, z0 + ft, x1, y1, z1 - ft, mats["MAT_aluminio_negro"], col)

def create_wall_with_openings(prefix, x0, y0, x1, y1, z_base, wall_h, mat, openings, mats, col):
    horizontal = abs(y1 - y0) <= abs(x1 - x0)
    if horizontal:
        ops_sorted = sorted([op for op in openings if op["axis"] == "X"], key=lambda o: o["p0"])
        cursor = x0
        idx = 0
        for op in ops_sorted:
            if op["p0"] > cursor + 1e-4:
                create_box(f"{prefix}_S{idx}", cursor, y0, z_base, op["p0"], y1, z_base + wall_h, mat, col)
                idx += 1
            if op["z_sill"] > 0.01:
                create_box(f"{prefix}_Sill{idx}", op["p0"], y0, z_base, op["p1"], y1, z_base + op["z_sill"], mat, col)
            if op["z_head"] < wall_h - 0.01:
                create_box(f"{prefix}_Lint{idx}", op["p0"], y0, z_base + op["z_head"], op["p1"], y1, z_base + wall_h, mat, col)
            if op["kind"] == "window":
                create_window_unit(f"{prefix}_Win{idx}", op["p0"], y0, z_base + op["z_sill"], op["p1"], y1, z_base + op["z_head"], "X", mats, col)
            elif op["kind"] == "sectional":
                panels = 4
                ph = (op["z_head"] - 0.04) / panels
                for p in range(panels):
                    create_box(f"{prefix}_Porton{idx}_P{p+1}", op["p0"], y0 + 0.02, z_base + 0.04 + p * ph + 0.01, op["p1"], y1 - 0.02, z_base + 0.04 + (p + 1) * ph - 0.01, mats["MAT_antracita"], col)
            else:
                dmat = mats["MAT_madera_ext"]
                create_hinged_door(f"{prefix}_Puerta{idx}", op["p0"], y0, op["p1"], y1, z_base + 0.04, op["z_head"] - 0.04, "X", dmat, col)
            cursor = op["p1"]
            idx += 1
        if cursor < x1 - 1e-4:
            create_box(f"{prefix}_S{idx}", cursor, y0, z_base, x1, y1, z_base + wall_h, mat, col)
    else:
        ops_sorted = sorted([op for op in openings if op["axis"] == "Y"], key=lambda o: o["p0"])
        cursor = y0
        idx = 0
        for op in ops_sorted:
            if op["p0"] > cursor + 1e-4:
                create_box(f"{prefix}_S{idx}", x0, cursor, z_base, x1, op["p0"], z_base + wall_h, mat, col)
                idx += 1
            if op["z_sill"] > 0.01:
                create_box(f"{prefix}_Sill{idx}", x0, op["p0"], z_base, x1, op["p1"], z_base + op["z_sill"], mat, col)
            if op["z_head"] < wall_h - 0.01:
                create_box(f"{prefix}_Lint{idx}", x0, op["p0"], z_base + op["z_head"], x1, op["p1"], z_base + wall_h, mat, col)
            if op["kind"] == "window":
                create_window_unit(f"{prefix}_Win{idx}", x0, op["p0"], z_base + op["z_sill"], x1, op["p1"], z_base + op["z_head"], "Y", mats, col)
            else:
                create_hinged_door(f"{prefix}_Puerta{idx}", x0, op["p0"], x1, op["p1"], z_base + 0.04, op["z_head"] - 0.04, "Y", mats["MAT_madera_ext"], col)
            cursor = op["p1"]
            idx += 1
        if cursor < y1 - 1e-4:
            create_box(f"{prefix}_S{idx}", x0, cursor, z_base, x1, y1, z_base + wall_h, mat, col)

def create_tropical_plant(name, cx, cy, z_base, height, mats, col):
    create_box(f"{name}_Maceta", cx - 0.24, cy - 0.24, z_base, cx + 0.24, cy + 0.24, z_base + 0.42, mats["MAT_concreto_arq"], col)
    create_box(f"{name}_Tierra", cx - 0.20, cy - 0.20, z_base + 0.38, cx + 0.20, cy + 0.20, z_base + 0.43, mats["MAT_tierra"], col)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=height * 0.65, location=(cx, cy, z_base + 0.42 + height * 0.32))
    trunk = bpy.context.active_object
    trunk.name = f"{name}_Tronco"
    for c in list(trunk.users_collection):
        c.objects.unlink(trunk)
    col.objects.link(trunk)
    trunk.data.materials.append(mats["MAT_madera_ext"])
    for k in range(5):
        ang = k * (2.0 * math.pi / 5.0)
        fx = cx + math.cos(ang) * 0.22
        fy = cy + math.sin(ang) * 0.22
        fz = z_base + 0.42 + height * 0.65 + (k % 2) * 0.14
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.28, location=(fx, fy, fz))
        leaf = bpy.context.active_object
        leaf.name = f"{name}_Follaje_{k+1}"
        leaf.scale = (1.2, 1.2, 0.55)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        for c in list(leaf.users_collection):
            c.objects.unlink(leaf)
        col.objects.link(leaf)
        leaf.data.materials.append(mats["MAT_follaje_tropical"])

def add_light(name, ltype, loc, energy, color, size, col):
    ldata = bpy.data.lights.new(name=name, type=ltype)
    ldata.energy = energy
    ldata.color = color
    if ltype == "AREA":
        ldata.size = size
    elif ltype == "POINT":
        ldata.shadow_soft_size = size
    elif ltype == "SUN":
        ldata.angle = 0.03
    lobj = bpy.data.objects.new(name=name, object_data=ldata)
    lobj.location = loc
    col.objects.link(lobj)
    return lobj

def build_context(cols, mats):
    create_box("Lindero_Oeste", -0.04, 0.0, 0.0, 0.0, 11.25, 0.08, mats["MAT_linderos"], cols["01_Linderos_Provisionales"])
    create_box("Lindero_Norte", 0.0, 11.25, 0.0, 8.0, 11.29, 0.08, mats["MAT_linderos"], cols["01_Linderos_Provisionales"])
    create_box("Lindero_Sur", 0.0, -0.04, 0.0, 8.0, 0.0, 0.08, mats["MAT_linderos"], cols["01_Linderos_Provisionales"])
    create_box("Lindero_Este", 8.0, 0.0, 0.0, 8.04, 11.25, 0.08, mats["MAT_linderos"], cols["01_Linderos_Provisionales"])
    create_box("Anden_Frontal", -2.5, -1.5, -0.05, 11.0, 0.0, 0.0, mats["MAT_anden"], cols["05_Andenes_Publicos"])
    create_box("Anden_Lateral", 8.0, 0.0, -0.05, 9.5, 12.5, 0.0, mats["MAT_anden"], cols["05_Andenes_Publicos"])
    create_box("Calle_Frontal", -3.0, -8.5, -0.12, 16.5, -1.5, -0.05, mats["MAT_calle"], cols["06_Calles"])
    create_box("Calle_Lateral", 9.5, -1.5, -0.12, 16.5, 13.0, -0.05, mats["MAT_calle"], cols["06_Calles"])

P1_ROOMS = [
    ("P1_Acceso_Peatonal", 0.15, 0.15, 4.50, 1.65, "MAT_porcelanato_ext"),
    ("P1_Sala", 0.15, 1.75, 4.50, 4.65, "MAT_porcelanato_ext"),
    ("P1_Garaje_Derecho", 4.60, 0.15, 7.85, 4.65, "MAT_concreto_arq"),
    ("P1_Bano_Social", 0.15, 4.75, 2.05, 6.65, "MAT_porcelanato_ext"),
    ("P1_Distribuidor", 2.15, 4.75, 3.10, 6.65, "MAT_porcelanato_ext"),
    ("P1_Escalera", 3.10, 4.75, 6.85, 5.70, "MAT_stair"),
    ("P1_Comedor", 3.10, 5.80, 5.65, 8.05, "MAT_porcelanato_ext"),
    ("P1_Cocina", 5.65, 5.80, 7.85, 8.05, "MAT_porcelanato_ext"),
    ("P1_Habitacion_Huespedes", 0.15, 8.15, 4.50, 11.10, "MAT_porcelanato_ext"),
    ("P1_Lavanderia_Patio", 4.60, 8.15, 7.85, 11.10, "MAT_porcelanato_ext"),
]

P1_WALLS = [
    ("P1_M_Oeste", 0.00, 1.65, 0.15, 11.25, "MAT_estuco_blanco", []),
    ("P1_M_Sur_Sala", 0.15, 1.65, 4.50, 1.75, "MAT_estuco_blanco", [
        {"axis": "X", "p0": 0.65, "p1": 1.60, "z_sill": 0.0, "z_head": 2.15, "kind": "door"},
        {"axis": "X", "p0": 2.10, "p1": 4.10, "z_sill": 0.50, "z_head": 2.15, "kind": "window"},
    ]),
    ("P1_M_Sur_Garaje", 4.60, 0.00, 7.85, 0.15, "MAT_concreto_arq", [
        {"axis": "X", "p0": 4.75, "p1": 7.70, "z_sill": 0.0, "z_head": 2.35, "kind": "sectional"},
    ]),
    ("P1_M_Este_Esquina", 7.85, 0.00, 8.00, 11.25, "MAT_estuco_blanco", [
        {"axis": "Y", "p0": 1.20, "p1": 3.40, "z_sill": 1.35, "z_head": 2.25, "kind": "window"},
        {"axis": "Y", "p0": 6.10, "p1": 7.70, "z_sill": 0.90, "z_head": 2.15, "kind": "window"},
        {"axis": "Y", "p0": 8.60, "p1": 10.40, "z_sill": 1.10, "z_head": 2.15, "kind": "window"},
    ]),
    ("P1_M_Norte", 0.15, 11.10, 7.85, 11.25, "MAT_estuco_blanco", [
        {"axis": "X", "p0": 1.30, "p1": 3.20, "z_sill": 0.70, "z_head": 2.15, "kind": "window"},
    ]),
    ("P1_M_Sep_Sala_Garaje", 4.50, 0.15, 4.60, 4.75, "MAT_wall_int", [
        {"axis": "Y", "p0": 3.70, "p1": 4.55, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P1_M_Bano_Norte", 0.15, 6.65, 2.05, 6.75, "MAT_wall_int", []),
    ("P1_M_Bano_Sur", 0.15, 4.65, 4.50, 4.75, "MAT_wall_int", [
        {"axis": "X", "p0": 2.15, "p1": 3.05, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P1_M_Bano_Este", 2.05, 4.75, 2.15, 6.65, "MAT_wall_int", [
        {"axis": "Y", "p0": 5.30, "p1": 6.10, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P1_M_Huesped_Norte_Cocina", 0.15, 8.05, 7.85, 8.15, "MAT_wall_int", [
        {"axis": "X", "p0": 2.15, "p1": 3.10, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        {"axis": "X", "p0": 6.20, "p1": 7.10, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P1_M_Huesped_Este", 4.50, 8.15, 4.60, 11.10, "MAT_wall_int", [
        {"axis": "Y", "p0": 8.60, "p1": 9.80, "z_sill": 0.75, "z_head": 2.10, "kind": "window"},
    ]),
]

P2_ROOMS = [
    ("P2_Habitacion_Principal", 0.15, 0.15, 4.50, 4.65, "MAT_porcelanato_ext"),
    ("P2_Balcon", 4.60, 0.15, 7.85, 1.65, "MAT_porcelanato_ext"),
    ("P2_Vestidor_Principal", 4.60, 1.75, 6.15, 4.65, "MAT_porcelanato_ext"),
    ("P2_Bano_Principal", 6.25, 1.75, 7.85, 4.65, "MAT_porcelanato_ext"),
    ("P2_Bano_Compartido", 0.15, 4.75, 2.05, 6.65, "MAT_porcelanato_ext"),
    ("P2_Distribuidor_Oeste", 2.15, 4.75, 3.10, 6.65, "MAT_porcelanato_ext"),
    ("P2_Llegada_Escalera", 6.85, 4.75, 7.85, 5.70, "MAT_porcelanato_ext"),
    ("P2_Distribuidor_Norte", 3.10, 5.70, 7.85, 6.65, "MAT_porcelanato_ext"),
    ("P2_Habitacion_Hija_1", 0.15, 6.75, 3.95, 9.85, "MAT_porcelanato_ext"),
    ("P2_Habitacion_Hija_2", 4.05, 6.75, 7.85, 9.85, "MAT_porcelanato_ext"),
]

P2_WALLS = [
    ("P2_M_Oeste", 0.00, 0.00, 0.15, 10.00, "MAT_estuco_blanco", []),
    ("P2_M_Este", 7.85, 0.00, 8.00, 10.00, "MAT_estuco_blanco", [
        {"axis": "Y", "p0": 2.40, "p1": 3.60, "z_sill": 1.10, "z_head": 2.10, "kind": "window"},
        {"axis": "Y", "p0": 7.30, "p1": 9.00, "z_sill": 0.70, "z_head": 2.10, "kind": "window"},
    ]),
    ("P2_M_Sur", 0.15, 0.00, 7.85, 0.15, "MAT_estuco_blanco", [
        {"axis": "X", "p0": 0.90, "p1": 3.80, "z_sill": 0.40, "z_head": 2.15, "kind": "window"},
        {"axis": "X", "p0": 4.70, "p1": 7.75, "z_sill": 0.10, "z_head": 1.05, "kind": "window"},
    ]),
    ("P2_M_Norte", 0.15, 9.85, 7.85, 10.00, "MAT_estuco_blanco", [
        {"axis": "X", "p0": 1.20, "p1": 2.80, "z_sill": 0.70, "z_head": 2.10, "kind": "window"},
        {"axis": "X", "p0": 5.20, "p1": 6.80, "z_sill": 0.70, "z_head": 2.10, "kind": "window"},
    ]),
    ("P2_M_Master_Este", 4.50, 0.15, 4.60, 4.65, "MAT_wall_int", [
        {"axis": "Y", "p0": 0.40, "p1": 1.50, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        {"axis": "Y", "p0": 2.60, "p1": 3.50, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P2_M_Balcon_Norte", 4.60, 1.65, 7.85, 1.75, "MAT_wall_int", []),
    ("P2_M_Vest_Bano", 6.15, 1.75, 6.25, 4.65, "MAT_wall_int", [
        {"axis": "Y", "p0": 2.70, "p1": 3.50, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P2_M_Banda_Sur", 0.15, 4.65, 7.85, 4.75, "MAT_wall_int", [
        {"axis": "X", "p0": 2.15, "p1": 3.05, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P2_M_Bano_Comp_Este", 2.05, 4.75, 2.15, 6.65, "MAT_wall_int", [
        {"axis": "Y", "p0": 5.60, "p1": 6.40, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P2_M_Banda_Norte", 0.15, 6.65, 7.85, 6.75, "MAT_wall_int", [
        {"axis": "X", "p0": 2.95, "p1": 3.85, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
        {"axis": "X", "p0": 4.15, "p1": 5.05, "z_sill": 0.0, "z_head": 2.10, "kind": "door"},
    ]),
    ("P2_M_Entre_Hijas", 3.95, 6.75, 4.05, 9.85, "MAT_wall_int", []),
]

P2_SLAB_SEGMENTS = [
    (0.015, 0.015, 7.985, 4.75),
    (0.015, 4.75, 3.10, 5.70),
    (6.85, 4.75, 7.985, 5.70),
    (0.015, 5.70, 7.985, 9.985),
]

COLUMNS = [
    (0.135, 0.135), (4.55, 0.135), (7.865, 0.135),
    (0.135, 4.70), (4.55, 4.70), (7.865, 4.70),
    (0.135, 8.10), (4.55, 8.10), (7.865, 8.10),
    (0.135, 9.865), (7.865, 9.865),
]

BEAMS = [
    (0.015, 0.015, 7.985, 0.255),
    (0.015, 4.58, 7.985, 4.82),
    (0.015, 7.98, 7.985, 8.22),
    (0.015, 9.745, 7.985, 9.985),
    (0.015, 0.255, 0.255, 9.745),
    (4.43, 0.255, 4.67, 8.00),
    (7.745, 0.255, 7.985, 9.745),
]

def build_architectural_envelopes(cols, mats):
    c_fach = cols["14_Fachadas_Y_Vegetacion"]

    create_box("Fach_Piedra_Pilar_Izq", -0.02, -0.02, 0.0, 0.42, 0.22, Z_P2, mats["MAT_piedra_natural"], c_fach)
    create_box("Fach_Piedra_Pilar_Centro", 4.38, -0.02, 0.0, 4.62, 0.22, Z_P2, mats["MAT_piedra_natural"], c_fach)
    create_box("Fach_Piedra_Esquina_P1", 7.72, -0.02, 0.0, 8.02, 0.42, Z_P2, mats["MAT_piedra_natural"], c_fach)
    create_box("Fach_Murete_Peatonal", 0.42, 0.0, 0.0, 4.38, 0.10, 0.95, mats["MAT_estuco_blanco"], c_fach)
    create_box("Fach_Remate_Murete", 0.42, -0.01, 0.95, 4.38, 0.11, 1.01, mats["MAT_aluminio_negro"], c_fach)

    create_box("Fach_Marco_P2_Sur", -0.02, -0.18, Z_P2 - 0.04, 4.58, 0.02, Z_P2 + 0.14, mats["MAT_concreto_arq"], c_fach)
    create_box("Fach_Marco_P2_Top", -0.02, -0.18, Z_ROOF - 0.04, 8.02, 0.02, Z_ROOF + SLAB_T + 0.55, mats["MAT_concreto_arq"], c_fach)
    create_box("Fach_Marco_P2_Lat", 7.98, -0.18, Z_P2 - 0.04, 8.16, 10.02, Z_P2 + 0.14, mats["MAT_concreto_arq"], c_fach)
    create_box("Fach_Alero_Ventanal_P2", 0.70, -0.45, Z_P2 + 2.15, 4.00, 0.0, Z_P2 + 2.26, mats["MAT_aluminio_negro"], c_fach)
    create_box("Fach_Alero_Lat_P1", 8.00, 5.90, Z_P1 + 2.15, 8.40, 7.90, Z_P1 + 2.24, mats["MAT_aluminio_negro"], c_fach)
    create_box("Fach_Alero_Lat_P2", 8.00, 7.10, Z_P2 + 2.10, 8.40, 9.20, Z_P2 + 2.19, mats["MAT_aluminio_negro"], c_fach)

    for i in range(9):
        y_cel = 1.85 + i * 0.18
        create_box(f"Celosia_Lat_P2_{i+1:02d}", 7.98, y_cel, Z_P2 + 0.15, 8.08, y_cel + 0.05, Z_P2 + 2.45, mats["MAT_madera_ext"], c_fach)
    for i in range(7):
        y_cel = 3.60 + i * 0.18
        create_box(f"Celosia_Lat_P1_{i+1:02d}", 7.98, y_cel, Z_P1 + 0.15, 8.08, y_cel + 0.05, Z_P1 + 2.55, mats["MAT_madera_ext"], c_fach)

    create_box("Balcon_Pasamanos_Sur", 4.65, 0.02, Z_P2 + 1.02, 7.82, 0.08, Z_P2 + 1.07, mats["MAT_aluminio_negro"], c_fach)
    create_box("Balcon_Poste_1", 4.65, 0.02, Z_P2, 4.71, 0.08, Z_P2 + 1.02, mats["MAT_aluminio_negro"], c_fach)
    create_box("Balcon_Poste_2", 6.20, 0.02, Z_P2, 6.26, 0.08, Z_P2 + 1.02, mats["MAT_aluminio_negro"], c_fach)
    create_box("Balcon_Poste_3", 7.76, 0.02, Z_P2, 7.82, 0.08, Z_P2 + 1.02, mats["MAT_aluminio_negro"], c_fach)

    create_box("Cubierta_Pendiente_Drenaje", 0.15, 0.15, Z_ROOF + SLAB_T, 7.85, 9.85, Z_ROOF + SLAB_T + 0.08, mats["MAT_concreto_arq"], c_fach)
    create_box("Bajante_Pluvial_Esquina", 7.88, 9.75, 0.0, 7.98, 9.85, Z_ROOF + SLAB_T, mats["MAT_aluminio_negro"], c_fach)
    create_box("Zona_Paneles_Solares_Base", 1.20, 2.20, Z_ROOF + SLAB_T + 0.08, 6.60, 6.00, Z_ROOF + SLAB_T + 0.14, mats["MAT_aluminio_negro"], c_fach)
    for r in range(2):
        for c in range(3):
            px0 = 1.35 + c * 1.72
            py0 = 2.35 + r * 1.75
            create_box(f"Panel_Solar_Res_{r}_{c}", px0, py0, Z_ROOF + SLAB_T + 0.14, px0 + 1.55, py0 + 1.50, Z_ROOF + SLAB_T + 0.20, mats["MAT_solar_panel"], c_fach)

    create_tropical_plant("Vegetacion_Frente_Izq", 0.55, 0.55, 0.04, 1.55, mats, c_fach)
    create_tropical_plant("Vegetacion_Frente_Der", 4.10, 0.55, 0.04, 1.35, mats, c_fach)
    create_tropical_plant("Vegetacion_Patio_Trasero", 7.35, 10.65, 0.04, 1.85, mats, c_fach)
    create_tropical_plant("Vegetacion_Balcon", 7.35, 1.25, Z_P2 + 0.04, 1.15, mats, c_fach)

def setup_day_lighting(col_lgt):
    for o in list(col_lgt.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    sun = add_light("Sun_Caribe_Dia", "SUN", (12.0, -10.0, 18.0), 4.2, (1.0, 0.96, 0.88), 0.05, col_lgt)
    sun.rotation_euler = (0.72, 0.25, -0.65)
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.58, 0.74, 0.92, 1.0)
        bg.inputs["Strength"].default_value = 1.15

def setup_night_lighting(col_lgt, mats):
    for o in list(col_lgt.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.025, 0.035, 0.075, 1.0)
        bg.inputs["Strength"].default_value = 0.45

    add_light("Luz_Arq_Porche", "AREA", (1.80, 0.80, 2.55), 140.0, (1.0, 0.80, 0.52), 0.8, col_lgt)
    add_light("Luz_Arq_Garaje", "AREA", (6.20, -0.25, 2.55), 110.0, (1.0, 0.82, 0.56), 0.6, col_lgt)
    add_light("Luz_Arq_Balcon", "AREA", (6.20, 0.80, Z_P2 + 2.45), 130.0, (1.0, 0.80, 0.52), 0.7, col_lgt)
    add_light("Luz_Arq_Master", "POINT", (2.30, 2.20, Z_P2 + 2.25), 180.0, (1.0, 0.84, 0.58), 0.4, col_lgt)
    add_light("Luz_Arq_Sala", "POINT", (2.30, 3.00, 2.35), 150.0, (1.0, 0.84, 0.58), 0.4, col_lgt)
    add_light("Luz_Arq_Esquina_1", "POINT", (8.25, 2.50, 2.30), 90.0, (1.0, 0.78, 0.48), 0.3, col_lgt)
    add_light("Luz_Arq_Esquina_2", "POINT", (8.25, 7.50, 2.30), 90.0, (1.0, 0.78, 0.48), 0.3, col_lgt)

def configure_cycles_optix(samples, res_x, res_y):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = (d.type == "OPTIX")
    scene.cycles.device = "GPU"
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPTIX"
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"

def main():
    clear_scene()
    cols = init_collections()
    mats = build_procedural_pbr_materials()
    build_context(cols, mats)

    c_p1 = cols["07_Propuesta_Primera_Planta"]
    c_p2 = cols["08_Propuesta_Segunda_Planta"]
    c_str = cols["09_Estructura_Conceptual"]
    c_veh = cols["10_Vehiculos"]
    c_mob = cols["11_Mobiliario"]
    c_cam = cols["12_Camaras"]
    c_lgt = cols["15_Iluminacion"]

    for rname, x0, y0, x1, y1, mkey in P1_ROOMS:
        create_box(f"P1_Piso_{rname}", x0, y0, Z_P1, x1, y1, Z_P1 + 0.04, mats[mkey], c_p1)

    for wname, x0, y0, x1, y1, mkey, ops in P1_WALLS:
        create_wall_with_openings(wname, x0, y0, x1, y1, Z_P1, CLEAR_H, mats[mkey], ops, mats, c_p1)

    steps = 16
    run = (6.85 - 3.10) / (steps - 1)
    rise = (Z_P2 - Z_P1) / steps
    for i in range(steps - 1):
        create_box(f"P1_Esc_Peldano_{i+1:02d}", 3.10 + i * run, 4.75, Z_P1 + i * rise, 3.10 + (i + 1) * run, 5.70, Z_P1 + (i + 1) * rise, mats["MAT_stair"], c_p1)

    create_box("P1_Veh_Swift_Dzire_2023", 4.75, 0.35, Z_P1 + 0.04, 6.485, 4.345, Z_P1 + 1.555, mats["MAT_vehicle_car"], c_veh)
    create_box("P1_Veh_VStrom_250_SX", 6.85, 1.60, Z_P1 + 0.04, 7.73, 3.78, Z_P1 + 1.395, mats["MAT_vehicle_moto"], c_veh)

    for idx, (cx, cy) in enumerate(COLUMNS):
        create_box(f"Col_P1_{idx+1:02d}", cx - 0.115, cy - 0.115, Z_P1, cx + 0.115, cy + 0.115, Z_P2, mats["MAT_concreto_arq"], c_str)
        create_box(f"Col_P2_{idx+1:02d}", cx - 0.115, cy - 0.115, Z_P2, cx + 0.115, cy + 0.115, Z_ROOF, mats["MAT_concreto_arq"], c_str)

    for idx, b in enumerate(BEAMS):
        create_box(f"Viga_P1_{idx+1:02d}", b[0], b[1], Z_P2 - SLAB_T - 0.24, b[2], b[3], Z_P2 - SLAB_T, mats["MAT_concreto_arq"], c_str)
        create_box(f"Viga_P2_{idx+1:02d}", b[0], b[1], Z_ROOF - 0.24, b[2], b[3], Z_ROOF, mats["MAT_concreto_arq"], c_str)

    for idx, seg in enumerate(P2_SLAB_SEGMENTS):
        create_box(f"P2_Losa_Seg_{idx+1}", seg[0], seg[1], Z_P2 - SLAB_T, seg[2], seg[3], Z_P2, mats["MAT_slab"], c_str)

    create_box("Cubierta_Plana_Superior", 0.00, 0.00, Z_ROOF, 8.00, 10.00, Z_ROOF + SLAB_T, mats["MAT_concreto_arq"], c_p2)
    create_box("Pretil_Sur", 0.00, 0.00, Z_ROOF + SLAB_T, 8.00, 0.15, Z_ROOF + SLAB_T + 0.55, mats["MAT_estuco_blanco"], c_p2)
    create_box("Pretil_Este", 7.85, 0.15, Z_ROOF + SLAB_T, 8.00, 10.00, Z_ROOF + SLAB_T + 0.55, mats["MAT_estuco_blanco"], c_p2)
    create_box("Pretil_Norte", 0.00, 9.85, Z_ROOF + SLAB_T, 7.85, 10.00, Z_ROOF + SLAB_T + 0.55, mats["MAT_estuco_blanco"], c_p2)
    create_box("Pretil_Oeste", 0.00, 0.15, Z_ROOF + SLAB_T, 0.15, 9.85, Z_ROOF + SLAB_T + 0.55, mats["MAT_estuco_blanco"], c_p2)

    for rname, x0, y0, x1, y1, mkey in P2_ROOMS:
        create_box(f"P2_Piso_{rname}", x0, y0, Z_P2, x1, y1, Z_P2 + 0.04, mats[mkey], c_p2)

    for wname, x0, y0, x1, y1, mkey, ops in P2_WALLS:
        create_wall_with_openings(wname, x0, y0, x1, y1, Z_P2, CLEAR_H, mats[mkey], ops, mats, c_p2)

    build_architectural_envelopes(cols, mats)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    world = bpy.data.worlds.new("World_Hito3")
    scene.world = world

    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.name = "Cam_Render_Ext"
    for c in list(cam.users_collection):
        c.objects.unlink(cam)
    c_cam.objects.link(cam)
    scene.camera = cam

    def aim(loc, tgt, lens=28.0):
        cam.data.type = "PERSP"
        cam.data.lens = lens
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - cam.location).to_track_quat("-Z", "Y").to_euler()

    configure_cycles_optix(samples=24, res_x=1280, res_y=720)
    setup_day_lighting(c_lgt)
    aim((14.5, -10.5, 3.2), (4.0, 4.5, 2.8), 28.0)
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_03_TEST_720P.png")
    bpy.ops.render.render(write_still=True)

    configure_cycles_optix(samples=64, res_x=2560, res_y=1440)
    setup_day_lighting(c_lgt)

    aim((4.0, -13.5, 2.6), (4.0, 2.0, 3.0), 35.0)
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_03_FRONTAL_DIA.png")
    bpy.ops.render.render(write_still=True)

    aim((21.5, 5.5, 2.8), (6.0, 5.5, 3.0), 35.0)
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_03_LATERAL_DIA.png")
    bpy.ops.render.render(write_still=True)

    aim((15.0, -10.0, 3.2), (4.2, 4.2, 2.9), 28.0)
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_03_ESQUINA_DIA.png")
    bpy.ops.render.render(write_still=True)

    aim((17.5, -12.5, 13.5), (4.0, 5.0, 2.5), 32.0)
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_03_AEREA.png")
    bpy.ops.render.render(write_still=True)

    setup_night_lighting(c_lgt, mats)

    aim((4.0, -13.5, 2.6), (4.0, 2.0, 3.0), 35.0)
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_03_FRONTAL_NOCHE.png")
    bpy.ops.render.render(write_still=True)

    aim((15.0, -10.0, 3.2), (4.2, 4.2, 2.9), 28.0)
    scene.render.filepath = os.path.join(PROJECT_DIR, "renders", "HITO_03_ESQUINA_NOCHE.png")
    bpy.ops.render.render(write_still=True)

    setup_day_lighting(c_lgt)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print("HITO_03_BUILD_COMPLETE")

main()
