# Informe de Cierre — Hito 1.2: Consolidación V3

**Modelo consolidado:** [HOME_PROJECT_HITO_01_V3.blend](file:///C:/Users/YAMI/Documents/projects/home-project/models/HOME_PROJECT_HITO_01_V3.blend)  
**Script reproducible (sin comentarios):** [build_hito_01_v3.py](file:///C:/Users/YAMI/Documents/projects/home-project/scripts/build_hito_01_v3.py)  
**Validación JSON:** [HITO_01_V3_VALIDATION.json](file:///C:/Users/YAMI/Documents/projects/home-project/validation/HITO_01_V3_VALIDATION.json)

---

## 1. Cumplimiento de Nuevas Restricciones Obligatorias

- **Garaje en el lado derecho (`X = 4,60..7,85 m`) con portón hacia Calle Principal (`Y-`):** **`PASS`**. Aloja **Suzuki Swift Dzire 2023** y **Suzuki V-Strom 250 SX** dentro del garaje.
- **Acceso peatonal independiente (`6,52 m²`) y Sala (`12,62 m²`) en el lado izquierdo (`X = 0,15..4,50 m`):** **`PASS`**, completamente separados del estacionamiento.
- **Aprovechamiento de Calle de la Esquina (`X+`) para iluminación y ventilación:** **`PASS`**, mediante ventanas en Garaje, Cocina/Comedor, Lavandería, Baño Principal y Habitación Hija 2.
- **Líneas base preservadas:** `HOME_PROJECT_HITO_01.blend`, `HOME_PROJECT_EXISTENTE.blend` y `HOME_PROJECT_HITO_01_V2_A/B/C.blend` permanecen intactos.

---

## 2. Validación Automatizada (`bpy`)

- **Escenario estricto `≤ 60 m²` cubiertos (`59,83 m²` P1 + `80,00 m²` P2 = `139,83 m²`):** **`PASS`**.
- **Escenario con terrazas/patio cubiertos (`75,94 m²` P1):** **`FAIL`** *(documentado como alternativa urbanística dependiente de POT)*.
- **Superposiciones de habitaciones / colisiones de mobiliario / conectividad BFS:** **`PASS`** (`0` superposiciones, `0` colisiones, `100%` conectado).
- **Escaleras alineadas + hueco real en losa P2 + altura libre `2,70 m`:** **`PASS`**.
- **Preparación Recorrido Virtual:** **`PASS`** (`14` puertas con pivote en bisagra, `12` ventanas independientes, `11` cámaras en `13_Recorrido_Virtual` a `1,65 m`, `0` geometría duplicada).
- **Verificación estructural y normativa POT:** **`PENDING`**.

---

## 3. Evidencias Visuales

- [HITO_01_V3_PLANTA_01.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_01_V3_PLANTA_01.png)
- [HITO_01_V3_PLANTA_02.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_01_V3_PLANTA_02.png)
- [HITO_01_V3_ISOMETRICA.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_01_V3_ISOMETRICA.png)
- [HITO_01_V3_ESQUINA.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_01_V3_ESQUINA.png)

**Ejecución detenida en espera de aprobación explícita para iniciar el Hito 2.**
