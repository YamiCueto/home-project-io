# Supuestos, Restricciones y Pendientes — Hito 1.1

## 1. Fotografías de Referencia
- El prompt de Hito 1.1 menciona dos fotografías de la vivienda existente (*vista frontal* y *vista en perspectiva desde la esquina*), las cuales **no fueron adjuntadas en la sesión ni se encontraban en el directorio `assets/`**.
- En consecuencia, la reconstrucción conceptual (`models/HOME_PROJECT_EXISTENTE.blend`) se basa estrictamente en las características confirmadas por el propietario y queda sujeta a ajuste tras la inspección de dichas fotografías y el levantamiento métrico en sitio.

## 2. Supuestos Geométricos Provisionales
1. **Geometría del lote (`90,00 m²`):** Se asume un lote rectangular de `8,00 m` de frente (`X`) por `11,25 m` de profundidad (`Y`). Las medidas reales de linderos deben verificarse con escritura pública y levantamiento topográfico.
2. **Construcción existente (`~6,00 m` de frente):** Se modela una crujía interior existente de `6,00 × 9,25 m` (`55,50 m²`), rodeada por una terraza frontal de `2,00 m` de fondo (`Y = 0,00..2,00`) y una terraza lateral de `2,00 m` de ancho (`X = 6,00..8,00`).
3. **Andenes y calles:** Se representan andenes públicos de `1,50 m` y calzadas de `5,00 m` únicamente como contexto gráfico exterior al cerramiento; **ninguna estructura propuesta invade espacio público ni predios vecinos**.

## 3. Criterio de Cómputo de Superficie Construida
- No se excluyen automáticamente las terrazas cubiertas ni el garaje techado del cómputo de área construida.
- En `docs/CUADRO_DE_AREAS_V2.md` y `validation/HITO_01_V2_VALIDATION.json` se presentan **ambos escenarios**:
  - **Escenario 1 (Incluyendo áreas cubiertas exteriores / garaje techado).**
  - **Escenario 2 (Solo edificación interior cerrada).**

## 4. Validaciones Pendientes (`PENDING`)
- **Urbanísticas:** Retiros obligatorios frontales/laterales, índice de ocupación (IO), índice de construcción (IC), altura máxima permitida y normativa de voladizos/portones según POT local.
- **Estructurales:** Capacidad portante del suelo, verificación de cimentación y columnas existentes vs. columnas nuevas requeridas en `X = 7,85 m` y ejes intermedios para soportar la segunda planta de `8,00 × 10,00 m`.
- **Levantamiento:** Cotas exactas de muros existentes, acometidas hidrosanitarias y eléctricas actuales.
