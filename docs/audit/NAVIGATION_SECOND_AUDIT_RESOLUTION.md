# Resolución de Segunda Auditoría de Navegabilidad — Hito 8.3.1

## Contexto

- **Repositorio:** `YamiCueto/home-project-io`
- **Rama:** `feature/hito-08-3-physics-stabilization` (PR #4)
- **Motor y pipeline:** Unity `6000.6.11f1` + `UniversalRenderPipelineAsset` (URP 17.6.0 Forward+, HDR, MSAA 4x, SSAO, Shadows 4096) + Blender 5.3.0 Beta
- **Modelo arquitectónico:** `models/HOME_PROJECT_HITO_06_V3.blend` (preservando `HOME_PROJECT_HITO_06_V2.blend` y versiones previas intactas)

---

## Cierre de hallazgos (ARQ-01 a ARQ-05, NAV-07, QA-01 y defectos de código)

| ID | Hallazgo | Resolución implementada | Evidencia / Verificación |
| :--- | :--- | :--- | :--- |
| **ARQ-01** | Murete bloquea acceso peatonal desde la calle | División de `Fach_Murete_Peatonal` en `Fach_Murete_Peatonal_Izq/Der` con abertura libre de `1.00 m`, portón articulado `Fach_Porton_Peatonal_Puerta1` (`swing_dir=-1`) y cerradura `Inst_Cerradura_Peatonal`. | `pedestrian_gate_width_m = 1.0`, `pedestrian_gate_pass = true`, `exterior_entry_passed = true` |
| **ARQ-02** | Cocina inaccesible por distribución del mobiliario | Reubicación de `P1_Mob_Mesa_Comedor` y sillas (`P1_PH_Chair_1..5`), recorte de `P1_Mob_Cocina_Barra` (`Y <= 6.75 m`) y reubicación de `P1_Mob_Nevecon` (`+1.43x, -1.45y`). | `dining_north_aisle_m = 0.955 m`, `kitchen_entry_aisle_m = 1.30 m`, `kitchen_aisle_pass = true` |
| **ARQ-03** | Lavandería inaccesible | Corrección de sentido de apertura (`dir = -1f`) en `InteractiveDoor.cs` para `Huesped_Norte_Cocina` (`P1_M_Huesped_Norte_Cocina_Puerta1/3`), evitando bloqueo en el pasillo de cocina, y ruta continua por `Cocina_Retorno`. | `Lavanderia / Patio` y `Habitacion de Huespedes` visitadas en recorrido continuo (`18/18`) |
| **ARQ-04** | Escalera sin protección lateral visible | Incorporación en P1/P2 de `Esc_Pasamanos_Norte`, postes `Esc_Poste_01..15`, antepechos metálicos `Esc_Baranda_P2_Oeste/Norte` y paneles de vidrio `Esc_Vidrio_P2_Oeste/Norte`. | `stair_handrail_present = true`, `p2_stairwell_guardrails_present = true`, visible en `10_ZONA_Escalera.png` y `PLANTA_02_V3.png` |
| **ARQ-05** | Garaje abierto hacia cocina y acceso bloqueado | Cierre norte del garaje con `P1_M_Norte_Garaje_S0`, `P1_M_Norte_Garaje_Lint1`, puerta `P1_M_Norte_Garaje_Puerta1`, losa de continuidad `P1_Piso_P1_Paso_Garaje` y ajuste de estacionamiento `Veh_VStrom` (`-0.55 m` en Y). | `garage_enclosure_present = true`, `Garaje` visitado (`07_ZONA_Garaje.png`) |
| **NAV-07** | Despeje perimetral alrededor de cama principal y rutas | Desplazamiento `-0.15 m` en X de `P2_Mob_Cama_Master*` y `P2_PH_Nightstand_*` para liberar el corredor este (`0.705 m`) hacia el retorno desde `Balcon` hasta `Exterior`. | `exterior_return_passed = true` en `HITO_08_3_1_NAVIGATION_TRACE.json` |
| **QA-01** | PlayMode aprobaba sin alcanzar `18/18` zonas y con teletransportes | Eliminación total de `TeleportTo()` en `ResidentialNavigationAgent.cs`; aserciones estrictas en `HomeProjectPlayModeTests.cs`: `teleport_count == 0`, `exterior_entry_passed == true`, `exterior_return_passed == true`, `zones_visited_count == 18`. | PlayMode `3/3 PASS` (`ContinuousAutonomousTourVisitsAll18ZonesAndMeasuresPerformance`) |
| **Colisiones** | Conteo de colisiones sin clasificar | Clasificación explícita en `ResidentialFirstPersonController.cs` y `NavigationTraceReport`: `floor_collisions`, `stair_collisions`, `wall_collisions`, `obstacle_collisions`. | `21941` suelo, `1383` escalera, `3839` muros, `3224` obstáculos (`total_collisions = 30387`) |
| **Puertas** | Apertura indiscriminada por proximidad en agente | Reemplazo por `ResidentialFirstPersonController.InteractWithDoor(InteractiveDoor)` respetando `interactDistance = 2.4 m`. Prueba real con tecla `E` mediante `InputSystem.QueueStateEvent`. | `InputSystemEKeyOpensDoorAndWindowBlocksPlayer` PASS |
| **C# limpio** | Comentarios en código C# | Eliminación total de comentarios (`//` y `/* */`) en scripts C# del proyecto. | Verificado en scripts de `unity/Assets/HomeProject/` |
