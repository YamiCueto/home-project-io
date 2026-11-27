# Cuadro de Áreas V4 — HOME PROJECT (Hito 2)

Todas las superficies calculadas directamente desde la geometría real (`bpy` / uniones poligonales 2D) en `validation/HITO_02_VALIDATION.json`.

---

## 1. Superficies Calculadas desde Geometría Real (`HOME_PROJECT_HITO_02.blend`)

| Concepto | Superficie (`m²`) | Método de Cálculo |
| :--- | :---: | :--- |
| **Lote provisional (`8,00 × 11,25 m`)** | `90,000` | Envolvente provisional |
| **Planta 1 — Área útil neta total (incluyendo acceso y patio)** | `75,850` | Unión poligonal de pisos `P1_Piso_*` |
| **Planta 1 — Área útil neta cubierta (interior + garaje derecho)** | **`59,738`** | Unión poligonal `P1_Piso_*` excluyendo acceso frontal y patio posterior |
| **Planta 1 — Área descubierta / semicubierta (acceso + patio lavandería)** | `16,112` | `75,850 - 59,738` |
| **Planta 2 — Área útil neta (pisos interiores + balcón)** | `68,022` | Unión poligonal `P2_Piso_*` |
| **Proyección horizontal losa de entrepiso P2 sobre P1 (con hueco real)** | `76,438` | Unión poligonal de `P2_Losa_Seg_*` (excluye hueco de escalera `3,562 m²`) |
| **Proyección horizontal cubierta plana superior** | `80,000` | Unión poligonal de `Cubierta_Plana_Superior` (`8,00 × 10,00 m`) |

---

## 2. Notas de Conciliación
- La reducción de `0,95 m` en el ancho de `P1_Bano_Social` (`1,90 × 1,90 m = 3,61 m²`) y `P2_Bano_Compartido` (`1,90 × 1,90 m = 3,61 m²`) permitió desplazar el arranque de la escalera a `X = 3,10 m`, logrando un **desembarco superior de `1,00 m` de profundidad** (`X = 6,85..7,85 m`) coherente con el ancho útil de la escalera (`0,95 m`).
- Las validaciones estructurales definitivas y de edificabilidad POT permanecen en estado `PENDING`.
