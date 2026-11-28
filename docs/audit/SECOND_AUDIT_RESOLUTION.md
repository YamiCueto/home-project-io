# Resolución de Segunda Auditoría Independiente — Hito 6.1

**Rama:** `feature/hito-06-technical-audit` (Pull Request #1 hacia `develop`)  
**Modelo:** [HOME_PROJECT_HITO_06_V2.blend](file:///C:/Users/YAMI/Documents/projects/home-project/models/HOME_PROJECT_HITO_06_V2.blend)  
**Validador:** [validate_hito_06_v2.py](file:///C:/Users/YAMI/Documents/projects/home-project/scripts/validate_hito_06_v2.py)  
**Resultados:** [HITO_06_V2_VALIDATION.json](file:///C:/Users/YAMI/Documents/projects/home-project/validation/HITO_06_V2_VALIDATION.json) · [HITO_06_V2_NEGATIVE_TESTS.json](file:///C:/Users/YAMI/Documents/projects/home-project/validation/HITO_06_V2_NEGATIVE_TESTS.json)

---

## 1. Cobertura Arquitectónica
- **Hallazgo resuelto:** Los `4,785 m²` descubiertos de `P1_Habitacion_Huespedes` correspondían a la franja posterior `Y = 10,00..11,10 m` más allá de `Cubierta_Plana_Superior` (`8 × 10 m`). Se incorporó `Cubierta_P1_Huespedes` (`4,55 × 1,25 m`), logrando **`100%` de cobertura física en los 4 dormitorios** (`all_bedrooms_100pct_covered: PASS`).
- **Superficies conciliadas (incluyendo `P1_Pasillo_Huesped` de `1,330 m²`):**
  - `p1_total_floors_net_m2`: `77,180 m²`
  - `p1_covered_by_upper_or_p1_roof_net_m2`: `73,605 m²` (exceso explícito de **`13,605 m²`** sobre `60,00 m²` si se computan garaje y acceso cubiertos; validación POT **`PENDING`**).
  - `p1_uncovered_net_m2`: `3,575 m²` (patio de lavandería).
  - `p2_floors_net_m2`: `68,022 m²` · `p2_slab_projection_m2`: `75,898 m²` · `Cubierta_Plana_Superior`: `80,000 m²` (`PASS ≤ 80 m²`).

## 2. Navegabilidad Real
- Validación continua en `0..1152` con **subdivisión adaptativa (`0,10 m`)** contra muros, columnas, vigas, barandas y mobiliario sólido, verificando apoyo transitable y altura libre.
- **Hallazgos reales corregidos en geometría:**
  - Recortada `Viga_P1_06` en `Y = 4,72 m` para despejar el hueco de escalera.
  - Desplazada la cama principal hacia `Y = 1,65..3,65 m` manteniendo orientación hacia `Y-` (`bed_street_dot = 1,0`) y liberando un pasillo de `1,00 m` tras el cabecero frente a la puerta de acceso.

## 3. Garaje y Puertas
- Modeladas puertas batientes reales del Suzuki Swift Dzire (`Veh_Swift_Puerta_Cond`, `Veh_Swift_Puerta_Pas`).
- Reubicados vehículo (`X = 5,05..6,785 m`) y motocicleta (`Y = 2,47..4,65 m`), logrando apertura libre a **`55°`** de la puerta del conductor sin colisionar con la V-Strom (`car_doors_swing_no_hit: PASS`). *(Nota: la puerta del pasajero queda limitada a `~25°` / `0,45 m` en el ancho de `3,25 m`, requiriendo descenso previo de acompañantes).*
- Definido `swing_dir` explícito (`+1` / `-1`) en las `13` puertas residenciales y validado giro `0°–90°` sin colisiones (`explicit_door_swing_0_90_clear: PASS`).

## 4. Pruebas Negativas (`12/12 FAIL` Controlado)
Ejecutadas mediante el mismo `run_validation_v2(write_json=False)`: puerta bloqueada, mueble en muro, cámara sin animación, recorrido en muro, textura faltante, PNG 720p/corrupto sin `IEND`, objeto fuera de lindero, geometría duplicada, recurso sin licencia CC0, **cámara atravesando mobiliario**, **puerta con sentido de giro incorrecto** y **dormitorio sin cubierta**.

## 5. Exportación Unity (`export_unity_v2.py`)
Exportados `6` FBX (`architecture.fbx`, `furniture.fbx`, `interactive_doors.fbx`, `installations.fbx`, `urban_context.fbx`, `colliders.fbx`) + `materials_textures_manifest.json` y `fbx_reimport_verification_v2.json` con `100%` coincidencia de mallas y dimensiones (`<= 0,02 m`). La compatibilidad efectiva dentro del motor Unity permanece pendiente hasta el **Hito 8**.
