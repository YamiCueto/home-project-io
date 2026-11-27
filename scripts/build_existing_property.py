import os
import bpy
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
BLEND_PATH = os.path.join(PROJECT_DIR, "models", "HOME_PROJECT_EXISTENTE.blend")
RENDER_TOP = os.path.join(PROJECT_DIR, "renders", "HITO_01_1_EXISTENTE_PLANTA.png")
RENDER_ISO = os.path.join(PROJECT_DIR, "renders", "HITO_01_1_EXISTENTE_ISO.png")

COLORS = {
    "propiedad": (0.76, 0.72, 0.64, 1.0),
    "muro_ext": (0.35, 0.35, 0.38, 1.0),
    "linderos": (0.95, 0.25, 0.20, 1.0),
    "terraza_f": (0.85, 0.75, 0.55, 1.0),
    "terraza_l": (0.78, 0.82, 0.60, 1.0),
    "techo_t": (0.65, 0.68, 0.72, 0.35),
    "cerramiento": (0.15, 0.15, 0.18, 1.0),
    "anden": (0.62, 0.62, 0.64, 1.0),
    "calle": (0.20, 0.21, 0.23, 1.0),
}

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

def get_col(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

def get_mat(name, rgba):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.8
        if rgba[3] < 1.0:
            bsdf.inputs["Alpha"].default_value = rgba[3]
    mat.diffuse_color = rgba
    return mat

def box(name, x0, y0, z0, x1, y1, z1, mat_key, col):
    cx = (x0 + x1) * 0.5
    cy = (y0 + y1) * 0.5
    cz = (z0 + z1) * 0.5
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    obj.data.materials.append(get_mat(f"MAT_{mat_key}", COLORS[mat_key]))
    return obj

def label(name, text, x, y, z, size, col):
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

def main():
    clear_scene()
    c_prop = get_col("00_Propiedad_Existente")
    c_lind = get_col("01_Linderos_Provisionales")
    c_tf = get_col("02_Terraza_Frontal")
    c_tl = get_col("03_Terraza_Lateral")
    c_cerr = get_col("04_Cerramiento_Existente")
    c_and = get_col("05_Andenes_Publicos")
    c_cal = get_col("06_Calles")
    c_cam = get_col("12_Camaras")

    box("Lote_Base_90m2", 0.0, 0.0, -0.05, 8.0, 11.25, 0.0, "propiedad", c_lind)
    box("Lindero_Oeste", -0.04, 0.0, 0.0, 0.0, 11.25, 0.12, "linderos", c_lind)
    box("Lindero_Norte", 0.0, 11.25, 0.0, 8.0, 11.29, 0.12, "linderos", c_lind)
    box("Lindero_Sur_Frente", 0.0, -0.04, 0.0, 8.0, 0.0, 0.12, "linderos", c_lind)
    box("Lindero_Este_Lateral", 8.0, 0.0, 0.0, 8.04, 11.25, 0.12, "linderos", c_lind)

    box("Existente_Piso_Interior", 0.0, 2.0, 0.0, 6.0, 11.25, 0.06, "propiedad", c_prop)
    box("Existente_Muro_Oeste", 0.0, 2.0, 0.06, 0.15, 11.25, 2.70, "muro_ext", c_prop)
    box("Existente_Muro_Norte", 0.15, 11.10, 0.06, 6.0, 11.25, 2.70, "muro_ext", c_prop)
    box("Existente_Muro_Este", 5.85, 2.0, 0.06, 6.0, 11.10, 2.70, "muro_ext", c_prop)
    box("Existente_Muro_Sur_Izq", 0.15, 2.0, 0.06, 2.40, 2.15, 2.70, "muro_ext", c_prop)
    box("Existente_Muro_Sur_Der", 3.50, 2.0, 0.06, 5.85, 2.15, 2.70, "muro_ext", c_prop)
    box("Existente_Cubierta", 0.0, 2.0, 2.70, 6.0, 11.25, 2.85, "techo_t", c_prop)
    label("Lbl_Existente", "Construccion Existente\n6.00 x 9.25 m (55.50 m2)", 3.0, 6.6, 0.15, 0.35, c_prop)

    box("Terraza_Frontal_Piso", 0.0, 0.0, 0.0, 8.0, 2.0, 0.04, "terraza_f", c_tf)
    box("Terraza_Frontal_Techo", 0.0, 0.0, 2.65, 8.0, 2.0, 2.75, "techo_t", c_tf)
    label("Lbl_TF", "Terraza Frontal Cubierta\n8.00 x 2.00 m (16.00 m2)", 4.0, 1.0, 0.15, 0.30, c_tf)

    box("Terraza_Lateral_Piso", 6.0, 2.0, 0.0, 8.0, 11.25, 0.04, "terraza_l", c_tl)
    box("Terraza_Lateral_Techo", 6.0, 2.0, 2.65, 8.0, 11.25, 2.75, "techo_t", c_tl)
    label("Lbl_TL", "Terraza Lateral\n2.00 x 9.25 m\n(18.50 m2)", 7.0, 6.6, 0.15, 0.28, c_tl)

    box("Cerramiento_Sur_Murete", 0.0, 0.0, 0.04, 8.0, 0.10, 1.90, "cerramiento", c_cerr)
    box("Cerramiento_Este_Murete", 7.90, 0.10, 0.04, 8.0, 11.25, 1.90, "cerramiento", c_cerr)

    box("Anden_Frontal", -1.5, -1.5, -0.04, 9.5, 0.0, 0.0, "anden", c_and)
    box("Anden_Lateral", 8.0, 0.0, -0.04, 9.5, 11.25, 0.0, "anden", c_and)
    label("Lbl_Anden_F", "Anden Publico Frontal", 4.0, -0.75, 0.05, 0.30, c_and)
    label("Lbl_Anden_L", "Anden Publico Lateral", 8.75, 5.5, 0.05, 0.25, c_and)

    box("Calle_Frontal", -1.5, -6.5, -0.10, 14.5, -1.5, -0.04, "calle", c_cal)
    box("Calle_Lateral", 9.5, -1.5, -0.10, 14.5, 11.25, -0.04, "calle", c_cal)
    label("Lbl_Calle_F", "Calle Principal (Y-)", 4.0, -4.0, 0.02, 0.45, c_cal)
    label("Lbl_Calle_L", "Calle Lateral (X+)", 12.0, 5.5, 0.02, 0.45, c_cal)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_object_outline = True
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200

    world = bpy.data.worlds.new("World_Ex")
    scene.world = world
    world.color = (0.92, 0.93, 0.95)

    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.name = "Cam_Existente"
    for c in list(cam.users_collection):
        c.objects.unlink(cam)
    c_cam.objects.link(cam)
    scene.camera = cam

    bpy.data.objects["Existente_Cubierta"].hide_render = True
    bpy.data.objects["Terraza_Frontal_Techo"].hide_render = True
    bpy.data.objects["Terraza_Lateral_Techo"].hide_render = True

    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 20.0
    cam.location = (6.0, 3.0, 20.0)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    scene.render.filepath = RENDER_TOP
    bpy.ops.render.render(write_still=True)

    cam.data.type = "PERSP"
    cam.data.lens = 35.0
    cam.location = (20.0, -14.0, 13.0)
    direction = Vector((5.0, 4.0, 1.0)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = RENDER_ISO
    bpy.ops.render.render(write_still=True)

    bpy.data.objects["Existente_Cubierta"].hide_render = False
    bpy.data.objects["Terraza_Frontal_Techo"].hide_render = False
    bpy.data.objects["Terraza_Lateral_Techo"].hide_render = False

    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print("EXISTING_PROPERTY_OK")

main()
