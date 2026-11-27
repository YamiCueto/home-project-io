import json
import os
import time
import bpy
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
HITO5_BLEND = os.path.join(PROJECT_DIR, "models", "HOME_PROJECT_HITO_05.blend")
OUT_BASE = os.path.join(PROJECT_DIR, "renders", "hito_05")
BENCH_JSON = os.path.join(PROJECT_DIR, "validation", "HITO_05_BENCHMARK.json")

Z_P1 = 0.00
Z_P2 = 2.90
Z_ROOF = 5.60

def set_world_nishita(elevation, rotation, strength=1.0, sun_disc=True):
    world = bpy.context.scene.world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_disc = sun_disc
    sky.sun_elevation = elevation
    sky.sun_rotation = rotation
    sky.air_density = 1.1
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

def set_world_night():
    world = bpy.context.scene.world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.02, 0.035, 0.08, 1.0)
    bg.inputs["Strength"].default_value = 0.28
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

def set_lights(interior_on, exterior_on):
    for o in bpy.data.collections["15_Iluminacion"].objects:
        if o.type == "LIGHT":
            if o.name.startswith("Lgt_Int_"):
                o.hide_render = not interior_on
            elif o.name.startswith("Sun_"):
                o.hide_render = True
            else:
                o.hide_render = not exterior_on

def setup_cycles(samples, rx, ry):
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
    scene.render.resolution_x = rx
    scene.render.resolution_y = ry
    scene.render.resolution_percentage = 100
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"

def aim_cam(cam, loc, tgt, lens=28.0, ortho=False, ortho_scale=14.0):
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = ortho_scale
    else:
        cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - cam.location).to_track_quat("-Z", "Y").to_euler()

def main():
    bpy.ops.wm.open_mainfile(filepath=HITO5_BLEND)
    scene = bpy.context.scene
    cam = bpy.data.objects.get("Cam_Render_Ext") or bpy.data.objects.get("Cam_Render_H4")
    scene.camera = cam

    timings = []

    def do_render(rel_path, loc, tgt, lens, samples, rx, ry, ortho=False):
        aim_cam(cam, loc, tgt, lens, ortho=ortho)
        fp = os.path.join(OUT_BASE, rel_path)
        scene.render.filepath = fp
        setup_cycles(samples, rx, ry)
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        dt = round(time.time() - t0, 2)
        timings.append({"file": rel_path, "res": f"{rx}x{ry}", "samples": samples, "seconds": dt})

    set_world_nishita(0.62, 0.78, 0.35)
    set_lights(False, False)
    scene.view_settings.exposure = -1.2
    do_render("exterior/01_ESQUINA_DIA_4K.png", (15.0, -10.0, 3.2), (4.2, 4.2, 2.9), 28.0, 64, 3840, 2160)
    do_render("exterior/04_AEREA_FOTOVOLTAICA.png", (17.5, -12.5, 13.5), (4.0, 5.0, 2.5), 32.0, 48, 2560, 1440)

    set_world_nishita(0.09, 1.15, 0.30)
    set_lights(True, True)
    scene.view_settings.exposure = -0.6
    do_render("exterior/02_ESQUINA_ATARDECER_4K.png", (15.0, -10.0, 3.2), (4.2, 4.2, 2.9), 28.0, 64, 3840, 2160)

    set_world_night()
    set_lights(True, True)
    scene.view_settings.exposure = 0.4
    do_render("exterior/03_FRONTAL_NOCHE.png", (4.0, -13.5, 2.6), (4.0, 2.0, 3.0), 35.0, 48, 2560, 1440)

    set_world_nishita(0.55, 0.78, 0.35)
    set_lights(True, False)
    scene.view_settings.exposure = 0.0
    do_render("interior/05_SALA_CONTEMPORANEA.png", (0.55, 4.30, Z_P1 + 1.55), (3.10, 2.25, Z_P1 + 1.05), 24.0, 64, 2560, 1440)
    do_render("interior/06_COCINA_COMEDOR.png", (3.25, 5.95, Z_P1 + 1.55), (6.50, 7.15, Z_P1 + 0.95), 22.0, 64, 2560, 1440)
    do_render("interior/07_SUITE_PRINCIPAL.png", (0.50, 4.20, Z_P2 + 1.55), (2.50, 1.15, Z_P2 + 0.95), 24.0, 64, 2560, 1440)

    set_lights(False, False)
    scene.view_settings.exposure = -1.0
    for o in bpy.data.collections["08_Propuesta_Segunda_Planta"].objects:
        if o.name.startswith(("Cubierta_", "Pretil_")):
            o.hide_render = True
    for o in bpy.data.collections["16_Instalaciones_Domotica"].objects:
        if "Ampliacion_Solar" in o.name:
            o.hide_render = True
    do_render("architectural/08_CORTE_ISOMETRICO_CONJUNTO.png", (16.5, -9.5, 16.5), (4.0, 5.0, 2.8), 32.0, 48, 2560, 1440, ortho=True)

    with open(BENCH_JSON, "w", encoding="utf-8") as f:
        json.dump({"gpu": "NVIDIA GeForce RTX 5070 Ti Laptop GPU", "backend": "OPTIX", "color_management": "AgX", "renders": timings}, f, indent=2)
    print("HITO_05_RENDERS_COMPLETE:", json.dumps(timings))

main()
