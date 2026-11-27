using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace HomeProject.Interaction
{
    [Serializable]
    public class NavigationTracePoint
    {
        public int step_index;
        public string label;
        public string detected_zone;
        public float[] target_unity;
        public float[] position_unity;
        public float horizontal_error_m;
        public float vertical_error_m;
        public bool reached;
        public float elapsed_s;
        public float distance_m;
        public int floor_collisions;
        public int stair_collisions;
        public int wall_collisions;
        public int obstacle_collisions;
        public string last_hit;
    }

    [Serializable]
    public class NavigationTraceReport
    {
        public string milestone = "Hito 8.3.1";
        public int teleport_count;
        public float total_time_s;
        public float total_distance_m;
        public int floor_collisions;
        public int stair_collisions;
        public int wall_collisions;
        public int obstacle_collisions;
        public int total_collisions;
        public int zones_expected = 18;
        public int zones_visited_count;
        public bool all_zones_visited;
        public bool exterior_entry_passed;
        public bool exterior_return_passed;
        public List<string> visited_zones = new List<string>();
        public List<string> unreachable_zones = new List<string>();
        public List<NavigationTracePoint> trace = new List<NavigationTracePoint>();
    }

    public class ResidentialNavigationAgent
    {
        private readonly ResidentialFirstPersonController player;
        private readonly InteractiveDoor[] allDoors;
        private readonly HashSet<string> visitedZones = new HashSet<string>();
        private readonly HashSet<string> capturedZones = new HashSet<string>();
        private readonly List<NavigationTracePoint> trace = new List<NavigationTracePoint>();
        private Vector3 lastPosition;
        private float totalDistance;
        private float startTime;
        private bool exteriorEntryPassed;
        private bool exteriorReturnPassed;

        private static readonly string[] Expected18Zones =
        {
            "Exterior / Contexto Urbano",
            "Acceso Peatonal",
            "Sala",
            "Bano Social",
            "Comedor",
            "Cocina",
            "Lavanderia / Patio",
            "Habitacion de Huespedes",
            "Garaje",
            "Escalera",
            "Corredor Superior",
            "Habitacion Hija 2",
            "Habitacion Hija 1",
            "Bano Compartido",
            "Habitacion Principal",
            "Vestidor",
            "Bano Principal",
            "Balcon"
        };

        public ResidentialNavigationAgent(ResidentialFirstPersonController controller)
        {
            player = controller;
            allDoors = UnityEngine.Object.FindObjectsByType<InteractiveDoor>(FindObjectsInactive.Include);
        }

        public IEnumerator ExecuteContinuousTour(Action<string> onZoneReachedScreenshot = null)
        {
            startTime = Time.unscaledTime;
            lastPosition = player.transform.position;
            totalDistance = 0f;
            visitedZones.Clear();
            capturedZones.Clear();
            trace.Clear();
            RecordStep(0, "Inicio_Exterior", player.transform.position, true);
            CaptureIfNewZone(onZoneReachedScreenshot, true);

            (string label, Vector3 target, string doorToOpen)[] waypoints =
            {
                ("Anden_Frontal", new Vector3(-1.12f, 0.08f, 0.75f), "Fach_Porton_Peatonal_Puerta1"),
                ("Acceso_Peatonal", new Vector3(-1.12f, 0.08f, -0.90f), "P1_M_Sur_Sala_Puerta1"),
                ("Sala_Entrada", new Vector3(-1.12f, 0.08f, -2.05f), ""),
                ("Sala_Pasillo_Este", new Vector3(-3.00f, 0.08f, -2.05f), ""),
                ("Sala_Centro", new Vector3(-3.00f, 0.08f, -4.125f), ""),
                ("Distribuidor_Puerta", new Vector3(-2.60f, 0.08f, -4.20f), "P1_M_Bano_Sur_Puerta1"),
                ("Distribuidor_Entrada", new Vector3(-2.60f, 0.08f, -5.70f), "P1_M_Bano_Este_Puerta1"),
                ("Bano_Social", new Vector3(-1.30f, 0.08f, -5.70f), ""),
                ("Distribuidor_Retorno", new Vector3(-2.60f, 0.08f, -5.70f), ""),
                ("Distribuidor_Norte", new Vector3(-2.60f, 0.08f, -7.75f), ""),
                ("Comedor", new Vector3(-4.50f, 0.08f, -7.75f), ""),
                ("Cocina_Pasillo", new Vector3(-6.70f, 0.08f, -7.75f), ""),
                ("Cocina", new Vector3(-6.70f, 0.08f, -6.50f), ""),
                ("Pasillo_Garaje_Norte", new Vector3(-7.35f, 0.08f, -5.25f), "P1_M_Norte_Garaje_Puerta1"),
                ("Garaje", new Vector3(-7.35f, 0.08f, -4.10f), ""),
                ("Retorno_Garaje_Norte", new Vector3(-7.35f, 0.08f, -5.25f), ""),
                ("Cocina_Retorno", new Vector3(-6.70f, 0.08f, -6.50f), ""),
                ("Cocina_Lavanderia_Puerta", new Vector3(-6.80f, 0.08f, -7.50f), "P1_M_Huesped_Norte_Cocina_Puerta3"),
                ("Lavanderia", new Vector3(-6.80f, 0.08f, -9.10f), ""),
                ("Retorno_Cocina_Norte", new Vector3(-6.80f, 0.08f, -7.45f), ""),
                ("Pasillo_Huespedes", new Vector3(-2.62f, 0.08f, -7.75f), "P1_M_Huesped_Norte_Cocina_Puerta1"),
                ("Hab_Huespedes", new Vector3(-2.62f, 0.08f, -9.10f), ""),
                ("Retorno_Distribuidor", new Vector3(-2.62f, 0.08f, -6.80f), ""),
                ("Base_Escalera", new Vector3(-2.75f, 0.08f, -5.22f), ""),
                ("Escalera_Media", new Vector3(-4.97f, 1.45f, -5.22f), ""),
                ("Desembarco_P2", new Vector3(-7.35f, 2.94f, -5.22f), ""),
                ("Desembarco_Norte_P2", new Vector3(-7.35f, 2.94f, -6.10f), ""),
                ("Corredor_P2_H2", new Vector3(-4.60f, 2.94f, -6.10f), "P2_M_Banda_Norte_Puerta3"),
                ("Hab_Hija_2", new Vector3(-4.60f, 2.94f, -8.10f), ""),
                ("Retorno_Corredor_H2", new Vector3(-4.60f, 2.94f, -6.10f), ""),
                ("Corredor_P2_H1", new Vector3(-3.40f, 2.94f, -6.10f), "P2_M_Banda_Norte_Puerta1"),
                ("Hab_Hija_1", new Vector3(-3.40f, 2.94f, -8.10f), ""),
                ("Retorno_Corredor_H1", new Vector3(-3.40f, 2.94f, -6.10f), ""),
                ("Corredor_P2_Bano", new Vector3(-2.55f, 2.94f, -6.00f), "P2_M_Bano_Comp_Este_Puerta1"),
                ("Bano_Compartido", new Vector3(-1.30f, 2.94f, -6.00f), ""),
                ("Retorno_Corredor_Bano", new Vector3(-2.60f, 2.94f, -6.00f), ""),
                ("Corredor_P2_Master_Puerta", new Vector3(-2.60f, 2.94f, -5.10f), "P2_M_Banda_Sur_Puerta1"),
                ("Hab_Principal", new Vector3(-2.60f, 2.94f, -3.05f), ""),
                ("Master_Puerta_Vest", new Vector3(-4.00f, 2.94f, -3.05f), "P2_M_Master_Este_Puerta3"),
                ("Vestidor", new Vector3(-5.40f, 2.94f, -3.05f), "P2_M_Vest_Bano_Puerta1"),
                ("Bano_Principal", new Vector3(-6.95f, 2.94f, -3.10f), ""),
                ("Retorno_Vestidor", new Vector3(-5.40f, 2.94f, -3.05f), ""),
                ("Retorno_Master", new Vector3(-3.80f, 2.94f, -0.95f), "P2_M_Master_Este_Puerta1"),
                ("Balcon", new Vector3(-5.80f, 2.94f, -0.95f), ""),
                ("Retorno_Master_Balcon", new Vector3(-3.80f, 2.94f, -0.95f), ""),
                ("Retorno_Master_Oeste", new Vector3(-4.10f, 2.94f, -3.80f), ""),
                ("Retorno_Master_Salir", new Vector3(-2.60f, 2.94f, -3.80f), ""),
                ("Corredor_P2_Descenso", new Vector3(-2.60f, 2.94f, -6.10f), ""),
                ("Corredor_P2_Escalera_Norte", new Vector3(-7.35f, 2.94f, -6.10f), ""),
                ("Corredor_P2_Escalera", new Vector3(-7.35f, 2.94f, -5.22f), ""),
                ("Descenso_Escalera", new Vector3(-2.75f, 0.08f, -5.22f), ""),
                ("Salida_Distribuidor", new Vector3(-2.60f, 0.08f, -4.20f), ""),
                ("Salida_Sala_Este", new Vector3(-3.00f, 0.08f, -2.05f), ""),
                ("Salida_Sala_Puerta", new Vector3(-1.12f, 0.08f, -2.05f), ""),
                ("Salida_Acceso_Peatonal", new Vector3(-1.12f, 0.08f, -0.90f), ""),
                ("Salida_Exterior", new Vector3(-1.12f, 0.08f, 1.40f), "")
            };

            for (int i = 0; i < waypoints.Length; i++)
            {
                bool reached = false;
                yield return WalkToWaypoint(waypoints[i].target, 6.0f, r => reached = r);
                RecordStep(i + 1, waypoints[i].label, waypoints[i].target, reached);

                if (waypoints[i].label == "Acceso_Peatonal" && reached && player.CurrentZoneName == "Acceso Peatonal")
                {
                    exteriorEntryPassed = true;
                }
                if (waypoints[i].label == "Salida_Exterior" && reached && player.CurrentZoneName == "Exterior / Contexto Urbano")
                {
                    exteriorReturnPassed = true;
                }

                CaptureIfNewZone(onZoneReachedScreenshot, reached);

                if (!string.IsNullOrEmpty(waypoints[i].doorToOpen))
                {
                    yield return InteractWithNamedDoor(waypoints[i].doorToOpen);
                }
            }

            player.SetInputOverride(false, Vector2.zero, Vector2.zero);
        }

        private IEnumerator InteractWithNamedDoor(string doorName)
        {
            InteractiveDoor targetDoor = null;
            for (int i = 0; i < allDoors.Length; i++)
            {
                if (allDoors[i] != null && allDoors[i].gameObject.name == doorName)
                {
                    targetDoor = allDoors[i];
                    break;
                }
            }
            if (targetDoor == null || targetDoor.IsOpen)
            {
                yield break;
            }

            Vector3 delta = targetDoor.transform.position - player.transform.position;
            float desiredYaw = Mathf.Atan2(delta.x, delta.z) * Mathf.Rad2Deg;
            float yawDiff = Mathf.DeltaAngle(player.CurrentYaw, desiredYaw);
            player.SetInputOverride(true, Vector2.zero, new Vector2(yawDiff, 0f));
            yield return null;

            player.InteractWithDoor(targetDoor);
            float waitStart = Time.unscaledTime;
            while (targetDoor.IsTransitioning && Time.unscaledTime - waitStart < 1.5f)
            {
                yield return null;
            }
        }

        private IEnumerator WalkToWaypoint(Vector3 target, float timeoutSeconds, Action<bool> onComplete)
        {
            float start = Time.unscaledTime;
            float lastProgressTime = start;
            Vector3 progressAnchor = player.transform.position;
            bool reached = false;

            while (Time.unscaledTime - start < timeoutSeconds)
            {
                Vector3 pos = player.transform.position;
                totalDistance += Vector3.Distance(pos, lastPosition);
                lastPosition = pos;
                visitedZones.Add(player.CurrentZoneName);

                Vector3 delta = target - pos;
                float horizDist = new Vector2(delta.x, delta.z).magnitude;
                float vertDist = Mathf.Abs(delta.y);
                if (horizDist <= 0.30f && vertDist <= 0.35f)
                {
                    reached = true;
                    break;
                }

                if (Time.unscaledTime - lastProgressTime > 1.2f)
                {
                    if (Vector3.Distance(pos, progressAnchor) < 0.06f)
                    {
                        break;
                    }
                    lastProgressTime = Time.unscaledTime;
                    progressAnchor = pos;
                }

                float desiredYaw = Mathf.Atan2(delta.x, delta.z) * Mathf.Rad2Deg;
                float yawDiff = Mathf.DeltaAngle(player.CurrentYaw, desiredYaw);
                player.SetInputOverride(true, new Vector2(0f, 1f), new Vector2(yawDiff * 0.35f, 0f));
                yield return null;
            }

            onComplete?.Invoke(reached);
        }

        private void CaptureIfNewZone(Action<string> onZoneReachedScreenshot, bool reached)
        {
            if (!reached || onZoneReachedScreenshot == null)
            {
                return;
            }
            string z = player.CurrentZoneName;
            if (!capturedZones.Contains(z) && Array.IndexOf(Expected18Zones, z) >= 0)
            {
                capturedZones.Add(z);
                onZoneReachedScreenshot(z);
            }
        }

        private void RecordStep(int index, string label, Vector3 target, bool reached)
        {
            Vector3 p = player.transform.position;
            string z = player.CurrentZoneName;
            visitedZones.Add(z);
            float hErr = new Vector2(target.x - p.x, target.z - p.z).magnitude;
            float vErr = Mathf.Abs(target.y - p.y);
            trace.Add(new NavigationTracePoint
            {
                step_index = index,
                label = label,
                detected_zone = z,
                target_unity = new[] { Round3(target.x), Round3(target.y), Round3(target.z) },
                position_unity = new[] { Round3(p.x), Round3(p.y), Round3(p.z) },
                horizontal_error_m = Round3(hErr),
                vertical_error_m = Round3(vErr),
                reached = reached,
                elapsed_s = Round3(Time.unscaledTime - startTime),
                distance_m = Round3(totalDistance),
                floor_collisions = player.FloorCollisions,
                stair_collisions = player.StairCollisions,
                wall_collisions = player.WallCollisions,
                obstacle_collisions = player.ObstacleCollisions,
                last_hit = player.LastHitObject
            });
        }

        public NavigationTraceReport BuildReport()
        {
            NavigationTraceReport rep = new NavigationTraceReport
            {
                teleport_count = 0,
                total_time_s = Round3(Time.unscaledTime - startTime),
                total_distance_m = Round3(totalDistance),
                floor_collisions = player.FloorCollisions,
                stair_collisions = player.StairCollisions,
                wall_collisions = player.WallCollisions,
                obstacle_collisions = player.ObstacleCollisions,
                total_collisions = player.CollisionCount,
                zones_expected = Expected18Zones.Length,
                exterior_entry_passed = exteriorEntryPassed,
                exterior_return_passed = exteriorReturnPassed,
                trace = trace
            };

            for (int i = 0; i < Expected18Zones.Length; i++)
            {
                if (visitedZones.Contains(Expected18Zones[i]))
                {
                    rep.visited_zones.Add(Expected18Zones[i]);
                }
                else
                {
                    rep.unreachable_zones.Add(Expected18Zones[i]);
                }
            }

            rep.zones_visited_count = rep.visited_zones.Count;
            rep.all_zones_visited = rep.unreachable_zones.Count == 0;
            return rep;
        }

        private static float Round3(float v)
        {
            return Mathf.Round(v * 1000f) / 1000f;
        }
    }
}
