# Informe Técnico — Hito 8.3 Fixes: Corrección de Bloqueos Espaciales y Circulación

## 1. Resumen Ejecutivo

- **Rama:** `feature/hito-08-3-fixes-spatial-blockers` (PR contra `feature/hito-08-3-spatial-refinement`)
- **Modelo Blender:** `models/HOME_PROJECT_HITO_08_3_FIXES.blend` (preservando `HOME_PROJECT_HITO_05.blend`, `HOME_PROJECT_HITO_06*.blend` y `HOME_PROJECT_HITO_08_3.blend` intactos)
- **Scripts del fix:**
  - `scripts/build_hito_08_3_fixes.py`
  - `scripts/validate_hito_08_3_fixes.py`
  - `scripts/export_unity_08_3_fixes.py`

---

## 2. Hallazgos Corregidos

### 2.1 Paso bloqueado entre Hall / Sala y Garaje (`P1_M_Sep_Sala_Garaje`)
- **Diagnóstico:** El estante `P1_Mob_Estante_Garaje` (`X = 4.62..4.95 m, Y = 3.60..4.55 m, Z = 1.65..2.20 m`) invadía la altura de cabeza justo frente a `P1_M_Sep_Sala_Garaje_Puerta1` (`0.85 m` de ancho), bloqueando la cápsula del controlador (`1.80 m` de altura).
- **Solución:**
  - Ampliación de `P1_M_Sep_Sala_Garaje_Puerta1` a **`0.95 m`** de ancho libre (`Y = 3.60..4.55 m`, `swing_dir = -1`) con ajuste de `P1_M_Sep_Sala_Garaje_S0` y `P1_M_Sep_Sala_Garaje_Lint1`.
  - Reubicación de `P1_Mob_Estante_Garaje` sobre el muro norte del garaje (`X = 4.90..6.50 m, Y = 4.30..4.64 m, Z = 1.65..2.20 m`), libre de todas las puertas.
  - Verificación explícita en PlayMode mediante los waypoints `Sala_Puerta_Garaje -> Garaje_Desde_Hall -> Retorno_Hall_Garaje` (`reached: true`, `detected_zone: "Garaje"`).

### 2.2 Comedor con sillas mal ubicadas
- **Diagnóstico:** `P1_PH_Chair_1/2` (`Y = 5.625..6.201 m`) colisionaban con el pasamanos `Esc_Pasamanos_Norte` (`Y = 5.66..5.71 m`) y `P1_PH_Chair_3/4` (`Y = 6.519..7.095 m`) atravesaban la mesa (`Y = 6.20..7.10 m`).
- **Solución:**
  - Reemplazo limpio de la mesa `P1_Mob_Mesa_Comedor_Sobre` (`X = 3.45..4.95 m, Y = 6.20..6.86 m, Z = 0.74..0.79 m`) y sus 4 patas (`P1_Mob_Mesa_Pata_*`) apoyadas en `Z = 0.04 m`.
  - Disposición simétrica de 4 sillas (`P1_PH_Chair_1..4` en `Y = 5.98 m` y `Y = 7.03 m`) apoyadas en `Z = 0.04 m`, sin intersección con mesa ni escalera, dejando **`0.775 m` libres** en el pasillo norte hacia cocina (`Y = 7.275..8.05 m`) y **`1.30 m` libres** al oeste.

### 2.3 Vigas y columnas invasivas en alcobas de las niñas
- **Diagnóstico:** La columna `Col_P2_08` (`X = 4.435..4.665 m, Y = 7.985..8.215 m`) sobresalía libremente `0.40 m` dentro de `Habitacion Hija 2` (la primera habitación subiendo las escaleras), junto con `Viga_P2_06` (`Y = 0.255..8.00 m`) y `Viga_P2_03` (`Z = 5.36..5.60 m`).
- **Solución:**
  - Integración de `Col_P2_08` (`X = 3.90..4.10 m, Y = 7.985..8.215 m`) al ras dentro del muro divisorio `P2_M_Entre_Hijas_S0` (`X = 3.95..4.05 m`).
  - Remate de `Viga_P2_06` en el muro del corredor (`Y <= 4.75 m`) y ajuste de `Viga_P2_03` al ras del cielo raso (`Z = 5.45..5.60 m`).

---

## 3. Validaciones y Pruebas

- **Validación Blender (`validation/HITO_08_3_FIXES_BLENDER_VALIDATION.json`):** `all_passed: true` (`hall_garage_door_width_m = 0.95`, `hall_garage_width_pass = true`, `estante_clear_of_doorway = true`, `dining_chairs_clear = true`, `col_p2_08_integrated_in_wall = true`, `viga_p2_06_clear_kids_room = true`).
- **Exportación FBX (`exports/unity/fbx_reimport_verification_v3.json`):** 6/6 paquetes (`mesh_match: true`, `dims_match: true`).
- **Validación Unity (`validation/HITO_08_3_1_VALIDATION.json`):** `overall_passed: true` (`649` GameObjects, `502` MeshRenderers, `711432` triángulos, `52/52` materiales URP Lit, `499/499` dimensionales dentro de `0.02 m`, `19/19` pivotes, `8/8` cápsula, `8/8` raycasts de suelo).
- **Pruebas negativas (`validation/HITO_08_3_1_NEGATIVE_TESTS.json`):** `9/9 PASS`.
- **EditMode Tests:** `5/5 PASS` (`0.77 s`).
- **PlayMode Tests:** `3/3 PASS` (`62.79 s`):
  - `ContinuousAutonomousTourVisitsAll18ZonesAndMeasuresPerformance`: **PASS**
  - `InputSystemEKeyOpensDoorAndWindowBlocksPlayer`: **PASS**
  - `OrbitalModeSingleActiveCameraRotationAndZoom`: **PASS**
- **Trazabilidad continua (`validation/HITO_08_3_1_NAVIGATION_TRACE.json`):** `18/18` zonas visitadas, `teleport_count = 0`, `exterior_entry_passed = true`, `exterior_return_passed = true`, `93.45 m` en `62.14 s`, `obstacle_collisions` reducidas a `899` (`30634` colisiones totales clasificadas).
- **Rendimiento URP (`validation/HITO_08_3_1_PERFORMANCE.json`):** `406.3 FPS` promedio (`2.46 ms`), `P95 = 3.53 ms`, `P99 = 7.58 ms`, `1% low = 84.5 FPS` a `2560x1440`.

---

## 4. Evidencias Antes / Después (`renders/hito_08_3_fixes/` y `renders/hito_08_3/`)

- **Hall -> Garaje:** `renders/hito_08_3_fixes/BEFORE_Hall_Garaje.png` vs `renders/hito_08_3_fixes/AFTER_Hall_Garaje.png`, y PlayMode `renders/hito_08_3/04_ZONA_Garaje.png`
- **Comedor:** `renders/hito_08_3_fixes/BEFORE_Comedor.png` vs `renders/hito_08_3_fixes/AFTER_Comedor.png`, y planta `renders/hito_08_3_fixes/PLANTA_01_FIXES.png`
- **Primera alcoba infantil (`Habitacion Hija 2`):** `renders/hito_08_3_fixes/BEFORE_Hija_2.png` vs `renders/hito_08_3_fixes/AFTER_Hija_2.png`, y planta `renders/hito_08_3_fixes/PLANTA_02_FIXES.png`
