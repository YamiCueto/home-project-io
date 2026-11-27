import math
import os
import bpy
import bmesh
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
HITO3_BLEND = os.path.join(PROJECT_DIR, "models", "HOME_PROJECT_HITO_03.blend")
HITO4_BLEND = os.path.join(PROJECT_DIR, "models", "HOME_PROJECT_HITO_04.blend")
RENDERS_DIR = os.path.join(PROJECT_DIR, "renders", "hito_04")

Z_P1 = 0.00
Z_P2 = 2.90
Z_ROOF = 5.60

def ensure_uvs(obj):
    if obj.type != "MESH" or not obj.data.polygons:
        return
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")
    uv_layer = obj.data.uv_layers.active.data
    verts = obj.data.vertices
    for poly in obj.data.polygons:
        n = poly.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for li in poly.loop_indices:
            v = verts[obj.data.loops[li].vertex_index].co
            if az >= ax and az >= ay:
                uv_layer[li].uv = (v.x, v.y)
            elif ax >= ay:
                uv_layer[li].uv = (v.y, v.z)
            else:
                uv_layer[li].uv = (v.x, v.z)

def get_or_create_mat(name, rgba, rough=0.6, metal=0.0, trans=0.0, emit_col=None, emit_str=0.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if trans > 0.0:
        bsdf.inputs["Transmission Weight"].default_value = trans
        bsdf.inputs["IOR"].default_value = 1.52
    if emit_col is not None and emit_str > 0.0:
        bsdf.inputs["Emission Color"].default_value = emit_col
        bsdf.inputs["Emission Strength"].default_value = emit_str
    mat.diffuse_color = rgba
    return mat

def get_col(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

def create_box(name, x0, y0, z0, x1, y1, z1, mat, col):
    sx, sy, sz = abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)
    if sx < 1e-4 or sy < 1e-4 or sz < 1e-4:
        return None
    cx, cy, cz = (x0 + x1) * 0.5, (y0 + y1) * 0.5, (z0 + z1) * 0.5
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = v.co.x * sx + cx
        v.co.y = v.co.y * sy + cy
        v.co.z = v.co.z * sz + cz
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    ensure_uvs(obj)
    obj.data.materials.append(mat)
    return obj

def create_cyl(name, cx, cy, cz, r, depth, rot_euler, mat, col):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=20, radius1=r, radius2=r, depth=depth)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj.location = (cx, cy, cz)
    obj.rotation_euler = rot_euler
    ensure_uvs(obj)
    obj.data.materials.append(mat)
    return obj

def build_sofa(prefix, x0, y0, x1, y1, z_base, mats, col):
    create_box(f"{prefix}_Base", x0, y0, z_base, x1, y1, z_base + 0.36, mats["textil"], col)
    create_box(f"{prefix}_Respaldo", x0, y0, z_base + 0.36, x0 + 0.22, y1, z_base + 0.78, mats["textil"], col)
    create_box(f"{prefix}_Brazo_1", x0, y0, z_base + 0.36, x1, y0 + 0.16, z_base + 0.60, mats["textil"], col)
    create_box(f"{prefix}_Brazo_2", x0, y1 - 0.16, z_base + 0.36, x1, y1, z_base + 0.60, mats["textil"], col)
    create_box(f"{prefix}_Cojin_1", x0 + 0.24, y0 + 0.18, z_base + 0.36, x1 - 0.04, (y0 + y1) * 0.5 - 0.02, z_base + 0.48, mats["textil_claro"], col)
    create_box(f"{prefix}_Cojin_2", x0 + 0.24, (y0 + y1) * 0.5 + 0.02, z_base + 0.36, x1 - 0.04, y1 - 0.18, z_base + 0.48, mats["textil_claro"], col)

def build_bed(prefix, x0, y0, x1, y1, z_base, head_side, mats, col):
    create_box(f"{prefix}_Base", x0, y0, z_base, x1, y1, z_base + 0.28, mats["madera"], col)
    create_box(f"{prefix}_Colchon", x0 + 0.03, y0 + 0.03, z_base + 0.28, x1 - 0.03, y1 - 0.03, z_base + 0.54, mats["textil_claro"], col)
    create_box(f"{prefix}_Edredon", x0 + 0.02, y0 + 0.02, z_base + 0.30, x1 - 0.02, y1 - 0.02, z_base + 0.56, mats["textil"], col)
    if head_side == "Y-":
        create_box(f"{prefix}_Cabecero", x0 - 0.05, y0, z_base, x1 + 0.05, y0 + 0.10, z_base + 1.15, mats["textil"], col)
        create_box(f"{prefix}_Almohada_1", x0 + 0.15, y0 + 0.14, z_base + 0.56, (x0 + x1) * 0.5 - 0.05, y0 + 0.50, z_base + 0.68, mats["textil_claro"], col)
        create_box(f"{prefix}_Almohada_2", (x0 + x1) * 0.5 + 0.05, y0 + 0.14, z_base + 0.56, x1 - 0.15, y0 + 0.50, z_base + 0.68, mats["textil_claro"], col)
    else:
        create_box(f"{prefix}_Cabecero", x0 - 0.05, y1 - 0.10, z_base, x1 + 0.05, y1, z_base + 1.15, mats["textil"], col)
        create_box(f"{prefix}_Almohada_1", x0 + 0.15, y1 - 0.50, z_base + 0.56, x1 - 0.15, y1 - 0.14, z_base + 0.68, mats["textil_claro"], col)

def build_swift_dzire(x0, y0, z_base, mats, col):
    create_box("Veh_Swift_Chasis", x0, y0, z_base + 0.18, x0 + 1.735, y0 + 3.995, z_base + 0.85, mats["car"], col)
    create_box("Veh_Swift_Cabina", x0 + 0.12, y0 + 1.05, z_base + 0.85, x0 + 1.615, y0 + 3.15, z_base + 1.515, mats["car"], col)
    create_box("Veh_Swift_Parabrisas", x0 + 0.16, y0 + 1.00, z_base + 0.88, x0 + 1.575, y0 + 3.10, z_base + 1.46, mats["vidrio"], col)
    for wx in (x0 + 0.12, x0 + 1.615):
        for wy in (y0 + 0.72, y0 + 3.25):
            create_cyl(f"Veh_Swift_Rueda_{wx:.1f}_{wy:.1f}", wx, wy, z_base + 0.28, 0.28, 0.19, (0.0, 1.5708, 0.0), mats["antracita"], col)

def build_vstrom(x0, y0, z_base, mats, col):
    create_box("Veh_VStrom_Cuerpo", x0 + 0.25, y0 + 0.35, z_base + 0.45, x0 + 0.63, y0 + 1.85, z_base + 1.12, mats["moto"], col)
    create_box("Veh_VStrom_Manillar", x0, y0 + 0.55, z_base + 1.08, x0 + 0.88, y0 + 0.68, z_base + 1.14, mats["aluminio"], col)
    create_box("Veh_VStrom_Cupula", x0 + 0.30, y0 + 0.38, z_base + 1.12, x0 + 0.58, y0 + 0.58, z_base + 1.355, mats["vidrio"], col)
    for wy in (y0 + 0.35, y0 + 1.82):
        create_cyl(f"Veh_VStrom_Rueda_{wy:.1f}", x0 + 0.44, wy, z_base + 0.32, 0.32, 0.13, (0.0, 1.5708, 0.0), mats["antracita"], col)

def main():
    bpy.ops.wm.open_mainfile(filepath=HITO3_BLEND)

    col_p2_03 = bpy.data.objects.get("Col_P2_03")
    if col_p2_03:
        col_p2_03.location.x -= 0.01
    col_p1_03 = bpy.data.objects.get("Col_P1_03")
    if col_p1_03:
        col_p1_03.location.x -= 0.01

    for o in list(bpy.data.collections["10_Vehiculos"].objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for o in list(bpy.data.collections["11_Mobiliario"].objects):
        bpy.data.objects.remove(o, do_unlink=True)

    c_mob = get_col("11_Mobiliario")
    c_veh = get_col("10_Vehiculos")
    c_inst = get_col("16_Instalaciones_Domotica")
    c_cam = get_col("12_Camaras")
    c_lgt = get_col("15_Iluminacion")

    mats = {
        "madera": bpy.data.materials.get("MAT_madera_ext") or get_or_create_mat("MAT_madera_ext", (0.38, 0.22, 0.11, 1.0), 0.45),
        "cuarzo": get_or_create_mat("MAT_cuarzo_blanco", (0.94, 0.94, 0.92, 1.0), 0.18),
        "textil": get_or_create_mat("MAT_textil_neutro", (0.45, 0.43, 0.40, 1.0), 0.88),
        "textil_claro": get_or_create_mat("MAT_textil_claro", (0.86, 0.84, 0.80, 1.0), 0.85),
        "acero": get_or_create_mat("MAT_acero_inox", (0.72, 0.74, 0.76, 1.0), 0.25, 0.92),
        "ceramica": get_or_create_mat("MAT_ceramica_sanitaria", (0.96, 0.96, 0.96, 1.0), 0.12),
        "aluminio": bpy.data.materials.get("MAT_aluminio_negro") or get_or_create_mat("MAT_aluminio_negro", (0.05, 0.05, 0.06, 1.0), 0.28, 0.88),
        "antracita": bpy.data.materials.get("MAT_antracita") or get_or_create_mat("MAT_antracita", (0.14, 0.15, 0.17, 1.0), 0.38, 0.45),
        "vidrio": bpy.data.materials.get("MAT_vidrio_arq") or get_or_create_mat("MAT_vidrio_arq", (0.86, 0.94, 0.97, 1.0), 0.03, 0.0, 0.92),
        "car": bpy.data.materials.get("MAT_vehicle_car") or get_or_create_mat("MAT_vehicle_car", (0.12, 0.30, 0.62, 1.0), 0.20, 0.65),
        "moto": bpy.data.materials.get("MAT_vehicle_moto") or get_or_create_mat("MAT_vehicle_moto", (0.78, 0.18, 0.12, 1.0), 0.25, 0.55),
        "luz": bpy.data.materials.get("MAT_luz_calida") or get_or_create_mat("MAT_luz_calida", (1.0, 0.84, 0.58, 1.0), 0.2, 0.0, 0.0, (1.0, 0.82, 0.55, 1.0), 6.0),
        "tv": get_or_create_mat("MAT_pantalla_tv", (0.04, 0.05, 0.06, 1.0), 0.08, 0.1),
        "blanco": get_or_create_mat("MAT_blanco_calido", (0.92, 0.90, 0.87, 1.0), 0.45),
        "antideslizante": get_or_create_mat("MAT_piso_antideslizante", (0.58, 0.57, 0.54, 1.0), 0.78),
        "domotica": get_or_create_mat("MAT_equipo_domotica", (0.15, 0.42, 0.32, 1.0), 0.35, 0.4),
        "solar": bpy.data.materials.get("MAT_solar_panel") or get_or_create_mat("MAT_solar_panel", (0.06, 0.10, 0.22, 1.0), 0.15, 0.35),
    }

    build_sofa("P1_Mob_Sofa", 0.25, 2.30, 1.15, 4.35, Z_P1 + 0.04, mats, c_mob)
    create_box("P1_Mob_Mesa_Centro", 1.50, 2.80, Z_P1 + 0.04, 2.10, 3.90, Z_P1 + 0.44, mats["madera"], c_mob)
    create_box("P1_Mob_Mueble_TV", 2.65, 1.78, Z_P1 + 0.04, 4.25, 2.18, Z_P1 + 0.52, mats["madera"], c_mob)
    create_box("P1_Mob_TV_65", 2.72, 1.82, Z_P1 + 0.65, 4.18, 1.88, Z_P1 + 1.48, mats["tv"], c_mob)
    create_box("P1_Mob_Cortina_Sala_1", 2.05, 1.76, Z_P1 + 0.05, 2.35, 1.84, Z_P1 + 2.40, mats["textil_claro"], c_mob)
    create_box("P1_Mob_Cortina_Sala_2", 3.85, 1.76, Z_P1 + 0.05, 4.15, 1.84, Z_P1 + 2.40, mats["textil_claro"], c_mob)
    create_box("P1_Inst_AC_Sala", 0.20, 2.80, Z_P1 + 2.25, 0.42, 3.70, Z_P1 + 2.55, mats["blanco"], c_inst)

    create_box("P1_Mob_Cocina_Bajo", 7.20, 5.85, Z_P1 + 0.04, 7.82, 8.00, Z_P1 + 0.90, mats["madera"], c_mob)
    create_box("P1_Mob_Cocina_Cuarzo", 7.18, 5.85, Z_P1 + 0.90, 7.82, 8.00, Z_P1 + 0.95, mats["cuarzo"], c_mob)
    create_box("P1_Mob_Cocina_Alto", 7.45, 5.85, Z_P1 + 1.65, 7.82, 8.00, Z_P1 + 2.40, mats["blanco"], c_mob)
    create_box("P1_Mob_Cocina_Estufa", 7.22, 6.45, Z_P1 + 0.95, 7.75, 7.05, Z_P1 + 0.98, mats["aluminio"], c_mob)
    create_box("P1_Mob_Cocina_Campana", 7.25, 6.45, Z_P1 + 1.60, 7.80, 7.05, Z_P1 + 2.40, mats["acero"], c_mob)
    create_box("P1_Mob_Cocina_Barra", 5.65, 5.95, Z_P1 + 0.04, 6.20, 7.25, Z_P1 + 0.92, mats["cuarzo"], c_mob)
    create_box("P1_Mob_Nevecon", 5.70, 7.35, Z_P1 + 0.04, 6.42, 8.00, Z_P1 + 1.82, mats["acero"], c_mob)

    create_box("P1_Mob_Mesa_Comedor", 3.55, 6.35, Z_P1 + 0.04, 5.05, 7.25, Z_P1 + 0.78, mats["madera"], c_mob)
    for idx, (sx, sy) in enumerate([(3.80, 5.95), (4.55, 5.95), (3.80, 7.35), (4.55, 7.35), (5.12, 6.60)]):
        create_box(f"P1_Mob_Silla_Com_{idx+1}", sx, sy, Z_P1 + 0.04, sx + 0.42, sy + 0.42, Z_P1 + 0.85, mats["textil"], c_mob)

    build_bed("P1_Mob_Cama_Huesped", 0.30, 9.05, 1.65, 10.95, Z_P1 + 0.04, "Y+", mats, c_mob)
    create_box("P1_Mob_Velador_H1", 1.75, 10.45, Z_P1 + 0.04, 2.20, 10.95, Z_P1 + 0.54, mats["madera"], c_mob)
    create_box("P1_Mob_Closet_Huesped", 3.85, 9.30, Z_P1 + 0.04, 4.45, 11.00, Z_P1 + 2.25, mats["madera"], c_mob)

    create_box("P1_Mob_Ducha_Social_Piso", 0.20, 5.70, Z_P1 + 0.04, 1.10, 6.60, Z_P1 + 0.06, mats["antideslizante"], c_mob)
    create_box("P1_Mob_Barra_Apoyo_1", 0.18, 5.85, Z_P1 + 0.85, 0.24, 6.45, Z_P1 + 0.90, mats["acero"], c_mob)
    create_box("P1_Mob_Inodoro_Social", 0.20, 4.85, Z_P1 + 0.04, 0.70, 5.50, Z_P1 + 0.46, mats["ceramica"], c_mob)
    create_box("P1_Mob_Lavabo_Social", 1.25, 6.10, Z_P1 + 0.04, 2.00, 6.60, Z_P1 + 0.85, mats["ceramica"], c_mob)

    build_swift_dzire(4.75, 0.35, Z_P1 + 0.04, mats, c_veh)
    build_vstrom(6.85, 1.60, Z_P1 + 0.04, mats, c_veh)
    create_box("P1_Mob_Estante_Garaje", 4.62, 3.60, Z_P1 + 1.65, 4.95, 4.55, Z_P1 + 2.20, mats["aluminio"], c_mob)

    create_box("P1_Mob_Lavadora", 4.75, 10.30, Z_P1 + 0.04, 5.45, 11.00, Z_P1 + 0.89, mats["blanco"], c_mob)
    create_box("P1_Mob_Lavadero", 5.55, 10.30, Z_P1 + 0.04, 6.35, 11.00, Z_P1 + 0.90, mats["ceramica"], c_mob)
    create_box("P1_Mob_Gabinete_Lav", 4.75, 10.45, Z_P1 + 1.55, 6.35, 11.00, Z_P1 + 2.25, mats["blanco"], c_mob)

    build_bed("P2_Mob_Cama_Master", 1.30, 0.45, 3.30, 2.45, Z_P2 + 0.04, "Y-", mats, c_mob)
    create_box("P2_Mob_Velador_M1", 0.75, 0.45, Z_P2 + 0.04, 1.22, 0.90, Z_P2 + 0.54, mats["madera"], c_mob)
    create_box("P2_Mob_Velador_M2", 3.38, 0.45, Z_P2 + 0.04, 3.85, 0.90, Z_P2 + 0.54, mats["madera"], c_mob)
    create_box("P2_Mob_TV_Master", 1.60, 4.55, Z_P2 + 1.00, 3.00, 4.62, Z_P2 + 1.80, mats["tv"], c_mob)
    create_box("P2_Inst_AC_Master", 0.20, 2.20, Z_P2 + 2.25, 0.42, 3.10, Z_P2 + 2.55, mats["blanco"], c_inst)
    create_box("P2_Mob_Closet_Vestidor", 5.55, 1.85, Z_P2 + 0.04, 6.10, 4.55, Z_P2 + 2.35, mats["madera"], c_mob)
    create_box("P2_Mob_Ducha_Master", 6.90, 1.80, Z_P2 + 0.04, 7.80, 2.70, Z_P2 + 0.06, mats["antideslizante"], c_mob)
    create_box("P2_Mob_Mampara_Master", 6.88, 1.80, Z_P2 + 0.06, 6.91, 2.70, Z_P2 + 2.05, mats["vidrio"], c_mob)
    create_box("P2_Mob_Inodoro_Master", 7.15, 2.90, Z_P2 + 0.04, 7.80, 3.45, Z_P2 + 0.46, mats["ceramica"], c_mob)
    create_box("P2_Mob_Lavabo_Master", 7.25, 3.70, Z_P2 + 0.04, 7.80, 4.55, Z_P2 + 0.85, mats["cuarzo"], c_mob)
    create_box("P2_Mob_Espejo_Master", 7.78, 3.75, Z_P2 + 1.05, 7.83, 4.50, Z_P2 + 1.95, mats["luz"], c_mob)

    create_box("P2_Mob_Ducha_Comp", 0.20, 4.80, Z_P2 + 0.04, 1.10, 5.70, Z_P2 + 0.06, mats["antideslizante"], c_mob)
    create_box("P2_Mob_Mampara_Comp", 1.10, 4.80, Z_P2 + 0.06, 1.13, 5.70, Z_P2 + 2.05, mats["vidrio"], c_mob)
    create_box("P2_Mob_Inodoro_Comp", 0.20, 5.85, Z_P2 + 0.04, 0.70, 6.50, Z_P2 + 0.46, mats["ceramica"], c_mob)
    create_box("P2_Mob_Lavabo_Comp", 1.25, 4.80, Z_P2 + 0.04, 1.95, 5.30, Z_P2 + 0.85, mats["cuarzo"], c_mob)

    build_bed("P2_Mob_Cama_Hija_1", 0.30, 7.80, 1.50, 9.75, Z_P2 + 0.04, "Y+", mats, c_mob)
    create_box("P2_Mob_Escritorio_H1", 0.30, 6.85, Z_P2 + 0.04, 1.55, 7.45, Z_P2 + 0.78, mats["madera"], c_mob)
    create_box("P2_Mob_Silla_H1", 0.70, 7.48, Z_P2 + 0.04, 1.15, 7.75, Z_P2 + 0.90, mats["textil"], c_mob)
    create_box("P2_Mob_Closet_H1", 2.30, 9.20, Z_P2 + 0.04, 3.90, 9.80, Z_P2 + 2.30, mats["madera"], c_mob)
    create_box("P2_Inst_AC_H1", 0.20, 8.20, Z_P2 + 2.25, 0.42, 9.10, Z_P2 + 2.55, mats["blanco"], c_inst)

    build_bed("P2_Mob_Cama_Hija_2", 6.50, 7.80, 7.70, 9.75, Z_P2 + 0.04, "Y+", mats, c_mob)
    create_box("P2_Mob_Escritorio_H2", 6.45, 6.85, Z_P2 + 0.04, 7.70, 7.45, Z_P2 + 0.78, mats["madera"], c_mob)
    create_box("P2_Mob_Silla_H2", 6.85, 7.48, Z_P2 + 0.04, 7.30, 7.75, Z_P2 + 0.90, mats["textil"], c_mob)
    create_box("P2_Mob_Closet_H2", 4.10, 9.20, Z_P2 + 0.04, 5.70, 9.80, Z_P2 + 2.30, mats["madera"], c_mob)
    create_box("P2_Inst_AC_H2", 7.58, 8.20, Z_P2 + 2.25, 7.80, 9.10, Z_P2 + 2.55, mats["blanco"], c_inst)

    create_box("Inst_Inversor_Hibrido", 4.64, 8.30, Z_P1 + 1.35, 4.86, 8.85, Z_P1 + 1.95, mats["domotica"], c_inst)
    create_box("Inst_Banco_Baterias", 4.64, 8.30, Z_P1 + 0.08, 4.92, 9.00, Z_P1 + 1.10, mats["antracita"], c_inst)
    create_box("Inst_Tablero_Electrico", 4.64, 9.10, Z_P1 + 1.35, 4.82, 9.55, Z_P1 + 1.90, mats["acero"], c_inst)
    create_box("Inst_WiFi_AP_P1", 2.50, 5.20, Z_P1 + 2.64, 2.70, 5.40, Z_P1 + 2.69, mats["blanco"], c_inst)
    create_box("Inst_WiFi_AP_P2", 4.50, 6.00, Z_P2 + 2.64, 4.70, 6.20, Z_P2 + 2.69, mats["blanco"], c_inst)
    create_box("Inst_Cerradura_Smart", 1.50, 1.66, Z_P1 + 1.00, 1.58, 1.74, Z_P1 + 1.22, mats["aluminio"], c_inst)
    create_box("Inst_Cam_Seguridad_Frente", 4.40, -0.05, Z_P1 + 2.45, 4.55, 0.05, Z_P1 + 2.58, mats["blanco"], c_inst)
    create_box("Inst_Cam_Seguridad_Esquina", 7.95, 0.05, Z_P1 + 2.45, 8.08, 0.20, Z_P1 + 2.58, mats["blanco"], c_inst)
    create_box("Inst_Zona_Ampliacion_Solar", 1.20, 6.25, Z_ROOF + 0.28, 6.60, 8.20, Z_ROOF + 0.34, mats["solar"], c_inst)

    for obj in list(bpy.data.objects):
        ensure_uvs(obj)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = (d.type == "OPTIX")
    scene.cycles.device = "GPU"
    scene.cycles.samples = 32
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPTIX"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"

    for idx, (lx, ly, lz, en) in enumerate([
        (2.3, 3.2, 2.5, 160), (4.4, 6.9, 2.5, 150), (6.7, 6.9, 2.5, 150),
        (2.3, 9.5, 2.5, 140), (1.1, 5.7, 2.5, 110), (6.2, 2.4, 2.5, 180),
        (6.2, 9.5, 2.5, 150), (2.3, 2.4, Z_P2 + 2.5, 180), (5.4, 3.2, Z_P2 + 2.5, 120),
        (7.0, 3.2, Z_P2 + 2.5, 120), (1.1, 5.7, Z_P2 + 2.5, 110), (2.0, 8.3, Z_P2 + 2.5, 160),
        (6.0, 8.3, Z_P2 + 2.5, 160), (4.8, 5.2, Z_P2 + 2.5, 140),
    ]):
        ld = bpy.data.lights.new(name=f"Lgt_Int_{idx+1:02d}", type="POINT")
        ld.energy = en
        ld.color = (1.0, 0.88, 0.72)
        ld.shadow_soft_size = 0.35
        lo = bpy.data.objects.new(name=f"Lgt_Int_{idx+1:02d}", object_data=ld)
        lo.location = (lx, ly, lz)
        c_lgt.objects.link(lo)

    cam = bpy.data.objects.get("Cam_Render_Ext")
    if not cam:
        cdata = bpy.data.cameras.new("Cam_Render_H4")
        cam = bpy.data.objects.new("Cam_Render_H4", cdata)
        c_cam.objects.link(cam)
    scene.camera = cam

    views = [
        ("01_SALA.png", (0.50, 4.30, Z_P1 + 1.50), (3.20, 2.20, Z_P1 + 1.00), 22.0),
        ("02_COMEDOR.png", (3.20, 6.00, Z_P1 + 1.55), (5.00, 7.20, Z_P1 + 0.80), 22.0),
        ("03_COCINA.png", (5.80, 6.10, Z_P1 + 1.55), (7.50, 7.20, Z_P1 + 1.00), 22.0),
        ("04_HAB_HUESPEDES.png", (4.10, 8.40, Z_P1 + 1.55), (1.10, 10.20, Z_P1 + 0.80), 22.0),
        ("05_BANO_SOCIAL.png", (1.90, 4.90, Z_P1 + 1.55), (0.50, 6.20, Z_P1 + 0.80), 20.0),
        ("06_GARAJE.png", (7.60, 4.45, Z_P1 + 1.65), (5.50, 1.50, Z_P1 + 0.80), 20.0),
        ("07_LAVANDERIA.png", (7.40, 8.40, Z_P1 + 1.55), (5.30, 10.50, Z_P1 + 1.00), 22.0),
        ("08_ESCALERA.png", (2.40, 5.22, Z_P1 + 1.60), (6.80, 5.22, Z_P2 + 0.60), 22.0),
        ("09_HAB_PRINCIPAL.png", (0.50, 4.20, Z_P2 + 1.55), (2.60, 1.20, Z_P2 + 0.90), 22.0),
        ("10_VESTIDOR.png", (4.80, 2.00, Z_P2 + 1.55), (5.85, 3.80, Z_P2 + 1.10), 20.0),
        ("11_BANO_PRINCIPAL.png", (6.45, 2.00, Z_P2 + 1.55), (7.50, 3.80, Z_P2 + 1.00), 20.0),
        ("12_HAB_HIJA_1.png", (3.60, 7.00, Z_P2 + 1.55), (1.00, 9.20, Z_P2 + 0.90), 22.0),
        ("13_HAB_HIJA_2.png", (4.40, 7.00, Z_P2 + 1.55), (7.00, 9.20, Z_P2 + 0.90), 22.0),
        ("14_BANO_COMPARTIDO.png", (1.90, 6.40, Z_P2 + 1.55), (0.50, 5.20, Z_P2 + 0.90), 20.0),
        ("15_BALCON.png", (4.80, 0.35, Z_P2 + 1.55), (7.40, 1.25, Z_P2 + 0.90), 22.0),
        ("16_CUBIERTA_FOTOVOLTAICA.png", (12.0, -4.0, Z_ROOF + 6.5), (4.0, 5.0, Z_ROOF + 0.4), 28.0),
    ]

    for fname, loc, tgt, lens in views:
        cam.data.type = "PERSP"
        cam.data.lens = lens
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = os.path.join(RENDERS_DIR, fname)
        bpy.ops.render.render(write_still=True)

    c_p2 = bpy.data.collections["08_Propuesta_Segunda_Planta"]
    c_str = bpy.data.collections["09_Estructura_Conceptual"]
    c_fach = bpy.data.collections["14_Fachadas_Y_Vegetacion"]

    c_p2.hide_render = True
    c_fach.hide_render = True
    c_inst.hide_render = True
    for o in c_str.objects:
        o.hide_render = o.name.startswith(("P2_Losa", "Viga_", "Col_P2"))
    for o in c_mob.objects:
        o.hide_render = o.name.startswith("P2_")
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 14.0
    cam.location = (16.0, -8.0, 14.0)
    cam.rotation_euler = (Vector((4.0, 5.5, 1.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(RENDERS_DIR, "17_P1_ISO_AMOBLADA.png")
    bpy.ops.render.render(write_still=True)

    c_p2.hide_render = False
    for o in c_p2.objects:
        o.hide_render = o.name.startswith(("Cubierta_", "Pretil_"))
    for o in c_str.objects:
        o.hide_render = o.name.startswith(("Viga_P2", "Col_P1"))
    for o in c_mob.objects:
        o.hide_render = not o.name.startswith("P2_")
    cam.location = (16.0, -8.0, 17.0)
    cam.rotation_euler = (Vector((4.0, 5.0, 3.8)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(RENDERS_DIR, "18_P2_ISO_AMOBLADA.png")
    bpy.ops.render.render(write_still=True)

    c_fach.hide_render = False
    c_inst.hide_render = False
    for o in c_p2.objects:
        o.hide_render = False
    for o in c_str.objects:
        o.hide_render = False
    for o in c_mob.objects:
        o.hide_render = False

    bpy.ops.wm.save_as_mainfile(filepath=HITO4_BLEND)
    print("HITO_04_BUILD_COMPLETE")

main()
