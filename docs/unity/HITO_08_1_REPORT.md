# Informe Técnico — Hito 8.1: Integración arquitectónica Blender–Unity (URP)

## 1. Resumen ejecutivo

Se completó la integración arquitectónica de `models/HOME_PROJECT_HITO_06_V2.blend` hacia el proyecto Unity 6.6 (`6000.6.11f1`) bajo **Universal Render Pipeline (URP 17.6.0)** en la escena principal [`Assets/HomeProject/Scenes/HomeProject_Main.unity`](../../unity/Assets/HomeProject/Scenes/HomeProject_Main.unity).

## 2. Entorno tecnológico verificado

| Componente | Versión / Estado |
|---|---|
| Blender / Blender MCP | `5.3.0 Beta` (conectado, `polyhaven: on`) |
| Unity Editor / Unity MCP | `6000.6.11f1` (`StandaloneWindows64`, `MCP for Unity`) |
| Render Pipeline | `UniversalRenderPipelineAsset` (`17.6.0`, Forward+, HDR) |
| Unity Test Framework | `1.8.0` (`EditMode` 4/4 PASS, `PlayMode` 1/1 PASS) |
| Unity CLI | `C:\Program Files\Unity\Hub\Editor\6000.6.11f1\Editor\Unity.exe` |

## 3. Estadísticas de la escena (`HITO_08_1_VALIDATION.json`)

- **GameObjects en `HOME_PROJECT`:** `612`
- **MeshRenderers activos:** `471` (`471` mallas únicas)
- **Triángulos totales:** `732,973`
- **Materiales únicos:** `46` (`46` `Universal Render Pipeline/Lit`, `0` incompatibles)
- **Colliders:** `247` (`144` `BoxCollider`, `103` `MeshCollider`)
- **Colliders visibles:** `0`
- **Referencias faltantes (mallas / materiales):** `0 / 0`

## 4. Resultados de pruebas automatizadas y negativas

- **EditMode (`HomeProjectEditModeTests`):** `4/4 PASS` (`0.2585s`)
  - `SixFbxPackagesAreImportedAndInstantiated`
  - `UrpIsActiveRenderPipeline`
  - `SceneValidationPassesDimensionalAndMaterialChecks`
  - `NegativeTestsDetectAllControlledFaults`
- **PlayMode (`HomeProjectPlayModeTests`):** `1/1 PASS` (`0.3353s`)
  - `MainSceneLoadsInitializesAndPassesPhysicsAudits`
- **Pruebas negativas (`validation/HITO_08_1_NEGATIVE_TESTS.json`):** `7/7` fallas controladas detectadas y restauradas (`NEG_01_WRONG_SCALE`, `NEG_02_MISSING_ASSET`, `NEG_03_INCOMPATIBLE_SHADER`, `NEG_04_COLLIDER_BLOCKING_DOOR`, `NEG_05_VISIBLE_COLLIDER`, `NEG_06_WRONG_PIVOT`, `NEG_07_FLOOR_MISALIGNMENT`).

## 5. Automatización reproducible

Menú `Tools > Home Project`:
1. `1. Import Architecture from Blender`
2. `2. Rebuild Scene`
3. `3. Rebuild URP Materials`
4. `4. Configure Colliders`
5. `5. Configure URP Graphics & Cameras`
6. `6. Run Validations`
7. `7. Generate Technical Report & Renders`
8. `Run Full Pipeline`

## 6. Hallazgos y limitaciones heredadas

- Se mantiene documentada la discrepancia de superficies cubiertas de primera planta reportada en el Hito 6.1.
- Se mantienen documentadas las restricciones de apertura lateral del automóvil dentro del garaje.
- En `furniture.fbx` (exportado en Hito 6.1), tres sub-mallas decorativas de guijarros (`PH_Plant1_1_potted_plant_01_pebbles`, `PH_Plant1_2_potted_plant_01_pebbles`, `PH_Plant1_3_potted_plant_01_pebbles`) presentan altura `0.0615 m` frente a `0.5428 m` del `.blend` original; se registran en `warnings` del validador sin alterar los modelos históricos.
- No se declara certificación estructural, eléctrica o urbanística.
