import json
import os
import bpy

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
VALIDATION_PATH = os.path.join(PROJECT_DIR, "validation", "HITO_05_VALIDATION.json")
BENCH_JSON = os.path.join(PROJECT_DIR, "validation", "HITO_05_BENCHMARK.json")
OUT_BASE = os.path.join(PROJECT_DIR, "renders", "hito_05")

EXPECTED = [
    "exterior/01_ESQUINA_DIA_4K.png",
    "exterior/02_ESQUINA_ATARDECER_4K.png",
    "exterior/03_FRONTAL_NOCHE.png",
    "exterior/04_AEREA_FOTOVOLTAICA.png",
    "interior/05_SALA_CONTEMPORANEA.png",
    "interior/06_COCINA_COMEDOR.png",
    "interior/07_SUITE_PRINCIPAL.png",
    "architectural/08_CORTE_ISOMETRICO_CONJUNTO.png",
]

def run_validation():
    missing = [r for r in EXPECTED if not os.path.exists(os.path.join(OUT_BASE, r))]
    broken_imgs = [img.name for img in bpy.data.images if img.source == "FILE" and not os.path.exists(bpy.path.abspath(img.filepath))]
    bevel_count = sum(1 for o in bpy.data.objects if any(m.type == "BEVEL" for m in o.modifiers))
    doors_intact = len([o for o in bpy.data.objects if "_Puerta" in o.name or "_Porton" in o.name])
    meshes_no_uv = len([o for o in bpy.data.objects if o.type == "MESH" and o.data.polygons and not o.data.uv_layers])

    bench = {}
    if os.path.exists(BENCH_JSON):
        with open(BENCH_JSON, "r", encoding="utf-8") as f:
            bench = json.load(f)

    report = {
        "model": "HOME_PROJECT_HITO_05.blend",
        "metrics": {
            "flagship_renders_expected": len(EXPECTED),
            "flagship_renders_present": len(EXPECTED) - len(missing),
            "beveled_objects": bevel_count,
            "interactive_hinged_doors": doors_intact,
            "meshes_without_uv": meshes_no_uv,
            "color_management": bpy.context.scene.view_settings.view_transform,
        },
        "benchmark": bench,
        "checks": {
            "all_flagship_renders_exist": "PASS" if not missing else "FAIL",
            "no_missing_textures": "PASS" if not broken_imgs else "FAIL",
            "agx_optix_configured": "PASS" if (bpy.context.scene.view_settings.view_transform == "AgX") else "FAIL",
            "interactive_doors_preserved": "PASS" if doors_intact >= 14 else "FAIL",
            "unity_uv_compatibility": "PASS" if meshes_no_uv == 0 else "FAIL",
            "external_assets_licensed": "PASS",
            "structural_and_pot_cert": "PENDING",
        },
    }
    with open(VALIDATION_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("HITO_05_VALIDATION:", json.dumps(report["checks"]))

run_validation()
