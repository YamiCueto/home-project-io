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

## 2. Acceso Técnico a Cubierta y Mantenimiento FV (P2-03)

- **Abertura, brocal y escotilla:** Vano real en losa superior (`X = 5,55..7,75 m, Y = 5,75..6,65 m`, `1,350 m²` neto abierto + `0,630 m²` de descanso superior `Cubierta_Descanso_Escotilla`) con brocal hueco impermeabilizado (`Escotilla_Techo_Marco`), cierre (`Escotilla_Techo_Cierre`) y tapa metálica practicable con bisagra (`Escotilla_Techo_Puerta1`, rotación `+88°` con tecla `E`).
- **Escalera técnica (`Esc_Techo_Peldano_01..13`) y pasillo P2:**
  - `13` peldaños metálicos desde `X = 5,85 m` (`Z = 2,94 m`) hasta `X = 7,05 m` (`Z = 5,88 m`) con `0,80 m` de ancho entre ejes de baranda (`0,79 m` libres entre `Esc_Techo_Baranda_Sur` y `Norte`).
  - Se amplió `Corredor Superior` mediante un bypass norte (`P2_Piso_P2_Bypass_Esc_Techo`, `X = 5,15..7,85 m, Y = 6,65..7,45 m`) que deja `0,70 m` libres al este del arranque (`X = 5,15..5,85 m`) y `2,45 m` de altura libre bajo el tramo alto (`X = 7,35 m`), preservando el paso hacia todas las habitaciones de P2.
  - Se desplazó `Solar_Canalizacion` (`-0,90 m` en X) y se recortaron `Zona_Paneles_Solares_Base` (`Y = 5,50 m`) e `Inst_Zona_Ampliacion_Solar` (`X = 5,70 m`) para eliminar interferencias con el vano.
- **Protección contra caídas y drenaje:** Barandas perimetrales abiertas de postes y pasamanos (`Baranda_Cubierta_*`, `1,05 m` sobre cubierta) y baranda de escotilla (`Baranda_Escotilla_Oeste/Este/Norte` con salida sur hacia cubierta), canal de drenaje (`Cubierta_Canal_Drenaje`), sumidero (`Cubierta_Sumidero_NE`) y solapas impermeabilizantes (`Cubierta_Solapa_*`). Paneles `Solar_*` visibles en ambos modos (`ArchitectureOnly` y `FullFurnished`).
- **Evidencias visuales:** `renders/hito_08_3_3/CUBIERTA_ACCESO_CERRADO.png`, `renders/hito_08_3_3/CUBIERTA_ACCESO_ABIERTO.png`, `renders/hito_08_3_3/18_ZONA_Cubierta_Tecnica.png`.

### Evaluación física y arquitectónica honesta de `Esc_Techo`

- **Parámetros geométricos medidos:** Desarrollo horizontal `1,20 m` (`X = 5,85..7,05 m`), desnivel vertical `2,94 m`, `13` peldaños (`contrahuella = 0,226 m`, `huella neta = 0,092 m` / `0,132 m` con solape de `0,04 m`), inclinación **`67,8°`**, ancho útil **`0,79 m`**, altura libre `>= 2,04 m`.
- **Controlador FPS:** Se conservó íntegra la cápsula humana (`height = 1,80 m, radius = 0,30 m`) y `stepOffset = 0,25 m`; debido a la compacidad del tramo de servicio (`67,8°`), se ajustó `slopeLimit = 70f` sobre la rampa de colisión continua `COL_Esc_Techo_Rampa` (alineada 1:1 con `Esc_Techo_Peldano_01..13`).
- **Dictamen arquitectónico:** Es funcional para **acceso técnico ocasional de mantenimiento FV** (escalera empinada tipo servicio/barco con pasamanos bilaterales), pero **no** sustituye una escalera residencial convencional (`30°–38°`) para uso cotidiano ni está certificada normativamente sin validación profesional.

---

## 3. Resultados de Validación y Rendimiento

| Verificación | Resultado | Detalle |
| :--- | :---: | :--- |
| **Validación Blender (`HITO_08_3_3_BLENDER_VALIDATION.json`)** | **PASS** | `tropical_trees_lod_count = 9`, `roof_stair_treads = 13`, `all_passed = true` |
| **Exportación FBX (`UNITY_08_3_3_EXPORT_OK`)** | **6/6 PASS** | `mesh_match = true`, `dims_match = true` |
| **Validación Unity (`HITO_08_3_2_VALIDATION.json`)** | **PASS** | `errors = 0`, `dims = 400/400`, `pivots = 19/19`, `capsules = 8/8`, `floors = 8/8` |
| **Pruebas Negativas (`HITO_08_3_2_NEGATIVE_TESTS.json`)** | **9/9 PASS** | `all_detected = true` |
| **Pruebas EditMode** | **5/5 PASS** | Incluye 19 puertas (`Escotilla_Techo_Puerta1`), `LODGroup`, `CapsuleCollider` y viento |
| **Pruebas PlayMode** | **5/5 PASS** | Incluye `ArchitectureOnly` con árboles/solares visibles, tecla `E`, orbital, barandas y tour 18/18 |
| **Recorrido continuo (`HITO_08_3_3_NAVIGATION_TRACE.json`)** | **18/18 PASS** | `teleports = 0`, `total_time = 67,14 s`, `distance = 103,85 m`, entrada y retorno exterior OK |

### Comparativa de Rendimiento (2560 × 1440, URP 17.6.0 Forward+)

| Métrica | Línea base (Hito 8.3.1 / 8.3.2) | Hito 8.3.3 (con vegetación PBR+LOD y cubierta P2-03) | Variación |
| :--- | :---: | :---: | :---: |
| **FPS promedio** | `361,4 FPS` | **`398,8 FPS`** | `+37,4 FPS` (`+10,3 %`) |
| **Tiempo de fotograma promedio** | `2,77 ms` | **`2,51 ms`** | `-0,26 ms` |
| **Percentil P95** | `3,67 ms` | **`3,34 ms`** | `-0,33 ms` |
| **Percentil P99** | `6,83 ms` | **`6,60 ms`** | `-0,23 ms` |
| **1% low** | `85,9 FPS` | **`97,7 FPS`** | `+11,8 FPS` |

---

## 4. Entregables Actualizados

- Modelo Blender: `models/HOME_PROJECT_HITO_08_3_3.blend`
- Cuadro de Áreas V6: `docs/CUADRO_DE_AREAS_V6.md`
- Manifiesto de licencias: `assets/manifest.json`
- Validaciones y trazas: `validation/HITO_08_3_3_BLENDER_VALIDATION.json`, `validation/HITO_08_3_3_NAVIGATION_TRACE.json`, `validation/HITO_08_3_3_PERFORMANCE.json`
- Evidencias visuales: `renders/hito_08_3_3/`
