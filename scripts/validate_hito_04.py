import json
import os
import bpy
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
VALIDATION_PATH = os.path.join(PROJECT_DIR, "validation", "HITO_04_VALIDATION.json")
RENDERS_DIR = os.path.join(PROJECT_DIR, "renders", "hito_04")

def bbox_world(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return (min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts), max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))

def overlap_3d(a, b, tol=1e-4):
    return (
        (min(a[3], b[3]) - max(a[0], b[0])) > tol and
        (min(a[4], b[4]) - max(a[1], b[1])) > tol and
        (min(a[5], b[5]) - max(a[2], b[2])) > tol
    )

def run_validation():
    cols = [o for o in bpy.data.collections["09_Estructura_Conceptual"].objects if o.name.startswith("Col_")]
    walls_ext = [o for o in bpy.data.objects if o.name.startswith(("P1_M_", "P2_M_")) and "_S" in o.name]
    coplanar = []
    for c in cols:
        cbb = bbox_world(c)
        for w in walls_ext:
            wbb = bbox_world(w)
            ox = min(cbb[3], wbb[3]) - max(cbb[0], wbb[0])
            oy = min(cbb[4], wbb[4]) - max(cbb[1], wbb[1])
            oz = min(cbb[5], wbb[5]) - max(cbb[2], wbb[2])
            if oz > 1e-3 and ((ox > 1e-3 and (abs(cbb[1] - wbb[1]) < 1e-4 or abs(cbb[4] - wbb[4]) < 1e-4)) or (oy > 1e-3 and (abs(cbb[0] - wbb[0]) < 1e-4 or abs(cbb[3] - wbb[3]) < 1e-4))):
                coplanar.append((c.name, w.name))

    mob = list(bpy.data.collections["11_Mobiliario"].objects)
    doors = [o for o in bpy.data.objects if "_Puerta" in o.name]
    door_blocks = []
    for d in doors:
        dbb = bbox_world(d)
        for m in mob:
            if overlap_3d(dbb, bbox_world(m)):
                door_blocks.append((d.name, m.name))

    meshes_no_uv = [o.name for o in bpy.data.objects if o.type == "MESH" and o.data.polygons and not o.data.uv_layers]
    inst_count = len(bpy.data.collections["16_Instalaciones_Domotica"].objects)
    renders_count = len([f for f in os.listdir(RENDERS_DIR) if f.endswith(".png")]) if os.path.exists(RENDERS_DIR) else 0

    report = {
        "model": "HOME_PROJECT_HITO_04.blend",
        "metrics": {
            "furniture_objects": len(mob),
            "vehicle_objects": len(bpy.data.collections["10_Vehiculos"].objects),
            "domotica_energy_objects": inst_count,
            "renders_generated": renders_count,
            "meshes_without_uv": len(meshes_no_uv),
        },
        "checks": {
            "col_p2_03_conflict_resolved": "PASS" if not coplanar else "FAIL",
            "no_furniture_blocking_doors": "PASS" if not door_blocks else "FAIL",
            "all_meshes_have_uvs_for_unity": "PASS" if not meshes_no_uv else "FAIL",
            "energy_and_domotica_modeled": "PASS" if inst_count >= 10 else "FAIL",
            "all_18_renders_generated": "PASS" if renders_count >= 18 else "FAIL",
            "electrical_and_structural_cert": "PENDING",
        },
        "details": {
            "coplanar": coplanar,
            "door_blocks": door_blocks,
        },
    }
    with open(VALIDATION_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("HITO_04_VALIDATION:", json.dumps(report["checks"]))

run_validation()
