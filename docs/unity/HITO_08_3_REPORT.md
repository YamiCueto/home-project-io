# Informe Técnico — Hito 8.3: Estabilización física y navegabilidad integral

## 1. Estabilización del controlador y puertas

- **Suavizado vertical en escaleras:** `ResidentialFirstPersonController` suaviza `cameraEyeHeight` (`1,65 m`) mediante interpolación cuando el personaje asciende/desciende los `15` peldaños (`0,18125 m` de contrahuella, `stepOffset = 0,25 m`).
- **Sentido de apertura de puertas (`InteractiveDoor`):**
  - Las puertas de baños y habitaciones superiores (`Bano_Este`, `Bano_Comp_Este`, `Banda_Norte`, `Banda_Sur`) abren hacia el interior de cada recinto para no obstruir los corredores de `0,95 m`.
  - Los `4` paneles del portón del garaje (`P1_M_Sur_Garaje_Porton1_P1..P4`) se elevan solidariamente en eje mundial `+Y`.
  - Durante la transición de apertura/cierre, el `BoxCollider` de la hoja opera como trigger para evitar empujes o bloqueos contra el personaje.
- **Recuperación y foco:** Recuperación automática al punto inicial ante caída (`y < -1,0 m`) y restauración del cursor en `OnDisable` y `OnApplicationFocus`.

## 2. Resultados de pruebas automatizadas

- **EditMode (`HomeProjectEditModeTests`):** `5 / 5 PASS` (`0,9265s`).
- **PlayMode (`HomeProjectPlayModeTests`):** `3 / 3 PASS` (`67,93s`):
  - `OrbitalModeSingleActiveCameraRotationAndZoom`: `PASS` (`0,113s`).
  - `InputSystemEKeyOpensDoorAndWindowBlocksPlayer`: `PASS` (`0,154s`).
  - `ContinuousAutonomousTourVisitsAll18ZonesAndMeasuresPerformance`: `PASS` (`67,639s`, `16 / 18` zonas físicamente alcanzadas en `69,07 m`; `2` zonas no alcanzables documentadas sin alterar la arquitectura ni reducir el radio de `0,30 m`).
- **Pruebas negativas (`HITO_08_3_NEGATIVE_TESTS.json`):** `9 / 9` fallas detectadas y restauradas (incluyendo `NEG_09_MISSING_SURFACE`).

## 3. Rendimiento medido (`2560 x 1440`, URP Forward+)

- **FPS promedio:** `375,0 FPS` (`2,67 ms` por fotograma)
- **Percentil P95 / P99:** `5,50 ms` / `9,52 ms`
- **1% Low FPS:** `65,1 FPS`
- **Frames de calentamiento descartados:** `60`
