# Informe de Cierre — Hito 3: Fachadas y Envolvente Arquitectónica

**Modelo:** [HOME_PROJECT_HITO_03.blend](file:///C:/Users/YAMI/Documents/projects/home-project/models/HOME_PROJECT_HITO_03.blend)  
**Scripts (sin comentarios):** [build_hito_03.py](file:///C:/Users/YAMI/Documents/projects/home-project/scripts/build_hito_03.py) · [validate_hito_03.py](file:///C:/Users/YAMI/Documents/projects/home-project/scripts/validate_hito_03.py)  
**Validación JSON:** [HITO_03_VALIDATION.json](file:///C:/Users/YAMI/Documents/projects/home-project/validation/HITO_03_VALIDATION.json)

---

## 1. Resumen de Implementación
- **Limpieza geométrica (3.0):** Eliminada la coplanaridad entre columnas/vigas y muros exteriores mediante retranqueo estructural de `1,5 cm`, preservando intactos los huecos de puertas, ventanas y escaleras de la distribución V3/Hito 2.
- **Fachada principal (3.1):** Garaje frontal derecho con portón seccional gris antracita, acceso peatonal independiente izquierdo con puerta en madera, ventanal panorámico en habitación principal, balcón con baranda de vidrio y perfilería negra, volúmenes contemporáneos, piedra natural e iluminación cálida.
- **Fachada lateral (3.2):** Ventanas alineadas hacia la Calle de la Esquina (`X+`), celosías verticales de madera para privacidad y control solar, aleros de protección climática y vegetación tropical dentro del perímetro privado (`0` accesos vehiculares laterales).
- **Materiales PBR (3.3):** `21` materiales PBR procedurales documentados en [CATALOGO_MATERIALES.md](file:///C:/Users/YAMI/Documents/projects/home-project/docs/CATALOGO_MATERIALES.md).
- **Cubierta y clima (3.4):** Cubierta plana con pendiente conceptual de drenaje, pretil perimetral, bajante pluvial en esquina y zona reservada para `6` paneles solares.
- **Renderizado Cycles + NVIDIA OptiX (3.5):** Ejecutado en **RTX 5070 Ti** con denoiser `OPTIX` (prueba `1280×720` + `6` vistas finales a `2560×1440`).

---

## 2. Evidencias Visuales (`2560 × 1440` Cycles OptiX)
- [HITO_03_FRONTAL_DIA.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_03_FRONTAL_DIA.png)
- [HITO_03_LATERAL_DIA.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_03_LATERAL_DIA.png)
- [HITO_03_ESQUINA_DIA.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_03_ESQUINA_DIA.png)
- [HITO_03_FRONTAL_NOCHE.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_03_FRONTAL_NOCHE.png)
- [HITO_03_ESQUINA_NOCHE.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_03_ESQUINA_NOCHE.png)
- [HITO_03_AEREA.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_03_AEREA.png)

**Ejecución detenida al finalizar el Hito 3 en espera de aprobación explícita.**
