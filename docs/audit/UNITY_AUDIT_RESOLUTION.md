# Resolución de Auditoría Técnica Unity — Hito 8.2.0

## Resumen de hallazgos resueltos (`UNI-01` a `UNI-05`)

| ID | Hallazgo | Resolución implementada | Evidencia |
|---|---|---|---|
| **UNI-01** | Objetos esperados ausentes, renderers faltantes y nombres duplicados | `SceneValidatorService.IndexSceneObjects` y `ValidateTransformsAndDimensions` prohíben omisiones silenciosas, contabilizan `missing_expected_objects = 0`, `duplicate_object_names = 0` y `missing_mesh_references = 0`. | `validation/HITO_08_2_VALIDATION.json` |
| **UNI-02** | Comparación individual de posición, rotación, escala y dimensiones | `blender_reference_manifest.json` exportado desde Blender MCP con `location_blender`, `rotation_euler_deg_blender`, `scale_blender` y `world_center_blender`. Validados `468 / 468` objetos en `<= 0.02 m`. | `SceneValidatorService.cs` |
| **UNI-03** | Sustitución de comprobaciones puntuales por barrido volumétrico | `ValidateCapsuleOpenings` ejecuta `Physics.CapsuleCast` con cápsula humana (`radius = 0.28 m`, `height = 1.80 m`) en `8 / 8` pasos y aberturas principales (`PASS`). | `validation/HITO_08_2_VALIDATION.json` |
| **UNI-04** | Tolerancia estricta de `0.02 m` en pivotes de puertas | `ValidateDoorPivots` exige `dist <= 0.02 m` en `17 / 17` hojas de puerta y paneles del portón (`PASS`). | `validation/HITO_08_2_VALIDATION.json` |
| **UNI-05** | Verificación de impacto de raycasts de suelo en superficies transitables | `ValidateFloorRaycasts` comprueba `8 / 8` zonas (`Anden_Frontal`, `Sala_P1`, `Garaje_P1`, `Cocina_P1`, `Huespedes_P1`, `Escalera_Peldano_08`, `Desembarco_P2`, `Master_P2`) contra los pisos/peldaños esperados. | `validation/HITO_08_2_VALIDATION.json` |

## Excepciones explícitas documentadas

- **`PH_Plant1_1_potted_plant_01_pebbles`, `PH_Plant1_2_potted_plant_01_pebbles`, `PH_Plant1_3_potted_plant_01_pebbles`:**
  - **Cantidad:** `3` sub-mallas.
  - **Magnitud de discrepancia:** `0.4813 m` en eje vertical (`0.0615 m` en `furniture.fbx` vs `0.5428 m` en `.blend`).
  - **Justificación:** Sub-mallas decorativas de guijarros dentro de macetas heredadas del export FBX de Hito 6.1; no forman parte de la estructura ni interfieren con la navegabilidad.

## Inspección arquitectónica adicional

- **Separación cocina–garaje:** Verificada en Blender y Unity (`P1_M_Sep_Sala_Garaje_S0/S2` en `X = 4.55`, `P1_Piso_P1_Garaje_Derecho` en `Y[0.15, 4.65]`, caja de escalera en `Y[4.75, 5.70]` y `P1_Piso_P1_Cocina` en `Y[5.80, 8.05]`).
- **Barandas, pasamanos, desembarco superior y hueco de escalera:** `Balcon_Pasamanos_Sur` (`Z[3.92, 3.97]`), `P2_Losa_Seg_1..4` dejando el hueco de escalera libre en `X[3.10, 6.85], Y[4.75, 5.70]`, y desembarco superior en `P2_Piso_P2_Llegada_Escalera` (`Y_unity = 2.94 m`) validados sin obstrucciones.
