# Informe Técnico — Hito 8.3: Refinamiento Espacial, Mobiliario y Experiencia Jugable

## 1. Resumen Ejecutivo

- **Rama:** `feature/hito-08-3-spatial-refinement` (base `feature/hito-08-2-first-person`)
- **Modelo Blender:** `models/HOME_PROJECT_HITO_08_3.blend` (preservando `HOME_PROJECT_HITO_05.blend`, `HOME_PROJECT_HITO_06.blend`, `HOME_PROJECT_HITO_06_V2.blend` y `HOME_PROJECT_HITO_06_V3.blend` intactos)
- **Scripts de construcción, validación y exportación:**
  - `scripts/build_hito_08_3.py`
  - `scripts/validate_hito_08_3.py`
  - `scripts/export_unity_08_3.py`
- **Motor y pipeline:** Unity `6000.6.11f1` + `UniversalRenderPipelineAsset` (`URP 17.6.0 Forward+, HDR, MSAA 4x, SSAO, Shadows 4096`)

---

## 2. Mejoras Implementadas

### 2.1 Garaje y Vehículos (`Veh_Swift_*` y `Veh_VStrom_*`)
- Sustitución de los volúmenes placeholder por modelos low-poly arquitectónicos esculpidos con `bmesh`:
  - **SUV compacto (`Veh_Swift_*`):** carrocería aerodinámica (`Veh_Swift_Carroceria`), cabina acristalada (`Veh_Swift_Cabina_Vidrios`), parrilla, faros delanteros/traseros, espejos laterales y 4 ruedas cilíndricas biseladas con rines metálicos (`Veh_Swift_Rueda_FL/FR/RL/RR`).
  - **Motocicleta adventure (`Veh_VStrom_*`):** carrocería esculpida (`Veh_VStrom_Carroceria`), bloque motor, asiento escalonado, cúpula, manillar con puños, horquilla delantera, escape y ruedas delantera/trasera con rines.
- **Despejes verificados (`validation/HITO_08_3_BLENDER_VALIDATION.json`):**
  - `car_north_door_clearance_m`: `0.585 m` respecto a `P1_M_Norte_Garaje_Puerta1`
  - `moto_north_door_clearance_m`: `1.094 m` respecto a `P1_M_Norte_Garaje_Puerta1`
  - `garage_vehicles_clear_pass`: `true`

### 2.2 Rediseño de la Suite Principal (`Dormitorio -> Vestidor -> Baño Principal`)
- **Alcoba principal:** Reorientación de la cama principal (`P2_Mob_Cama_Master_*`, `P2_Mob_LED_Cabecero`, `P2_PH_Nightstand_*`) contra el muro oeste (`X = 0.15 m`), liberando completamente la puerta de acceso desde el corredor (`P2_M_Banda_Sur_Puerta1` en `X = 2.15..3.05 m`, libre del hueco de escalera) y ofreciendo lectura visual continua hacia el ventanal sur, el balcón y el eje del vestidor.
- **Vestidor de paso ampliado (`X = 4.60..5.95 m`, `Y = 1.75..4.65 m`):** Dos módulos simétricos de clóset de piso a techo (`P2_Mob_Closet_Vestidor` y `P2_Mob_Closet_Vestidor_Sur`) dejando un paso axial central de `1.70 m` conectado mediante vano de `1.00 m` (`P2_M_Master_Este_Puerta3`) con el dormitorio y mediante `P2_M_Vest_Bano_Puerta1` (`0.90 m`) con el baño privado.
- **Baño privado ampliado (`X = 6.05..7.85 m`, `Y = 1.75..4.65 m`, `1.80 m` de ancho):** Ducha walk-in con mampara de vidrio (`P2_Mob_Ducha_Master`, `P2_Mob_Mampara_Master`), sanitario (`P2_Mob_Inodoro_Master`), lavabo flotante amplio (`P2_Mob_Lavabo_Master`) y espejo (`P2_Mob_Espejo_Master`).
- Actualización coherente de zonas en `unity/Assets/HomeProject/Scripts/Core/ResidentialZoneTracker.cs` y de la ruta continua en `unity/Assets/HomeProject/Scripts/Interaction/ResidentialNavigationAgent.cs`.

---

## 3. Resultados de Validación y Pruebas

- **Validación Blender (`validation/HITO_08_3_BLENDER_VALIDATION.json`):** `all_passed: true` (`vestidor_width_m = 1.35`, `bano_principal_width_m = 1.8`, `master_entry_clear_stairwell = true`).
- **Exportación FBX (`exports/unity/fbx_reimport_verification_v3.json`):** 6/6 paquetes (`architecture.fbx`, `furniture.fbx`, `interactive_doors.fbx`, `installations.fbx`, `urban_context.fbx`, `colliders.fbx`) con `mesh_match: true` y `dims_match: true`.
- **Validación estructural Unity (`validation/HITO_08_3_1_VALIDATION.json`):** `overall_passed: true` (`650` GameObjects, `503` MeshRenderers, `734725` triángulos, `51/51` materiales URP Lit, `500/500` comprobaciones dimensionales dentro de `0.02 m`, `19/19` pivotes, `8/8` barridos de cápsula, `8/8` raycasts de suelo, `0` objetos faltantes o duplicados).
- **Pruebas negativas (`validation/HITO_08_3_1_NEGATIVE_TESTS.json`):** `9/9 PASS` (`all_detected: true`).
- **EditMode Tests:** `5/5 PASS` (`0.83 s`).
- **PlayMode Tests:** `3/3 PASS` (`61.79 s`):
  - `ContinuousAutonomousTourVisitsAll18ZonesAndMeasuresPerformance`: **PASS**
  - `InputSystemEKeyOpensDoorAndWindowBlocksPlayer`: **PASS**
  - `OrbitalModeSingleActiveCameraRotationAndZoom`: **PASS**
- **Trazabilidad continua (`validation/HITO_08_3_1_NAVIGATION_TRACE.json`):** `18/18` zonas visitadas, `teleport_count = 0`, `exterior_entry_passed = true`, `exterior_return_passed = true`, `90.23 m` en `61.07 s`, `27897` colisiones clasificadas (`21089` suelo, `1519` escalera, `3796` muros, `1493` obstáculos).
- **Rendimiento URP (`validation/HITO_08_3_1_PERFORMANCE.json`):** `374.2 FPS` promedio (`2.67 ms`), `P95 = 3.83 ms`, `P99 = 7.99 ms`, `1% low = 77.6 FPS` a `2560x1440`.

---

## 4. Evidencias Visuales (`renders/hito_08_3/`)

- Plantas arquitectónicas actualizadas: `PLANTA_01_HITO_08_3.png`, `PLANTA_02_HITO_08_3.png`
- Capturas PlayMode del recorrido autónomo: `01_ZONA_Exterior_Contexto_Urbano.png` a `17_ZONA_Balcon.png` (destacando `07_ZONA_Garaje.png`, `14_ZONA_Habitacion_Principal.png`, `15_ZONA_Vestidor.png`, `16_ZONA_Bano_Principal.png`).

---

## 5. Riesgos y Pendientes

- **Pendiente de siguientes hitos:** No se ha iniciado la integración domótica ni la lógica de automatización residencial (Hito 8.4).
- **Riesgo menor:** Se mantienen 3 excepciones explícitas heredadas en `validation/HITO_08_3_1_VALIDATION.json` para sub-mallas decorativas de guijarros en macetas (`PH_Plant1_1/2/3_potted_plant_01_pebbles`), sin impacto estructural ni de navegabilidad.
