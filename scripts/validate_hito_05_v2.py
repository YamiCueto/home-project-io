import json
import os
import bpy

PROJECT_DIR = r"C:\Users\YAMI\Documents\projects\home-project"
OUT_DIR = os.path.join(PROJECT_DIR, "renders", "hito_05_v2")
VAL_JSON = os.path.join(PROJECT_DIR, "validation", "HITO_05_V2_VALIDATION.json")
BENCH_JSON = os.path.join(PROJECT_DIR, "validation", "HITO_05_V2_BENCHMARK.json")

EXPECTED = [
    "01_ESQUINA_DIA_4K.png",
    "02_ESQUINA_NOCHE_4K.png",
    "03_SALA_CONTEMPORANEA_4K.png",
    "04_COCINA_COMEDOR_4K.png",
    "05_SUITE_PRINCIPAL_4K.png",
    "06_CUBIERTA_FOTOVOLTAICA_4K.png",
]

def run_validation():
    missing = [r for r in EXPECTED if not os.path.exists(os.path.join(OUT_DIR, r))]
    ph_count = len([o for o in bpy.data.objects if "_PH_" in o.name or o.name.startswith("PH_")])
    urb_count = len(bpy.data.collections["17_Contexto_Urbano"].objects) if "17_Contexto_Urbano" in bpy.data.collections else 0
    linderos_hidden = all(o.hide_render for o in bpy.data.collections["01_Linderos_Provisionales"].objects)
    tv_sala = bpy.data.objects.get("P1_Mob_TV_65")
    tv_freed_window = (tv_sala.location.x > 4.0) if tv_sala else False
    bed_master = bpy.data.objects.get("P2_Mob_Cama_Master_Cabecero")
    bed_facing_street = (bed_master.location.y > 4.0) if bed_master else False

    bench = {}
    if os.path.exists(BENCH_JSON):
        with open(BENCH_JSON, "r", encoding="utf-8") as f:
            bench = json.load(f)

    report = {
        "model": "HOME_PROJECT_HITO_05_V2.blend",
        "metrics": {
            "polyhaven_objects_placed": ph_count,
            "urban_context_objects": urb_count,
            "renders_4k_present": len(EXPECTED) - len(missing),
        },
        "benchmark": bench,
        "checks": {
            "polyhaven_cc0_assets_integrated": "PASS" if ph_count >= 10 else "FAIL",
            "urban_context_separated": "PASS" if urb_count >= 10 else "FAIL",
            "lot_markers_hidden_in_commercial": "PASS" if linderos_hidden else "FAIL",
            "tv_relocated_window_freed": "PASS" if tv_freed_window else "FAIL",
            "master_bed_oriented_to_street": "PASS" if bed_facing_street else "FAIL",
            "all_6_4k_renders_generated": "PASS" if not missing else "FAIL",
            "structural_and_pot_cert": "PENDING",
        },
    }
    with open(VAL_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("HITO_05_V2_VALIDATION:", json.dumps(report["checks"]))

run_validation()
