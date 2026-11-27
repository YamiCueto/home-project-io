# Validación de Importación y Dimensionalidad — Hito 8.1

## 1. Paquetes FBX verificados

| Paquete FBX | Ubicación en Unity | Tamaño | Estado |
|---|---|---|---|
| `architecture.fbx` | `Assets/HomeProject/Architecture/architecture.fbx` | `96,390,316` B | Binario real |
| `furniture.fbx` | `Assets/HomeProject/Furniture/furniture.fbx` | `28,963,724` B | Binario real |
| `urban_context.fbx` | `Assets/HomeProject/Environment/urban_context.fbx` | `20,269,564` B | Binario real |
| `colliders.fbx` | `Assets/HomeProject/Colliders/colliders.fbx` | `259,132` B | Binario real |
| `interactive_doors.fbx` | `Assets/HomeProject/Architecture/interactive_doors.fbx` | `64,588` B | Binario real |
| `installations.fbx` | `Assets/HomeProject/Installations/installations.fbx` | `55,788` B | Binario real |

## 2. Conversión de coordenadas y escala métrica

- **Escala:** `globalScale = 1.0f`, `useFileScale = true` (métrica 1:1).
- **Conversión de ejes:** Blender Z-Up `(X, Y, Z)` hacia Unity Y-Up `(-X, Z, -Y)` preservada en todos los paquetes sin centrado individual.
- **Tolerancia dimensional:** `0.02 m` (`2 cm`).

## 3. Resultados de validación (`validation/HITO_08_1_VALIDATION.json`)

- **Objetos validados dentro de tolerancia:** `468 / 468` (`0` fallos en elementos arquitectónicos, losas, muros, columnas, vigas, escaleras, puertas, ventanas, vehículos, mobiliario relevante y paneles fotovoltaicos).
- **Pivotes de puertas interactivas (`doors_pivots_manifest.json`):** `17 / 17` puertas y paneles del portón verificados dentro de tolerancia.
- **Excepción documentada:** `3` sub-mallas decorativas (`PH_Plant1_*_potted_plant_01_pebbles`) con diferencia de `0.4813 m` heredada del export FBX de Hito 6.1, reportadas en `warnings`.
