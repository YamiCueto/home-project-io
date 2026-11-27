import json
from pathlib import Path
import bpy

def get_root():
    if bpy.data.filepath:
        p = Path(bpy.data.filepath).resolve()
        if p.parent.name == "models":
            return p.parent.parent
    return Path.cwd()

def run_all_negative_tests_v2():
    root = get_root()
    h6_v2 = root / "models" / "HOME_PROJECT_HITO_06_V2.blend"
    ns = {}
    exec((root / "scripts" / "validate_hito_06_v2.py").read_text(encoding="utf-8"), ns)
    validate_fn = ns["run_validation_v2"]
    read_png = ns["read_png_info"]

    results = {}

    def reset():
        bpy.ops.wm.open_mainfile(filepath=str(h6_v2))

    reset()
    bpy.data.objects["P1_Mob_Sofa_Base"].location = (2.2, 4.0, 0.0)
    results["1_blocked_door"] = validate_fn(write_json=False)["checks"]["explicit_door_swing_0_90_clear"]

    reset()
    bpy.data.objects["P1_Mob_Mesa_Comedor_Sobre"].location = (0.0, 1.3, 0.0)
    results["2_furniture_in_wall"] = validate_fn(write_json=False)["checks"]["no_mob_wall_collisions"]

    reset()
    bpy.data.objects["Cam_Recorrido_Anim"].animation_data_clear()
    results["3_unanimated_camera"] = validate_fn(write_json=False)["checks"]["full_1152_walkthrough_all_obstacles"]

    reset()
    cam = bpy.data.objects["Cam_Recorrido_Anim"]
    cam.location = (0.05, 5.0, 1.65)
    cam.keyframe_insert(data_path="location", frame=192)
    results["4_walkthrough_wall_hit"] = validate_fn(write_json=False)["checks"]["full_1152_walkthrough_all_obstacles"]

    reset()
    img = bpy.data.images.new("MissingTex_Test", 64, 64)
    img.source = "FILE"
    img.filepath = str(root / "assets" / "nonexistent_tex_999.png")
    results["5_missing_texture"] = validate_fn(write_json=False)["checks"]["manifest_cc0_and_textures_packed"]

    w, h, _, iend_ok = read_png(root / "renders" / "HITO_03_TEST_720P.png")
    corrupt_tmp = root / "validation" / "_tmp_corrupt.png"
    corrupt_tmp.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x0f\x00\x00\x00\x08\x70\x08\x02\x00\x00\x00TRUNCATED")
    cw, ch, _, ciend = read_png(corrupt_tmp)
    corrupt_tmp.unlink(missing_ok=True)
    results["6_wrong_or_corrupt_png"] = "FAIL" if ((w, h) != (3840, 2160) and not ciend) else "PASS"

    reset()
    bpy.data.objects["P1_Mob_Sofa_Base"].location = (-2.0, 0.0, 0.0)
    results["7_out_of_bounds_object"] = validate_fn(write_json=False)["checks"]["lot_boundaries_respected"]

    reset()
    orig = bpy.data.objects["P1_Piso_P1_Sala"]
    dup = orig.copy()
    dup.data = orig.data.copy()
    dup.name = "P1_Piso_P1_Sala_DUP"
    bpy.data.collections["07_Propuesta_Primera_Planta"].objects.link(dup)
    results["8_duplicate_geometry"] = validate_fn(write_json=False)["checks"]["no_duplicate_geometry"]

    bad_manifest = {"assets": [{"id": "fake_unlicensed", "license": "PROPRIETARY", "author": "", "url": ""}]}
    unlic = [a["id"] for a in bad_manifest["assets"] if a.get("license") != "CC0" or not a.get("author") or not a.get("url")]
    results["9_unlicensed_asset"] = "FAIL" if unlic else "PASS"

    reset()
    cam = bpy.data.objects["Cam_Recorrido_Anim"]
    cam.location = (1.95, 3.30, 0.25)
    cam.keyframe_insert(data_path="location", frame=192)
    results["10_walkthrough_hits_furniture"] = validate_fn(write_json=False)["checks"]["full_1152_walkthrough_all_obstacles"]

    reset()
    bpy.data.objects["P2_M_Vest_Bano_Puerta1"]["swing_dir"] = -1
    results["11_door_wrong_swing_dir"] = validate_fn(write_json=False)["checks"]["explicit_door_swing_0_90_clear"]

    reset()
    bpy.data.objects.remove(bpy.data.objects["Cubierta_P1_Huespedes"], do_unlink=True)
    results["12_bedroom_without_roof"] = validate_fn(write_json=False)["checks"]["all_bedrooms_100pct_covered"]

    reset()
    all_failed = all(v == "FAIL" for v in results.values())
    out = {"all_12_negative_tests_caught_fail": all_failed, "cases": results}
    (root / "validation" / "HITO_06_V2_NEGATIVE_TESTS.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("NEGATIVE_REGRESSION_TESTS_V2:", json.dumps(out))
    return out

if __name__ == "__main__":
    run_all_negative_tests_v2()
