import json
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
    out_dir.mkdir(parents=True, exist_ok=True)
    h6_v2_blend = root / "models" / "HOME_PROJECT_HITO_06_V2.blend"
    bpy.ops.wm.open_mainfile(filepath=str(h6_v2_blend))

    arch_objs = []
    for cname in ("07_Propuesta_Primera_Planta", "08_Propuesta_Segunda_Planta", "09_Estructura_Conceptual", "14_Fachadas_Y_Vegetacion"):
        arch_objs.extend([o for o in bpy.data.collections[cname].objects if o.type == "MESH" and "_Puerta" not in o.name and "_Porton" not in o.name])

    furn_objs = [o for o in list(bpy.data.collections["11_Mobiliario"].objects) + list(bpy.data.collections["10_Vehiculos"].objects) if o.type == "MESH" and not o.hide_viewport]
    door_objs = [o for o in bpy.data.objects if o.type == "MESH" and ("_Puerta" in o.name or "_Porton" in o.name) and not o.name.startswith("Veh_")]
    inst_objs = [o for o in bpy.data.collections["16_Instalaciones_Domotica"].objects if o.type == "MESH"]
    urb_objs = []
    for cname in ("05_Andenes_Publicos", "06_Calles", "17_Contexto_Urbano"):
        urb_objs.extend([o for o in bpy.data.collections[cname].objects if o.type == "MESH"])

    col_temp = bpy.data.collections.new("_Temp_Colliders")
    bpy.context.scene.collection.children.link(col_temp)
    collider_objs = []
    for o in arch_objs:
        if any(k in o.name for k in ("_Piso_", "_S", "P2_Losa_", "Cubierta_")):
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

    mat_tex_manifest = []
    for m in bpy.data.materials:
        texs = []
        if m.use_nodes and m.node_tree:
            for n in m.node_tree.nodes:
                if n.type == "TEX_IMAGE" and n.image:
                    texs.append({"image": n.image.name, "packed": n.image.packed_file is not None})
        mat_tex_manifest.append({"material": m.name, "textures": texs})
    (out_dir / "materials_textures_manifest.json").write_text(json.dumps(mat_tex_manifest, indent=2), encoding="utf-8")

    reimport_v2 = {}
    for fname, ostats in orig_stats.items():
        for o in list(bpy.data.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.ops.import_scene.fbx(filepath=str(out_dir / fname))
        imp_objs = [o for o in bpy.data.objects if o.type == "MESH"]
        istats = scene_stats(imp_objs)
        dim_diff = [round(abs(ostats["dims_m"][i] - istats["dims_m"][i]), 3) for i in range(3)]
        reimport_v2[fname] = {
            "original": ostats,
            "reimported": istats,
            "mesh_count_match": ostats["meshes"] == istats["meshes"],
            "dims_match_within_2cm": max(dim_diff) <= 0.02,
            "dim_diff_m": dim_diff,
            "file_size_kb": round((out_dir / fname).stat().st_size / 1024.0, 2),
        }

    (out_dir / "fbx_reimport_verification_v2.json").write_text(json.dumps(reimport_v2, indent=2), encoding="utf-8")
    bpy.ops.wm.open_mainfile(filepath=str(h6_v2_blend))
    print("UNITY_V2_EXPORT_OK:", json.dumps({k: {"mesh_match": v["mesh_count_match"], "dims_match": v["dims_match_within_2cm"]} for k, v in reimport_v2.items()}))

if __name__ == "__main__":
    main()
