# Auditoría de Aprovechamiento Espacial — Hito 8.3.2 (`ArchitectureOnly`)

## 1. Alcance de la Inspección

Inspección integral de Planta 1 y Planta 2 con la vivienda completamente vacía (`InspectionMode.ArchitectureOnly` en Unity y colección oculta en Blender `HOME_PROJECT_HITO_08_3_2.blend`).

---

## 2. Intervenciones Ejecutadas

1. **P1-01 — Eliminación de espacio residual junto al Baño Social:**
   - Se detectó un recinto cerrado e inaccesible de `2,00 × 1,30 m` (`2,60 m²`) al norte de `P1_M_Bano_Norte_S0` (`X = 0,15..2,15 m, Y = 6,75..8,05 m`).
   - Se eliminó `P1_M_Bano_Norte_S0`, se prolongó `P1_M_Bano_Este_S2` hasta `Y = 8,05 m` y se amplió `P1_Piso_P1_Bano_Social` a `6,27 m²` (`1,90 × 3,30 m`), con ducha sin desnivel y radio de giro accesible para adulto mayor.
2. **P2-02 — Eliminación de balcón esquinero y optimización de Suite Principal:**
   - Se suprimió el balcón esquinero (`4,875 m²`), `P2_M_Balcon_Norte_S0` y la puerta redundante `P2_M_Master_Este_Puerta1`.
   - Se consolidó la secuencia **Dormitorio Principal (`19,575 m²`) → Vestier de paso (`6,525 m²`) → Baño Principal (`7,650 m²`)**, manteniendo la huella P2 en `80,00 m²` y rediseñando la fachada sur con ventana alta de privacidad (`P2_M_Sur_Win3_*`).

---

## 3. Hallazgos Documentados Fuera de Alcance (Sin Modificación sin Aprobación)

Durante la inspección en vivienda vacía se documentan para evaluación del propietario en futuros hitos:
- **P1 — Escalera y bajo-escalera (`X = 3,10..6,85 m, Y = 4,75..5,70 m`):** El volumen inferior bajo los peldaños altos (`Z > 1,50 m`) permanece abierto hacia el garaje/comedor; podría aprovecharse como clóset de linos o alacena cerrada si el propietario lo aprueba.
- **P2 — Ventana sur del baño principal (`P2_M_Sur_Win3`):** Queda alineada con el alféizar de `4,00 m` (`1,10 m` sobre piso P2) para privacidad; en fachada sur se mantiene el contraste de vanos respecto a `P2_M_Sur_Win1`.
- **Implicaciones estructurales:** No se eliminaron columnas ni vigas portantes en este hito; `Col_P1_01..11`, `Col_P2_01..11` y `Viga_P1/P2_*` permanecen íntegras y activas.
