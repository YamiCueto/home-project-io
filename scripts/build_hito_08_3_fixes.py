import bpy
import bmesh
import math
from pathlib import Path
from mathutils import Vector


def remove_obj(name):
    obj = bpy.data.objects.get(name)
    if obj:
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data and data.users == 0:
            bpy.data.meshes.remove(data)


def get_mat(name, fallback_rgba=(0.8, 0.8, 0.8, 1.0)):
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


def render_view(out_path, loc, target, lens=28.0, samples=24):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    cam_data = bpy.data.cameras.new("_TMP_FIX_CAM")
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new("_TMP_FIX_CAM", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = Vector(loc)
    direction = Vector(target) - Vector(loc)
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    prev_cam = scene.camera
    scene.camera = cam_obj
    scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    scene.camera = prev_cam
    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.cameras.remove(cam_data)


def apply_fixes():
    c_p1 = bpy.data.collections.get("07_Propuesta_Primera_Planta") or bpy.context.scene.collection
    c_mob = bpy.data.collections.get("11_Mobiliario") or bpy.context.scene.collection
    c_est = bpy.data.collections.get("09_Estructura_Conceptual") or bpy.context.scene.collection
    m_stucco = get_mat("MAT_stucco_blanco")
    m_madera = get_mat("MAT_madera_nogal")
    m_roble = get_mat("MAT_madera_roble")
    m_hormigon = get_mat("MAT_hormigon")

    for n in ["P1_M_Sep_Sala_Garaje_S0", "P1_M_Sep_Sala_Garaje_Lint1", "P1_M_Sep_Sala_Garaje_Puerta1", "P1_Mob_Estante_Garaje"]:
        remove_obj(n)
    make_box("P1_M_Sep_Sala_Garaje_S0", 4.50, 4.60, 0.15, 3.60, 0.00, 2.70, m_stucco, c_p1)
    make_box("P1_M_Sep_Sala_Garaje_Lint1", 4.50, 4.60, 3.60, 4.55, 2.10, 2.70, m_stucco, c_p1)
    p_gar = create_hinged_panel("P1_M_Sep_Sala_Garaje_Puerta1", 4.55, 3.60, 0.04, 0.05, 0.95, 2.06, "Y", m_madera, c_p1)
    p_gar["swing_dir"] = -1
    make_box("P1_Mob_Estante_Garaje", 4.90, 6.50, 4.30, 4.64, 1.65, 2.20, m_roble, c_mob)

    for obj in list(bpy.data.objects):
        if obj.name == "P1_Mob_Mesa_Comedor_Sobre" or obj.name.startswith("P1_Mob_Mesa_Pata_"):
            remove_obj(obj.name)
    m_negro = get_mat("MAT_aluminio_negro", (0.09, 0.09, 0.10, 1.0))
    make_box("P1_Mob_Mesa_Comedor_Sobre", 3.45, 4.95, 6.20, 6.86, 0.74, 0.79, m_madera, c_mob)
    for px, py in [(3.50, 6.25), (3.50, 6.81), (4.90, 6.25), (4.90, 6.81)]:
        make_box(f"P1_Mob_Mesa_Pata_{px:.2f}_{py:.2f}", px - 0.03, px + 0.03, py - 0.03, py + 0.03, 0.04, 0.74, m_negro, c_mob)

    chair_layout = {
        "P1_PH_Chair_1_dining_chair_02": ((3.85, 5.98, 0.04), 0.0),
        "P1_PH_Chair_2_dining_chair_02": ((4.55, 5.98, 0.04), 0.0),
        "P1_PH_Chair_3_dining_chair_02": ((3.85, 7.03, 0.04), 180.0),
        "P1_PH_Chair_4_dining_chair_02": ((4.55, 7.03, 0.04), 180.0),
    }
    for cname, (loc, rot_z) in chair_layout.items():
        obj = bpy.data.objects.get(cname)
        if obj:
            obj.location = Vector(loc)
            obj.rotation_euler = (0.0, 0.0, math.radians(rot_z))
    remove_obj("P1_PH_Chair_5_dining_chair_02")

    remove_obj("Col_P2_08")
    make_box("Col_P2_08", 3.90, 4.10, 7.985, 8.215, 2.90, 5.60, m_stucco, c_est)

    remove_obj("Viga_P2_06")
    make_box("Viga_P2_06", 4.43, 4.67, 0.255, 4.75, 5.36, 5.60, m_hormigon, c_est)

    remove_obj("Viga_P2_03")
    make_box("Viga_P2_03", 0.015, 7.985, 7.98, 8.22, 5.45, 5.60, m_hormigon, c_est)


def main():
    root = Path(r"C:\Users\YAMI\Documents\projects\home-project")
    src = root / "models" / "HOME_PROJECT_HITO_08_3.blend"
    dst = root / "models" / "HOME_PROJECT_HITO_08_3_FIXES.blend"
    rdir = root / "renders" / "hito_08_3_fixes"
    rdir.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.open_mainfile(filepath=str(src))

    render_view(rdir / "BEFORE_Hall_Garaje.png", (3.20, 4.05, 1.55), (5.20, 4.05, 1.40))
    render_view(rdir / "BEFORE_Comedor.png", (5.80, 7.65, 1.60), (3.85, 6.50, 0.70))
    render_view(rdir / "BEFORE_Hija_2.png", (6.50, 7.20, 1.65 + 2.90), (4.45, 8.20, 1.40 + 2.90))

    apply_fixes()
    bpy.ops.wm.save_as_mainfile(filepath=str(dst))

    p_gar = bpy.data.objects.get("P1_M_Sep_Sala_Garaje_Puerta1")
    if p_gar:
        p_gar.rotation_euler.z = math.radians(-85.0)
    render_view(rdir / "AFTER_Hall_Garaje.png", (3.20, 4.05, 1.55), (5.60, 3.80, 1.30))
    if p_gar:
        p_gar.rotation_euler.z = 0.0
    render_view(rdir / "AFTER_Comedor.png", (5.80, 7.65, 1.60), (3.85, 6.85, 0.70))
    render_view(rdir / "AFTER_Hija_2.png", (6.50, 7.20, 1.65 + 2.90), (4.45, 8.20, 1.40 + 2.90))

    print(f"HITO_08_3_FIXES_SAVED: {dst}")


if __name__ == "__main__":
    main()
