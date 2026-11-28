import json
from pathlib import Path
import bpy
from mathutils import Vector

def get_root():
    if bpy.data.filepath:
        p = Path(bpy.data.filepath).resolve()
        if p.parent.name == "models":
            return p.parent.parent
    return Path.cwd()

def bbox(name):
    o = bpy.data.objects.get(name)
    if not o:
        return None
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts), min(p.z for p in pts), max(p.z for p in pts))

def main():
    root = get_root()
    h6_v3 = root / "models" / "HOME_PROJECT_HITO_06_V3.blend"
    bpy.ops.wm.open_mainfile(filepath=str(h6_v3))

    izq = bbox("Fach_Murete_Peatonal_Izq")
    der = bbox("Fach_Murete_Peatonal_Der")
    ped_gap = round(der[0] - izq[1], 3) if (izq and der) else 0.0

    ch3 = bbox("P1_PH_Chair_3_dining_chair_02")
    ch4 = bbox("P1_PH_Chair_4_dining_chair_02")
    north_wall = bbox("P1_M_Huesped_Norte_Cocina_S2")
    dining_north_aisle = round(north_wall[2] - max(ch3[3], ch4[3]), 3) if (ch3 and ch4 and north_wall) else 0.0

    barra = bbox("P1_Mob_Cocina_Barra")
    kitchen_aisle = round(north_wall[2] - barra[3], 3) if (barra and north_wall) else 0.0

    garage_wall = bbox("P1_M_Norte_Garaje_S0")
    garage_door = bbox("P1_M_Norte_Garaje_Puerta1")
    handrail = bbox("Esc_Pasamanos_Norte")
    p2_guard_w = bbox("Esc_Baranda_P2_Oeste")
    p2_guard_n = bbox("Esc_Baranda_P2_Norte")

    checks = {
        "pedestrian_gate_width_m": ped_gap,
        "pedestrian_gate_pass": ped_gap >= 0.90,
        "dining_north_aisle_m": dining_north_aisle,
        "kitchen_entry_aisle_m": kitchen_aisle,
        "kitchen_aisle_pass": kitchen_aisle >= 0.90,
        "garage_enclosure_present": garage_wall is not None and garage_door is not None,
        "stair_handrail_present": handrail is not None,
        "p2_stairwell_guardrails_present": p2_guard_w is not None and p2_guard_n is not None,
    }
    checks["all_passed"] = all([
        checks["pedestrian_gate_pass"],
        checks["kitchen_aisle_pass"],
        checks["garage_enclosure_present"],
        checks["stair_handrail_present"],
        checks["p2_stairwell_guardrails_present"],
    ])

    out_dir = root / "renders" / "hito_08_3_1"
    out_dir.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960

    cam_data = bpy.data.cameras.new("_TMP_PLAN_CAM")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 14.0
    cam_obj = bpy.data.objects.new("_TMP_PLAN_CAM", cam_data)
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
    scene.render.filepath = str(out_dir / "PLANTA_01_V3.png")
    bpy.ops.render.render(write_still=True)

    for o in hidden_p2:
        o.hide_render = False
    from mathutils import Vector
    for o in bpy.data.objects:
        if o.type == "MESH":
            z_min = min((o.matrix_world @ Vector(c)).z for c in o.bound_box)
            if z_min >= 5.2 or "Solar" in o.name or "Cubierta" in o.name or "Techo" in o.name:
                if not o.hide_render:
                    o.hide_render = True
    cam_obj.location = (4.0, 5.6, 8.0)
    scene.render.filepath = str(out_dir / "PLANTA_02_V3.png")
    bpy.ops.render.render(write_still=True)

    scene.camera = prev_cam
    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.cameras.remove(cam_data)
    bpy.ops.wm.open_mainfile(filepath=str(h6_v3))

    (root / "validation" / "HITO_06_V3_BLENDER_VALIDATION.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print("VALIDATE_V3:", json.dumps(checks))

if __name__ == "__main__":
    main()
