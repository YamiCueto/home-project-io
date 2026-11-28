# Resolución de Auditoría de Navegabilidad — Hito 8.3.0

## 1. Hallazgos `NAV-01` a `NAV-06`

| ID | Requisito | Resolución implementada | Evidencia |
|---|---|---|---|
| **NAV-01** | Recorridos continuos sin teletransportes intermedios | `ResidentialNavigationAgent` conduce a `ResidentialFirstPersonController` mediante `SetInputOverride` (`CharacterController.Move`) a `1,60 m/s` (`69,07 m` recorridos en `67,12 s`). | `validation/HITO_08_3_NAVIGATION_TRACE.json` |
| **NAV-02** | Validación de las 18 zonas de `NAVIGATION_MAP.md` | `16 / 18` zonas alcanzadas físicamente; `2` zonas (`Cocina`, `Lavanderia / Patio`) y el acceso peatonal directo desde `Anden_Frontal` registrados honestamente como bloqueados por geometría real. | `validation/HITO_08_3_NAVIGATION_TRACE.json` |
| **NAV-03** | Modo orbital + cámara única activa + dimensiones unificadas | `OrbitalModeSingleActiveCameraRotationAndZoom` verifica exactamente `1` cámara activa en modo FPS y `1` en modo Orbital (`yaw`, `pitch`, `zoom`). Barridos `Physics.CapsuleCast` unificados a `radius = 0,30 m`, `height = 1,80 m`. | `HomeProjectPlayModeTests.cs` |
| **NAV-04** | Interacción real con `InputSystem` y tecla `E` | `InputSystemEKeyOpensDoorAndWindowBlocksPlayer` inyecta `Key.E` mediante `InputSystem.QueueStateEvent` y confirma apertura real de `P1_M_Sur_Sala_Puerta1`. | `HomeProjectPlayModeTests.cs` |
| **NAV-05** | Colisiones con ventanas y estabilidad física | `ColliderAuditService` asigna `MeshCollider` a los `6` paños de vidrio (`*_Glass`), alcanzando `585` colliders totales (`144` Box, `441` Mesh). | `validation/HITO_08_3_VALIDATION.json` |
| **NAV-06** | Estadísticas de rendimiento con percentiles reales | `ResidentialHudController` descarta `60` frames de calentamiento y calcula `average_fps = 375,0`, `average_frame_time_ms = 2,67 ms`, `p95 = 5,50 ms`, `p99 = 9,52 ms`, `1% low = 65,1 FPS` a `2560 x 1440`. | `validation/HITO_08_3_PERFORMANCE.json` |

## 2. Hallazgos arquitectónicos que requieren autorización de diseño

1. **Acceso peatonal desde el andén (`Fach_Murete_Peatonal`):**
   - `Fach_Murete_Peatonal` (`X[0.42, 4.38], Y[0.00, 0.10], Z[0.00, 0.95]`) cierra el frente del porche sin vano ni portón peatonal; el lateral oeste entre `Fach_Piedra_Pilar_Izq` y `Vecino_Oeste_Vol` deja `< 0,30 m` libres. Requiere abrir un vano peatonal de `>= 0,90 m` en `Fach_Murete_Peatonal` para permitir ingreso peatonal directo desde `Anden_Frontal`.
2. **Paso hacia `Cocina` y `Lavanderia / Patio`:**
   - Las sillas de comedor `P1_PH_Chair_3/4` (`Y_max = 7,83 m`) frente al muro `P1_M_Huesped_Norte_Cocina_S2` (`Y = 8,05 m`) dejan solo `0,22 m` libres, y `P1_Mob_Cocina_Barra` (`Y[5,95, 7,25]`) junto a `P1_Mob_Nevecon` (`Y[7,35, 8,00]`) dejan `0,10 m` entre sí, impidiendo el paso de la cápsula de `0,60 m` (`radius = 0,30 m`) hacia `Cocina` y `Lavanderia / Patio`. Requiere ajustar la disposición del comedor o la barra de cocina en un hito de diseño autorizado.
