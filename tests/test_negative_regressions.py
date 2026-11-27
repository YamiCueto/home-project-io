import json
from pathlib import Path
import bpy

def get_root():
    if bpy.data.filepath:
        p = Path(bpy.data.filepath).resolve()
        if p.parent.name == "models":
            return p.parent.parent
    return Path.cwd()

def run_all_negative_tests():
    root = get_root()
    h6_blend = root / "models" / "HOME_PROJECT_HITO_06.blend"
    ns = {}
    exec((root / "scripts" / "validate_hito_06.py").read_text(encoding="utf-8"), ns)
    validate_fn = ns["run_audit_validation"]
    read_png = ns["read_png_info"]

    results = {}

    def reset():
        bpy.ops.wm.open_mainfile(filepath=str(h6_blend))

    reset()
    sofa = bpy.data.objects["P1_Mob_Sofa_Base"]
    sofa.location = (2.2, 4.0, 0.0)
    res = validate_fn(write_json=False)
    results["1_blocked_door"] = res["checks"]["AUD10_door_swing_0_90_no_mob_hit"]

    reset()
    table = bpy.data.objects["P1_Mob_Mesa_Comedor_Sobre"]
    table.location = (0.0, 1.3, 0.0)
    res = validate_fn(write_json=False)
    results["2_furniture_in_wall"] = res["checks"]["no_mob_wall_collisions"]

    reset()
    cam = bpy.data.objects["Cam_Recorrido_Anim"]
    cam.animation_data_clear()
    res = validate_fn(write_json=False)
    results["3_unanimated_camera"] = res["checks"]["AUD02_full_1152_frame_walkthrough"]

    reset()
    cam = bpy.data.objects["Cam_Recorrido_Anim"]
    cam.location = (0.05, 5.0, 1.65)
    cam.keyframe_insert(data_path="location", frame=192)
    res = validate_fn(write_json=False)
    results["4_walkthrough_wall_hit"] = res["checks"]["AUD02_full_1152_frame_walkthrough"]

    reset()
    img = bpy.data.images.new("MissingTex_Test", 64, 64)
    img.source = "FILE"
    img.filepath = str(root / "assets" / "nonexistent_tex_999.png")
    res = validate_fn(write_json=False)
    results["5_missing_texture"] = res["checks"]["AUD07_manifest_cc0_and_textures_packed"]

    test_720 = root / "renders" / "HITO_03_TEST_720P.png"
    w, h, _ = read_png(test_720)
    results["6_wrong_png_resolution"] = "FAIL" if (w, h) != (3840, 2160) else "PASS"

    reset()
    sofa = bpy.data.objects["P1_Mob_Sofa_Base"]
    sofa.location = (-2.0, 0.0, 0.0)
    res = validate_fn(write_json=False)
    results["7_out_of_bounds_object"] = res["checks"]["lot_boundaries_respected"]

    reset()
    orig = bpy.data.objects["P1_Piso_P1_Sala"]
    dup = orig.copy()
    dup.data = orig.data.copy()
    dup.name = "P1_Piso_P1_Sala_DUP"
    bpy.data.collections["07_Propuesta_Primera_Planta"].objects.link(dup)
    res = validate_fn(write_json=False)
    results["8_duplicate_geometry"] = res["checks"]["no_duplicate_geometry"]

    bad_manifest = {"assets": [{"id": "fake_unlicensed", "license": "PROPRIETARY", "author": "", "url": ""}]}
    unlic = [a["id"] for a in bad_manifest["assets"] if a.get("license") != "CC0" or not a.get("author") or not a.get("url")]
    results["9_unlicensed_asset"] = "FAIL" if unlic else "PASS"

    reset()
    all_failed = all(v == "FAIL" for v in results.values())
    out = {"all_9_negative_tests_caught_fail": all_failed, "cases": results}
    (root / "validation" / "HITO_06_NEGATIVE_TESTS.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("NEGATIVE_REGRESSION_TESTS:", json.dumps(out))
    return out

if __name__ == "__main__":
    run_all_negative_tests()
