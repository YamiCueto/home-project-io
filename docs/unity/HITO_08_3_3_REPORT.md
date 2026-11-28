# Informe Técnico — HOME PROJECT Hito 8.3.3

**Rama:** `feature/hito-08-3-3-rooftop-landscape` (base: `feature/hito-08-3-2-spatial-optimization`)  
**Entorno:** Blender 5.3.0 Beta + Blender MCP | Unity 6000.6.11f1 (URP 17.6.0 Forward+) + Unity MCP | DirectX 12 | NVIDIA RTX 5070 Ti Laptop GPU

---

## 1. Refinamiento de Vegetación Tropical y Contexto Urbano

- **Modelos CC0 Poly Haven (Soledad, Atlántico):** Se reemplazaron los árboles geométricos básicos (`Arbol_Urbano_*`) por tres ejemplares realistas (`Arbol_Tropical_01` y `03` basados en `tree_small_02`; `Arbol_Tropical_02` basado en `island_tree_02`), con variaciones de escala, orientación y posición sin interferir con fachadas, ventanas, acceso peatonal ni portón de garaje.
- **Materiales PBR URP + Alpha Clipping:** Se extrajeron 20 texturas PBR (diffuse, normal OpenGL, roughness y alpha) en `unity/Assets/HomeProject/Textures/Foliage/` y se integraron en `UrpMaterialBuilderService.cs` con `_AlphaClip = 1.0`, `_Cutoff = 0.45` y doble cara (`_Cull = 0.0`) para el follaje (`tree_small_02_leaves`, `island_tree_02_leaves`), proyectando sombras naturales sobre calle y andenes.
- **Optimización y Física:** Cada árbol cuenta con `LODGroup` de 3 niveles (`_LOD0` 100–35 %, `_LOD1` 35–12 %, `_LOD2` 12–2 %), `CapsuleCollider` simplificado en tronco (`radius = 0,24 m, height = 2,70 m`) y movimiento sutil por viento (`TropicalFoliageWind.cs`) sin desplazar el collider.
- **Visibilidad y Licencias:** Los árboles permanecen visibles tanto en `ArchitectureOnly` (modo predeterminado) como en `FullFurnished`. Licencias registradas en `assets/manifest.json`.
- **Evidencias visuales:** `renders/hito_08_3_3/BEFORE_EXTERIOR_VEGETATION.png` vs. `renders/hito_08_3_3/AFTER_EXTERIOR_VEGETATION.png`.

---

## 2. Acceso Técnico Retráctil a Cubierta y Mantenimiento FV (P2-03)

- **Abertura, brocal y escotilla impermeabilizada:** Vano en losa superior (`X = 5,45..6,75 m, Y = 5,80..6,60 m`, `1,040 m²` neto abierto) sobre el corredor superior, con brocal perimetral elevado `15 cm` (`Escotilla_Techo_Marco`, `Z = 5,88..6,03 m`), junta de estanqueidad (`Escotilla_Techo_Junta`), cierre (`Escotilla_Techo_Cierre`) y tapa metálica exterior solapada con bisagra (`Escotilla_Techo_Puerta1`, rotación `+88°`).
- **Escalera retráctil plegable de 3 tramos (`Esc_Techo_Tramo_1/2/3`) y accionamiento por tecla `E`:**
  - Compuerta inferior integrada al cielo raso (`Escotilla_Techo_Compuerta`, `Z = 5,60 m`) con cordel y tirador visibles (`Escotilla_Techo_Cordel`, `Escotilla_Techo_Tirador`, colliders `isTrigger = true` para no obstruir la circulación peatonal).
  - Tres segmentos articulados en aluminio (`1,12 m` por tramo, `4` peldaños por tramo) completamente ocultos sobre la compuerta cuando el estado es `Closed`, dejando el corredor superior 100 % despejado y restaurando `Habitación Hija 2` (`11,780 m²`) a Hito 8.3.2.
  - Máquina de estados en `RetractableAtticStair.cs` (`Closed`, `Opening`, `Open`, `Closing`) accionada mediante tecla `E` (raycast/spherecast con `QueryTriggerInteraction.Collide`), sincronizando visibilidad y colliders de despliegue y bloqueando el plegado mientras `IsPlayerOnStair()` detecte al usuario sobre la escalera.
  - Se reubicaron `Solar_Canalizacion` (`X = 5,15..5,23 m`), `Zona_Paneles_Solares_Base` (`Y = 5,50 m`) e `Inst_Zona_Ampliacion_Solar` (`X = 5,70 m`) para mantener el vano completamente libre.
- **Protección contra caídas y drenaje:** Barandas perimetrales abiertas de postes y pasamanos (`Baranda_Cubierta_*`, `1,05 m` sobre cubierta) y baranda de escotilla (`Baranda_Escotilla_Oeste/Este/Norte` con salida sur hacia cubierta), canal de drenaje (`Cubierta_Canal_Drenaje`), sumidero (`Cubierta_Sumidero_NE`) y solapas impermeabilizantes (`Cubierta_Solapa_*`). Paneles `Solar_*` visibles en ambos modos (`ArchitectureOnly` y `FullFurnished`).
- **Evidencias visuales:** `renders/hito_08_3_3/CUBIERTA_ACCESO_CERRADO.png`, `renders/hito_08_3_3/CUBIERTA_ACCESO_ABIERTO.png`, `renders/hito_08_3_3/18_ZONA_Cubierta_Tecnica.png`, y secuencia de 4 estados `renders/hito_08_3_3/ESCALERA_RETRACTIL_1_CLOSED.png` .. `4_CLOSING.png`.

### Evaluación física, arquitectónica y de exposición exterior de la escotilla

- **Controlador FPS:** Se conservó íntegra la cápsula humana (`height = 1,80 m, radius = 0,30 m`) y `stepOffset = 0,25 m`; debido a la inclinación compacta del acceso retráctil dentro del vano (`1,30 m` horizontales × `3,02 m` de desnivel), se configuró `slopeLimit = 76f` sobre `Esc_Techo_Rampa_Collider` (habilitado solo en estado `Open`) y fuerza de adherencia en descenso (`verticalVelocity = -6,0f`), permitiendo ascenso y descenso continuos sin teletransportes.
- **Exposición exterior e impermeabilización:** El brocal elevado (`15 cm` sobre losa) combinado con solapa de tapa metálica (`+3 cm` perimetrales), junta elastomérica (`Escotilla_Techo_Junta`) y pendiente/canal de drenaje evita empozamientos directos sobre el vano; para exposición climática real en Soledad, Atlántico (lluvias tropicales y radiación UV), se recomienda especificar burlete EPDM continuo, sello de poliuretano en la unión losa-brocal y acabado marino/anodizado de aluminio en obra.
- **Dictamen arquitectónico:** Adecuada exclusivamente para **acceso técnico ocasional de mantenimiento FV**, preservando al 100 % la habitabilidad y circulación del corredor superior cuando permanece plegada.

---

## 3. Resultados de Validación y Rendimiento

| Verificación | Resultado | Detalle |
| :--- | :---: | :--- |
| **Validación Blender (`HITO_08_3_3_BLENDER_VALIDATION.json`)** | **PASS** | `tropical_trees_lod_count = 9`, `roof_stair_segments = 3`, `all_passed = true` |
| **Exportación FBX (`UNITY_08_3_3_EXPORT_OK`)** | **6/6 PASS** | `mesh_match = true`, `dims_match = true` |
| **Validación Unity (`HITO_08_3_2_VALIDATION.json`)** | **PASS** | `errors = 0`, `dims = 389/389`, `negative_tests = 9/9` |
| **Pruebas Negativas (`HITO_08_3_2_NEGATIVE_TESTS.json`)** | **9/9 PASS** | `all_detected = true` |
| **Pruebas EditMode** | **5/5 PASS** | Incluye `RetractableAtticStair` en estado `Closed`, 19 puertas (`Escotilla_Techo_Puerta1`), `LODGroup` y viento |
| **Pruebas PlayMode** | **5/5 PASS** | Incluye 4 estados de escalera retráctil, bloqueo de plegado con jugador encima, tecla `E` en cordel, orbital y tour 18/18 |
| **Recorrido continuo (`HITO_08_3_3_NAVIGATION_TRACE.json`)** | **18/18 PASS** | `teleports = 0`, `total_time = 65,37 s`, `distance = 102,94 m`, entrada y retorno exterior OK |

### Comparativa de Rendimiento (2560 × 1440, URP 17.6.0 Forward+)

| Métrica | Línea base (Hito 8.3.1 / 8.3.2) | Hito 8.3.3 (con vegetación PBR+LOD y escalera retráctil) | Variación |
| :--- | :---: | :---: | :---: |
| **FPS promedio** | `361,4 FPS` | **`334,1 FPS`** | `-27,3 FPS` |
| **Tiempo de fotograma promedio** | `2,77 ms` | **`2,99 ms`** | `+0,22 ms` |
| **Percentil P95** | `3,67 ms` | **`4,06 ms`** | `+0,39 ms` |
| **Percentil P99** | `6,83 ms` | **`7,55 ms`** | `+0,72 ms` |
| **1% low** | `85,9 FPS` | **`86,4 FPS`** | `+0,5 FPS` |

---

## 4. Entregables Actualizados

- Modelo Blender: `models/HOME_PROJECT_HITO_08_3_3.blend`
- Cuadro de Áreas V6: `docs/CUADRO_DE_AREAS_V6.md`
- Manifiesto de licencias: `assets/manifest.json`
- Validaciones y trazas: `validation/HITO_08_3_3_BLENDER_VALIDATION.json`, `validation/HITO_08_3_3_NAVIGATION_TRACE.json`, `validation/HITO_08_3_3_PERFORMANCE.json`
- Evidencias visuales: `renders/hito_08_3_3/`
