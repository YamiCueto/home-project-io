# Modo de Inspección Arquitectónica — `ArchitecturalInspectionMode`

## 1. Objetivo

Permitir recorrer la vivienda completamente vacía (`ArchitectureOnly`) para evaluar arquitectura, proporciones, iluminación y circulaciones sin interferencia de mobiliario, vehículos, equipamiento o domótica, alternando en tiempo real con `FullFurnished` sin duplicar escenas ni geometría.

---

## 2. Organización en Blender (`HOME_PROJECT_HITO_08_3_2.blend`)

Colecciones semánticas independientes:
- **Visibles en `ARCHITECTURE_ONLY` (predeterminado):** `Arquitectura`, `Estructura`, `Puertas_Y_Ventanas`, `Contexto_Urbano`.
- **Ocultas en `ARCHITECTURE_ONLY` y visibles en `FULL_FURNISHED`:** `Mobiliario`, `Vehiculos`, `Equipamiento`, `Decoracion`, `Instalaciones`.

Todos los recursos existentes (incluidos Suzuki Swift Dzire 2023, Suzuki V-Strom 250 SX e instalación fotovoltaica) se conservan intactos y se exportan en los paquetes FBX para su activación en Unity.

---

## 3. Implementación en Unity (`ArchitecturalInspectionMode.cs`)

- **Archivo:** `unity/Assets/HomeProject/Scripts/Infrastructure/ArchitecturalInspectionMode.cs` (0 comentarios).
- **Estado inicial:** `InspectionMode.ArchitectureOnly` en `Awake()`.
- **Alternancia:** Tecla `M` (`InputSystem.devices`) sin conflicto con `WASD`, `E` (puertas), `V` (orbital), `R` (inicio) ni `Esc` (pausa).
- **Aislamiento físico y visual:**
  - En `ArchitectureOnly` desactiva `Renderer.enabled` y `Collider.enabled` de `Furniture`, `Vehicles`, `Installations` y props decorativos/equipamiento (`Veh_`, `Inst_`, `PH_Plant`, `P1_Mob_`, `P2_Mob_`, `P1_PH_`, `P2_PH_`, `Aplique_`, `Cortina`, `Tapete`, `Espejo`, `Solar`, etc.).
  - Mantiene activos el 100 % de colliders arquitectónicos (`Architecture`, `InteractiveDoors`, `UrbanContext`, `CollisionGeometry`).
- **Prevención de solapamiento con el jugador:** Antes de pasar a `FullFurnished`, `WouldOverlapPlayer(...)` verifica si `CharacterController.bounds` intersecta algún collider por reactivar (excluyendo tapetes planos `Tapete`). Si hay intersección, bloquea el cambio, conserva `ArchitectureOnly` y reporta el objeto bloqueante en el HUD (`ResidentialHudController.cs`).
