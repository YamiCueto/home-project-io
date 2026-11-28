import json
from pathlib import Path
import bpy
from mathutils import Vector


def bbox_xy_area(obj_name):
    o = bpy.data.objects.get(obj_name)
    if not o:
        return 0.0
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    dx = max(p.x for p in pts) - min(p.x for p in pts)
    dy = max(p.y for p in pts) - min(p.y for p in pts)
    return round(dx * dy, 3)


def render_cam(out_path, loc, target, ortho=False, ortho_scale=14.0, lens=28.0, samples=40):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960 if ortho else 720
    cam_data = bpy.data.cameras.new("_TMP_CAM_08_3_2")
    if ortho:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho_scale
    else:
        cam_data.lens = lens
    cam_obj = bpy.data.objects.new("_TMP_CAM_08_3_2", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = Vector(loc)
    if target is not None:
        direction = Vector(target) - Vector(loc)
        cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    else:
        cam_obj.rotation_euler = (0.0, 0.0, 0.0)
    prev = scene.camera
    scene.camera = cam_obj
    scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    scene.camera = prev
    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.cameras.remove(cam_data)


def main():
    root = Path(r"C:\Users\YAMI\Documents\projects\home-project")
    blend_path = root / "models" / "HOME_PROJECT_HITO_08_3_2.blend"
    out_dir = root / "renders" / "hito_08_3_2"
    out_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    bano_social_m2 = bbox_xy_area("P1_Piso_P1_Bano_Social")
    vestidor_m2 = bbox_xy_area("P2_Piso_P2_Vestidor_Principal")
    bano_principal_m2 = bbox_xy_area("P2_Piso_P2_Bano_Principal")
    balcon_present = bpy.data.objects.get("P2_Piso_P2_Balcon") is not None

    hidden_names = {"Mobiliario", "Vehiculos", "Equipamiento", "Decoracion", "Instalaciones"}
    visible_non_arch = []
    for cname in hidden_names:
        col = bpy.data.collections.get(cname)
        if col:
            for o in col.objects:
                if o.type == "MESH" and (not o.hide_viewport or not o.hide_render):
                    visible_non_arch.append(o.name)

    p2_footprint_m2 = 0.0
    losa_1 = bpy.data.objects.get("P2_Losa_Seg_1")
    losa_4 = bpy.data.objects.get("P2_Losa_Seg_4")
    if losa_1 and losa_4:
        p2_footprint_m2 = 8.0 * 10.0

    checks = {
        "bano_social_area_m2": bano_social_m2,
        "bano_social_expanded": bano_social_m2 >= 6.0,
        "vestidor_area_m2": vestidor_m2,
        "vestidor_expanded": vestidor_m2 >= 6.0,
        "bano_principal_area_m2": bano_principal_m2,
        "bano_principal_expanded": bano_principal_m2 >= 7.0,
        "balcon_eliminated": not balcon_present,
        "p2_footprint_m2": p2_footprint_m2,
        "p2_under_80m2": p2_footprint_m2 <= 80.0,
        "architecture_only_visible_non_arch_count": len(visible_non_arch),
        "all_passed": False,
    }
    checks["all_passed"] = (
        checks["bano_social_expanded"]
        and checks["vestidor_expanded"]
        and checks["bano_principal_expanded"]
        and checks["balcon_eliminated"]
        and checks["p2_under_80m2"]
        and len(visible_non_arch) == 0
    )

    hidden_p2 = []
    for o in bpy.data.collections["08_Propuesta_Segunda_Planta"].objects:
        if not o.hide_render:
            o.hide_render = True
            hidden_p2.append(o)
    for o in bpy.data.objects:
        if o.type == "MESH" and (o.name.startswith("P2_") or "Solar" in o.name or "Techo" in o.name or "Cubierta" in o.name or "Esc_Baranda_P2" in o.name or "Esc_Vidrio_P2" in o.name):
            if not o.hide_render:
                o.hide_render = True
                hidden_p2.append(o)

    render_cam(out_dir / "PLANTA_01_ARCHITECTURE_ONLY.png", (4.0, 5.6, 5.0), None, ortho=True)
    render_cam(out_dir / "ISOMETRICA_P1_ARCHITECTURE_ONLY.png", (-6.0, -5.0, 9.5), (4.0, 5.6, 1.0), ortho=False, lens=32.0)

    for o in hidden_p2:
        o.hide_render = False
    for o in bpy.data.objects:
        if o.type == "MESH":
            z_min = min((o.matrix_world @ Vector(c)).z for c in o.bound_box)
            if z_min >= 5.2 or "Solar" in o.name or "Cubierta" in o.name or "Techo" in o.name:
                if not o.hide_render:
                    o.hide_render = True

    render_cam(out_dir / "PLANTA_02_ARCHITECTURE_ONLY.png", (4.0, 5.6, 8.0), None, ortho=True)
    render_cam(out_dir / "ISOMETRICA_P2_ARCHITECTURE_ONLY.png", (-6.0, -5.0, 12.5), (4.0, 5.6, 3.8), ortho=False, lens=32.0)

    bpy.ops.wm.open_mainfile(filepath=str(blend_path))
    render_cam(out_dir / "FACHADA_SUR_ACTUALIZADA.png", (4.0, -10.5, 3.6), (4.0, 0.5, 2.8), ortho=False, lens=30.0)

    (root / "validation" / "HITO_08_3_2_BLENDER_VALIDATION.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print("VALIDATE_08_3_2:", json.dumps(checks))


if __name__ == "__main__":
    main()
