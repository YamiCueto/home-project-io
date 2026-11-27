# Auditoría Técnica — Hito 1.1 (Correcciones respecto al Hito 1)

## 1. Correcciones Obligatorias Verificadas

| Corrección Solicitada | Estado | Implementación en `build_hito_01_v2.py` |
| :--- | :---: | :--- |
| Acceso independiente a Habitación Principal | **PASS** | Puerta real (`0,90 m`) desde `P2_Distribuidor` en muro `P2_M_Banda_Sur` |
| Aberturas reales para puertas y ventanas | **PASS** | Muros segmentados con antepechos, dinteles, vidrios (`window_glass`) y umbrales de puerta |
| Hueco geométrico real de escalera en losa P2 | **PASS** | Losa P2 construida en 4 segmentos dejando hueco libre en `X: 2,40..6,30`, `Y: 4,45..5,40` |
| Continuidad, desembarco y altura libre de escalera | **PASS** | 16 contrahuellas, alineación vertical exacta P1↔P2, altura libre `2,70 m` (`≥ 2,05 m`) |
| Vestidor principal y holguras corregidas | **PASS** | `1,50 × 2,70 m` (`4,05 m²`): módulo clóset `0,55 m` + pasillo libre `0,95 m` |
| Optimización de cocina y comodidad de sala | **PASS (B, C)** | En B y C: `Sala` = `9,64 m²` / `8,70 m²`; `Cocina` = `5,44 m²` / `6,29 m²` |
| Conciliación de áreas sin duplicidades | **PASS** | Separación estricta entre interior cerrado, cubiertas exteriores y muros |
| Validación real sin valores `True` fijos | **PASS** | Comprobaciones geométricas de colisión, BFS de conectividad, holguras y linderos |
| Verificación de vehículos y columnas de apoyo | **PASS** | Columnas `0,24 × 0,24 m` en `09_Estructura_Conceptual` dentro del lote `8,00 × 11,25 m` |

---

## 2. Resumen de Validación Automatizada (`validation/HITO_01_V2_VALIDATION.json`)

- **A — Garaje Frontal:** `11 PASS` · `4 FAIL` (`sala_comfort_8m2`: `5,41 m² < 8,00 m²`; y Escenario 1 con terrazas cubiertas) · `2 PENDING` (estructura y normativa POT).
- **B — Garaje Lateral:** `12 PASS` · `3 FAIL` (solo Escenario 1 si terrazas cubiertas computan en 60 m²) · `2 PENDING`.
- **C — Perimetral Optimizado:** `12 PASS` · `3 FAIL` (solo Escenario 1 si terrazas cubiertas computan en 60 m²) · `2 PENDING`.

**Línea base del Hito 1 original (`HOME_PROJECT_HITO_01.blend` y `build_hito_01.py`) preservada intacta.**
