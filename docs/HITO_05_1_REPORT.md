# Informe de Cierre — Hito 5.1: Refinamiento Visual y Funcional

**Modelo:** [HOME_PROJECT_HITO_05_V2.blend](file:///C:/Users/YAMI/Documents/projects/home-project/models/HOME_PROJECT_HITO_05_V2.blend)  
**Scripts (sin comentarios):** [build_hito_05_v2.py](file:///C:/Users/YAMI/Documents/projects/home-project/scripts/build_hito_05_v2.py) · [validate_hito_05_v2.py](file:///C:/Users/YAMI/Documents/projects/home-project/scripts/validate_hito_05_v2.py)  
**Validación JSON:** [HITO_05_V2_VALIDATION.json](file:///C:/Users/YAMI/Documents/projects/home-project/validation/HITO_05_V2_VALIDATION.json)

---

## 1. Mejoras Ejecutadas
- **Integración Poly Haven (CC0):** Importados `wide_street_01` (HDRI), `concrete_pavement_03`, `asphalt_02`, `dark_wood` (PBR 2K) y modelos 3D (`modern_coffee_table_01`, `dining_chair_02`, `side_table_01`, `potted_plant_01`, `potted_plant_02`).
- **Correcciones funcionales:** TV 65" reubicado al muro este de la Sala (`X = 4,38 m`), liberando completamente el ventanal frontal; cama King Size reorientada con cabecero en `Y = 4,55 m` mirando hacia el ventanal frontal y la calle, conservando `> 1,10 m` de circulación lateral; cortinas de piso a techo agregadas.
- **Contextualización urbana (`17_Contexto_Urbano`):** Bordillos, señalización vial, viviendas vecinas genéricas y arbolado urbano; linderos rojos ocultos en renders comerciales (`hide_render = True`).
- **Instalación fotovoltaica refinada:** `6` paneles con marcos de aluminio, celdas fotovoltaicas, vidrio protector, soportes inclinados a `10°` y canalización hacia tablero.
- **Iluminación nocturna corregida:** Apliques cálidos (`2700–3000K`) + iluminación urbana, logrando lectura clara de volúmenes y materiales.

---

## 2. Renders 4K (`3840 × 2160` Cycles OptiX + AgX)
- [01_ESQUINA_DIA_4K.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05_v2/01_ESQUINA_DIA_4K.png) (`11,71 s`)
- [02_ESQUINA_NOCHE_4K.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05_v2/02_ESQUINA_NOCHE_4K.png) (`9,17 s`)
- [03_SALA_CONTEMPORANEA_4K.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05_v2/03_SALA_CONTEMPORANEA_4K.png) (`21,86 s`)
- [04_COCINA_COMEDOR_4K.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05_v2/04_COCINA_COMEDOR_4K.png) (`19,59 s`)
- [05_SUITE_PRINCIPAL_4K.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05_v2/05_SUITE_PRINCIPAL_4K.png) (`21,39 s`)
- [06_CUBIERTA_FOTOVOLTAICA_4K.png](file:///C:/Users/YAMI/Documents/projects/home-project/renders/hito_05_v2/06_CUBIERTA_FOTOVOLTAICA_4K.png) (`7,84 s`)

**Ejecución detenida antes del Hito 6.**
