# Mapeo de Materiales URP — Hito 8.1

## 1. Estrategia de reconstrucción

Todos los materiales se reconstruyeron como activos persistentes `.mat` en `Assets/HomeProject/Materials/` usando el shader `Universal Render Pipeline/Lit`, remapeados mediante `ModelImporter.AddRemap` y asignados con `sharedMaterials`.

## 2. Texturas Poly Haven CC0 y conversiones PBR

- Se extrajeron `38` texturas empaquetadas desde `HOME_PROJECT_HITO_06_V2.blend` hacia `Assets/HomeProject/Textures/`.
- Se convirtieron los mapas de `Roughness` (+ `Metallic` cuando existe) al formato empacado de URP `*_MetallicSmoothness.png` (`R = Metallic`, `A = 1 - Roughness`).
- Para follaje con transparencia recortada (`potted_plant_01_leaves`, `potted_plant_02_leaves`) se combinó `_diff.png` + `_alpha.png` en `*_diff_alpha.png` con `_AlphaClip = 1` (`_Cutoff = 0.45`).
- Los mapas normales `*_nor_gl.png` y `*_gl_normal.png` se configuraron con `TextureImporterType.NormalMap`.

## 3. Bake de materiales procedurales desde Blender MCP

Los `8` materiales procedurales que no se transfieren nativamente vía FBX fueron horneados en Cycles (`512x512`, `DIFFUSE` y `ROUGHNESS`) mediante Blender MCP sin alterar el `.blend` histórico:

- `MAT_antracita` (`TEX_NOISE`) -> `MAT_antracita_diff.png`, `MAT_antracita_MetallicSmoothness.png`
- `MAT_concreto_arq` (`TEX_NOISE`) -> `MAT_concreto_arq_diff.png`, `MAT_concreto_arq_MetallicSmoothness.png`
- `MAT_cuarzo_blanco` (`TEX_NOISE`, `VALTORGB`) -> `MAT_cuarzo_blanco_diff.png`, `MAT_cuarzo_blanco_MetallicSmoothness.png`
- `MAT_estuco_blanco` (`TEX_NOISE`) -> `MAT_estuco_blanco_diff.png`, `MAT_estuco_blanco_MetallicSmoothness.png`
- `MAT_follaje_tropical` (`TEX_NOISE`) -> `MAT_follaje_tropical_diff.png`, `MAT_follaje_tropical_MetallicSmoothness.png`
- `MAT_madera_ext` (`TEX_NOISE`, `VALTORGB`) -> `MAT_madera_ext_diff.png`, `MAT_madera_ext_MetallicSmoothness.png`
- `MAT_piedra_natural` (`TEX_BRICK`) -> `MAT_piedra_natural_diff.png`, `MAT_piedra_natural_MetallicSmoothness.png`
- `MAT_porcelanato_ext` (`TEX_BRICK`) -> `MAT_porcelanato_ext_diff.png`, `MAT_porcelanato_ext_MetallicSmoothness.png`

## 4. Transparencia y emisión

- `MAT_vidrio_arq`: superficie Transparent (`_Surface = 1`), `Alpha = 0.28`, `Smoothness = 0.95`.
- `MAT_aplique_calido`, `MAT_led_indirecto`, `MAT_luz_calida`: `_EMISSION` habilitado con `_EmissionColor` escalado según `emission_strength`.
