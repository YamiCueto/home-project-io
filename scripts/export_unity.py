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
    h6_blend = root / "models" / "HOME_PROJECT_HITO_06.blend"
    bpy.ops.wm.open_mainfile(filepath=str(h6_blend))

    arch_objs = []
    for cname in ("07_Propuesta_Primera_Planta", "08_Propuesta_Segunda_Planta", "09_Estructura_Conceptual", "14_Fachadas_Y_Vegetacion"):
        arch_objs.extend([o for o in bpy.data.collections[cname].objects if o.type == "MESH" and "_Puerta" not in o.name and "_Porton" not in o.name])

    furn_objs = [o for o in list(bpy.data.collections["11_Mobiliario"].objects) + list(bpy.data.collections["10_Vehiculos"].objects) if o.type == "MESH" and not o.hide_viewport]
    door_objs = [o for o in bpy.data.objects if o.type == "MESH" and ("_Puerta" in o.name or "_Porton" in o.name)]
    urb_objs = []
    for cname in ("05_Andenes_Publicos", "06_Calles", "17_Contexto_Urbano"):
        urb_objs.extend([o for o in bpy.data.collections[cname].objects if o.type == "MESH"])

    export_fbx_group(out_dir / "architecture.fbx", arch_objs)
    export_fbx_group(out_dir / "furniture.fbx", furn_objs)
    export_fbx_group(out_dir / "interactive_doors.fbx", door_objs)
    export_fbx_group(out_dir / "urban_context.fbx", urb_objs)

    mat_manifest = []
    for m in bpy.data.materials:
        mat_manifest.append({"name": m.name, "use_nodes": m.use_nodes})
    (out_dir / "materials_manifest.json").write_text(json.dumps(mat_manifest, indent=2), encoding="utf-8")

    doors_manifest = []
    for d in door_objs:
        doors_manifest.append({
            "name": d.name,
            "pivot_location_m": [round(d.location.x, 4), round(d.location.y, 4), round(d.location.z, 4)],
            "dimensions_m": [round(d.dimensions.x, 4), round(d.dimensions.y, 4), round(d.dimensions.z, 4)],
        })
    (out_dir / "doors_pivots_manifest.json").write_text(json.dumps(doors_manifest, indent=2), encoding="utf-8")

    objs_manifest = {
        "architecture_count": len(arch_objs),
        "furniture_count": len(furn_objs),
        "interactive_doors_count": len(door_objs),
        "urban_context_count": len(urb_objs),
    }
    (out_dir / "objects_manifest.json").write_text(json.dumps(objs_manifest, indent=2), encoding="utf-8")

    expected_counts = {
        "architecture.fbx": len(arch_objs),
        "furniture.fbx": len(furn_objs),
        "interactive_doors.fbx": len(door_objs),
        "urban_context.fbx": len(urb_objs),
    }
    reimport_results = {}
    for fname, exp_cnt in expected_counts.items():
        for o in list(bpy.data.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.ops.import_scene.fbx(filepath=str(out_dir / fname))
        imp_meshes = [o for o in bpy.data.objects if o.type == "MESH"]
        reimport_results[fname] = {
            "expected_meshes": exp_cnt,
            "reimported_meshes": len(imp_meshes),
            "match": len(imp_meshes) == exp_cnt,
            "file_size_kb": round((out_dir / fname).stat().st_size / 1024.0, 2),
        }

    (out_dir / "fbx_reimport_verification.json").write_text(json.dumps(reimport_results, indent=2), encoding="utf-8")
    bpy.ops.wm.open_mainfile(filepath=str(h6_blend))
    print("UNITY_FBX_EXPORT_AND_REIMPORT_OK:", json.dumps(reimport_results))

main()
