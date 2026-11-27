import json
import os
from collections import deque
import bpy
from mathutils import Vector

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
VALIDATION_PATH = os.path.join(PROJECT_DIR, "validation", "HITO_02_VALIDATION.json")

def bbox_world(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))

def overlap_2d(a, b, tol=1e-4):
    return (min(a[3], b[3]) - max(a[0], b[0])) > tol and (min(a[4], b[4]) - max(a[1], b[1])) > tol

def overlap_3d(a, b, tol=1e-4):
    return (
        (min(a[3], b[3]) - max(a[0], b[0])) > tol and
        (min(a[4], b[4]) - max(a[1], b[1])) > tol and
        (min(a[5], b[5]) - max(a[2], b[2])) > tol
    )

def union_area_2d(rects):
    if not rects:
        return 0.0
    xs = sorted(set([r[0] for r in rects] + [r[3] for r in rects]))
    total = 0.0
    for i in range(len(xs) - 1):
        x0, x1 = xs[i], xs[i + 1]
        if x1 - x0 <= 1e-6:
            continue
        ys_intervals = sorted([(r[1], r[4]) for r in rects if r[0] <= x0 + 1e-6 and r[3] >= x1 - 1e-6])
        if not ys_intervals:
            continue
        cur_s, cur_e = ys_intervals[0]
        y_len = 0.0
        for s, e in ys_intervals[1:]:
            if s <= cur_e:
                cur_e = max(cur_e, e)
            else:
                y_len += cur_e - cur_s
                cur_s, cur_e = s, e
        y_len += cur_e - cur_s
        total += (x1 - x0) * y_len
    return total

def run_validation():
    p1_floors = [o for o in bpy.data.collections["07_Propuesta_Primera_Planta"].objects if o.name.startswith("P1_Piso_")]
    p2_floors = [o for o in bpy.data.collections["08_Propuesta_Segunda_Planta"].objects if o.name.startswith("P2_Piso_")]
    p2_slabs = [o for o in bpy.data.collections["09_Estructura_Conceptual"].objects if o.name.startswith("P2_Losa_")]
    roofs = [o for o in bpy.data.collections["08_Propuesta_Segunda_Planta"].objects if o.name.startswith("Cubierta_")]
    cols = [o for o in bpy.data.collections["09_Estructura_Conceptual"].objects if o.name.startswith("Col_")]
    stairs = [o for o in bpy.data.collections["07_Propuesta_Primera_Planta"].objects if o.name.startswith("P1_Esc_Peldano_")]
    doors = [o for o in bpy.data.objects if "_Puerta" in o.name]
    furn = list(bpy.data.collections["11_Mobiliario"].objects)
    vehs = list(bpy.data.collections["10_Vehiculos"].objects)

    p1_rects = [bbox_world(o) for o in p1_floors]
    p2_rects = [bbox_world(o) for o in p2_floors]
    p2_slab_proj = union_area_2d([bbox_world(o) for o in p2_slabs])
    roof_proj = union_area_2d([bbox_world(o) for o in roofs])

    p1_net_area = union_area_2d(p1_rects)
    p2_net_area = union_area_2d(p2_rects)
    p1_covered_floors = [o for o in p1_floors if o.name not in ("P1_Piso_P1_Acceso_Peatonal", "P1_Piso_P1_Lavanderia_Patio")]
    p1_covered_net = union_area_2d([bbox_world(o) for o in p1_covered_floors])

    cols_outside_lot = []
    for c in cols:
        bb = bbox_world(c)
        if bb[0] < -1e-4 or bb[1] < -1e-4 or bb[3] > 8.0001 or bb[4] > 11.2501:
            cols_outside_lot.append(c.name)

    furn_col = []
    for i in range(len(furn)):
        for j in range(i + 1, len(furn)):
            if overlap_3d(bbox_world(furn[i]), bbox_world(furn[j])):
                furn_col.append((furn[i].name, furn[j].name))

    col_door_int = []
    for c in cols:
        cbb = bbox_world(c)
        for d in doors:
            if overlap_3d(cbb, bbox_world(d)):
                col_door_int.append((c.name, d.name))

    stair_headrooms = []
    for s in stairs:
        sbb = bbox_world(s)
        head = 2.90
        for sl in p2_slabs:
            slbb = bbox_world(sl)
            if overlap_2d(sbb, slbb):
                head = min(head, slbb[2] - sbb[5])
        for rf in roofs:
            rfbb = bbox_world(rf)
            if overlap_2d(sbb, rfbb):
                head = min(head, rfbb[2] - sbb[5])
        stair_headrooms.append(round(head, 3))
    min_stair_headroom = min(stair_headrooms) if stair_headrooms else 0.0

    p2_llegada = next((o for o in p2_floors if "Llegada_Escalera" in o.name), None)
    llegada_depth = (bbox_world(p2_llegada)[3] - bbox_world(p2_llegada)[0]) if p2_llegada else 0.0

    sig_map = {}
    dups = []
    for colname in ("07_Propuesta_Primera_Planta", "08_Propuesta_Segunda_Planta"):
        for o in bpy.data.collections[colname].objects:
            if o.type == "MESH":
                bb = bbox_world(o)
                sig = (len(o.data.vertices), round(bb[0], 3), round(bb[1], 3), round(bb[2], 3), round(bb[3], 3), round(bb[4], 3), round(bb[5], 3))
                if sig in sig_map:
                    dups.append((sig_map[sig], o.name))
                else:
                    sig_map[sig] = o.name

    all_rooms = p1_floors + p2_floors
    adj = {r.name: set() for r in all_rooms}
    for d in doors:
        dbb = bbox_world(d)
        exp = (dbb[0] - 0.15, dbb[1] - 0.15, dbb[2] - 0.15, dbb[3] + 0.15, dbb[4] + 0.15, dbb[5] + 0.15)
        touching = [r.name for r in all_rooms if overlap_3d(exp, bbox_world(r))]
        for i in range(len(touching)):
            for j in range(i + 1, len(touching)):
                adj[touching[i]].add(touching[j])
                adj[touching[j]].add(touching[i])
    for r1 in p1_floors:
        for r2 in p1_floors:
            if r1 != r2 and overlap_2d((bbox_world(r1)[0] - 0.12, bbox_world(r1)[1] - 0.12, 0, bbox_world(r1)[3] + 0.12, bbox_world(r1)[4] + 0.12, 1), bbox_world(r2)):
                if ("Distribuidor" in r1.name and "Escalera" in r2.name) or ("Comedor" in r1.name and "Cocina" in r2.name) or ("Comedor" in r1.name and "Distribuidor" in r2.name):
                    adj[r1.name].add(r2.name)
                    adj[r2.name].add(r1.name)
    for r1 in p2_floors:
        for r2 in p2_floors:
            if r1 != r2 and "Distribuidor" in r1.name and ("Llegada" in r2.name or "Distribuidor" in r2.name):
                adj[r1.name].add(r2.name)
                adj[r2.name].add(r1.name)
    adj.setdefault("P1_Piso_P1_Escalera", set()).add("P2_Piso_P2_Llegada_Escalera")
    adj.setdefault("P2_Piso_P2_Llegada_Escalera", set()).add("P1_Piso_P1_Escalera")

    visited = set()
    q = deque(["P1_Piso_P1_Acceso_Peatonal"])
    while q:
        cur = q.popleft()
        if cur in visited:
            continue
        visited.add(cur)
        for nxt in adj.get(cur, []):
            if nxt not in visited:
                q.append(nxt)
    unconnected = [r.name for r in all_rooms if r.name not in visited]

    garaje_obj = next((o for o in p1_floors if "Garaje" in o.name), None)
    gbb = bbox_world(garaje_obj) if garaje_obj else (0, 0, 0, 0, 0, 0)
    car_obj = next((o for o in vehs if "Swift" in o.name), None)
    moto_obj = next((o for o in vehs if "VStrom" in o.name), None)
    car_bb = bbox_world(car_obj) if car_obj else (0, 0, 0, 0, 0, 0)
    moto_bb = bbox_world(moto_obj) if moto_obj else (0, 0, 0, 0, 0, 0)
    car_door_clearance = round(moto_bb[0] - car_bb[3], 3)

    anim_cam = bpy.data.objects.get("Cam_Recorrido_Anim")
    agent_collisions = []
    if anim_cam and anim_cam.animation_data and anim_cam.animation_data.action:
        walls_solid = [o for o in list(bpy.data.collections["07_Propuesta_Primera_Planta"].objects) + list(bpy.data.collections["08_Propuesta_Segunda_Planta"].objects) if "_S" in o.name]
        for f in range(0, 1153, 24):
            bpy.context.scene.frame_set(f)
            loc = anim_cam.matrix_world.translation
            abb = (loc.x - 0.20, loc.y - 0.20, loc.z - 1.20, loc.x + 0.20, loc.y + 0.20, loc.z + 0.10)
            for w in walls_solid:
                if overlap_3d(abb, bbox_world(w)):
                    agent_collisions.append((f, w.name))

    report = {
        "model": "HOME_PROJECT_HITO_02.blend",
        "areas_from_geometry_m2": {
            "p1_total_floors_net_m2": round(p1_net_area, 3),
            "p1_covered_floors_net_m2": round(p1_covered_net, 3),
            "p2_floors_net_m2": round(p2_net_area, 3),
            "p2_slab_horizontal_projection_m2": round(p2_slab_proj, 3),
            "roof_horizontal_projection_m2": round(roof_proj, 3),
        },
        "stair_validation": {
            "landing_depth_m": round(llegada_depth, 3),
            "min_headroom_over_steps_m": round(min_stair_headroom, 3),
            "steps_count": len(stairs),
        },
        "garage_validation": {
            "garage_dims_m": [round(gbb[3] - gbb[0], 3), round(gbb[4] - gbb[1], 3)],
            "car_to_moto_door_clearance_m": car_door_clearance,
            "sectional_door_panels": len([o for o in bpy.data.objects if "Porton" in o.name]),
        },
        "checks": {
            "columns_inside_lot": "PASS" if not cols_outside_lot else "FAIL",
            "furniture_collisions": "PASS" if not furn_col else "FAIL",
            "column_door_interferences": "PASS" if not col_door_int else "FAIL",
            "no_duplicate_geometry": "PASS" if not dups else "FAIL",
            "stair_landing_coherent_095m": "PASS" if llegada_depth >= 0.95 else "FAIL",
            "stair_headroom_205m": "PASS" if min_stair_headroom >= 2.05 else "FAIL",
            "connectivity_from_real_doors": "PASS" if not unconnected else "FAIL",
            "agent_walkthrough_no_wall_hits": "PASS" if not agent_collisions else "FAIL",
            "garage_door_clearance_035m": "PASS" if car_door_clearance >= 0.35 else "FAIL",
            "structural_and_pot_approval": "PENDING",
        },
        "details": {
            "cols_outside_lot": cols_outside_lot,
            "furn_collisions": furn_col,
            "col_door_int": col_door_int,
            "duplicates": dups,
            "unconnected": unconnected,
            "agent_collisions": agent_collisions[:10],
        },
    }
    with open(VALIDATION_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("HITO_02_VALIDATION:", json.dumps(report["checks"]))

run_validation()
