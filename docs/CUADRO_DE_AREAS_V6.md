# Cuadro de Áreas V6 — HOME PROJECT (Hito 8.3.3)

Superficies actualizadas desde la geometría real evaluada en `models/HOME_PROJECT_HITO_08_3_3.blend` (`validation/HITO_08_3_3_BLENDER_VALIDATION.json`).

---

## 1. Cambios Geométricos y Funcionales (Hito 8.3.3 — P2-03)

| Ambiente / Elemento | Hito 8.3.2 (`m²`) | Hito 8.3.3 (`m²`) | Variación (`m²`) | Observación geométrica |
| :--- | :---: | :---: | :---: | :--- |
| **Vano de escalera y escotilla en losa superior (`Escotilla_Techo_Marco`)** | `0,000` | **`1,980`** (`1,350` neto abierto) | `+1,980` | Abertura longitudinal `2,20 × 0,90 m` (`X = 5,55..7,75 m, Y = 5,75..6,65 m`) con descanso superior `Cubierta_Descanso_Escotilla` (`0,630 m²`, `X = 7,05..7,75 m`) y tapa metálica practicable con bisagra (`Escotilla_Techo_Puerta1`). |
| **Bypass Corredor Superior (`P2_Piso_P2_Bypass_Esc_Techo`)** | `0,000` | **`2,065`** | `+2,065` | Ensanche lateral (`0,80 m` útiles, `X = 5,15..7,85 m, Y = 6,65..7,45 m`) que rodea `Esc_Techo` dejando `0,70 m` libres en el acceso este (`X = 5,15..5,85 m`) y `2,45 m` de altura libre bajo el tramo alto en `X = 7,35 m`. |
| **Habitación Hija 2 (`P2_Piso_P2_Habitacion_Hija_2`)** | `11,780` | **`9,620`** | `-2,160` | Ajuste del tramo oeste del muro `P2_M_Banda_Norte_S4` (`Y = 7,45..7,55 m`) para alojar el bypass del corredor; conserva cama, clóset y escritorio funcionales. |
| **Cubierta Técnica transitable (servicio FV)** | `0,000` | **`78,650`** | `+78,650` | Superficie técnica exterior de mantenimiento (`80,000 m²` huella menos `1,350 m²` de hueco neto de escalera), protegida con barandas perimetrales y de escotilla (`1,05 m`). |

---

## 2. Resumen General de Superficies (`HOME_PROJECT_HITO_08_3_3.blend`)

| Concepto | Superficie (`m²`) | Estado / Nota |
| :--- | :---: | :--- |
| **Lote provisional (`8,00 × 11,25 m`)** | `90,000` | Envolvente provisional preservada |
| **Planta 1 — Área útil neta cubierta (interior + garaje + paso garaje + baño ampliado)** | **`62,338`** | **Exceso explícito de `+2,338 m²` respecto al límite referencial de `60,000 m²`** (heredado de Hito 8.3.2). |
| **Planta 1 — Área descubierta / semicubierta (acceso frontal + patio lavandería)** | `16,112` | Preservada |
| **Planta 2 — Área útil neta interior (sin cubierta técnica)** | `67,927` | Redistribuida con bypass de acceso técnico P2-03 |
| **Cubierta Técnica — Área neta de mantenimiento FV (exterior)** | `78,650` | Uso exclusivo de mantenimiento técnico (no contabilizada como área habitable interior) |
| **Proyección horizontal losa de entrepiso P2 sobre P1 (con hueco escalera)** | `76,438` | Sin cambios estructurales |
| **Proyección horizontal cubierta plana superior (huella exterior)** | `80,000` | Dentro del límite máximo de `80,00 m²` |

> **Nota regulatoria:** Las certificaciones estructurales, eléctricas y urbanísticas (POT) permanecen pendientes de aprobación profesional.
