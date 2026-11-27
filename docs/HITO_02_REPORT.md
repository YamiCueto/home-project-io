# Informe de Cierre — Hito 2: Volumetría Arquitectónica y Corrección Geométrica

**Modelo principal:** [HOME_PROJECT_HITO_02.blend](file:///C:/Users/YAMI/Documents/projects/home-project/models/HOME_PROJECT_HITO_02.blend)  
**Scripts reproducibles (sin comentarios):** [build_hito_02.py](file:///C:/Users/YAMI/Documents/projects/home-project/scripts/build_hito_02.py) · [validate_hito_02.py](file:///C:/Users/YAMI/Documents/projects/home-project/scripts/validate_hito_02.py)  
**Validación JSON:** [HITO_02_VALIDATION.json](file:///C:/Users/YAMI/Documents/projects/home-project/validation/HITO_02_VALIDATION.json)

---

## 1. Resumen de Ejecución por Subhito
- **2.0 Validaciones:** Eliminados valores `True` fijos; implementadas comprobaciones geométricas reales por unión poligonal 2D, conectividad desde aberturas reales, detección de duplicados y colisión de agente peatonal.
- **2.1 Muros y cerramientos:** Volumetría completa de dos plantas (`2,70 m` altura libre c/u), losa de entrepiso (`0,20 m`), cubierta plana y pretil.
- **2.2 Escaleras funcionales:** Desembarco superior ampliado a **`1,00 m`** (`15` peldaños, altura libre mínima **`2,881 m`**, barandas de seguridad en P2).
- **2.3 Estructura conceptual:** Columnas (`0,25 × 0,25 m`) y vigas (`0,25 × 0,35 m`) dentro de los linderos `[0,00..8,00] × [0,00..11,25]`, sin interferencias con puertas o vehículos.
- **2.4 Garaje funcional:** Portón seccional de 4 paneles hacia Calle Principal (`Y-`), Swift Dzire 2023 y V-Strom 250 SX a escala real en `3,25 × 4,50 m`.
- **2.5 Recorrido virtual:** `11` cámaras en `13_Recorrido_Virtual` a `1,65 m` + animación MP4 preliminar de `48 s` (`1152` frames a `24 fps`) sin colisiones: [HITO_02_RECORRIDO_PRELIMINAR.mp4](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_02_RECORRIDO_PRELIMINAR.mp4).
- **2.6 Presentación arquitectónica:**
  - [HITO_02_FACHADA_FRONTAL.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_02_FACHADA_FRONTAL.png)
  - [HITO_02_FACHADA_LATERAL.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_02_FACHADA_LATERAL.png)
  - [HITO_02_ESQUINA.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_02_ESQUINA.png)
  - [HITO_02_CORTE_ESCALERA.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_02_CORTE_ESCALERA.png)
  - [HITO_02_PLANTA_01.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_02_PLANTA_01.png)
  - [HITO_02_PLANTA_02.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/HITO_02_PLANTA_02.png)

**Ejecución detenida en espera de aprobación explícita antes de iniciar el Hito 3.**
