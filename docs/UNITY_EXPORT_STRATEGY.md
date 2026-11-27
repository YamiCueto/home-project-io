# Estrategia de Exportación a Unity (FBX) — HOME PROJECT

## 1. Estándares Aplicados en `HOME_PROJECT_HITO_01_V3.blend`

- **Escala real:** `1 unidad Blender = 1 metro` (`unit_settings.system = "METRIC"`), transformaciones aplicadas (`scale = (1, 1, 1)`).
- **Orientación de normales:** Todas las mallas procesadas con `bmesh.ops.recalc_face_normals` hacia el exterior.
- **Sin geometría duplicada:** Se eliminó la planta comparativa duplicada del archivo principal; cada elemento existe una única vez en su coordenada 3D real.
- **Separación por colecciones:**
  - Arquitectura: `07_Propuesta_Primera_Planta`, `08_Propuesta_Segunda_Planta`, `09_Estructura_Conceptual`.
  - Mobiliario y vehículos: `10_Vehiculos`, `11_Mobiliario`.
  - Cámaras de recorrido virtual: `13_Recorrido_Virtual` (11 cámaras a `1,65 m` sobre nivel de piso terminado).
- **Puertas interactivas (`*_Puerta*`):** Creadas como objetos independientes con su **origen/pivote exacto en la bisagra**, listas para animación o scripts `Rotate` en Unity sobre el eje vertical.
- **Ventanas independientes (`*_Win*`):** Separadas de los muros para asignación de shader transparente en Unity URP/HDRP.
- **Materiales compatibles:** Basados en `Principled BSDF` estándar con identificadores únicos `MAT_*`.

## 2. Flujo Recomendado para Exportación Futura (Hito Posterior)
1. Exportar mediante `File > Export > FBX (.fbx)` con `Apply Scalings: FBX Units Scale`, `Forward: -Z Forward`, `Up: Y Up`.
2. Generar colliders tipo *Mesh Collider* (o *Box Collider* por muro/losa) para la arquitectura y *Box Collider* para mobiliario.
3. Configurar controlador *First Person* en Unity con altura de cámara `1,65 m` y radio de cápsula `0,35 m`, validando los mismos `11` puntos de vista definidos en `13_Recorrido_Virtual`.
