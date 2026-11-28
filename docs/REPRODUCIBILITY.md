# Guía de Reproducibilidad — HOME PROJECT (Hito 6)

## 1. Requisitos del Entorno
- **Blender:** `5.3.0 Beta` (o superior compatible con `AgX` y `Cycles OPTIX` / `CPU`).
- **Python:** Integrado en Blender (`bpy`, `bmesh`, `mathutils`, `pathlib`, `json`, `hashlib`, `struct`).
- **Git & Git LFS:** `git-lfs >= 3.0` para descarga automática de modelos `.blend` y `.fbx`.
- **MCP (opcional para re-descarga):** `MCP for Blender 2.0` con **Poly Haven** habilitado (`CC0`).

## 2. Reconstrucción desde un Clon Limpio
```bash
git clone https://github.com/YamiCueto/home-project-io.git
cd home-project-io
git lfs pull
```
1. Abrir `models/HOME_PROJECT_HITO_06.blend` en Blender (las `38` texturas de Poly Haven están empaquetadas internamente y catalogadas en `assets/manifest.json`).
2. Ejecutar verificación de activos y manifiesto:
   ```python
   exec(open("scripts/bootstrap_assets.py", encoding="utf-8").read())
   ```
3. Ejecutar auditoría geométrica completa (`AUD-01`..`AUD-10`):
   ```python
   exec(open("scripts/validate_hito_06.py", encoding="utf-8").read())
   ```
4. Ejecutar pruebas negativas de regresión (`9` casos controlados):
   ```python
   exec(open("tests/test_negative_regressions.py", encoding="utf-8").read())
   ```
5. Exportar y verificar FBX para Unity:
   ```python
   exec(open("scripts/export_unity.py", encoding="utf-8").read())
   ```
