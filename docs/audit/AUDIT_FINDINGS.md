# Hallazgos de Auditoría Técnica Independiente — Línea Base `440412d`

**Repositorio:** `https://github.com/YamiCueto/home-project-io`  
**Commit auditado:** `440412d5dbcfedcd10437ae1bd4da516ad6327e9` (Hito 5.1)  
**Modalidad:** Inspección estática independiente (ChatGPT)

| ID | Severidad | Componente | Evidencia en Línea Base | Impacto | Solución en Hito 6 |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **AUD-01** | **Alta** | Superficies cubiertas | `validate_hito_02.py` excluía `Acceso_Peatonal` y `Lavanderia_Patio` por nombre sin verificar proyección física de losa/cubierta. | Posible discrepancia entre superficie útil neta y bruta cubierta real. | Calcular unión poligonal 2D real de `P2_Losa_Seg_*` y `Cubierta_Plana_Superior` e intersectarla geométricamente con P1. |
| **AUD-02** | **Alta** | Recorrido virtual | `validate_hito_02.py` usaba `range(0, 1153, 24)` (`49` muestras) y no fallaba sin cámara animada. | Colisiones entre fotogramas o falsos `PASS` si falta animación. | Validar los `1153` fotogramas (`0..1152`) con segmentos continuos, soporte transitable y altura libre; fallar si no hay animación. |
| **AUD-03** | **Alta** | Garaje | Solo se medía distancia estática auto-moto (`0,365 m`). | No garantizaba apertura de puertas del auto ni maniobra de entrada/salida. | Simular barrido de apertura de puertas (`65°`), pasillo libre a moto y envolvente de trayectoria hasta el portón. |
| **AUD-04** | **Alta** | Conectividad | `validate_hito_02.py` agregaba aristas explícitas al grafo BFS por nombre. | Podría reportar conectividad válida sin paso físico real. | Derivar el grafo exclusivamente de intersecciones físicas entre pisos, puertas abiertas y peldaños. |
| **AUD-05** | **Media** | Refinamiento visual | `validate_hito_05_v2.py` solo comprobaba `tv.location.x > 4.0` y `bed.location.y > 4.0`. | No demostraba ventana libre ni orientación vectorial de la cama. | Verificar proyección ortogonal del TV vs. ventana frontal y vector normal de cabecera hacia `Y-`. |
| **AUD-06** | **Media** | Integridad 4K | Solo verificaba `os.path.exists` de los 6 PNG. | No garantizaba resolución `3840 × 2160` ni integridad de archivo. | Leer cabecera IHDR real de cada PNG (`3840 × 2160`) y registrar su `SHA-256`. |
| **AUD-07** | **Media** | Licencias y procedencia | Contaba objetos con prefijo `PH_` en lugar de verificar manifiesto/autores. | Trazabilidad documental incompleta de recursos CC0. | Crear `assets/manifest.json` y validar correspondencia real de activos, licencias y texturas empaquetadas. |
| **AUD-08** | **Alta** | Reproducibilidad | `build_hito_05_v2.py` usaba rutas absolutas `C:\Users\YAMI\...` y `HOME_PROJECT_HITO_05_PH_STAGING.blend` (ignorado). | Imposible reproducir directamente tras clonar en otra máquina. | Migrar a `pathlib` relativo a la raíz del repo y crear `scripts/bootstrap_assets.py` reproducible. |
| **AUD-09** | **Media** | Compatibilidad Unity | Solo verificaba existencia de capa UV (`uv_layers`). | No demostraba exportación FBX limpia, jerarquías ni escalas al reimportar. | Crear `scripts/export_unity.py`, exportar 5 FBX + manifiestos y validar mediante reimportación en Blender. |
| **AUD-10** | **Media** | Apertura de puertas | `validate_hito_04.py` comprobaba colisión de puerta cerrada, no su arco de giro `0°–90°`. | Un mueble dentro del arco de giro bloquearía la puerta al abrir. | Simular rotación `0°–90°` de cada hoja sobre su pivote de bisagra y comprobar colisión contra mobiliario y columnas. |
