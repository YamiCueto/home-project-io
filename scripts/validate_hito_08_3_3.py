import json
import math
from pathlib import Path
import bpy
from mathutils import Vector


def render_cam(out_path, loc, target, lens=26.0, samples=32):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    cam_data = bpy.data.cameras.new("_TMP_CAM_08_3_3")
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new("_TMP_CAM_08_3_3", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = Vector(loc)
    cam_obj.rotation_euler = (Vector(target) - cam_obj.location).to_track_quat("-Z", "Y").to_euler()
    prev = scene.camera
    scene.camera = cam_obj
    scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    scene.camera = prev
    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.cameras.remove(cam_data)


def main():
    root = Path(r"C:\Users\YAMI\Documents\projects\home-project")
    blend_path = root / "models" / "HOME_PROJECT_HITO_08_3_3.blend"
    out_dir = root / "renders" / "hito_08_3_3"
    out_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    tree_lods = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Arbol_Tropical_") and "_LOD" in o.name]
    old_trees = [o for o in bpy.data.objects if o.name.startswith("Arbol_Urbano_")]
    stair_treads = [o for o in bpy.data.objects if o.name.startswith("Esc_Techo_Peldano_")]
    solar_hidden = [o for o in bpy.data.objects if "Solar" in o.name and (o.hide_viewport or o.hide_render)]

    checks = {
        "tropical_trees_lod_count": len(tree_lods),
        "placeholder_trees_removed": len(old_trees) == 0,
        "roof_hatch_present": bpy.data.objects.get("Escotilla_Techo_Puerta1") is not None and bpy.data.objects.get("Escotilla_Techo_Marco") is not None,
        "roof_stair_treads": len(stair_treads),
        "roof_guardrails_present": all(bpy.data.objects.get(n) is not None for n in ("Baranda_Cubierta_Sur", "Baranda_Cubierta_Norte", "Baranda_Cubierta_Este", "Baranda_Cubierta_Oeste", "Baranda_Escotilla_Oeste")),
        "roof_drainage_present": bpy.data.objects.get("Cubierta_Canal_Drenaje") is not None and bpy.data.objects.get("Cubierta_Sumidero_NE") is not None,
        "solar_visible_in_arch_only": len(solar_hidden) == 0,
        "all_passed": False,
    }
    checks["all_passed"] = (
        checks["tropical_trees_lod_count"] == 9
        and checks["placeholder_trees_removed"]
        and checks["roof_hatch_present"]
        and checks["roof_stair_treads"] >= 11
        and checks["roof_guardrails_present"]
        and checks["roof_drainage_present"]
        and checks["solar_visible_in_arch_only"]
    )

    for o in tree_lods:
        if not o.name.endswith("_LOD0"):
            o.hide_render = True

    render_cam(out_dir / "AFTER_EXTERIOR_VEGETATION.png", (-5.5, -10.5, 3.2), (3.0, 1.5, 2.5), lens=26.0)
    render_cam(out_dir / "CUBIERTA_ACCESO_CERRADO.png", (8.8, 3.2, 8.2), (5.5, 6.2, 5.9), lens=28.0)

    lid = bpy.data.objects.get("Escotilla_Techo_Puerta1")
    if lid:
        lid.rotation_euler.x = math.radians(88.0)
    render_cam(out_dir / "CUBIERTA_ACCESO_ABIERTO.png", (8.4, 4.6, 7.6), (6.9, 6.2, 5.9), lens=28.0)

    (root / "validation" / "HITO_08_3_3_BLENDER_VALIDATION.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print("VALIDATE_08_3_3:", json.dumps(checks))


if __name__ == "__main__":
    main()
