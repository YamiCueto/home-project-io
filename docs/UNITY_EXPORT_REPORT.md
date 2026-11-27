# Informe de Exportación de Prueba a Unity (FBX) — Hito 6

**Script:** [export_unity.py](file:///C:/Users/YAMI/Documents/projects/home-project/scripts/export_unity.py)  
**Verificación por reimportación:** [fbx_reimport_verification.json](file:///C:/Users/YAMI/Documents/projects/home-project/exports/unity/fbx_reimport_verification.json)

---

## 1. Paquetes FBX Exportados (`exports/unity/`)
Configuración aplicada: `FBX_SCALE_UNITS`, `axis_forward='-Z'`, `axis_up='Y'`, texturas embebidas (`path_mode='COPY'`, `embed_textures=True`).

| Archivo FBX | Mallas Exportadas | Mallas Reimportadas | Coincidencia | Tamaño (`KB`) |
| :--- | :---: | :---: | :---: | :---: |
| `architecture.fbx` | `312` | `312` | **`true`** | `94.128,87` |
| `furniture.fbx` | `101` | `101` | **`true`** | `28.279,59` |
| `interactive_doors.fbx` | `17` | `17` | **`true`** | `63,07` |
| `urban_context.fbx` | `25` | `25` | **`true`** | `19.794,50` |

## 2. Manifiestos Generados
- `exports/unity/materials_manifest.json`
- `exports/unity/doors_pivots_manifest.json` (`17` puertas/paneles con pivote en bisagra y dimensiones en metros)
- `exports/unity/objects_manifest.json`

> **Nota:** La compatibilidad efectiva dentro del motor Unity se confirmará en el **Hito 8** al importar estos paquetes dentro de un proyecto Unity.
