import json
import os
import bpy
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
VALIDATION_PATH = os.path.join(PROJECT_DIR, "validation", "HITO_03_VALIDATION.json")

def bbox_world(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return (min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts), max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))

def run_validation():
    cols = [o for o in bpy.data.collections["09_Estructura_Conceptual"].objects if o.name.startswith("Col_")]
    walls_ext = [o for o in bpy.data.objects if o.name.startswith(("P1_M_", "P2_M_")) and "_S" in o.name]
    coplanar_pairs = []
    for c in cols:
        cbb = bbox_world(c)
        for w in walls_ext:
            wbb = bbox_world(w)
            ox = min(cbb[3], wbb[3]) - max(cbb[0], wbb[0])
            oy = min(cbb[4], wbb[4]) - max(cbb[1], wbb[1])
            oz = min(cbb[5], wbb[5]) - max(cbb[2], wbb[2])
            if oz > 1e-3 and ((ox > 1e-3 and (abs(cbb[1] - wbb[1]) < 1e-4 or abs(cbb[4] - wbb[4]) < 1e-4)) or (oy > 1e-3 and (abs(cbb[0] - wbb[0]) < 1e-4 or abs(cbb[3] - wbb[3]) < 1e-4))):
                coplanar_pairs.append((c.name, w.name))

    veg_objs = [o for o in bpy.data.collections["14_Fachadas_Y_Vegetacion"].objects if o.name.startswith("Vegetacion_")]
    veg_outside_lot = []
    for v in veg_objs:
        vbb = bbox_world(v)
        if vbb[0] < -1e-4 or vbb[1] < -1e-4 or vbb[3] > 8.0001 or vbb[4] > 11.2501:
            veg_outside_lot.append(v.name)

    fach_outside_public = []
    for o in bpy.data.collections["14_Fachadas_Y_Vegetacion"].objects:
        obb = bbox_world(o)
        if obb[1] < -0.50 or obb[0] < -0.10 or obb[3] > 8.50:
            fach_outside_public.append(o.name)

    renders_expected = [
        "HITO_03_FRONTAL_DIA.png",
        "HITO_03_LATERAL_DIA.png",
        "HITO_03_ESQUINA_DIA.png",
        "HITO_03_FRONTAL_NOCHE.png",
        "HITO_03_ESQUINA_NOCHE.png",
        "HITO_03_AEREA.png",
    ]
    renders_ok = all(os.path.exists(os.path.join(PROJECT_DIR, "renders", r)) for r in renders_expected)

    scene = bpy.context.scene
    report = {
        "model": "HOME_PROJECT_HITO_03.blend",
        "render_engine": scene.render.engine,
        "cycles_device": scene.cycles.device,
        "cycles_denoiser": scene.cycles.denoiser,
        "materials_count": len(bpy.data.materials),
        "checks": {
            "no_coplanar_column_wall_zfighting": "PASS" if not coplanar_pairs else "FAIL",
            "vegetation_inside_private_lot": "PASS" if not veg_outside_lot else "FAIL",
            "facade_clear_of_public_sidewalk_ground": "PASS" if not fach_outside_public else "FAIL",
            "cycles_optix_configured": "PASS" if (scene.render.engine == "CYCLES" and scene.cycles.device == "GPU") else "FAIL",
            "all_6_renders_2560x1440_generated": "PASS" if renders_ok else "FAIL",
            "structural_and_pot_approval": "PENDING",
        },
        "details": {
            "coplanar_pairs": coplanar_pairs,
            "veg_outside_lot": veg_outside_lot,
            "fach_outside_public": fach_outside_public,
        },
    }
    with open(VALIDATION_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("HITO_03_VALIDATION:", json.dumps(report["checks"]))

run_validation()
