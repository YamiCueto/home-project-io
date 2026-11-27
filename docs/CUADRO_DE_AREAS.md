# Cuadro de Áreas — HOME PROJECT (Hito 1)

Datos verificados programáticamente en Blender 5.3.0 Beta mediante `scripts/build_hito_01.py` y registrados en `validation/HITO_01_VALIDATION.json`.

---

## Resumen General

| Nivel | Superficie Bruta (`m²`) | Límite Máximo (`m²`) | Estado | Muros Exteriores (`m²`) | Muros Interiores (`m²`) | Áreas Útiles + Circulación (`m²`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Planta 1** (`6,00 × 10,00 m`) | `60,000` | `60,00` | Cumple | `4,710` | `1,890` | `52,695` *(+0,705 m² en remates)* |
| **Planta 2** (`6,00 × 12,15 m`) | `72,900` | `80,00` | Cumple | `5,355` | `3,030` | `63,895` *(+0,620 m² en remates)* |
| **Total** | **`132,900`** | **`140,00`** | **Cumple** | **`10,065`** | **`4,920`** | **`116,590`** |

*(Nota: Los remates corresponden a intersecciones ortogonales y frentes de tabiques menores de `0,10 m` no duplicados en el conteo neto).*

---

## Desglose — Primera Planta (`Z = 0,00 m`)

| Espacio | Dimensiones (`X × Y` m) | Área Útil (`m²`) | Categoría |
| :--- | :---: | :---: | :--- |
| `P1_Garaje` | `3,30 × 4,55` | `15,015` | Garaje (Swift Dzire + V-Strom 250 SX) |
| `P1_Acceso_Peatonal` | `2,30 × 1,45` | `3,335` | Circulación / Acceso |
| `P1_Escalera` | `0,95 × 3,90` | `3,705` | Escalera (16 peldaños) |
| `P1_Pasillo_Acceso` | `1,25 × 3,10` | `3,875` | Circulación |
| `P1_Bano_Social` | `1,95 × 1,75` | `3,413` | Baño completo |
| `P1_Distribuidor_Huesped` | `1,25 × 1,75` | `2,188` | Circulación |
| `P1_Habitacion_Huespedes` | `2,80 × 3,20` | `8,960` | Habitación (Adulta mayor) |
| `P1_Sala` + `P1_Sala_Zona` | `1,25×0,80 + 2,30×1,95` | `5,485` | Zona social *(ajustada)* |
| `P1_Comedor` | `1,60 × 2,40` | `3,840` | Zona social |
| `P1_Cocina` | `1,20 × 2,40` | `2,880` | Servicio |
| `P1_Lavanderia_Bajo_Esc` | `0,95 × 1,40` | `1,330` | Servicio *(compartido bajo escalera)* |
| **Subtotal neto Planta 1** | — | **`52,695`** | *(sin doble conteo de lavandería bajo escalera)* |

---

## Desglose — Segunda Planta (`Z = 2,90 m`)

| Espacio | Dimensiones (`X × Y` m) | Área Útil (`m²`) | Categoría |
| :--- | :---: | :---: | :--- |
| `P2_Habitacion_Principal` | `3,30 × 4,30` | `14,190` | Habitación (vista a calle `Y-`) |
| `P2_Balcon` | `2,30 × 1,35` | `3,105` | Balcón (retranqueado en huella) |
| `P2_Escalera_Hueco` | `0,95 × 3,90` | `3,705` | Hueco escalera (alineado con P1) |
| `P2_Distribuidor_Norte` | `1,25 × 3,90` | `4,875` | Circulación |
| `P2_Bano_Principal` | `1,80 × 2,20` | `3,960` | Baño privado completo |
| `P2_Vestidor_Principal` | `1,40 × 2,20` | `3,080` | Vestidor |
| `P2_Distribuidor_Central` | `2,30 × 1,25` | `2,875` | Circulación |
| `P2_Bano_Compartido` | `2,25 × 1,75` | `3,938` | Baño completo compartido |
| `P2_Corredor_Hijas` | `1,05 × 1,75` | `1,838` | Circulación |
| `P2_Estudio_Blancos` | `2,20 × 1,75` | `3,850` | Estudio / Blancos |
| `P2_Habitacion_Hija_1` | `2,80 × 3,30` | `9,240` | Habitación |
| `P2_Habitacion_Hija_2` | `2,80 × 3,30` | `9,240` | Habitación |
| **Subtotal neto Planta 2** | — | **`63,895`** | — |
