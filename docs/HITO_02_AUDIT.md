# Auditoría Técnica — Hito 2 (Subhitos 2.0 – 2.6)

## 1. Correcciones de Validación y Geometría (Subhitos 2.0 – 2.4)

| Aspecto Auditado | Estado | Evidencia (`validate_hito_02.py` / `HITO_02_VALIDATION.json`) |
| :--- | :---: | :--- |
| **Cálculo de áreas por geometría real** | **`PASS`** | Unión poligonal 2D real sin valores fijos (`59,738 m²` P1 cubierto neto, `76,438 m²` losa P2, `80,000 m²` cubierta) |
| **Columnas dentro de linderos provisionales** | **`PASS`** | `cols_outside_lot: []` (centros ajustados a `0,125` y `7,875` con sección `0,25 × 0,25 m`) |
| **Muros a altura completa (`2,70 m`)** | **`PASS`** | Muros P1 (`Z: 0,00..2,70`) y P2 (`Z: 2,90..5,60`) completos con cubierta plana y pretil |
| **Desembarco superior de escalera** | **`PASS`** | Rediseñado de `0,30 m` a **`1,00 m`** (`≥ 0,95 m`), `15` peldaños, barandas en P2 |
| **Altura libre sobre cada peldaño** | **`PASS`** | Mínimo verificado sobre peldaños: **`2,881 m`** (`≥ 2,05 m`) |
| **Garaje funcional + portón seccional** | **`PASS`** | `3,25 × 4,50 m`, portón seccional de `4` paneles, holgura puerta auto-moto `0,365 m` |
| **Conectividad derivada de aberturas reales** | **`PASS`** | `unconnected: []` mediante grafo BFS sobre puertas reales |
| **Colisiones de mobiliario / columnas-puertas** | **`PASS`** | `furn_collisions: []`, `col_door_int: []` |
| **Trayectoria de agente peatonal (recorrido virtual)** | **`PASS`** | `agent_collisions: []` a lo largo de `1152` fotogramas (`48 s` a `24 fps`) |
| **Ausencia de geometría duplicada** | **`PASS`** | `duplicates: []` |
| **Aprobación estructural y normativa POT** | **`PENDING`** | Requiere cálculo estructural e ingeniería de suelos/curaduría |

---

## 2. Nota sobre Z-fighting en Esquina (`HITO_02_ESQUINA.png`)
En la vista exterior de esquina se aprecia ligera coplanaridad visual entre caras exteriores de columnas (`0,25 m`) y muros (`0,15 m`) en el plano límite `X = 8,00` / `Y = 0,00`. En el Hito 3 (materiales y detalles) se aplicará un retranqueo o recubrimiento de fachada de `1-2 cm` para eliminar cualquier coplanaridad en Cycles.
