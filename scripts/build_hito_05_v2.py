import json
import math
import os
import time
import bpy
import bmesh
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
STAGING_BLEND = os.path.join(PROJECT_DIR, "models", "HOME_PROJECT_HITO_05_PH_STAGING.blend")
V2_BLEND = os.path.join(PROJECT_DIR, "models", "HOME_PROJECT_HITO_05_V2.blend")
OUT_DIR = os.path.join(PROJECT_DIR, "renders", "hito_05_v2")
BENCH_JSON = os.path.join(PROJECT_DIR, "validation", "HITO_05_V2_BENCHMARK.json")

Z_P1 = 0.00
Z_P2 = 2.90
Z_ROOF = 5.60

def get_col(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

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

def create_box(name, x0, y0, z0, x1, y1, z1, mat, col, rot_x=0.0):
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
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj.location = (cx, cy, cz)
    obj.rotation_euler = (rot_x, 0.0, 0.0)
    ensure_uvs(obj)
    obj.data.materials.append(mat)
    return obj

def place_ph_asset(src_names, new_prefix, loc, rot_z, target_col, scale=1.0):
    created = []
    for sname in src_names:
        src = bpy.data.objects.get(sname)
        if not src:
            continue
        dup = src.copy()
        dup.data = src.data.copy()
        dup.name = f"{new_prefix}_{sname}"
        dup.location = (loc[0] + src.location.x * scale, loc[1] + src.location.y * scale, loc[2] + src.location.z * scale)
        dup.rotation_euler = (src.rotation_euler.x, src.rotation_euler.y, rot_z)
        dup.scale = (scale, scale, scale)
        target_col.objects.link(dup)
        created.append(dup)
    return created

def new_mat(name, rgba, rough=0.6, metal=0.0, trans=0.0, emit_col=None, emit_str=0.0):
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
    return mat

def add_light(name, ltype, loc, energy, color, size, col):
    ld = bpy.data.lights.new(name=name, type=ltype)
    ld.energy = energy
    ld.color = color
    if ltype == "AREA":
        ld.size = size
    elif ltype == "POINT":
        ld.shadow_soft_size = size
    lo = bpy.data.objects.new(name=name, object_data=ld)
    lo.location = loc
    col.objects.link(lo)
    return lo

def build_urban_context(c_urb, c_and, c_cal):
    m_curb = new_mat("MAT_bordillo", (0.72, 0.71, 0.69, 1.0), 0.85)
    m_line = new_mat("MAT_senal_vial", (0.92, 0.88, 0.78, 1.0), 0.7)
    m_vecino = new_mat("MAT_vecino_neutro", (0.78, 0.76, 0.72, 1.0), 0.85)
    m_vecino_techo = new_mat("MAT_vecino_techo", (0.45, 0.46, 0.48, 1.0), 0.80)
    m_fol = bpy.data.materials.get("MAT_follaje_tropical") or new_mat("MAT_follaje_tropical", (0.12, 0.34, 0.11, 1.0), 0.55)
    m_tronco = bpy.data.materials.get("MAT_madera_ext") or new_mat("MAT_madera_ext", (0.35, 0.20, 0.10, 1.0), 0.7)

    create_box("Bordillo_Frontal", -3.0, -1.55, -0.05, 9.55, -1.45, 0.03, m_curb, c_urb)
    create_box("Bordillo_Lateral", 9.45, -1.45, -0.05, 9.55, 13.0, 0.03, m_curb, c_urb)

    for i in range(6):
        x0 = -2.0 + i * 3.0
        create_box(f"Senal_Linea_Frontal_{i+1}", x0, -4.8, -0.05, x0 + 1.4, -4.65, -0.045, m_line, c_urb)
    for i in range(5):
        y0 = -1.0 + i * 3.0
        create_box(f"Senal_Linea_Lateral_{i+1}", 12.6, y0, -0.05, 12.75, y0 + 1.4, -0.045, m_line, c_urb)

    create_box("Vecino_Oeste_Vol", -8.0, 0.5, 0.0, -0.15, 10.5, 5.4, m_vecino, c_urb)
    create_box("Vecino_Oeste_Techo", -8.1, 0.4, 5.4, -0.1, 10.6, 5.7, m_vecino_techo, c_urb)
    create_box("Vecino_Norte_Vol", 0.0, 11.4, 0.0, 7.8, 18.5, 3.2, m_vecino, c_urb)
    create_box("Vecino_Norte_Techo", -0.1, 11.3, 3.2, 7.9, 18.6, 3.5, m_vecino_techo, c_urb)

    for idx, (tx, ty) in enumerate([(-1.8, -1.1), (10.2, 11.0)]):
        create_box(f"Arbol_Urbano_Tronco_{idx+1}", tx - 0.12, ty - 0.12, 0.0, tx + 0.12, ty + 0.12, 2.4, m_tronco, c_urb)
        mesh = bpy.data.meshes.new(f"Arbol_Urbano_Copa_{idx+1}")
        obj = bpy.data.objects.new(f"Arbol_Urbano_Copa_{idx+1}", mesh)
        c_urb.objects.link(obj)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.25)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()
        obj.location = (tx, ty, 3.1)
        obj.scale = (1.1, 1.1, 0.85)
        for p in obj.data.polygons:
            p.use_smooth = True
        obj.data.materials.append(m_fol)

    for obj in list(c_and.objects) + list(c_cal.objects):
        ensure_uvs(obj)

def refine_solar_panels(c_fach):
    for o in list(c_fach.objects):
        if o.name.startswith("Panel_Solar_Res_"):
            bpy.data.objects.remove(o, do_unlink=True)
    m_alu = bpy.data.materials["MAT_aluminio_negro"]
    m_pv = new_mat("MAT_celdas_pv", (0.04, 0.08, 0.18, 1.0), 0.12, 0.25)
    m_glass = bpy.data.materials["MAT_vidrio_arq"]
    tilt = math.radians(10.0)
    for r in range(2):
        for c in range(3):
            px0 = 1.35 + c * 1.72
            py0 = 2.35 + r * 1.75
            create_box(f"Solar_Soporte_{r}_{c}_L", px0 + 0.15, py0 + 0.15, Z_ROOF + 0.28, px0 + 0.22, py0 + 1.35, Z_ROOF + 0.42, m_alu, c_fach)
            create_box(f"Solar_Soporte_{r}_{c}_R", px0 + 1.33, py0 + 0.15, Z_ROOF + 0.28, px0 + 1.40, py0 + 1.35, Z_ROOF + 0.42, m_alu, c_fach)
            create_box(f"Solar_Marco_{r}_{c}", px0, py0, Z_ROOF + 0.38, px0 + 1.55, py0 + 1.50, Z_ROOF + 0.43, m_alu, c_fach, rot_x=tilt)
            create_box(f"Solar_Celdas_{r}_{c}", px0 + 0.04, py0 + 0.04, Z_ROOF + 0.41, px0 + 1.51, py0 + 1.46, Z_ROOF + 0.435, m_pv, c_fach, rot_x=tilt)
            create_box(f"Solar_Vidrio_{r}_{c}", px0 + 0.04, py0 + 0.04, Z_ROOF + 0.435, px0 + 1.51, py0 + 1.46, Z_ROOF + 0.445, m_glass, c_fach, rot_x=tilt)
    create_box("Solar_Canalizacion", 6.55, 4.00, Z_ROOF + 0.28, 6.62, 9.75, Z_ROOF + 0.34, m_alu, c_fach)

def main():
    bpy.ops.wm.open_mainfile(filepath=STAGING_BLEND)

    c_mob = get_col("11_Mobiliario")
    c_fach = get_col("14_Fachadas_Y_Vegetacion")
    c_lgt = get_col("15_Iluminacion")
    c_urb = get_col("17_Contexto_Urbano")
    c_and = get_col("05_Andenes_Publicos")
    c_cal = get_col("06_Calles")

    for o in list(bpy.data.collections["01_Linderos_Provisionales"].objects):
        o.hide_render = True

    for o in list(c_fach.objects):
        if o.name.startswith("Vegetacion_"):
            bpy.data.objects.remove(o, do_unlink=True)

    for o in list(c_mob.objects):
        if o.name.startswith((
            "P1_Mob_Mesa_Centro", "P1_Mob_Florero_Centro", "P1_Mob_Mueble_TV", "P1_Mob_TV_65", "P1_Mob_LED_TV",
            "P1_Mob_Silla_Com_", "P2_Mob_Cama_Master", "P2_Mob_Velador_M", "P2_Mob_LED_Cabecero", "P2_Mob_Tapete_Master", "P2_Mob_TV_Master"
        )):
            bpy.data.objects.remove(o, do_unlink=True)

    m_mad = bpy.data.materials.get("dark_wood") or bpy.data.materials["MAT_madera_ext"]
    m_tv = bpy.data.materials["MAT_pantalla_tv"]
    m_led = bpy.data.materials["MAT_led_indirecto"]
    m_txt = bpy.data.materials["MAT_textil_neutro"]
    m_txt_c = bpy.data.materials["MAT_textil_claro"]
    m_rug = bpy.data.materials["MAT_tapete_tejido"]
    m_acero = bpy.data.materials["MAT_acero_inox"]

    create_box("P1_Mob_Mueble_TV", 4.08, 2.00, Z_P1 + 0.04, 4.48, 3.60, Z_P1 + 0.52, m_mad, c_mob)
    create_box("P1_Mob_TV_65", 4.38, 2.08, Z_P1 + 0.65, 4.44, 3.52, Z_P1 + 1.48, m_tv, c_mob)
    create_box("P1_Mob_LED_TV", 4.44, 2.12, Z_P1 + 0.68, 4.46, 3.48, Z_P1 + 1.45, m_led, c_mob)

    place_ph_asset(["modern_coffee_table_01"], "P1_PH_CoffeeTable", (1.95, 3.30, Z_P1 + 0.055), math.pi * 0.5, c_mob)

    for idx, (cx, cy, rz) in enumerate([(3.95, 6.02, 0.0), (4.65, 6.02, 0.0), (3.95, 7.58, math.pi), (4.65, 7.58, math.pi), (5.32, 6.80, -math.pi * 0.5)]):
        place_ph_asset(["dining_chair_02"], f"P1_PH_Chair_{idx+1}", (cx, cy, Z_P1 + 0.04), rz, c_mob)

    for idx, (cx, cy) in enumerate([(0.70, 0.55), (4.10, 0.55), (7.35, 10.65)]):
        place_ph_asset(["potted_plant_01_leaves", "potted_plant_01_pebbles", "potted_plant_01_pot", "potted_plant_01_stem"], f"PH_Plant1_{idx+1}", (cx, cy, Z_P1 + 0.04), idx * 1.1, c_fach)
    place_ph_asset(["potted_plant_02_dirt", "potted_plant_02_leaves", "potted_plant_02_pot"], "PH_Plant2_Balcon", (7.30, 1.15, Z_P2 + 0.04), 0.5, c_fach)

    create_box("P2_Mob_Tapete_Master", 0.90, 1.75, Z_P2 + 0.04, 3.70, 4.25, Z_P2 + 0.055, m_rug, c_mob)
    create_box("P2_Mob_Cama_Master_Base", 1.30, 2.55, Z_P2 + 0.055, 3.30, 4.55, Z_P2 + 0.30, m_mad, c_mob)
    create_box("P2_Mob_Cama_Master_Colchon", 1.33, 2.58, Z_P2 + 0.30, 3.27, 4.52, Z_P2 + 0.56, m_txt_c, c_mob)
    create_box("P2_Mob_Cama_Master_Edredon", 1.31, 2.56, Z_P2 + 0.32, 3.29, 4.00, Z_P2 + 0.59, m_txt, c_mob)
    create_box("P2_Mob_Cama_Master_Cabecero", 1.22, 4.50, Z_P2 + 0.055, 3.38, 4.62, Z_P2 + 1.22, m_txt, c_mob)
    create_box("P2_Mob_LED_Cabecero", 1.24, 4.62, Z_P2 + 0.15, 3.36, 4.64, Z_P2 + 1.18, m_led, c_mob)
    create_box("P2_Mob_Cama_Master_Alm_1", 1.45, 4.05, Z_P2 + 0.56, 2.25, 4.45, Z_P2 + 0.70, m_txt_c, c_mob)
    create_box("P2_Mob_Cama_Master_Alm_2", 2.35, 4.05, Z_P2 + 0.56, 3.15, 4.45, Z_P2 + 0.70, m_txt_c, c_mob)
    place_ph_asset(["side_table_01"], "P2_PH_Nightstand_1", (0.98, 4.25, Z_P2 + 0.04), 0.0, c_mob)
    place_ph_asset(["side_table_01"], "P2_PH_Nightstand_2", (3.62, 4.25, Z_P2 + 0.04), 0.0, c_mob)
    create_box("P2_Mob_Cortina_Master_L", 0.85, 0.18, Z_P2 + 0.05, 1.25, 0.28, Z_P2 + 2.55, m_txt_c, c_mob)
    create_box("P2_Mob_Cortina_Master_R", 3.55, 0.18, Z_P2 + 0.05, 3.95, 0.28, Z_P2 + 2.55, m_txt_c, c_mob)

    for sname in ("modern_coffee_table_01", "dining_chair_02", "side_table_01", "potted_plant_01_leaves", "potted_plant_01_pebbles", "potted_plant_01_pot", "potted_plant_01_stem", "potted_plant_02_dirt", "potted_plant_02_leaves", "potted_plant_02_pot"):
        orig = bpy.data.objects.get(sname)
        if orig:
            orig.hide_render = True
            orig.hide_viewport = True

    build_urban_context(c_urb, c_and, c_cal)
    refine_solar_panels(c_fach)

    m_aplique = new_mat("MAT_aplique_calido", (1.0, 0.82, 0.52, 1.0), 0.2, 0.0, 0.0, (1.0, 0.78, 0.45, 1.0), 12.0)
    for idx, (ax, ay, az) in enumerate([(1.15, 1.62, 2.25), (6.20, -0.02, 2.45), (8.02, 2.50, 2.25), (8.02, 7.50, 2.25), (6.20, 0.15, Z_P2 + 2.35)]):
        create_box(f"Aplique_Ext_{idx+1}", ax - 0.08, ay - 0.04, az - 0.06, ax + 0.08, ay + 0.04, az + 0.06, m_aplique, c_fach)

    bpy.ops.wm.save_as_mainfile(filepath=V2_BLEND)

    scene = bpy.context.scene
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = (d.type == "OPTIX")
    scene.cycles.device = "GPU"
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPTIX"
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"

    cam = bpy.data.objects.get("Cam_Render_Ext") or bpy.data.objects.get("Cam_Render_H4")
    scene.camera = cam
    timings = []

    def render_view(fname, loc, tgt, lens, samples, rx, ry):
        cam.data.type = "PERSP"
        cam.data.lens = lens
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.cycles.samples = samples
        scene.render.resolution_x = rx
        scene.render.resolution_y = ry
        scene.render.filepath = os.path.join(OUT_DIR, fname)
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        timings.append({"file": fname, "res": f"{rx}x{ry}", "samples": samples, "seconds": round(time.time() - t0, 2)})

    def set_night_world():
        w = scene.world
        w.use_nodes = True
        nt = w.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputWorld")
        bg = nt.nodes.new("ShaderNodeBackground")
        bg.inputs["Color"].default_value = (0.03, 0.05, 0.12, 1.0)
        bg.inputs["Strength"].default_value = 0.45
        nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    saved_world_nodes = scene.world.node_tree.nodes.get("Environment Texture") is not None

    for o in c_lgt.objects:
        if o.type == "LIGHT":
            o.hide_render = o.name.startswith("Sun_")
    scene.view_settings.exposure = -0.2
    render_view("01_ESQUINA_DIA_4K.png", (15.0, -10.0, 3.2), (4.2, 4.2, 2.9), 28.0, 64, 3840, 2160)
    render_view("06_CUBIERTA_FOTOVOLTAICA_4K.png", (12.0, -4.5, Z_ROOF + 6.5), (4.0, 4.5, Z_ROOF + 0.4), 28.0, 48, 3840, 2160)

    scene.view_settings.exposure = 0.0
    render_view("03_SALA_CONTEMPORANEA_4K.png", (0.45, 4.35, Z_P1 + 1.55), (3.20, 2.35, Z_P1 + 0.95), 24.0, 64, 3840, 2160)
    render_view("04_COCINA_COMEDOR_4K.png", (3.25, 5.95, Z_P1 + 1.55), (6.50, 7.15, Z_P1 + 0.95), 22.0, 64, 3840, 2160)
    render_view("05_SUITE_PRINCIPAL_4K.png", (0.50, 0.45, Z_P2 + 1.55), (2.40, 3.60, Z_P2 + 0.90), 24.0, 64, 3840, 2160)

    set_night_world()
    for o in c_lgt.objects:
        if o.type == "LIGHT" and not o.name.startswith("Sun_"):
            o.hide_render = False
            o.data.energy *= 2.8
    add_light("Luz_Urbana_Poste_1", "POINT", (10.5, -5.0, 5.5), 450.0, (1.0, 0.82, 0.58), 0.8, c_lgt)
    add_light("Luz_Urbana_Poste_2", "POINT", (-2.0, -5.0, 5.5), 380.0, (1.0, 0.82, 0.58), 0.8, c_lgt)
    scene.view_settings.exposure = 0.65
    render_view("02_ESQUINA_NOCHE_4K.png", (15.0, -10.0, 3.2), (4.2, 4.2, 2.9), 28.0, 64, 3840, 2160)

    with open(BENCH_JSON, "w", encoding="utf-8") as f:
        json.dump({"renders": timings}, f, indent=2)
    print("HITO_05_V2_COMPLETE:", json.dumps(timings))

main()
