# Cuadro de Áreas V5 — HOME PROJECT (Hito 8.3.2)

Superficies recalculadas desde la geometría real evaluada en `models/HOME_PROJECT_HITO_08_3_2.blend` (`validation/HITO_08_3_2_BLENDER_VALIDATION.json`).

---

## 1. Comparativa de Superficies Antes vs. Después (P1-01 y P2-02)

| Ambiente / Intervención | Antes (`m²`) | Después (`m²`) | Variación (`m²` / `%`) | Observación geométrica |
| :--- | :---: | :---: | :---: | :--- |
| **P1-01 — Baño Social (`P1_Piso_P1_Bano_Social`)** | `3,610` | **`6,270`** | `+2,660` (`+73,7 %`) | Integra el vacío residual norte (`X = 0,15..2,05 m, Y = 6,65..8,05 m`) eliminado el muro `P1_M_Bano_Norte_S0`. |
| **P1-01 — Espacio residual norte de Baño Social** | `2,600` (inaccesible) | **`0,000`** | `-2,600` (`-100 %`) | Absorción total al baño social manteniendo `Distribuidor` (`1,805 m²`) y `Pasillo_Huesped` (`1,330 m²`). |
| **P2-02 — Balcón esquinero (`P2_Piso_P2_Balcon`)** | `4,875` | **`0,000`** | `-4,875` (`-100 %`) | Eliminado e incorporado a la envolvente interior de la suite principal. |
| **P2-02 — Vestier de paso (`P2_Piso_P2_Vestidor_Principal`)** | `3,915` | **`6,525`** | `+2,610` (`+66,7 %`) | `1,45 × 4,50 m` con reserva para módulos de clóset de `0,60 m` y eje axial de paso. |
| **P2-02 — Baño Principal (`P2_Piso_P2_Bano_Principal`)** | `5,220` | **`7,650`** | `+2,430` (`+46,6 %`) | `1,70 × 4,50 m` con ducha walk-in, sanitario, lavabo y doble fuente de iluminación/ventilación natural. |
| **P2 — Huella exterior total (`8,00 × 10,00 m`)** | `80,000` | **`80,000`** | `0,000` (`0 %`) | Cumple estrictamente el máximo de `80,00 m²`. |

---

## 2. Resumen General de Superficies (`HOME_PROJECT_HITO_08_3_2.blend`)

| Concepto | Superficie (`m²`) | Estado / Nota |
| :--- | :---: | :--- |
| **Lote provisional (`8,00 × 11,25 m`)** | `90,000` | Envolvente provisional preservada |
| **Planta 1 — Área útil neta cubierta (interior + garaje + paso garaje + baño ampliado)** | **`62,338`** | **Exceso explícito de `+2,338 m²` respecto al límite referencial de `60,000 m²`**, debido a la recuperación del vacío residual de `2,600 m²` ya cubierto bajo la losa P2 (`76,438 m²`). |
| **Planta 1 — Área descubierta / semicubierta (acceso frontal + patio lavandería)** | `16,112` | Preservada |
| **Planta 2 — Área útil neta interior (sin balcón)** | `68,022` | Redistribuida entre Dormitorio Principal (`19,575 m²`), Vestier (`6,525 m²`), Baño Principal (`7,650 m²`), Dormitorios Hija 1/2, Baño Compartido y Corredor |
| **Proyección horizontal losa de entrepiso P2 sobre P1 (con hueco escalera)** | `76,438` | Sin cambios estructurales |
| **Proyección horizontal cubierta plana superior** | `80,000` | Dentro del límite de `80,00 m²` |

> **Nota regulatoria:** Las certificaciones estructurales, eléctricas y urbanísticas (POT) permanecen pendientes de aprobación profesional.
