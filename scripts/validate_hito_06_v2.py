import hashlib
import json
import math
import struct
from collections import deque
from pathlib import Path
import bpy
from mathutils import Euler, Matrix, Vector

def get_root():
    if bpy.data.filepath:
        p = Path(bpy.data.filepath).resolve()
        if p.parent.name == "models":
            return p.parent.parent
    return Path.cwd()

def bbox_eval(obj, depsgraph):
    ev = obj.evaluated_get(depsgraph)
    pts = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
    return (
        min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts),
        max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts),
    )

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

def intersect_rect_with_union(rect, union_rects):
    clipped = []
    for ur in union_rects:
        ix0 = max(rect[0], ur[0])
        iy0 = max(rect[1], ur[1])
        ix1 = min(rect[3], ur[3])
        iy1 = min(rect[4], ur[4])
        if (ix1 - ix0) > 1e-5 and (iy1 - iy0) > 1e-5:
            clipped.append((ix0, iy0, 0.0, ix1, iy1, 0.0))
    return union_area_2d(clipped)

def rotated_door_bbox(door_obj, angle_rad):
    mw = door_obj.matrix_world.copy()
    pivot = door_obj.location.copy()
    rot_m = Matrix.Translation(pivot) @ Euler((0.0, 0.0, angle_rad), "XYZ").to_matrix().to_4x4() @ Matrix.Translation(-pivot)
    pts = [rot_m @ (mw @ Vector(c)) for c in door_obj.bound_box]
    return (
        min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts),
        max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts),
    )

def read_png_info(path):
    data = path.read_bytes()
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None, None, None, False
    w, h = struct.unpack(">II", data[16:24])
    has_iend = data.endswith(b"\x00\x00\x00\x00IEND\xaeB`\x82")
    sha = hashlib.sha256(data).hexdigest()
    return w, h, sha, has_iend

def run_validation_v2(write_json=True):
    root = get_root()
    depsgraph = bpy.context.evaluated_depsgraph_get()

    p1_floors = [o for o in bpy.data.collections["07_Propuesta_Primera_Planta"].objects if o.name.startswith("P1_Piso_")]
    p2_floors = [o for o in bpy.data.collections["08_Propuesta_Segunda_Planta"].objects if o.name.startswith("P2_Piso_")]
    p2_slabs = [o for o in bpy.data.collections["09_Estructura_Conceptual"].objects if o.name.startswith("P2_Losa_")]
    roofs = [o for o in bpy.data.objects if o.name.startswith("Cubierta_") and o.type == "MESH"]
    cols = [o for o in bpy.data.collections["09_Estructura_Conceptual"].objects if o.name.startswith("Col_")]
    beams = [o for o in bpy.data.collections["09_Estructura_Conceptual"].objects if o.name.startswith("Viga_")]
    railings = [o for o in bpy.data.objects if "Baranda" in o.name and o.type == "MESH"]
    walls_solid = [o for o in list(bpy.data.collections["07_Propuesta_Primera_Planta"].objects) + list(bpy.data.collections["08_Propuesta_Segunda_Planta"].objects) if o.type == "MESH" and "_Puerta" not in o.name and "_Porton" not in o.name and "_Win" not in o.name and (o.name.split("_")[-1].startswith("S") or "_Sill" in o.name or "_Lint" in o.name)]
    doors = [o for o in bpy.data.objects if "_Puerta" in o.name and o.type == "MESH" and not o.name.startswith("Veh_")]
    mob = [o for o in bpy.data.collections["11_Mobiliario"].objects if o.type == "MESH" and not o.hide_viewport]
    vehs = [o for o in bpy.data.collections["10_Vehiculos"].objects if o.type == "MESH"]
    stairs = [o for o in bpy.data.collections["07_Propuesta_Primera_Planta"].objects if o.name.startswith("P1_Esc_Peldano_")]

    upper_cover_rects = [bbox_eval(o, depsgraph) for o in (p2_slabs + roofs)]
    p1_covered_net = 0.0
    p1_uncovered_net = 0.0
    bedrooms_uncovered = []
    for rf in p1_floors:
        rbb = bbox_eval(rf, depsgraph)
        r_area = (rbb[3] - rbb[0]) * (rbb[4] - rbb[1])
        cov_area = intersect_rect_with_union(rbb, upper_cover_rects)
        uncov_area = max(0.0, r_area - cov_area)
        p1_covered_net += cov_area
        p1_uncovered_net += uncov_area
        if "Habitacion" in rf.name and uncov_area > 0.05:
            bedrooms_uncovered.append((rf.name, round(uncov_area, 3)))

    for rf in p2_floors:
        if "Habitacion" in rf.name:
            rbb = bbox_eval(rf, depsgraph)
            r_area = (rbb[3] - rbb[0]) * (rbb[4] - rbb[1])
            cov_area = intersect_rect_with_union(rbb, [bbox_eval(r, depsgraph) for r in roofs])
            if (r_area - cov_area) > 0.05:
                bedrooms_uncovered.append((rf.name, round(r_area - cov_area, 3)))

    p1_total_net = union_area_2d([bbox_eval(o, depsgraph) for o in p1_floors])
    p2_total_net = union_area_2d([bbox_eval(o, depsgraph) for o in p2_floors])
    p2_slab_proj = union_area_2d([bbox_eval(o, depsgraph) for o in p2_slabs])
    p2_roof_objs = [r for r in roofs if r.name == "Cubierta_Plana_Superior"]
    p2_roof_proj = union_area_2d([bbox_eval(o, depsgraph) for o in p2_roof_objs])
    roof_proj = union_area_2d([bbox_eval(o, depsgraph) for o in roofs])

    all_rooms = p1_floors + p2_floors
    adj = {r.name: set() for r in all_rooms}
    for d in doors:
        dbb = bbox_eval(d, depsgraph)
        exp = (dbb[0] - 0.18, dbb[1] - 0.18, dbb[2] - 0.15, dbb[3] + 0.18, dbb[4] + 0.18, dbb[5] + 0.15)
        if any(overlap_3d(dbb, bbox_eval(m, depsgraph)) for m in mob if "Tapete" not in m.name):
            continue
        touching = [r.name for r in all_rooms if overlap_3d(exp, bbox_eval(r, depsgraph))]
        for i in range(len(touching)):
            for j in range(i + 1, len(touching)):
                adj[touching[i]].add(touching[j])
                adj[touching[j]].add(touching[i])

    for i in range(len(all_rooms)):
        for j in range(i + 1, len(all_rooms)):
            ra, rb = all_rooms[i], all_rooms[j]
            ba, bb = bbox_eval(ra, depsgraph), bbox_eval(rb, depsgraph)
            if abs(ba[2] - bb[2]) > 0.5:
                continue
            exp_a = (ba[0] - 0.12, ba[1] - 0.12, ba[2], ba[3] + 0.12, ba[4] + 0.12, ba[5] + 1.5)
            if overlap_3d(exp_a, bb):
                mid_x = (max(ba[0], bb[0]) + min(ba[3], bb[3])) * 0.5
                mid_y = (max(ba[1], bb[1]) + min(ba[4], bb[4])) * 0.5
                probe = (mid_x - 0.22, mid_y - 0.22, ba[2] + 0.2, mid_x + 0.22, mid_y + 0.22, ba[2] + 1.5)
                if not any(overlap_3d(probe, bbox_eval(w, depsgraph)) for w in walls_solid):
                    adj[ra.name].add(rb.name)
                    adj[rb.name].add(ra.name)

    if stairs:
        s_first = min(stairs, key=lambda s: bbox_eval(s, depsgraph)[0])
        s_last = max(stairs, key=lambda s: bbox_eval(s, depsgraph)[0])
        sf_bb = bbox_eval(s_first, depsgraph)
        sl_bb = bbox_eval(s_last, depsgraph)
        p1_esc = [r.name for r in p1_floors if overlap_2d((sf_bb[0] - 0.2, sf_bb[1] - 0.2, 0, sf_bb[3] + 0.2, sf_bb[4] + 0.2, 1), bbox_eval(r, depsgraph))]
        p2_lleg = [r.name for r in p2_floors if overlap_2d((sl_bb[0] - 0.2, sl_bb[1] - 0.2, 0, sl_bb[3] + 0.2, sl_bb[4] + 0.2, 1), bbox_eval(r, depsgraph))]
        for a in p1_esc:
            for b in p2_lleg:
                adj[a].add(b)
                adj[b].add(a)

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

    door_swing_collisions = []
    mob_solid = [m for m in mob if "Tapete" not in m.name]
    for d in doors:
        sdir = d.get("swing_dir", None)
        if sdir not in (1, -1):
            door_swing_collisions.append((d.name, 0, "MISSING_SWING_DIR"))
            continue
        for deg in (0, 30, 60, 90):
            rbb = rotated_door_bbox(d, math.radians(deg * sdir))
            for obs in mob_solid + cols:
                if overlap_3d(rbb, bbox_eval(obs, depsgraph)):
                    door_swing_collisions.append((d.name, deg * sdir, obs.name))

    mob_wall_collisions = []
    for m in mob:
        mbb = bbox_eval(m, depsgraph)
        for w in walls_solid:
            if overlap_3d(mbb, bbox_eval(w, depsgraph), tol=0.015):
                mob_wall_collisions.append((m.name, w.name))

    anim_cam = bpy.data.objects.get("Cam_Recorrido_Anim")
    has_anim = bool(anim_cam and anim_cam.animation_data and anim_cam.animation_data.action)
    walk_collisions = []
    walk_unsupported = []
    walk_obstacles = walls_solid + cols + beams + railings + mob_solid
    if has_anim:
        prev_loc = None
        for f in range(0, 1153):
            bpy.context.scene.frame_set(f)
            loc = anim_cam.matrix_world.translation.copy()
            steps_n = 1 if prev_loc is None else max(1, int((loc - prev_loc).length / 0.10))
            for s in range(1, steps_n + 1):
                pt = loc if prev_loc is None else prev_loc.lerp(loc, s / steps_n)
                abb = (pt.x - 0.18, pt.y - 0.18, pt.z - 1.25, pt.x + 0.18, pt.y + 0.18, pt.z + 0.15)
                for obs in walk_obstacles:
                    if overlap_3d(abb, bbox_eval(obs, depsgraph)):
                        walk_collisions.append((f, obs.name))
                if 0.0 <= pt.x <= 8.0 and 0.0 <= pt.y <= 11.25:
                    foot_z = pt.z - 1.65
                    supported = any(
                        (bbox_eval(fl, depsgraph)[0] - 0.35 <= pt.x <= bbox_eval(fl, depsgraph)[3] + 0.35) and
                        (bbox_eval(fl, depsgraph)[1] - 0.35 <= pt.y <= bbox_eval(fl, depsgraph)[4] + 0.35) and
                        (abs(bbox_eval(fl, depsgraph)[5] - foot_z) <= 0.35)
                        for fl in (all_rooms + stairs)
                    )
                    if not supported:
                        walk_unsupported.append(f)
            prev_loc = loc

    car_door_cond = bpy.data.objects.get("Veh_Swift_Puerta_Cond")
    car_door_pas = bpy.data.objects.get("Veh_Swift_Puerta_Pas")
    car_door_hits = []
    vstrom_objs = [v for v in vehs if "VStrom" in v.name]
    if car_door_cond and car_door_pas:
        for deg in (15, 35, 55):
            rbb_c = rotated_door_bbox(car_door_cond, math.radians(deg))
            for obs in vstrom_objs + walls_solid + cols:
                if overlap_3d(rbb_c, bbox_eval(obs, depsgraph)):
                    car_door_hits.append(("Cond", deg, obs.name))
        for deg in (15, 25):
            rbb_p = rotated_door_bbox(car_door_pas, math.radians(-deg))
            for obs in vstrom_objs + walls_solid + cols:
                if overlap_3d(rbb_p, bbox_eval(obs, depsgraph)):
                    car_door_hits.append(("Pas", deg, obs.name))
    else:
        car_door_hits.append(("MISSING_CAR_DOORS", 0, "NONE"))

    tv = bpy.data.objects.get("P1_Mob_TV_65")
    win_sala = bpy.data.objects.get("P1_M_Sur_Sala_Win3_Glass")
    tv_ok = False
    if tv and win_sala:
        tbb, wbb = bbox_eval(tv, depsgraph), bbox_eval(win_sala, depsgraph)
        tv_blocks = (min(tbb[3], wbb[3]) - max(tbb[0], wbb[0])) > 0.01 and (min(tbb[4], wbb[4]) - max(tbb[1], wbb[1])) > 0.01
        tv_ok = not tv_blocks

    cab = bpy.data.objects.get("P2_Mob_Cama_Master_Cabecero")
    colchon = bpy.data.objects.get("P2_Mob_Cama_Master_Colchon")
    bed_dot = 0.0
    if cab and colchon:
        c_pos = Vector(((bbox_eval(cab, depsgraph)[0] + bbox_eval(cab, depsgraph)[3]) * 0.5, (bbox_eval(cab, depsgraph)[1] + bbox_eval(cab, depsgraph)[4]) * 0.5, 0.0))
        m_pos = Vector(((bbox_eval(colchon, depsgraph)[0] + bbox_eval(colchon, depsgraph)[3]) * 0.5, (bbox_eval(colchon, depsgraph)[1] + bbox_eval(colchon, depsgraph)[4]) * 0.5, 0.0))
        bed_dot = round((m_pos - c_pos).normalized().dot(Vector((0.0, -1.0, 0.0))), 4)

    renders_dir = root / "renders" / "hito_05_v2"
    render_checks = {}
    all_4k_ok = True
    for fname in ["01_ESQUINA_DIA_4K.png", "02_ESQUINA_NOCHE_4K.png", "03_SALA_CONTEMPORANEA_4K.png", "04_COCINA_COMEDOR_4K.png", "05_SUITE_PRINCIPAL_4K.png", "06_CUBIERTA_FOTOVOLTAICA_4K.png"]:
        p = renders_dir / fname
        if p.exists():
            w, h, sha, has_iend = read_png_info(p)
            ok = (w == 3840 and h == 2160 and has_iend)
            if not ok:
                all_4k_ok = False
            render_checks[fname] = {"width": w, "height": h, "has_iend": has_iend, "sha256": sha, "ok": ok}
        else:
            all_4k_ok = False
            render_checks[fname] = {"ok": False}

    manifest_path = root / "assets" / "manifest.json"
    manifest_ok = False
    unlicensed = []
    if manifest_path.exists():
        mdata = json.loads(manifest_path.read_text(encoding="utf-8"))
        assets = mdata.get("assets", [])
        unlicensed = [a["id"] for a in assets if a.get("license") != "CC0" or not a.get("author") or not a.get("url")]
        manifest_ok = (len(assets) >= 9 and not unlicensed)
    missing_imgs = [img.name for img in bpy.data.images if img.source == "FILE" and not img.packed_file and not Path(bpy.path.abspath(img.filepath)).exists()]

    lot_violations = []
    for colname in ("07_Propuesta_Primera_Planta", "08_Propuesta_Segunda_Planta", "09_Estructura_Conceptual", "10_Vehiculos", "11_Mobiliario"):
        for o in bpy.data.collections[colname].objects:
            if o.type == "MESH" and not o.hide_viewport:
                obb = bbox_eval(o, depsgraph)
                if obb[0] < -0.02 or obb[1] < -0.02 or obb[3] > 8.02 or obb[4] > 11.27:
                    lot_violations.append(o.name)

    sig_map = {}
    dups = []
    for colname in ("07_Propuesta_Primera_Planta", "08_Propuesta_Segunda_Planta"):
        for o in bpy.data.collections[colname].objects:
            if o.type == "MESH":
                bb = bbox_eval(o, depsgraph)
                sig = (len(o.data.vertices), round(bb[0], 3), round(bb[1], 3), round(bb[2], 3), round(bb[3], 3), round(bb[4], 3), round(bb[5], 3))
                if sig in sig_map:
                    dups.append((sig_map[sig], o.name))
                else:
                    sig_map[sig] = o.name

    report = {
        "model": "HOME_PROJECT_HITO_06_V2.blend",
        "areas_evaluated_m2": {
            "p1_total_floors_net_m2": round(p1_total_net, 3),
            "p1_covered_by_upper_or_p1_roof_net_m2": round(p1_covered_net, 3),
            "p1_uncovered_net_m2": round(p1_uncovered_net, 3),
            "p1_excess_over_60m2_if_all_covered_counted": round(max(0.0, p1_covered_net - 60.0), 3),
            "p2_floors_net_m2": round(p2_total_net, 3),
            "p2_slab_projection_m2": round(p2_slab_proj, 3),
            "roof_projection_m2": round(roof_proj, 3),
        },
        "checks": {
            "all_bedrooms_100pct_covered": "PASS" if not bedrooms_uncovered else "FAIL",
            "p2_roof_within_80m2": "PASS" if (p2_roof_objs and p2_roof_proj <= 80.05) else "FAIL",
            "full_1152_walkthrough_all_obstacles": "PASS" if (has_anim and not walk_collisions and not walk_unsupported) else "FAIL",
            "car_doors_swing_no_hit": "PASS" if not car_door_hits else "FAIL",
            "physical_doorway_connectivity": "PASS" if not unconnected else "FAIL",
            "explicit_door_swing_0_90_clear": "PASS" if not door_swing_collisions else "FAIL",
            "no_mob_wall_collisions": "PASS" if not mob_wall_collisions else "FAIL",
            "tv_window_clear_and_bed_vector": "PASS" if (tv_ok and bed_dot >= 0.9) else "FAIL",
            "all_6_4k_png_ihdr_iend_valid": "PASS" if all_4k_ok else "FAIL",
            "manifest_cc0_and_textures_packed": "PASS" if (manifest_ok and not missing_imgs) else "FAIL",
            "lot_boundaries_respected": "PASS" if not lot_violations else "FAIL",
            "no_duplicate_geometry": "PASS" if not dups else "FAIL",
            "structural_electrical_pot_cert": "PENDING",
        },
        "details": {
            "bedrooms_uncovered": bedrooms_uncovered,
            "car_door_hits": car_door_hits[:10],
            "walk_collisions": walk_collisions[:10],
            "walk_unsupported_frames": walk_unsupported[:10],
            "door_swing_collisions": door_swing_collisions[:10],
            "mob_wall_collisions": mob_wall_collisions[:10],
            "unconnected": unconnected,
            "lot_violations": lot_violations[:10],
            "duplicates": dups,
            "missing_imgs": missing_imgs,
            "renders_4k": render_checks,
        },
    }

    if write_json:
        (root / "validation" / "HITO_06_V2_VALIDATION.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report

if __name__ == "__main__":
    res = run_validation_v2(write_json=True)
    print("HITO_06_V2_VALIDATION:", json.dumps(res["checks"]))
