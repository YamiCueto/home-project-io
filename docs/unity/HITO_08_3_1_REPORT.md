# Informe Técnico — Hito 8.3.1: Corrección Arquitectónica y Certificación de Navegabilidad Virtual

## 1. Resumen Ejecutivo

- **Modelo Blender V3:** `models/HOME_PROJECT_HITO_06_V3.blend` (generado por `scripts/build_hito_06_v3.py`, validado por `scripts/validate_hito_06_v3.py`, exportado por `scripts/export_unity_v3.py`).
- **Validación geométrica Blender V3 (`validation/HITO_06_V3_BLENDER_VALIDATION.json`):** `all_passed: true` (`pedestrian_gate_width_m = 1.0`, `dining_north_aisle_m = 0.955`, `kitchen_entry_aisle_m = 1.3`, `garage_enclosure_present = true`, `stair_handrail_present = true`, `p2_stairwell_guardrails_present = true`).
- **Validación estructural Unity (`validation/HITO_08_3_1_VALIDATION.json`):** `overall_passed: true` (`636` GameObjects, `489` MeshRenderers, `733189` triángulos, `46/46` materiales URP Lit, `486/486` comprobaciones dimensionales dentro de `0.02 m`, `19/19` pivotes, `8/8` barridos de cápsula, `8/8` raycasts de suelo, `0` objetos faltantes o duplicados).
- **Pruebas negativas (`validation/HITO_08_3_1_NEGATIVE_TESTS.json`):** `9/9 PASS` (`all_detected: true`).
- **Pruebas EditMode:** `5/5 PASS` (`0.81 s`).
- **Pruebas PlayMode:** `3/3 PASS` (`64.76 s`).

## 2. Certificación de Navegabilidad Autónoma (`validation/HITO_08_3_1_NAVIGATION_TRACE.json`)

- **Teletransportes (`teleport_count`):** `0`
- **Zonas visitadas:** `18 / 18` (`all_zones_visited: true`, `unreachable_zones: []`)
- **Acceso peatonal desde exterior (`exterior_entry_passed`):** `true`
- **Retorno continuo al exterior (`exterior_return_passed`):** `true`
- **Distancia total recorrida:** `90.72 m`
- **Tiempo total del recorrido:** `63.99 s`
- **Clasificación de colisiones:**
  - `floor_collisions`: `21941`
  - `stair_collisions`: `1383`
  - `wall_collisions`: `3839`
  - `obstacle_collisions`: `3224`
  - `total_collisions`: `30387`

## 3. Rendimiento en URP (`validation/HITO_08_3_1_PERFORMANCE.json`)

- **Resolución:** `2560 x 1440` (`warmup_frames = 60`)
- **Pipeline:** `URP 17.6.0 (Forward+, HDR, MSAA 4x, SSAO, Shadows 4096)`
- **FPS promedio:** `368.5 FPS` (`2.71 ms` promedio por fotograma)
- **Percentil P95:** `3.70 ms`
- **Percentil P99:** `8.01 ms`
- **1% low:** `80.3 FPS`

## 4. Preservación de Áreas y Versiones Anteriores

- Se preservan intactos `models/HOME_PROJECT_HITO_05.blend`, `models/HOME_PROJECT_HITO_06.blend`, `models/HOME_PROJECT_HITO_06_V2.blend` y la referencia arquitectónica en `docs/CUADRO_DE_AREAS_V4.md`.
- Las correcciones de V3 ajustaron exclusivamente la abertura peatonal del murete frontal, el mobiliario interior de comedor/cocina/dormitorio principal/moto, el cerramiento norte del garaje con su losa de paso (`P1_Piso_P1_Paso_Garaje`) y los pasamanos/barandas de escalera.

## 5. Evidencias Visuales (`renders/hito_08_3_1/`)

- Plantas arquitectónicas V3: `PLANTA_01_V3.png`, `PLANTA_02_V3.png`
- Capturas en PlayMode durante el recorrido continuo: `01_ZONA_Exterior_Contexto_Urbano.png` a `16_ZONA_Balcon.png` (incluyendo `02_ZONA_Acceso_Peatonal.png`, `06_ZONA_Cocina.png`, `07_ZONA_Garaje.png`, `08_ZONA_Lavanderia_Patio.png`, `10_ZONA_Escalera.png`).
