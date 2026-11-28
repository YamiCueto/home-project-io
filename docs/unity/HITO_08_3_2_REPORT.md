# Informe Técnico — Hito 8.3.2: Optimización Arquitectónica, Habitabilidad e Inspección Espacial

## 1. Resumen Ejecutivo

- **Rama:** `feature/hito-08-3-2-spatial-optimization`
- **Modelo Blender:** `models/HOME_PROJECT_HITO_08_3_2.blend`
- **Motor y pipeline:** Unity `6000.6.11f1` + `UniversalRenderPipelineAsset` (`URP 17.6.0 Forward+, HDR, MSAA 4x, SSAO, Shadows 4096`)
- **Modo de inicio en Unity:** `InspectionMode.ArchitectureOnly` (vivienda vacía por defecto, alternable con `M`).

---

## 2. Correcciones Arquitectónicas Implementadas

- **P1-01 (Baño Social):** Eliminación del vacío residual de `2,60 m²` al norte del baño social e integración completa, pasando de `3,61 m²` a **`6,27 m²`** (`1,90 × 3,30 m`) con ducha sin desnivel y circulación accesible.
- **P2-02 (Suite Principal):** Eliminación del balcón esquinero (`4,875 m²`) y consolidación de la secuencia **Dormitorio Principal (`19,575 m²`) → Vestier de paso (`6,525 m²`, `1,45 × 4,50 m`) → Baño Principal (`7,650 m²`, `1,70 × 4,50 m`)**, manteniendo la huella de segunda planta en `80,00 m²` y actualizando la fachada sur (`P2_M_Sur_Win3_*`, `Fach_Marco_P2_Sur`).
- **Zonas residenciales:** Actualización de `18` a **`17` zonas** en `ResidentialZoneTracker.cs` y `ResidentialNavigationAgent.cs`.

---

## 3. Validaciones y Pruebas (Tras la Última Edición)

- **Validación Blender (`validation/HITO_08_3_2_BLENDER_VALIDATION.json`):** `all_passed: true` (`bano_social_area_m2 = 6.27`, `vestidor_area_m2 = 6.525`, `bano_principal_area_m2 = 7.65`, `balcon_eliminated = true`, `p2_footprint_m2 = 80.0`, `architecture_only_visible_non_arch_count = 0`).
- **Exportación FBX (`exports/unity/fbx_reimport_verification_08_3_2.json`):** `6/6` paquetes con `mesh_match: true` y `dims_match: true`.
- **Validación estructural Unity (`validation/HITO_08_3_2_VALIDATION.json`):** `overall_passed: true` (`592` GameObjects, `489` MeshRenderers, `641122` triángulos, `50/50` materiales URP Lit, `310/310` comprobaciones dimensionales dentro de `0,02 m`, `18/18` pivotes, `8/8` barridos de cápsula, `8/8` raycasts de suelo, `0` objetos faltantes o duplicados).
- **Pruebas negativas (`validation/HITO_08_3_2_NEGATIVE_TESTS.json`):** `9/9 PASS` (`all_detected: true`).
- **EditMode Tests:** `5/5 PASS` (`0,79 s`).
- **PlayMode Tests:** `4/4 PASS` (`57,52 s`):
  - `ArchitecturalInspectionModeTogglesAndPreventsPlayerOverlap`: **PASS**
  - `ContinuousAutonomousTourVisitsAll18ZonesAndMeasuresPerformance`: **PASS** (`17/17` zonas en `ArchitectureOnly`)
  - `InputSystemEKeyOpensDoorAndWindowBlocksPlayer`: **PASS**
  - `OrbitalModeSingleActiveCameraRotationAndZoom`: **PASS**
- **Trazabilidad continua (`validation/HITO_08_3_2_NAVIGATION_TRACE.json`):** `17/17` zonas visitadas, `teleport_count = 0`, `exterior_entry_passed = true`, `exterior_return_passed = true`, `86,82 m` recorridos en `56,53 s`, `23348` colisiones clasificadas (`18797` suelo, `1399` escalera, `2806` muros, `346` obstáculos).
- **Rendimiento URP (`validation/HITO_08_3_1_PERFORMANCE.json`):** `361,4 FPS` promedio (`2,77 ms`), `P95 = 3,67 ms`, `P99 = 6,83 ms`, `1% low = 85,9 FPS` a `2560×1440`.

---

## 4. Evidencias Visuales (`renders/hito_08_3_2/`)

- **Blender (`ArchitectureOnly`):** `PLANTA_01_ARCHITECTURE_ONLY.png`, `PLANTA_02_ARCHITECTURE_ONLY.png`, `ISOMETRICA_P1_ARCHITECTURE_ONLY.png`, `ISOMETRICA_P2_ARCHITECTURE_ONLY.png`, `FACHADA_SUR_ACTUALIZADA.png`.
- **Unity PlayMode (`ArchitectureOnly`):** `01_ZONA_Exterior_Contexto_Urbano.png` a `17_ZONA_Bano_Principal.png`.
- **Comparativa de modos:** `COMPARATIVA_ARCHITECTURE_ONLY.png` vs `COMPARATIVA_FULL_FURNISHED.png`.
