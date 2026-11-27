import json
from pathlib import Path
import bpy

def get_root():
    if bpy.data.filepath:
        p = Path(bpy.data.filepath).resolve()
        if p.parent.name == "models":
            return p.parent.parent
    return Path.cwd()

def bootstrap():
    root = get_root()
    manifest_path = root / "assets" / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(str(manifest_path))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    packed_imgs = [img.name for img in bpy.data.images if img.packed_file is not None]
    missing_objs = []
    for item in manifest.get("assets", []):
        for target in item.get("used_in", []):
            if target != "World_Hito3" and bpy.data.objects.get(target) is None:
                if not any(o.name.startswith(target) for o in bpy.data.objects):
                    missing_objs.append(target)
    report = {
        "manifest_assets_count": len(manifest.get("assets", [])),
        "packed_images_count": len(packed_imgs),
        "missing_scene_targets": missing_objs,
        "reproducible": len(missing_objs) == 0,
    }
    print("BOOTSTRAP_REPORT:", json.dumps(report))
    return report

if __name__ == "__main__":
    bootstrap()
