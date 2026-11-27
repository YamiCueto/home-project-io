# Cuadro de Áreas Final Conciliado — HOME PROJECT (Hito 6)

Calculado programáticamente desde geometría evaluada (`bpy.context.evaluated_depsgraph_get()`) en `validation/HITO_06_VALIDATION.json`, intersectando físicamente la proyección de losas y cubiertas superiores sobre la primera planta (sin exclusiones por nombre).

---

## 1. Primera Planta — Desglose Geométrico Real

| Espacio (`P1_Piso_*`) | Área Neta Total (`m²`) | Cubierta por Losa/Cubierta (`m²`) | Descubierta (`m²`) |
| :--- | :---: | :---: | :---: |
| `P1_Acceso_Peatonal` | `6,525` | `6,525` | `0,000` |
| `P1_Sala` | `12,615` | `12,615` | `0,000` |
| `P1_Garaje_Derecho` | `14,625` | `14,625` | `0,000` |
| `P1_Bano_Social` | `3,610` | `3,610` | `0,000` |
| `P1_Distribuidor` | `1,805` | `1,805` | `0,000` |
| `P1_Escalera` | `3,562` | `3,562` | `0,000` |
| `P1_Comedor` | `5,738` | `5,738` | `0,000` |
| `P1_Cocina` | `4,950` | `4,950` | `0,000` |
| `P1_Habitacion_Huespedes` | `12,833` | `8,048` | `4,785` |
| `P1_Lavanderia_Patio` | `9,588` | `6,013` | `3,575` |
| **Totales P1 (pisos modelados)** | **`75,850`** | **`67,490`** | **`8,360`** |

*(Adicionalmente se incorporó `P1_Pasillo_Huesped` de `0,95 × 1,40 m = 1,330 m²` para continuidad física del corredor).*

## 2. Segunda Planta y Proyecciones

| Concepto | Área (`m²`) | Observación |
| :--- | :---: | :--- |
| **Planta 2 — Área útil neta (`P2_Piso_*`)** | `68,022` | Incluye suite, baños, vestidor, distribuidores, hijas y balcón |
| **Proyección Losa Entrepiso P2 (`P2_Losa_Seg_*`)** | `75,898` | Con hueco real de escalera |
| **Proyección Cubierta Plana Superior** | `80,000` | `8,00 × 10,00 m` (dentro del límite de `80 m²`) |

## 3. Conciliación Normativa (`PENDING`)
- Al proyectarse la segunda planta de `8,00 × 10,00 m` sobre el frente (`Y = 0..10 m`), el área neta de Planta 1 físicamente cubierta por losa/cubierta superior asciende a **`67,490 m²`** (superando `60,00 m²` si la curaduría computa el garaje y el acceso frontal cubiertos dentro del área construida de primer piso).
- La aprobación urbanística definitiva (índice de ocupación, retiros y cómputo de áreas semicubiertas según POT) permanece **`PENDING`**.
