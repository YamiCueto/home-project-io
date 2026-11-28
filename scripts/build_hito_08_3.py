import bpy
import bmesh
import math
from pathlib import Path
from mathutils import Vector, Matrix


def remove_obj(name):
    obj = bpy.data.objects.get(name)
    if obj:
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data and data.users == 0:
            bpy.data.meshes.remove(data)


def get_mat(name, fallback_rgba=(0.7, 0.7, 0.7, 1.0), metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = fallback_rgba
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def link_obj(name, mesh, col):
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    return obj


def make_box(name, x0, x1, y0, y1, z0, z1, mat, col):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = [
        bm.verts.new((x0, y0, z0)),
        bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)),
        bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)),
        bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)),
        bm.verts.new((x0, y1, z1)),
    ]
    faces = [
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ]
    for f in faces:
        bm.faces.new([verts[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = link_obj(name, mesh, col)
    obj.data.materials.append(mat)
    return obj


def make_prism_profile(name, profile_yz, x_half, cx, cy, cz, mat, col, bevel_width=0.02):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    n = len(profile_yz)
    left = [bm.verts.new((cx - x_half, cy + y, cz + z)) for (y, z) in profile_yz]
    right = [bm.verts.new((cx + x_half, cy + y, cz + z)) for (y, z) in profile_yz]
    bm.faces.new(list(reversed(left)))
    bm.faces.new(right)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([left[i], left[j], right[j], right[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel_width > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel_width, segments=2, affect="EDGES")
    bm.to_mesh(mesh)
    bm.free()
    obj = link_obj(name, mesh, col)
    obj.data.materials.append(mat)
    return obj


def make_wheel(name, center, radius, width, mat_tire, mat_rim, col):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    segs = 24
    half_w = width * 0.5
    ring_l = []
    ring_r = []
    for i in range(segs):
        a = 2.0 * math.pi * i / segs
        y = center[1] + radius * math.cos(a)
        z = center[2] + radius * math.sin(a)
        ring_l.append(bm.verts.new((center[0] - half_w, y, z)))
        ring_r.append(bm.verts.new((center[0] + half_w, y, z)))
    f_l = bm.faces.new(list(reversed(ring_l)))
    f_r = bm.faces.new(ring_r)
    for i in range(segs):
        j = (i + 1) % segs
        bm.faces.new([ring_l[i], ring_l[j], ring_r[j], ring_r[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.bevel(bm, geom=list(f_l.edges) + list(f_r.edges), offset=min(0.03, width * 0.18), segments=2, affect="EDGES")
    bm.to_mesh(mesh)
    bm.free()
    obj = link_obj(name, mesh, col)
    obj.data.materials.append(mat_tire)

    rim_mesh = bpy.data.meshes.new(name + "_Rim")
    bm_r = bmesh.new()
    r_rim = radius * 0.58
    rim_w = width * 0.54
    rl, rr = [], []
    for i in range(16):
        a = 2.0 * math.pi * i / 16
        y = center[1] + r_rim * math.cos(a)
        z = center[2] + r_rim * math.sin(a)
        rl.append(bm_r.verts.new((center[0] - rim_w, y, z)))
        rr.append(bm_r.verts.new((center[0] + rim_w, y, z)))
    bm_r.faces.new(list(reversed(rl)))
    bm_r.faces.new(rr)
    for i in range(16):
        j = (i + 1) % 16
        bm_r.faces.new([rl[i], rl[j], rr[j], rr[i]])
    bmesh.ops.recalc_face_normals(bm_r, faces=bm_r.faces)
    bm_r.to_mesh(rim_mesh)
    bm_r.free()
    rim_obj = link_obj(name + "_Rim", rim_mesh, col)
    rim_obj.data.materials.append(mat_rim)
    return obj


def create_hinged_panel(name, px, py, pz, lx, ly, lz, axis, mat, col):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    if axis == "X":
        x0, x1 = 0.0, lx
        y0, y1 = -ly * 0.5, ly * 0.5
    else:
        x0, x1 = -lx * 0.5, lx * 0.5
        y0, y1 = 0.0, ly
    verts = [
        bm.verts.new((x0, y0, 0.0)),
        bm.verts.new((x1, y0, 0.0)),
        bm.verts.new((x1, y1, 0.0)),
        bm.verts.new((x0, y1, 0.0)),
        bm.verts.new((x0, y0, lz)),
        bm.verts.new((x1, y0, lz)),
        bm.verts.new((x1, y1, lz)),
        bm.verts.new((x0, y1, lz)),
    ]
    for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
        bm.faces.new([verts[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = link_obj(name, mesh, col)
    obj.location = (px, py, pz)
    obj.data.materials.append(mat)
    return obj


def build_vehicles():
    for o in list(bpy.data.objects):
        if o.name.startswith("Veh_"):
            remove_obj(o.name)

    col_veh = bpy.data.collections.get("10_Vehiculos") or bpy.data.collections.get("11_Mobiliario") or bpy.context.scene.collection
    m_car = get_mat("MAT_vehicle_car", (0.22, 0.28, 0.36, 1.0), metallic=0.65, roughness=0.25)
    m_moto = get_mat("MAT_vehicle_moto", (0.58, 0.10, 0.10, 1.0), metallic=0.55, roughness=0.28)
    m_glass = get_mat("MAT_vidrio_arq", (0.12, 0.18, 0.24, 1.0), metallic=0.1, roughness=0.08)
    m_tire = get_mat("MAT_antracita", (0.08, 0.08, 0.09, 1.0), metallic=0.05, roughness=0.78)
    m_rim = get_mat("MAT_aluminio", (0.76, 0.78, 0.80, 1.0), metallic=0.85, roughness=0.22)
    m_black = get_mat("MAT_aluminio_negro", (0.09, 0.09, 0.10, 1.0), metallic=0.4, roughness=0.45)

    cx_car, cy_car, cz_car = 5.88, 2.25, 0.04
    car_profile = [
        (-1.85, 0.22),
        (-1.82, 0.62),
        (-1.25, 0.76),
        (-0.78, 1.38),
        (0.85, 1.40),
        (1.68, 0.88),
        (1.85, 0.68),
        (1.85, 0.24),
    ]
    make_prism_profile("Veh_Swift_Carroceria", car_profile, 0.86, cx_car, cy_car, cz_car, m_car, col_veh, bevel_width=0.035)

    cabin_glass_profile = [
        (-1.20, 0.82),
        (-0.76, 1.34),
        (0.80, 1.35),
        (1.48, 0.90),
        (1.40, 0.82),
    ]
    make_prism_profile("Veh_Swift_Cabina_Vidrios", cabin_glass_profile, 0.78, cx_car, cy_car, cz_car, m_glass, col_veh, bevel_width=0.015)

    make_box("Veh_Swift_Parrilla", cx_car - 0.56, cx_car + 0.56, cy_car - 1.88, cy_car - 1.82, 0.28, 0.52, m_tire, col_veh)
    make_box("Veh_Swift_Faro_L", cx_car - 0.78, cx_car - 0.48, cy_car - 1.87, cy_car - 1.78, 0.54, 0.66, m_rim, col_veh)
    make_box("Veh_Swift_Faro_R", cx_car + 0.48, cx_car + 0.78, cy_car - 1.87, cy_car - 1.78, 0.54, 0.66, m_rim, col_veh)
    make_box("Veh_Swift_Piloto_Tras", cx_car - 0.76, cx_car + 0.76, cy_car + 1.82, cy_car + 1.87, 0.66, 0.78, m_moto, col_veh)
    make_box("Veh_Swift_Espejo_L", cx_car - 0.96, cx_car - 0.84, cy_car - 0.88, cy_car - 0.72, 0.86, 0.96, m_black, col_veh)
    make_box("Veh_Swift_Espejo_R", cx_car + 0.84, cx_car + 0.96, cy_car - 0.88, cy_car - 0.72, 0.86, 0.96, m_black, col_veh)

    for wname, wx, wy in [
        ("Veh_Swift_Rueda_FL", cx_car - 0.80, cy_car - 1.18),
        ("Veh_Swift_Rueda_FR", cx_car + 0.80, cy_car - 1.18),
        ("Veh_Swift_Rueda_RL", cx_car - 0.80, cy_car + 1.22),
        ("Veh_Swift_Rueda_RR", cx_car + 0.80, cy_car + 1.22),
    ]:
        make_wheel(wname, (wx, wy, 0.34), 0.30, 0.21, m_tire, m_rim, col_veh)

    cx_m, cy_m, cz_m = 7.36, 2.75, 0.04
    moto_body_profile = [
        (-0.72, 0.62),
        (-0.48, 0.92),
        (-0.12, 1.02),
        (0.28, 0.78),
        (0.68, 0.92),
        (0.86, 0.86),
        (0.55, 0.58),
        (-0.55, 0.52),
    ]
    make_prism_profile("Veh_VStrom_Carroceria", moto_body_profile, 0.16, cx_m, cy_m, cz_m, m_moto, col_veh, bevel_width=0.025)
    make_box("Veh_VStrom_Motor", cx_m - 0.14, cx_m + 0.14, cy_m - 0.32, cy_m + 0.28, 0.26, 0.62, m_black, col_veh)
    make_box("Veh_VStrom_Asiento", cx_m - 0.14, cx_m + 0.14, cy_m + 0.05, cy_m + 0.65, 0.78, 0.89, m_tire, col_veh)
    make_box("Veh_VStrom_Cupula", cx_m - 0.13, cx_m + 0.13, cy_m - 0.58, cy_m - 0.42, 1.02, 1.32, m_glass, col_veh)
    make_box("Veh_VStrom_Manillar", cx_m - 0.40, cx_m + 0.40, cy_m - 0.45, cy_m - 0.35, 1.02, 1.08, m_black, col_veh)
    make_box("Veh_VStrom_Horquilla", cx_m - 0.11, cx_m + 0.11, cy_m - 0.68, cy_m - 0.50, 0.36, 1.02, m_rim, col_veh)
    make_box("Veh_VStrom_Escape", cx_m + 0.15, cx_m + 0.23, cy_m + 0.15, cy_m + 0.78, 0.36, 0.50, m_rim, col_veh)
    make_wheel("Veh_VStrom_Rueda_F", (cx_m, cy_m - 0.68, 0.36), 0.32, 0.12, m_tire, m_rim, col_veh)
    make_wheel("Veh_VStrom_Rueda_R", (cx_m, cy_m + 0.66, 0.34), 0.30, 0.15, m_tire, m_rim, col_veh)


def redesign_master_suite():
    c_p2 = bpy.data.collections.get("08_Propuesta_Segunda_Planta") or bpy.context.scene.collection
    c_mob = bpy.data.collections.get("11_Mobiliario") or bpy.context.scene.collection

    m_stucco = get_mat("MAT_stucco_blanco", (0.90, 0.90, 0.89, 1.0), 0.0, 0.65)
    m_madera = get_mat("MAT_madera_nogal", (0.36, 0.24, 0.15, 1.0), 0.0, 0.45)
    m_porc = get_mat("MAT_porcelanato", (0.85, 0.84, 0.82, 1.0), 0.0, 0.25)
    m_vidrio = get_mat("MAT_vidrio_arq", (0.72, 0.82, 0.88, 1.0), 0.05, 0.08)
    m_aluminio = get_mat("MAT_aluminio", (0.76, 0.78, 0.80, 1.0), 0.85, 0.22)
    m_roble = get_mat("MAT_madera_roble", (0.58, 0.42, 0.26, 1.0), 0.0, 0.48)
    m_ceramica = get_mat("MAT_ceramica_blanca", (0.94, 0.94, 0.94, 1.0), 0.0, 0.18)

    for n in [
        "P2_M_Banda_Sur_S0", "P2_M_Banda_Sur_S2", "P2_M_Banda_Sur_Lint1", "P2_M_Banda_Sur_Puerta1",
        "P2_M_Master_Este_S0", "P2_M_Master_Este_S2", "P2_M_Master_Este_S4",
        "P2_M_Master_Este_Lint1", "P2_M_Master_Este_Lint3",
        "P2_M_Master_Este_Puerta1", "P2_M_Master_Este_Puerta3",
        "P2_M_Vest_Bano_S0", "P2_M_Vest_Bano_S2", "P2_M_Vest_Bano_Lint1", "P2_M_Vest_Bano_Puerta1",
        "P2_Piso_P2_Vestidor_Principal", "P2_Piso_P2_Bano_Principal",
    ]:
        remove_obj(n)

    make_box("P2_M_Banda_Sur_S0", 0.15, 2.15, 4.65, 4.75, 2.90, 5.60, m_stucco, c_p2)
    make_box("P2_M_Banda_Sur_Lint1", 2.15, 3.05, 4.65, 4.75, 5.00, 5.60, m_stucco, c_p2)
    make_box("P2_M_Banda_Sur_S2", 3.05, 7.85, 4.65, 4.75, 2.90, 5.60, m_stucco, c_p2)
    p_entry = create_hinged_panel("P2_M_Banda_Sur_Puerta1", 2.15, 4.70, 2.94, 0.90, 0.05, 2.06, "X", m_madera, c_p2)
    p_entry["swing_dir"] = -1

    make_box("P2_M_Master_Este_S0", 4.50, 4.60, 0.15, 0.40, 2.90, 5.60, m_stucco, c_p2)
    make_box("P2_M_Master_Este_Lint1", 4.50, 4.60, 0.40, 1.50, 5.00, 5.60, m_stucco, c_p2)
    make_box("P2_M_Master_Este_S2", 4.50, 4.60, 1.50, 2.55, 2.90, 5.60, m_stucco, c_p2)
    make_box("P2_M_Master_Este_Lint3", 4.50, 4.60, 2.55, 3.55, 5.00, 5.60, m_stucco, c_p2)
    make_box("P2_M_Master_Este_S4", 4.50, 4.60, 3.55, 4.65, 2.90, 5.60, m_stucco, c_p2)
    create_hinged_panel("P2_M_Master_Este_Puerta1", 4.55, 0.40, 2.94, 0.05, 1.10, 2.06, "Y", m_vidrio, c_p2)
    create_hinged_panel("P2_M_Master_Este_Puerta3", 4.55, 2.55, 2.94, 0.05, 1.00, 2.06, "Y", m_madera, c_p2)

    make_box("P2_M_Vest_Bano_S0", 5.95, 6.05, 1.75, 2.60, 2.90, 5.60, m_stucco, c_p2)
    make_box("P2_M_Vest_Bano_Lint1", 5.95, 6.05, 2.60, 3.50, 5.00, 5.60, m_stucco, c_p2)
    make_box("P2_M_Vest_Bano_S2", 5.95, 6.05, 3.50, 4.65, 2.90, 5.60, m_stucco, c_p2)
    create_hinged_panel("P2_M_Vest_Bano_Puerta1", 6.00, 2.60, 2.94, 0.05, 0.90, 2.06, "Y", m_madera, c_p2)

    make_box("P2_Piso_P2_Vestidor_Principal", 4.60, 5.95, 1.75, 4.65, 2.90, 2.94, m_porc, c_p2)
    make_box("P2_Piso_P2_Bano_Principal", 6.05, 7.85, 1.75, 4.65, 2.90, 2.94, m_porc, c_p2)

    pivot_bed = Vector((2.15, 2.60, 0.0))
    rot_bed = Matrix.Rotation(math.radians(90.0), 4, "Z")
    target_center = Vector((1.20, 2.35, 0.0))
    for obj in bpy.data.objects:
        if obj.name.startswith(("P2_Mob_Cama_Master", "P2_Mob_LED_Cabecero", "P2_PH_Nightstand_")):
            rel = obj.location - pivot_bed
            rel_rot = rot_bed @ rel
            obj.location = Vector((target_center.x + rel_rot.x, target_center.y + rel_rot.y, obj.location.z))
            obj.rotation_euler.z += math.radians(90.0)
        elif obj.name == "P2_Mob_Tapete_Master":
            obj.location.x -= 0.25
            obj.location.y += 0.30

    for n in [
        "P2_Mob_Closet_Vestidor", "P2_Mob_Closet_Vestidor_Sur",
        "P2_Mob_Ducha_Master", "P2_Mob_Mampara_Master",
        "P2_Mob_Inodoro_Master", "P2_Mob_Lavabo_Master", "P2_Mob_Espejo_Master",
    ]:
        remove_obj(n)

    make_box("P2_Mob_Closet_Vestidor", 4.65, 5.92, 4.08, 4.62, 2.94, 5.25, m_roble, c_mob)
    make_box("P2_Mob_Closet_Vestidor_Sur", 4.65, 5.92, 1.78, 2.32, 2.94, 5.25, m_roble, c_mob)

    make_box("P2_Mob_Ducha_Master", 6.85, 7.82, 1.78, 2.75, 2.94, 2.97, m_ceramica, c_mob)
    make_box("P2_Mob_Mampara_Master", 6.83, 6.87, 1.78, 2.75, 2.97, 4.95, m_vidrio, c_mob)
    make_box("P2_Mob_Inodoro_Master", 7.18, 7.82, 2.95, 3.45, 2.94, 3.36, m_ceramica, c_mob)
    make_box("P2_Mob_Lavabo_Master", 7.22, 7.82, 3.65, 4.60, 2.94, 3.76, m_roble, c_mob)
    make_box("P2_Mob_Espejo_Master", 7.79, 7.84, 3.70, 4.55, 3.92, 4.92, m_aluminio, c_mob)


def main():
    root = Path(r"C:\Users\YAMI\Documents\projects\home-project")
    src = root / "models" / "HOME_PROJECT_HITO_06_V3.blend"
    dst = root / "models" / "HOME_PROJECT_HITO_08_3.blend"

    bpy.ops.wm.open_mainfile(filepath=str(src))
    build_vehicles()
    redesign_master_suite()
    bpy.ops.wm.save_as_mainfile(filepath=str(dst))
    print(f"HITO_08_3_MODEL_SAVED: {dst}")


if __name__ == "__main__":
    main()
