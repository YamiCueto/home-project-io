# Cuadro de Áreas V2 — HOME PROJECT (Hito 1.1)

Lote provisional: **`8,00 × 11,25 m = 90,00 m²`**.  
Datos verificados programáticamente en `validation/HITO_01_V2_VALIDATION.json`.

---

## 1. Comparativa de Escenarios de Cómputo (Planta 1 + Planta 2)

> **Escenario 1:** Incluye edificación interior cerrada + garaje techado + terrazas/lavandería cubiertas.  
> **Escenario 2:** Solo edificación interior cerrada en Planta 1 + Planta 2 completa (`80,00 m²`).

| Alternativa | P1 Interior Cerrada (`m²`) | P1 Cubiertas Ext. / Garaje (`m²`) | P1 Total Esc. 1 (`m²`) | P2 Bruta (`m²`) | Total Esc. 2 (`≤140 m²`) | Total Esc. 1 (`≤140 m²`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **A — Garaje Frontal** | `44,00` (`PASS`) | `21,30` | `65,30` (`FAIL >60`) | `80,00` (`PASS`) | **`124,00`** (`PASS`) | `145,30` (`FAIL`) |
| **B — Garaje Lateral** | `46,80` (`PASS`) | `29,50` | `76,30` (`FAIL >60`) | `80,00` (`PASS`) | **`126,80`** (`PASS`) | `156,30` (`FAIL`) |
| **C — Perimetral Optimizado** | `48,10` (`PASS`) | `25,00` | `73,10` (`FAIL >60`) | `80,00` (`PASS`) | **`128,10`** (`PASS`) | `153,10` (`FAIL`) |

*Nota: En las tres alternativas, si la normativa local computa las terrazas/garajes cubiertos dentro del límite de 60 m² de primera planta (Escenario 1), se excede el tope de 60 m² en Planta 1; bajo el Escenario 2 (edificación interior cerrada ≤ 60 m²), las tres cumplen holgadamente.*

---

## 2. Áreas Útiles por Espacio — Primera Planta

| Espacio | Alt. A (`m²`) | Alt. B (`m²`) | Alt. C (`m²`) | Observación |
| :--- | :---: | :---: | :---: | :--- |
| **Sala** | `5,41` (`FAIL <8`) | `9,64` (`PASS`) | `8,70` (`PASS`) | B y C superan los `8,00 m²` |
| **Comedor** | `4,84` | `3,53` | `4,47` | Integrado a Sala/Cocina |
| **Cocina** | `5,72` | `5,44` | `6,29` | C ofrece mayor mesón y holgura |
| **Habitación Huéspedes** | `9,60` | `10,20` | `10,20` | Accesible adulta mayor (sin gradas) |
| **Baño Social** | `3,78` | `3,88` | `3,88` | Completo con ducha `0,90×0,90 m` |
| **Escalera** | `3,71` | `3,71` | `3,71` | Alineada verticalmente con P2 |
| **Distribuidor** | `1,32` | `1,89` | `2,16` | Conecta suite huéspedes y social |
| **Garaje / Estacionamiento** | `14,09` (frontal) | `16,39` (lateral) | `13,52` (auto) + `4,81` (moto) | Swift Dzire + V-Strom a escala real |
| **Terraza / Acceso / Patio** | `17,87` | `13,86` | `14,75` | C incluye patio lateral `4,49 m²` |
| **Lavandería** | `2,65` | `3,45` | `3,45` | En patio posterior |

---

## 3. Áreas Útiles — Segunda Planta Común (`8,00 × 10,00 m = 80,00 m²`)

| Espacio | Dimensiones (`m`) | Área Útil (`m²`) | Observación |
| :--- | :---: | :---: | :--- |
| `P2_Habitacion_Principal` | `4,40 × 4,20` | `18,48` | Ventanal panorámico hacia calle (`Y-`) + puerta propia |
| `P2_Balcon` | `3,20 × 1,40` | `4,48` | Esquinero retranqueado dentro del lote |
| `P2_Vestidor_Principal` | `1,50 × 2,70` | `4,05` | Clóset `0,55 m` + pasillo libre `0,95 m` |
| `P2_Bano_Principal` | `1,60 × 2,70` | `4,32` | Completo + ventana hacia calle lateral (`X+`) |
| `P2_Bano_Compartido` | `2,15 × 1,90` | `4,09` | Acceso directo desde distribuidor |
| `P2_Habitacion_Hija_1` | `3,80 × 3,40` | `12,92` | Dimensionada hasta edad adulta |
| `P2_Habitacion_Hija_2` | `3,80 × 3,40` | `12,92` | Doble fachada (`Y+` y `X+`) |
| `P2_Distribuidor + Llegada` | — | `6,65` | Conecta todas las estancias |
| `P2_Escalera_Hueco` | `3,90 × 0,95` | `3,71` | Hueco real en losa superior |
