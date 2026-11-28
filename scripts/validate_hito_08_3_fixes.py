import json
from pathlib import Path
import bpy
from mathutils import Vector


def bbox(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))


def main():
    root = Path(r"C:\Users\YAMI\Documents\projects\home-project")
    blend_path = root / "models" / "HOME_PROJECT_HITO_08_3_FIXES.blend"
    out_dir = root / "renders" / "hito_08_3_fixes"
    out_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    gar_door = bpy.data.objects.get("P1_M_Sep_Sala_Garaje_Puerta1")
    estante = bpy.data.objects.get("P1_Mob_Estante_Garaje")
    mesa = bpy.data.objects.get("P1_Mob_Mesa_Comedor_Sobre")
    handrail = bpy.data.objects.get("Esc_Pasamanos_Norte")
    col_p2_08 = bpy.data.objects.get("Col_P2_08")
    viga_p2_06 = bpy.data.objects.get("Viga_P2_06")

    gd_yr = bbox(gar_door)[1] if gar_door else (0, 0)
    est_xr, est_yr = bbox(estante)[0], bbox(estante)[1]
    mesa_yr = bbox(mesa)[1] if mesa else (0, 0)
    hr_yr = bbox(handrail)[1] if handrail else (5.71, 5.71)
    col_xr = bbox(col_p2_08)[0] if col_p2_08 else (0, 0)
    viga6_yr = bbox(viga_p2_06)[1] if viga_p2_06 else (0, 10)

    chairs_clear = True
    for i in range(1, 6):
        ch = bpy.data.objects.get(f"P1_PH_Chair_{i}_dining_chair_02")
        if ch:
            cxr, cyr, czr = bbox(ch)
            if cyr[0] <= hr_yr[1]:
                chairs_clear = False
            if i in (1, 2) and cyr[1] > mesa_yr[0] + 0.25:
                chairs_clear = False
            if i in (3, 4) and cyr[0] < mesa_yr[1] - 0.25:
                chairs_clear = False
            if abs(czr[0] - 0.04) > 0.02:
                chairs_clear = False

    checks = {
        "hall_garage_door_width_m": round(gd_yr[1] - gd_yr[0], 3),
        "hall_garage_width_pass": (gd_yr[1] - gd_yr[0]) >= 0.90,
        "estante_clear_of_doorway": est_xr[0] >= 4.85 and est_yr[0] >= 4.25,
        "dining_chairs_clear": chairs_clear,
        "col_p2_08_integrated_in_wall": col_xr[0] >= 3.85 and col_xr[1] <= 4.15,
        "viga_p2_06_clear_kids_room": viga6_yr[1] <= 4.80,
        "all_passed": False,
    }
    checks["all_passed"] = (
        checks["hall_garage_width_pass"]
        and checks["estante_clear_of_doorway"]
        and checks["dining_chairs_clear"]
        and checks["col_p2_08_integrated_in_wall"]
        and checks["viga_p2_06_clear_kids_room"]
    )

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 48
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    cam_data = bpy.data.cameras.new("_TMP_PLAN_FIX")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 14.0
    cam_obj = bpy.data.objects.new("_TMP_PLAN_FIX", cam_data)
    scene.collection.objects.link(cam_obj)
    prev_cam = scene.camera
    scene.camera = cam_obj

    hidden_p2 = []
    for o in bpy.data.collections["08_Propuesta_Segunda_Planta"].objects:
        if not o.hide_render:
            o.hide_render = True
            hidden_p2.append(o)
    for o in bpy.data.objects:
        if o.type == "MESH" and (o.name.startswith("P2_") or "Solar" in o.name or "Techo" in o.name or "Cubierta" in o.name or "Balcon" in o.name or "Esc_Baranda_P2" in o.name or "Esc_Vidrio_P2" in o.name):
            if not o.hide_render:
                o.hide_render = True
                hidden_p2.append(o)
    cam_obj.location = (4.0, 5.6, 5.0)
    cam_obj.rotation_euler = (0.0, 0.0, 0.0)
    scene.render.filepath = str(out_dir / "PLANTA_01_FIXES.png")
    bpy.ops.render.render(write_still=True)

    for o in hidden_p2:
        o.hide_render = False
    for o in bpy.data.objects:
        if o.type == "MESH":
            z_min = min((o.matrix_world @ Vector(c)).z for c in o.bound_box)
            if z_min >= 5.2 or "Solar" in o.name or "Cubierta" in o.name or "Techo" in o.name:
                if not o.hide_render:
                    o.hide_render = True
    cam_obj.location = (4.0, 5.6, 8.0)
    scene.render.filepath = str(out_dir / "PLANTA_02_FIXES.png")
    bpy.ops.render.render(write_still=True)

    scene.camera = prev_cam
    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.cameras.remove(cam_data)
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    (root / "validation" / "HITO_08_3_FIXES_BLENDER_VALIDATION.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print("VALIDATE_08_3_FIXES:", json.dumps(checks))


if __name__ == "__main__":
    main()
