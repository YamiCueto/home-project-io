import json
import math
import shutil
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

def get_root():
    if bpy.data.filepath:
        p = Path(bpy.data.filepath).resolve()
        if p.parent.name == "models":
            return p.parent.parent
    return Path.cwd()

def scene_stats(objs):
    meshes = [o for o in objs if o.type == "MESH"]
    tris = 0
    mats = set()
    xs, ys, zs = [], [], []
    for o in meshes:
        for p in o.data.polygons:
            tris += max(1, len(p.vertices) - 2)
        for m in o.data.materials:
            if m:
                mats.add(m.name)
        for c in o.bound_box:
            wc = o.matrix_world @ Vector(c)
            xs.append(wc.x)
            ys.append(wc.y)
            zs.append(wc.z)
    dims = [round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3), round(max(zs) - min(zs), 3)] if xs else [0, 0, 0]
    return {"meshes": len(meshes), "triangles": tris, "materials": len(mats), "dims_m": dims}

def export_fbx_group(filepath, objs):
    vis_objs = [o for o in objs if not o.hide_viewport]
    if not vis_objs:
        return
    with bpy.context.temp_override(selected_objects=vis_objs, active_object=vis_objs[0]):
        bpy.ops.export_scene.fbx(
            filepath=str(filepath),
            use_selection=True,
            apply_scale_options="FBX_SCALE_UNITS",
            axis_forward="-Z",
            axis_up="Y",
            object_types={"MESH"},
            mesh_smooth_type="FACE",
            path_mode="COPY",
            embed_textures=True,
        )

def main():
    root = get_root()
    out_dir = root / "exports" / "unity"
    unity_home = root / "unity" / "Assets" / "HomeProject"
    out_dir.mkdir(parents=True, exist_ok=True)
    h6_v3_blend = root / "models" / "HOME_PROJECT_HITO_08_3_FIXES.blend"
    bpy.ops.wm.open_mainfile(filepath=str(h6_v3_blend))

    arch_objs = []
    for cname in ("07_Propuesta_Primera_Planta", "08_Propuesta_Segunda_Planta", "09_Estructura_Conceptual", "14_Fachadas_Y_Vegetacion"):
        arch_objs.extend([o for o in bpy.data.collections[cname].objects if o.type == "MESH" and "_Puerta" not in o.name and "_Porton1" not in o.name])

    furn_objs = [o for o in list(bpy.data.collections["11_Mobiliario"].objects) + list(bpy.data.collections["10_Vehiculos"].objects) if o.type == "MESH" and not o.hide_viewport]
    door_objs = [o for o in bpy.data.objects if o.type == "MESH" and ("_Puerta" in o.name or "_Porton1" in o.name) and not o.name.startswith("Veh_")]
    inst_objs = [o for o in bpy.data.collections["16_Instalaciones_Domotica"].objects if o.type == "MESH"]
    urb_objs = []
    for cname in ("05_Andenes_Publicos", "06_Calles", "17_Contexto_Urbano"):
        urb_objs.extend([o for o in bpy.data.collections[cname].objects if o.type == "MESH"])

    door_pivots = []
    for d in sorted(door_objs, key=lambda x: x.name):
        pts = [d.matrix_world @ Vector(c) for c in d.bound_box]
        dims = [
            round(max(p.x for p in pts) - min(p.x for p in pts), 4),
            round(max(p.y for p in pts) - min(p.y for p in pts), 4),
            round(max(p.z for p in pts) - min(p.z for p in pts), 4),
        ]
        door_pivots.append({
            "name": d.name,
            "pivot_location_m": [round(d.location.x, 4), round(d.location.y, 4), round(d.location.z, 4)],
            "dimensions_m": dims,
        })
    (out_dir / "doors_pivots_manifest.json").write_text(json.dumps(door_pivots, indent=2), encoding="utf-8")

    obj_records = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        bbox_world = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        xs = [v.x for v in bbox_world]
        ys = [v.y for v in bbox_world]
        zs = [v.z for v in bbox_world]
        center_w = [(min(xs)+max(xs))*0.5, (min(ys)+max(ys))*0.5, (min(zs)+max(zs))*0.5]
        loc, rot, scale = obj.matrix_world.decompose()
        rot_euler_deg = [round(math.degrees(a), 3) for a in rot.to_euler("XYZ")]
        cols = [c.name for c in obj.users_collection]
        mats = [m.name if m else None for m in obj.data.materials]
        tri_count = sum(max(0, len(p.vertices) - 2) for p in obj.data.polygons)
        obj_records.append({
            "name": obj.name,
            "collections": cols,
            "location_blender": [round(loc.x, 5), round(loc.y, 5), round(loc.z, 5)],
            "rotation_euler_deg_blender": rot_euler_deg,
            "scale_blender": [round(scale.x, 5), round(scale.y, 5), round(scale.z, 5)],
            "world_center_blender": [round(center_w[0], 5), round(center_w[1], 5), round(center_w[2], 5)],
            "world_min_blender": [round(min(xs), 5), round(min(ys), 5), round(min(zs), 5)],
            "world_max_blender": [round(max(xs), 5), round(max(ys), 5), round(max(zs), 5)],
            "size_blender": [round(max(xs)-min(xs), 5), round(max(ys)-min(ys), 5), round(max(zs)-min(zs), 5)],
            "triangles": tri_count,
            "materials": mats,
            "visible_viewport": not obj.hide_viewport,
            "visible_render": not obj.hide_render,
        })
    (out_dir / "blender_reference_manifest.json").write_text(json.dumps({"blend_file": str(h6_v3_blend), "objects": obj_records}, indent=2), encoding="utf-8")

    col_temp = bpy.data.collections.new("_Temp_Colliders")
    bpy.context.scene.collection.children.link(col_temp)
    collider_objs = []
    for o in arch_objs:
        if any(k in o.name for k in ("_Piso_", "_S", "P2_Losa_", "Cubierta_", "Fach_Murete_", "Esc_Baranda_")):
            pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
            x0, y0, z0 = min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)
            x1, y1, z1 = max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)
            mesh = bpy.data.meshes.new(f"COL_{o.name}")
            co = bpy.data.objects.new(f"COL_{o.name}", mesh)
            col_temp.objects.link(co)
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            for v in bm.verts:
                v.co.x = v.co.x * (x1 - x0) + (x0 + x1) * 0.5
                v.co.y = v.co.y * (y1 - y0) + (y0 + y1) * 0.5
                v.co.z = v.co.z * (z1 - z0) + (z0 + z1) * 0.5
            bm.to_mesh(mesh)
            bm.free()
            collider_objs.append(co)

    groups = {
        "architecture.fbx": arch_objs,
        "furniture.fbx": furn_objs,
        "interactive_doors.fbx": door_objs,
        "installations.fbx": inst_objs,
        "urban_context.fbx": urb_objs,
        "colliders.fbx": collider_objs,
    }

    orig_stats = {}
    for fname, objs in groups.items():
        orig_stats[fname] = scene_stats(objs)
        export_fbx_group(out_dir / fname, objs)

    shutil.copy2(out_dir / "architecture.fbx", unity_home / "Architecture" / "architecture.fbx")
    shutil.copy2(out_dir / "interactive_doors.fbx", unity_home / "Architecture" / "interactive_doors.fbx")
    shutil.copy2(out_dir / "furniture.fbx", unity_home / "Furniture" / "furniture.fbx")
    shutil.copy2(out_dir / "installations.fbx", unity_home / "Installations" / "installations.fbx")
    shutil.copy2(out_dir / "urban_context.fbx", unity_home / "Environment" / "urban_context.fbx")
    shutil.copy2(out_dir / "colliders.fbx", unity_home / "Colliders" / "colliders.fbx")
    shutil.copy2(out_dir / "blender_reference_manifest.json", unity_home / "Settings" / "blender_reference_manifest.json")
    shutil.copy2(out_dir / "doors_pivots_manifest.json", unity_home / "Settings" / "doors_pivots_manifest.json")

    reimport_v3 = {}
    for fname, ostats in orig_stats.items():
        for o in list(bpy.data.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.ops.import_scene.fbx(filepath=str(out_dir / fname))
        imp_objs = [o for o in bpy.data.objects if o.type == "MESH"]
        istats = scene_stats(imp_objs)
        dim_diff = [round(abs(ostats["dims_m"][i] - istats["dims_m"][i]), 3) for i in range(3)]
        reimport_v3[fname] = {
            "original": ostats,
            "reimported": istats,
            "mesh_count_match": ostats["meshes"] == istats["meshes"],
            "dims_match_within_2cm": max(dim_diff) <= 0.02,
            "dim_diff_m": dim_diff,
            "file_size_kb": round((out_dir / fname).stat().st_size / 1024.0, 2),
        }

    (out_dir / "fbx_reimport_verification_v3.json").write_text(json.dumps(reimport_v3, indent=2), encoding="utf-8")
    bpy.ops.wm.open_mainfile(filepath=str(h6_v3_blend))
    print("UNITY_V3_EXPORT_OK:", json.dumps({k: {"mesh_match": v["mesh_count_match"], "dims_match": v["dims_match_within_2cm"]} for k, v in reimport_v3.items()}))

if __name__ == "__main__":
    main()


