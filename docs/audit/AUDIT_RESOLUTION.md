# Resolución de Hallazgos de Auditoría — Hito 6

| ID | Estado | Evidencia de Resolución |
| :--- | :---: | :--- |
| **AUD-01** | **RESOLVED** *(con nota urbanística)* | `validate_hito_06.py` calcula la unión poligonal 2D real de `P2_Losa_Seg_*` (`75,898 m²`) y `Cubierta_Plana_Superior` (`80,000 m²`) sobre P1: `67,490 m²` netos cubiertos y `8,360 m²` descubiertos (`75,850 m²` totales). Documentado que `67,490 m² > 60 m²` si se computan garaje y acceso bajo losa superior (`POT: PENDING`). |
| **AUD-02** | **RESOLVED** | `validate_hito_06.py` inspecciona los `1153` fotogramas (`0..1152`) con interpolación continua, verifica piso transitable debajo y falla si falta cámara o animación (`PASS`; detectó y corrigió el pasillo faltante `P1_Pasillo_Huesped` y la trayectoria diagonal P2). |
| **AUD-03** | **RESOLVED** | Verificado barrido de puerta del conductor (`65°` / `0,35 m` libre sin colisionar con la V-Strom) y corredor independiente de salida de motocicleta hasta el portón (`PASS`). |
| **AUD-04** | **RESOLVED** | Grafo BFS derivado exclusivamente de intersecciones físicas de pisos, puertas sin bloqueo y peldaños de escalera (`unconnected: []`). |
| **AUD-05** | **RESOLVED** | Verificada proyección `X-Z` del TV 65" (`0%` intersección con ventanal) y producto punto vectorial de la cama principal hacia `Y-` (`bed_street_dot = 1,0`). |
| **AUD-06** | **RESOLVED** | Lectura binaria de cabecera PNG IHDR (`3840 × 2160`) y cálculo `SHA-256` de los `6` renders 4K en `validation/HITO_06_VALIDATION.json`. |
| **AUD-07** | **RESOLVED** | Creado `assets/manifest.json` con `9` activos CC0, autores, URLs y `38` imágenes empaquetadas verificadas (`missing_imgs: []`, `unlicensed: []`). |
| **AUD-08** | **RESOLVED** | Eliminadas rutas absolutas de usuario; migrado a `pathlib` relativo a raíz del repositorio; creado `scripts/bootstrap_assets.py` y configurado Git LFS (`*.blend`, `*.fbx`). |
| **AUD-09** | **RESOLVED** *(parcial hasta importar en Unity)* | Exportados `4` FBX (`architecture.fbx`, `furniture.fbx`, `interactive_doors.fbx`, `urban_context.fbx`) + manifiestos y verificados mediante reimportación exacta en Blender (`100%` coincidencia de mallas). |
| **AUD-10** | **RESOLVED** | Simulación de giro `0°–90°` de las `13` puertas abatibles; detectó y corrigió la colisión de `P2_M_Vest_Bano_Puerta1` ajustando el clóset del vestidor (`door_swing_collisions: []`). |
