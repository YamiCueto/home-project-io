# Informe Técnico — Hito 8.2: Navegación residencial en primera persona

## 1. Controlador en primera persona (`ResidentialFirstPersonController`)

Implementado con `CharacterController` y **Unity Input System** (`Keyboard`, `Mouse`) sin mecánicas de videojuego innecesarias:

- **Altura del personaje:** `1.80 m`
- **Altura de cámara:** `1.65 m`
- **Radio:** `0.30 m`
- **Velocidad de caminata:** `1.60 m/s` (independiente de `Time.deltaTime`)
- **Gravedad:** `-9.81 m/s²`
- **Step Offset:** `0.25 m` (calibrado para peldaños reales de `0.18125 m` de contrahuella)
- **Controles:** `WASD` (desplazamiento), `Ratón` (orientación), `E` (abrir/cerrar puertas), `V` (modo orbital exterior), `R` (volver al punto inicial), `Escape` (liberar cursor y pausar).

## 2. Puertas interactivas y modos de cámara

- **`InteractiveDoor`:** `17` componentes instalados sobre las hojas de puertas batientes y los `4` paneles del portón seccional del garaje, rotando/deslizando sobre sus pivotes reales exportados desde Blender.
- **`OrbitalInspectionCamera`:** Modo de inspección exterior orbital (`V`) alrededor de la vivienda con rotación y zoom.
- **`ResidentialHudController`:** Interfaz mínima con modo activo, ubicación residencial, altura en metros, FPS, tiempo de fotograma y controles.

## 3. Resultados de pruebas automatizadas y telemetría real

- **EditMode (`HomeProjectEditModeTests`):** `5 / 5 PASS` (`0.7601s`).
- **PlayMode (`HomeProjectPlayModeTests.FullFirstPersonNavigationAndPhysicsVerification`):** `1 / 1 PASS` (`10.54s`).
  - Bloqueo por puerta cerrada (`P1_M_Sur_Sala_Puerta1`): `PASS`
  - Apertura e ingreso a `Sala`: `PASS`
  - Bloqueo por muro oeste (`P1_M_Oeste_S0`): `PASS`
  - Ascenso completo por escalera hasta `P2` (`stair_top_y = 2.96 m`): `PASS`
  - Descenso completo hasta `P1` (`stair_bottom_y = 0.06 m`): `PASS`
  - Retorno al punto inicial (`R`): `PASS`
- **Pruebas negativas (`HITO_08_2_NEGATIVE_TESTS.json`):** `8 / 8` fallas detectadas y restauradas.
- **Rendimiento medido en PlayMode (`HITO_08_2_PLAYMODE_METRICS.json`):**
  - **Resolución:** `2560 x 1440` (URP `17.6.0`, Forward+, HDR, MSAA 4x, SSAO, sombras `4096px`)
  - **FPS promedio:** `422.6 FPS` (`2.59 ms` por fotograma; mínimo inicial durante carga: `2.6 FPS`)
