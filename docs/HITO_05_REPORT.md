# Informe de Cierre — Hito 5: Visualización Arquitectónica Fotorrealista

**Modelo:** [HOME_PROJECT_HITO_05.blend](file:///C:/Users/YAMI/Documents/projects/home-project/models/HOME_PROJECT_HITO_05.blend)  
**Scripts (sin comentarios):** [build_hito_05.py](file:///C:/Users/YAMI/Documents/projects/home-project/scripts/build_hito_05.py) · [render_hito_05.py](file:///C:/Users/YAMI/Documents/projects/home-project/scripts/render_hito_05.py) · [validate_hito_05.py](file:///C:/Users/YAMI/Documents/projects/home-project/scripts/validate_hito_05.py)  
**Validación JSON:** [HITO_05_VALIDATION.json](file:///C:/Users/YAMI/Documents/projects/home-project/validation/HITO_05_VALIDATION.json)

---

## 1. Auditoría Visual Hito 4 → Mejoras Aplicadas en Hito 5
1. **Mobiliario esquemático:** Se sustituyeron bloques prismáticos de comedor, sofá, cama principal y detalles de cocina por geometría subdividida (`Subsurf`), cojines suavizados, patas cilíndricas esbeltas y modificadores `Bevel` (`8–12 mm`) en toda la carpintería y mesones.
2. **Materiales planos/repetitivos:** Se actualizó `MAT_porcelanato_ext` a placas de gran formato (`0,90 × 0,90 m` con `Coat Weight 0,25`), `MAT_madera_ext` a veta natural estirada sin distorsión ondulatoria, `MAT_cuarzo_blanco` con veteado sutil y textiles con `Sheen Weight 0,65`.
3. **Iluminación y color:** Incorporación de **AgX** (`Medium High Contrast`), cielo físico `MULTIPLE_SCATTERING` (Nishita) para día y atardecer cálido, e iluminación nocturna diferenciada en `Cycles GPU OptiX` (RTX 5070 Ti).

---

## 2. Renders Insignia (`8` vistas: `2` en 4K + `6` en `2560 × 1440`)
- **Exteriores:**
  - [01_ESQUINA_DIA_4K.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05/exterior/01_ESQUINA_DIA_4K.png)
  - [02_ESQUINA_ATARDECER_4K.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05/exterior/02_ESQUINA_ATARDECER_4K.png)
  - [03_FRONTAL_NOCHE.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05/exterior/03_FRONTAL_NOCHE.png)
  - [04_AEREA_FOTOVOLTAICA.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05/exterior/04_AEREA_FOTOVOLTAICA.png)
- **Interiores:**
  - [05_SALA_CONTEMPORANEA.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05/interior/05_SALA_CONTEMPORANEA.png)
  - [06_COCINA_COMEDOR.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05/interior/06_COCINA_COMEDOR.png)
  - [07_SUITE_PRINCIPAL.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05/interior/07_SUITE_PRINCIPAL.png)
- **Presentación:**
  - [08_CORTE_ISOMETRICO_CONJUNTO.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05/architectural/08_CORTE_ISOMETRICO_CONJUNTO.png)

**Ejecución detenida al finalizar el Hito 5 en espera de aprobación explícita antes del Hito 6.**
