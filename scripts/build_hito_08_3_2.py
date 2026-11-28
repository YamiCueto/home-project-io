import bpy
import bmesh
from pathlib import Path
from mathutils import Vector


def remove_obj(name):
    obj = bpy.data.objects.get(name)
    if obj:
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data and data.users == 0:
            bpy.data.meshes.remove(data)


def get_mat(name, fallback_rgba=(0.85, 0.85, 0.84, 1.0)):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = fallback_rgba
    return mat


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
    for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
        bm.faces.new([verts[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat)
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
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = (px, py, pz)
    obj.data.materials.append(mat)
    return obj


def fix_p1_bano_social():
    c_p1 = bpy.data.collections.get("07_Propuesta_Primera_Planta") or bpy.context.scene.collection
    c_mob = bpy.data.collections.get("11_Mobiliario") or bpy.context.scene.collection
    m_stucco = get_mat("MAT_stucco_blanco")
    m_porc = get_mat("MAT_porcelanato")
    m_cer = get_mat("MAT_ceramica_blanca")
    m_roble = get_mat("MAT_madera_roble")
    m_alum = get_mat("MAT_aluminio")

    for n in [
        "P1_M_Bano_Norte_S0", "P1_M_Bano_Este_S2", "P1_Piso_P1_Bano_Social",
        "P1_Mob_Ducha_Social_Piso", "P1_Mob_Inodoro_Social", "P1_Mob_Lavabo_Social", "P1_Mob_Barra_Apoyo_1",
    ]:
        remove_obj(n)

    make_box("P1_M_Bano_Este_S2", 2.05, 2.15, 6.10, 8.05, 0.00, 2.70, m_stucco, c_p1)
    make_box("P1_Piso_P1_Bano_Social", 0.15, 2.05, 4.75, 8.05, 0.00, 0.04, m_porc, c_p1)

    make_box("P1_Mob_Ducha_Social_Piso", 0.20, 1.35, 6.85, 8.00, 0.04, 0.055, m_cer, c_mob)
    make_box("P1_Mob_Barra_Apoyo_1", 0.18, 0.24, 7.00, 7.70, 0.85, 0.90, m_alum, c_mob)
    make_box("P1_Mob_Inodoro_Social", 0.20, 0.72, 5.65, 6.35, 0.04, 0.46, m_cer, c_mob)
    make_box("P1_Mob_Lavabo_Social", 0.20, 0.75, 4.85, 5.45, 0.04, 0.85, m_roble, c_mob)


def fix_p2_suite_principal():
    c_p2 = bpy.data.collections.get("08_Propuesta_Segunda_Planta") or bpy.context.scene.collection
    c_mob = bpy.data.collections.get("11_Mobiliario") or bpy.context.scene.collection
    c_fach = bpy.data.collections.get("14_Fachadas_Y_Vegetacion") or bpy.context.scene.collection

    m_stucco = get_mat("MAT_stucco_blanco")
    m_porc = get_mat("MAT_porcelanato")
    m_madera = get_mat("MAT_madera_nogal")
    m_roble = get_mat("MAT_madera_roble")
    m_cer = get_mat("MAT_ceramica_blanca")
    m_vidrio = get_mat("MAT_vidrio_arq")
    m_alum = get_mat("MAT_aluminio")
    m_marco = get_mat("MAT_antracita")

    for n in [
        "Balcon_Pasamanos_Sur", "Balcon_Poste_1", "Balcon_Poste_2", "Balcon_Poste_3",
        "P2_M_Balcon_Norte_S0", "P2_Piso_P2_Balcon",
        "P2_M_Master_Este_S0", "P2_M_Master_Este_Lint1", "P2_M_Master_Este_Puerta1",
        "P2_M_Master_Este_S2", "P2_M_Master_Este_Lint3", "P2_M_Master_Este_Puerta3", "P2_M_Master_Este_S4",
        "P2_M_Vest_Bano_S0", "P2_M_Vest_Bano_Lint1", "P2_M_Vest_Bano_Puerta1", "P2_M_Vest_Bano_S2",
        "P2_Piso_P2_Vestidor_Principal", "P2_Piso_P2_Bano_Principal",
        "P2_M_Sur_S2", "P2_M_Sur_S4", "P2_M_Sur_Sill3", "P2_M_Sur_Lint3",
        "P2_M_Sur_Win3_FrameB", "P2_M_Sur_Win3_FrameL", "P2_M_Sur_Win3_FrameR", "P2_M_Sur_Win3_FrameT", "P2_M_Sur_Win3_Glass",
        "Fach_Marco_P2_Sur",
        "P2_Mob_Closet_Vestidor", "P2_Mob_Closet_Vestidor_Sur",
        "P2_Mob_Ducha_Master", "P2_Mob_Mampara_Master", "P2_Mob_Inodoro_Master", "P2_Mob_Lavabo_Master", "P2_Mob_Espejo_Master",
    ]:
        remove_obj(n)

    for obj in list(bpy.data.objects):
        if "Balcon" in obj.name:
            remove_obj(obj.name)

    make_box("P2_M_Master_Este_S0", 4.50, 4.60, 0.15, 2.55, 2.90, 5.60, m_stucco, c_p2)
    make_box("P2_M_Master_Este_Lint3", 4.50, 4.60, 2.55, 3.55, 5.00, 5.60, m_stucco, c_p2)
    make_box("P2_M_Master_Este_S4", 4.50, 4.60, 3.55, 4.65, 2.90, 5.60, m_stucco, c_p2)
    create_hinged_panel("P2_M_Master_Este_Puerta3", 4.55, 2.55, 2.94, 0.05, 1.00, 2.06, "Y", m_madera, c_p2)

    make_box("P2_M_Vest_Bano_S0", 6.05, 6.15, 0.15, 2.55, 2.90, 5.60, m_stucco, c_p2)
    make_box("P2_M_Vest_Bano_Lint1", 6.05, 6.15, 2.55, 3.45, 5.00, 5.60, m_stucco, c_p2)
    make_box("P2_M_Vest_Bano_S2", 6.05, 6.15, 3.45, 4.65, 2.90, 5.60, m_stucco, c_p2)
    create_hinged_panel("P2_M_Vest_Bano_Puerta1", 6.10, 2.55, 2.94, 0.05, 0.90, 2.06, "Y", m_madera, c_p2)

    make_box("P2_Piso_P2_Vestidor_Principal", 4.60, 6.05, 0.15, 4.65, 2.90, 2.94, m_porc, c_p2)
    make_box("P2_Piso_P2_Bano_Principal", 6.15, 7.85, 0.15, 4.65, 2.90, 2.94, m_porc, c_p2)

    make_box("P2_M_Sur_S2", 3.80, 6.35, 0.00, 0.15, 2.90, 5.60, m_stucco, c_p2)
    make_box("P2_M_Sur_Sill3", 6.35, 7.65, 0.00, 0.15, 2.90, 4.00, m_stucco, c_p2)
    make_box("P2_M_Sur_Lint3", 6.35, 7.65, 0.00, 0.15, 5.00, 5.60, m_stucco, c_p2)
    make_box("P2_M_Sur_S4", 7.65, 7.85, 0.00, 0.15, 2.90, 5.60, m_stucco, c_p2)
    make_box("P2_M_Sur_Win3_FrameB", 6.35, 7.65, 0.00, 0.15, 4.00, 4.045, m_marco, c_p2)
    make_box("P2_M_Sur_Win3_FrameL", 6.35, 6.395, 0.00, 0.15, 4.045, 4.955, m_marco, c_p2)
    make_box("P2_M_Sur_Win3_FrameR", 7.605, 7.65, 0.00, 0.15, 4.045, 4.955, m_marco, c_p2)
    make_box("P2_M_Sur_Win3_FrameT", 6.35, 7.65, 0.00, 0.15, 4.955, 5.00, m_marco, c_p2)
    make_box("P2_M_Sur_Win3_Glass", 6.395, 7.605, 0.06, 0.09, 4.045, 4.955, m_vidrio, c_p2)
    make_box("Fach_Marco_P2_Sur", -0.02, 8.16, -0.18, 0.02, 2.86, 3.04, m_marco, c_fach)

    make_box("P2_Mob_Closet_Vestidor", 4.65, 6.00, 4.05, 4.63, 2.94, 5.25, m_roble, c_mob)
    make_box("P2_Mob_Closet_Vestidor_Sur", 4.65, 6.00, 0.18, 0.78, 2.94, 5.25, m_roble, c_mob)

    make_box("P2_Mob_Ducha_Master", 6.20, 7.80, 0.20, 1.35, 2.94, 2.96, m_cer, c_mob)
    make_box("P2_Mob_Mampara_Master", 6.20, 7.80, 1.35, 1.39, 2.96, 4.95, m_vidrio, c_mob)
    make_box("P2_Mob_Inodoro_Master", 7.15, 7.82, 1.65, 2.25, 2.94, 3.36, m_cer, c_mob)
    make_box("P2_Mob_Lavabo_Master", 7.20, 7.82, 3.55, 4.60, 2.94, 3.76, m_roble, c_mob)
    make_box("P2_Mob_Espejo_Master", 7.79, 7.84, 3.60, 4.55, 3.92, 4.92, m_alum, c_mob)


def organize_semantic_collections():
    names = [
        "Arquitectura", "Estructura", "Puertas_Y_Ventanas",
        "Mobiliario", "Vehiculos", "Equipamiento",
        "Decoracion", "Instalaciones", "Contexto_Urbano",
    ]
    cols = {}
    for n in names:
        c = bpy.data.collections.get(n)
        if not c:
            c = bpy.data.collections.new(n)
            bpy.context.scene.collection.children.link(c)
        cols[n] = c

    hidden_cols = {"Mobiliario", "Vehiculos", "Equipamiento", "Decoracion", "Instalaciones"}
    for n, c in cols.items():
        hide = n in hidden_cols
        c.hide_viewport = hide
        c.hide_render = hide

    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        nm = o.name
        if nm.startswith("Veh_"):
            target = cols["Vehiculos"]
        elif nm.startswith("Inst_") or "Inst_AC" in nm or "Solar" in nm or "Aplique" in nm:
            target = cols["Instalaciones"]
        elif nm.startswith("PH_Plant") or "Tapete" in nm or "Cortina" in nm or "Espejo" in nm or "LED_" in nm:
            target = cols["Decoracion"]
        elif any(k in nm for k in ("Inodoro", "Lavabo", "Ducha", "Mampara", "Grifo", "Lavadora", "Lavadero", "Estufa", "Campana", "Nevecon", "TV_65", "Barra_Apoyo")):
            target = cols["Equipamiento"]
        elif "_Mob_" in nm or "_PH_" in nm:
            target = cols["Mobiliario"]
        elif "_Puerta" in nm or "_Porton" in nm or "_Win" in nm:
            target = cols["Puertas_Y_Ventanas"]
        elif nm.startswith(("Col_", "Viga_", "P2_Losa", "Losa_")):
            target = cols["Estructura"]
        elif any(c.name in ("05_Andenes_Publicos", "06_Calles", "17_Contexto_Urbano", "01_Linderos_Provisionales") for c in o.users_collection):
            target = cols["Contexto_Urbano"]
        else:
            target = cols["Arquitectura"]

        if o.name not in target.objects:
            target.objects.link(o)

        is_hidden = target.name in hidden_cols
        o.hide_viewport = is_hidden
        o.hide_render = is_hidden


def main():
    root = Path(r"C:\Users\YAMI\Documents\projects\home-project")
    src = root / "models" / "HOME_PROJECT_HITO_08_3_FIXES.blend"
    dst = root / "models" / "HOME_PROJECT_HITO_08_3_2.blend"

    bpy.ops.wm.open_mainfile(filepath=str(src))
    fix_p1_bano_social()
    fix_p2_suite_principal()
    organize_semantic_collections()
    bpy.ops.wm.save_as_mainfile(filepath=str(dst))
    print(f"HITO_08_3_2_SAVED: {dst}")


if __name__ == "__main__":
    main()
