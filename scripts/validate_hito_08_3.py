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
    blend_path = root / "models" / "HOME_PROJECT_HITO_08_3.blend"
    out_dir = root / "renders" / "hito_08_3"
    out_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    car_body = bpy.data.objects.get("Veh_Swift_Carroceria")
    moto_body = bpy.data.objects.get("Veh_VStrom_Carroceria")
    garaje_door = bpy.data.objects.get("P1_M_Norte_Garaje_Puerta1")
    vest_floor = bpy.data.objects.get("P2_Piso_P2_Vestidor_Principal")
    bano_floor = bpy.data.objects.get("P2_Piso_P2_Bano_Principal")
    entry_door = bpy.data.objects.get("P2_M_Banda_Sur_Puerta1")

    car_yr = bbox(car_body)[1] if car_body else (0, 0)
    moto_yr = bbox(moto_body)[1] if moto_body else (0, 0)
    gd_yr = bbox(garaje_door)[1] if garaje_door else (4.71, 4.71)
    vest_xr = bbox(vest_floor)[0] if vest_floor else (0, 0)
    bano_xr = bbox(bano_floor)[0] if bano_floor else (0, 0)

    checks = {
        "car_redesigned": car_body is not None and bpy.data.objects.get("Veh_Swift_Cabina_Vidrios") is not None,
        "moto_redesigned": moto_body is not None and bpy.data.objects.get("Veh_VStrom_Asiento") is not None,
        "car_north_door_clearance_m": round(gd_yr[0] - car_yr[1], 3),
        "moto_north_door_clearance_m": round(gd_yr[0] - moto_yr[1], 3),
        "garage_vehicles_clear_pass": (gd_yr[0] - car_yr[1] >= 0.40) and (gd_yr[0] - moto_yr[1] >= 0.80),
        "vestidor_width_m": round(vest_xr[1] - vest_xr[0], 3),
        "bano_principal_width_m": round(bano_xr[1] - bano_xr[0], 3),
        "master_entry_clear_stairwell": entry_door is not None and 2.10 <= entry_door.location.x <= 2.20,
        "all_passed": False,
    }
    checks["all_passed"] = (
        checks["car_redesigned"]
        and checks["moto_redesigned"]
        and checks["garage_vehicles_clear_pass"]
        and checks["vestidor_width_m"] >= 1.30
        and checks["bano_principal_width_m"] >= 1.75
        and checks["master_entry_clear_stairwell"]
    )

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 48
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960

    cam_data = bpy.data.cameras.new("_TMP_CAM_08_3")
    cam_obj = bpy.data.objects.new("_TMP_CAM_08_3", cam_data)
    scene.collection.objects.link(cam_obj)
    prev_cam = scene.camera
    scene.camera = cam_obj

    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 14.0
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
    scene.render.filepath = str(out_dir / "PLANTA_01_HITO_08_3.png")
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
    scene.render.filepath = str(out_dir / "PLANTA_02_HITO_08_3.png")
    bpy.ops.render.render(write_still=True)

    scene.camera = prev_cam
    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.cameras.remove(cam_data)
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    (root / "validation" / "HITO_08_3_BLENDER_VALIDATION.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print("VALIDATE_08_3:", json.dumps(checks))


if __name__ == "__main__":
    main()
