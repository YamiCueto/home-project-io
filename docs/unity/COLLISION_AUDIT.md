# Auditoría de Colisiones — Hito 8.1

## 1. Configuración de `CollisionGeometry`

- Los `127` objetos de `colliders.fbx` se instanciaron bajo `HOME_PROJECT/CollisionGeometry` en la capa dedicada `CollisionGeometry`.
- Todos los `MeshRenderer` de `CollisionGeometry` permanecen deshabilitados (`enabled = false`) tanto en edición como al iniciar `PlayMode` (`HomeProjectSystemInitializer`), garantizando `0` colliders visibles.
- Las geometrías prismáticas simples utilizan `BoxCollider` (`144` en total incluyendo puertas) y las mallas complejas de mobiliario y vehículos utilizan `MeshCollider` estático (`103` en total), sumando `247` colliders en la escena.

## 2. Auditoría de aberturas transitables (`Physics.OverlapBox`)

Se evaluaron `17 / 17` aberturas de puertas y paneles del portón del garaje frente a la capa `CollisionGeometry` (`half_extents = [0.08, 0.20, 0.08]` m):

- **Aberturas libres de bloqueo:** `17 / 17` (`PASS`).
- **Prueba en PlayMode (`HomeProjectPlayModeTests`):**
  - Raycast vertical sobre `P1_Piso_P1_Sala` confirma superficie transitable.
  - `Physics.OverlapBox` sobre `P1_M_Sur_Sala_Puerta1` confirma paso libre en ejecución.
