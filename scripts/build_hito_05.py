import math
import os
import bpy
import bmesh
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
HITO4_BLEND = os.path.join(PROJECT_DIR, "models", "HOME_PROJECT_HITO_04.blend")
HITO5_BLEND = os.path.join(PROJECT_DIR, "models", "HOME_PROJECT_HITO_05.blend")

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

def add_bevel(obj, width=0.01, segments=2):
    if obj.type != "MESH":
        return
    for m in obj.modifiers:
        if m.type == "BEVEL":
            return
    bev = obj.modifiers.new(name="Bevel_H5", type="BEVEL")
    bev.width = width
    bev.segments = segments
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(30.0)

def create_box(name, x0, y0, z0, x1, y1, z1, mat, col, bevel_w=0.01):
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
    if bevel_w > 0.0:
        add_bevel(obj, bevel_w, 2)
    return obj

def create_soft_cushion(name, x0, y0, z0, x1, y1, z1, mat, col):
    obj = create_box(name, x0, y0, z0, x1, y1, z1, mat, col, bevel_w=0.025)
    if obj:
        sub = obj.modifiers.new(name="Subsurf_H5", type="SUBSURF")
        sub.levels = 1
        sub.render_levels = 2
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj

def create_cyl(name, cx, cy, cz, r, depth, rot_euler, mat, col):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=r, radius2=r, depth=depth)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj.location = (cx, cy, cz)
    obj.rotation_euler = rot_euler
    for p in obj.data.polygons:
        p.use_smooth = True
    ensure_uvs(obj)
    obj.data.materials.append(mat)
    return obj

def upgrade_materials():
    porc = bpy.data.materials.get("MAT_porcelanato_ext")
    if porc:
        nt = porc.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = 0.20
        bsdf.inputs["Coat Weight"].default_value = 0.25
        bsdf.inputs["Coat Roughness"].default_value = 0.12
        tc = nt.nodes.new("ShaderNodeTexCoord")
        brk = nt.nodes.new("ShaderNodeTexBrick")
        brk.inputs["Scale"].default_value = 1.1
        brk.inputs["Brick Width"].default_value = 0.90
        brk.inputs["Row Height"].default_value = 0.90
        brk.inputs["Mortar Size"].default_value = 0.005
        brk.inputs["Color1"].default_value = (0.84, 0.82, 0.78, 1.0)
        brk.inputs["Color2"].default_value = (0.81, 0.79, 0.75, 1.0)
        brk.inputs["Mortar"].default_value = (0.52, 0.50, 0.48, 1.0)
        bmp = nt.nodes.new("ShaderNodeBump")
        bmp.inputs["Strength"].default_value = 0.04
        nt.links.new(tc.outputs["Object"], brk.inputs["Vector"])
        nt.links.new(brk.outputs["Color"], bsdf.inputs["Base Color"])
        nt.links.new(brk.outputs["Fac"], bmp.inputs["Height"])
        nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    mad = bpy.data.materials.get("MAT_madera_ext")
    if mad:
        nt = mad.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = 0.36
        bsdf.inputs["Coat Weight"].default_value = 0.18
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1.5, 16.0, 16.0)
        ns = nt.nodes.new("ShaderNodeTexNoise")
        ns.inputs["Scale"].default_value = 4.5
        ns.inputs["Detail"].default_value = 8.0
        ns.inputs["Roughness"].default_value = 0.6
        rmp = nt.nodes.new("ShaderNodeValToRGB")
        rmp.color_ramp.elements[0].position = 0.25
        rmp.color_ramp.elements[0].color = (0.24, 0.13, 0.06, 1.0)
        rmp.color_ramp.elements[1].position = 0.78
        rmp.color_ramp.elements[1].color = (0.40, 0.23, 0.12, 1.0)
        bmp = nt.nodes.new("ShaderNodeBump")
        bmp.inputs["Strength"].default_value = 0.06
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], ns.inputs["Vector"])
        nt.links.new(ns.outputs["Fac"], rmp.inputs["Fac"])
        nt.links.new(rmp.outputs["Color"], bsdf.inputs["Base Color"])
        nt.links.new(ns.outputs["Fac"], bmp.inputs["Height"])
        nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    cz = bpy.data.materials.get("MAT_cuarzo_blanco")
    if cz:
        nt = cz.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = 0.12
        bsdf.inputs["Coat Weight"].default_value = 0.30
        tc = nt.nodes.new("ShaderNodeTexCoord")
        ns = nt.nodes.new("ShaderNodeTexNoise")
        ns.inputs["Scale"].default_value = 3.2
        ns.inputs["Detail"].default_value = 6.0
        rmp = nt.nodes.new("ShaderNodeValToRGB")
        rmp.color_ramp.elements[0].position = 0.45
        rmp.color_ramp.elements[0].color = (0.93, 0.93, 0.91, 1.0)
        rmp.color_ramp.elements[1].position = 0.72
        rmp.color_ramp.elements[1].color = (0.80, 0.79, 0.77, 1.0)
        nt.links.new(tc.outputs["Object"], ns.inputs["Vector"])
        nt.links.new(ns.outputs["Fac"], rmp.inputs["Fac"])
        nt.links.new(rmp.outputs["Color"], bsdf.inputs["Base Color"])
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    for tname, col_val in [("MAT_textil_neutro", (0.42, 0.40, 0.37, 1.0)), ("MAT_textil_claro", (0.88, 0.86, 0.82, 1.0))]:
        tm = bpy.data.materials.get(tname)
        if tm:
            bsdf = tm.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs["Base Color"].default_value = col_val
            bsdf.inputs["Roughness"].default_value = 0.90
            bsdf.inputs["Sheen Weight"].default_value = 0.65

def new_mat(name, rgba, rough=0.6, metal=0.0, emit_col=None, emit_str=0.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit_col is not None and emit_str > 0.0:
        bsdf.inputs["Emission Color"].default_value = emit_col
        bsdf.inputs["Emission Strength"].default_value = emit_str
    return mat

def build_detailed_chair(prefix, cx, cy, z_base, rot_z, mat_seat, mat_leg, col):
    for dx in (-0.18, 0.18):
        for dy in (-0.18, 0.18):
            lx = cx + dx * math.cos(rot_z) - dy * math.sin(rot_z)
            ly = cy + dx * math.sin(rot_z) + dy * math.cos(rot_z)
            create_cyl(f"{prefix}_Pata_{dx:.2f}_{dy:.2f}", lx, ly, z_base + 0.22, 0.015, 0.44, (0, 0, 0), mat_leg, col)
    seat = create_soft_cushion(f"{prefix}_Asiento", cx - 0.21, cy - 0.21, z_base + 0.44, cx + 0.21, cy + 0.21, z_base + 0.50, mat_seat, col)
    bx = cx - 0.19 * math.sin(rot_z)
    by = cy + 0.19 * math.cos(rot_z)
    if abs(math.cos(rot_z)) > 0.5:
        create_soft_cushion(f"{prefix}_Respaldo", cx - 0.20, by - 0.03, z_base + 0.50, cx + 0.20, by + 0.03, z_base + 0.88, mat_seat, col)
    else:
        bx2 = cx - 0.19 * math.cos(rot_z)
        create_soft_cushion(f"{prefix}_Respaldo", bx2 - 0.03, cy - 0.20, z_base + 0.50, bx2 + 0.03, cy + 0.20, z_base + 0.88, mat_seat, col)

def main():
    bpy.ops.wm.open_mainfile(filepath=HITO4_BLEND)
    upgrade_materials()

    c_mob = bpy.data.collections["11_Mobiliario"]
    m_mad = bpy.data.materials["MAT_madera_ext"]
    m_alu = bpy.data.materials["MAT_aluminio_negro"]
    m_txt = bpy.data.materials["MAT_textil_neutro"]
    m_txt_c = bpy.data.materials["MAT_textil_claro"]
    m_cz = bpy.data.materials["MAT_cuarzo_blanco"]
    m_acero = bpy.data.materials["MAT_acero_inox"]
    m_rug = new_mat("MAT_tapete_tejido", (0.76, 0.73, 0.68, 1.0), 0.95)
    m_art = new_mat("MAT_arte_mural", (0.22, 0.32, 0.38, 1.0), 0.45)
    m_led = new_mat("MAT_led_indirecto", (1.0, 0.80, 0.50, 1.0), 0.2, 0.0, (1.0, 0.78, 0.48, 1.0), 8.0)

    to_replace = [o for o in c_mob.objects if o.name.startswith(("P1_Mob_Silla_Com_", "P1_Mob_Mesa_Comedor", "P1_Mob_Sofa_", "P2_Mob_Cama_Master_"))]
    for o in to_replace:
        bpy.data.objects.remove(o, do_unlink=True)

    create_box("P1_Mob_Tapete_Sala", 1.20, 2.15, Z_P1 + 0.04, 2.75, 4.45, Z_P1 + 0.055, m_rug, c_mob, 0.005)
    create_box("P1_Mob_Sofa_Base", 0.26, 2.30, Z_P1 + 0.14, 1.15, 4.35, Z_P1 + 0.36, m_txt, c_mob, 0.02)
    for lx in (0.30, 1.10):
        for ly in (2.35, 4.30):
            create_cyl(f"P1_Mob_Sofa_Pata_{lx:.2f}_{ly:.2f}", lx, ly, Z_P1 + 0.09, 0.02, 0.10, (0, 0, 0), m_alu, c_mob)
    create_soft_cushion("P1_Mob_Sofa_Resp", 0.26, 2.32, Z_P1 + 0.36, 0.48, 4.33, Z_P1 + 0.78, m_txt, c_mob)
    create_soft_cushion("P1_Mob_Sofa_Coj1", 0.48, 2.38, Z_P1 + 0.36, 1.14, 3.30, Z_P1 + 0.49, m_txt_c, c_mob)
    create_soft_cushion("P1_Mob_Sofa_Coj2", 0.48, 3.34, Z_P1 + 0.36, 1.14, 4.27, Z_P1 + 0.49, m_txt_c, c_mob)
    create_box("P1_Mob_Cuadro_Sala_Marco", 0.16, 2.85, Z_P1 + 1.25, 0.19, 3.85, Z_P1 + 1.95, m_alu, c_mob, 0.005)
    create_box("P1_Mob_Cuadro_Sala_Lienzo", 0.19, 2.90, Z_P1 + 1.30, 0.20, 3.80, Z_P1 + 1.90, m_art, c_mob, 0.002)
    create_box("P1_Mob_LED_TV", 2.75, 1.76, Z_P1 + 0.68, 4.15, 1.78, Z_P1 + 1.45, m_led, c_mob, 0.002)
    create_cyl("P1_Mob_Florero_Centro", 1.80, 3.35, Z_P1 + 0.56, 0.08, 0.24, (0, 0, 0), m_cz, c_mob)

    create_box("P1_Mob_Mesa_Comedor_Sobre", 3.55, 6.35, Z_P1 + 0.74, 5.05, 7.25, Z_P1 + 0.79, m_mad, c_mob, 0.012)
    for lx in (3.63, 4.97):
        for ly in (6.43, 7.17):
            create_cyl(f"P1_Mob_Mesa_Pata_{lx:.2f}_{ly:.2f}", lx, ly, Z_P1 + 0.39, 0.03, 0.70, (0, 0, 0), m_alu, c_mob)
    for idx, (cx, cy, rz) in enumerate([(3.95, 6.08, math.pi), (4.65, 6.08, math.pi), (3.95, 7.52, 0.0), (4.65, 7.52, 0.0), (5.28, 6.80, math.pi * 0.5)]):
        build_detailed_chair(f"P1_Mob_Silla_Com_{idx+1}", cx, cy, Z_P1 + 0.04, rz, m_txt, m_alu, c_mob)

    create_box("P1_Mob_Grifo_Cocina", 7.55, 7.35, Z_P1 + 0.95, 7.62, 7.42, Z_P1 + 1.25, m_acero, c_mob, 0.005)
    create_box("P1_Mob_Fregadero", 7.25, 7.15, Z_P1 + 0.94, 7.72, 7.65, Z_P1 + 0.96, m_acero, c_mob, 0.005)

    create_box("P2_Mob_Tapete_Master", 0.90, 0.85, Z_P2 + 0.04, 3.70, 2.75, Z_P2 + 0.055, m_rug, c_mob, 0.005)
    create_box("P2_Mob_Cama_Master_Base", 1.30, 0.45, Z_P2 + 0.055, 3.30, 2.45, Z_P2 + 0.30, m_mad, c_mob, 0.015)
    create_soft_cushion("P2_Mob_Cama_Master_Colchon", 1.33, 0.48, Z_P2 + 0.30, 3.27, 2.42, Z_P2 + 0.56, m_txt_c, c_mob)
    create_soft_cushion("P2_Mob_Cama_Master_Edredon", 1.31, 0.95, Z_P2 + 0.32, 3.29, 2.44, Z_P2 + 0.59, m_txt, c_mob)
    create_soft_cushion("P2_Mob_Cama_Master_Cabecero", 1.22, 0.40, Z_P2 + 0.055, 3.38, 0.50, Z_P2 + 1.20, m_txt, c_mob)
    create_box("P2_Mob_LED_Cabecero", 1.24, 0.38, Z_P2 + 0.15, 3.36, 0.40, Z_P2 + 1.18, m_led, c_mob, 0.002)
    for idx, px in enumerate([1.45, 2.35]):
        create_soft_cushion(f"P2_Mob_Cama_Master_Alm_{idx+1}", px, 0.54, Z_P2 + 0.56, px + 0.80, 0.92, Z_P2 + 0.70, m_txt_c, c_mob)

    for obj in list(bpy.data.objects):
        if obj.type == "MESH":
            ensure_uvs(obj)
            if obj.name.startswith(("P1_Mob_", "P2_Mob_")):
                add_bevel(obj, 0.008, 2)

    scene = bpy.context.scene
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0

    bpy.ops.wm.save_as_mainfile(filepath=HITO5_BLEND)
    print("HITO_05_BUILD_COMPLETE")

main()
