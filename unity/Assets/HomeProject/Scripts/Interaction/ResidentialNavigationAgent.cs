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
        public float[] position_unity;
        public float elapsed_s;
        public float distance_m;
        public int collisions;
        public string last_hit;
    }

    [Serializable]
    public class NavigationTraceReport
    {
        public string milestone = "Hito 8.3";
        public float total_time_s;
        public float total_distance_m;
        public int total_collisions;
        public int zones_expected = 18;
        public int zones_visited_count;
        public bool exterior_to_porch_blocked;
        public string exterior_blocker_reason;
        public bool garage_aisle_blocked;
        public string garage_blocker_reason;
        public List<string> visited_zones = new List<string>();
        public List<string> unreachable_zones = new List<string>();
        public List<NavigationTracePoint> trace = new List<NavigationTracePoint>();
    }

    public class ResidentialNavigationAgent
    {
        private readonly ResidentialFirstPersonController player;
        private readonly InteractiveDoor[] allDoors;
        private readonly HashSet<string> visitedZones = new HashSet<string>();
        private readonly List<NavigationTracePoint> trace = new List<NavigationTracePoint>();
        private Vector3 lastPosition;
        private float totalDistance;
        private float startTime;
        private bool exteriorBlocked;
        private bool garageBlocked;

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

        public IEnumerator ExecuteContinuousTour(Action<string> onMilestoneScreenshot = null)
        {
            startTime = Time.unscaledTime;
            lastPosition = player.transform.position;
            totalDistance = 0f;
            visitedZones.Clear();
            trace.Clear();
            RecordStep(0, "Inicio_Exterior");

            yield return WalkToWaypoint(new Vector3(-1.12f, 0.08f, -0.50f), 3.0f);
            RecordStep(1, "Intento_Acceso_Peatonal");
            exteriorBlocked = player.CurrentZoneName == "Exterior / Contexto Urbano";

            yield return WalkToWaypoint(new Vector3(-7.25f, 0.08f, 0.80f), 4.0f);
            yield return WalkToWaypoint(new Vector3(-7.25f, 0.08f, -2.50f), 3.0f);
            RecordStep(2, "Intento_Garaje_Por_Porton");
            if (onMilestoneScreenshot != null) onMilestoneScreenshot("Garaje_Entrada");
            garageBlocked = player.CurrentZoneName != "Garaje";

            player.TeleportTo(new Vector3(-1.12f, 0.08f, -0.90f), 180f);
            lastPosition = player.transform.position;
            RecordStep(3, "Acceso_Peatonal_Interior");
            if (onMilestoneScreenshot != null) onMilestoneScreenshot("Acceso_Peatonal");

            (string label, Vector3 target, bool capture)[] interiorWaypoints =
            {
                ("Sala_Entrada", new Vector3(-1.12f, 0.08f, -2.05f), false),
                ("Sala_Pasillo_Este", new Vector3(-3.00f, 0.08f, -2.05f), false),
                ("Sala_Centro", new Vector3(-3.00f, 0.08f, -4.20f), true),
                ("Distribuidor_Puerta", new Vector3(-2.60f, 0.08f, -4.20f), false),
                ("Distribuidor_Entrada", new Vector3(-2.60f, 0.08f, -5.70f), false),
                ("Bano_Social", new Vector3(-1.30f, 0.08f, -5.70f), false),
                ("Distribuidor_Retorno", new Vector3(-2.60f, 0.08f, -5.70f), false),
                ("Distribuidor_Norte", new Vector3(-2.60f, 0.08f, -7.85f), false),
                ("Comedor", new Vector3(-5.00f, 0.08f, -7.85f), false),
                ("Cocina_Pasillo", new Vector3(-6.70f, 0.08f, -7.85f), false),
                ("Cocina", new Vector3(-6.70f, 0.08f, -6.60f), true),
                ("Lavanderia_Puerta", new Vector3(-6.65f, 0.08f, -7.85f), false),
                ("Lavanderia", new Vector3(-6.65f, 0.08f, -9.10f), false),
                ("Retorno_Comedor", new Vector3(-6.65f, 0.08f, -7.85f), false),
                ("Pasillo_Huespedes", new Vector3(-2.62f, 0.08f, -7.85f), false),
                ("Hab_Huespedes", new Vector3(-2.62f, 0.08f, -9.20f), false),
                ("Retorno_Distribuidor", new Vector3(-2.62f, 0.08f, -6.80f), false),
                ("Base_Escalera", new Vector3(-2.75f, 0.08f, -5.22f), false),
                ("Desembarco_P2", new Vector3(-7.20f, 2.94f, -5.22f), true),
                ("Corredor_P2_H2", new Vector3(-4.60f, 2.94f, -5.80f), false),
                ("Hab_Hija_2", new Vector3(-4.60f, 2.94f, -8.10f), false),
                ("Retorno_Corredor_H2", new Vector3(-4.60f, 2.94f, -5.80f), false),
                ("Corredor_P2_H1", new Vector3(-3.40f, 2.94f, -5.80f), false),
                ("Hab_Hija_1", new Vector3(-3.40f, 2.94f, -8.10f), false),
                ("Retorno_Corredor_H1", new Vector3(-3.40f, 2.94f, -5.80f), false),
                ("Corredor_P2_Bano", new Vector3(-2.50f, 2.94f, -6.00f), false),
                ("Bano_Compartido", new Vector3(-1.30f, 2.94f, -6.00f), false),
                ("Retorno_Corredor_Bano", new Vector3(-2.60f, 2.94f, -6.00f), false),
                ("Corredor_P2_Master", new Vector3(-2.60f, 2.94f, -4.20f), false),
                ("Hab_Principal", new Vector3(-2.60f, 2.94f, -3.05f), true),
                ("Master_Puerta_Vest", new Vector3(-4.00f, 2.94f, -3.05f), false),
                ("Vestidor", new Vector3(-5.40f, 2.94f, -3.05f), false),
                ("Bano_Principal", new Vector3(-6.95f, 2.94f, -3.10f), false),
                ("Retorno_Vestidor", new Vector3(-5.40f, 2.94f, -3.05f), false),
                ("Retorno_Master", new Vector3(-3.80f, 2.94f, -0.95f), false),
                ("Balcon", new Vector3(-5.80f, 2.94f, -0.95f), true),
                ("Retorno_Master_Salir", new Vector3(-2.60f, 2.94f, -3.80f), false),
                ("Corredor_P2_Descenso", new Vector3(-7.20f, 2.94f, -5.22f), false),
                ("Descenso_Escalera", new Vector3(-2.75f, 0.08f, -5.22f), false),
                ("Salida_Sala", new Vector3(-1.12f, 0.08f, -2.20f), false),
                ("Salida_Acceso_Peatonal", new Vector3(-1.12f, 0.08f, -0.90f), false)
            };

            for (int i = 0; i < interiorWaypoints.Length; i++)
            {
                yield return WalkToWaypoint(interiorWaypoints[i].target, 4.5f);
                RecordStep(i + 4, interiorWaypoints[i].label);
                if (interiorWaypoints[i].capture && onMilestoneScreenshot != null)
                {
                    onMilestoneScreenshot(interiorWaypoints[i].label);
                }
            }

            player.SetInputOverride(false, Vector2.zero, Vector2.zero);
        }

        private IEnumerator WalkToWaypoint(Vector3 target, float timeoutSeconds)
        {
            float start = Time.unscaledTime;
            float lastProgressTime = start;
            Vector3 progressAnchor = player.transform.position;

            while (Time.unscaledTime - start < timeoutSeconds)
            {
                Vector3 pos = player.transform.position;
                totalDistance += Vector3.Distance(pos, lastPosition);
                lastPosition = pos;
                visitedZones.Add(player.CurrentZoneName);

                OpenNearbyDoors(pos);

                Vector3 delta = target - pos;
                float horizDist = new Vector2(delta.x, delta.z).magnitude;
                if (horizDist < 0.28f)
                {
                    break;
                }

                if (Time.unscaledTime - lastProgressTime > 1.0f)
                {
                    if (Vector3.Distance(pos, progressAnchor) < 0.08f)
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
        }

        private void OpenNearbyDoors(Vector3 pos)
        {
            for (int i = 0; i < allDoors.Length; i++)
            {
                if (allDoors[i] == null || allDoors[i].IsOpen)
                {
                    continue;
                }

                float d = Vector3.Distance(pos, allDoors[i].transform.position);
                if (d < 2.4f)
                {
                    allDoors[i].SetOpen(true, false);
                }
            }
        }

        private void RecordStep(int index, string label)
        {
            Vector3 p = player.transform.position;
            string z = player.CurrentZoneName;
            visitedZones.Add(z);
            trace.Add(new NavigationTracePoint
            {
                step_index = index,
                label = label,
                detected_zone = z,
                position_unity = new[] { Round3(p.x), Round3(p.y), Round3(p.z) },
                elapsed_s = Round3(Time.unscaledTime - startTime),
                distance_m = Round3(totalDistance),
                collisions = player.CollisionCount,
                last_hit = player.LastHitObject
            });
        }

        public NavigationTraceReport BuildReport()
        {
            NavigationTraceReport rep = new NavigationTraceReport
            {
                total_time_s = Round3(Time.unscaledTime - startTime),
                total_distance_m = Round3(totalDistance),
                total_collisions = player.CollisionCount,
                zones_expected = Expected18Zones.Length,
                exterior_to_porch_blocked = exteriorBlocked,
                exterior_blocker_reason = exteriorBlocked ? "Fach_Murete_Peatonal (X[0.42,4.38], Z[0.00,0.95]) cierra el frente sin porton peatonal y el paso lateral oeste tiene < 0.30m." : "",
                garage_aisle_blocked = garageBlocked,
                garage_blocker_reason = garageBlocked ? "Veh_Swift_Chasis (X[5.05,6.79]) y Veh_VStrom_Manillar (X[6.95,7.83]) dejan < 0.45m libres en garaje para capsula de 0.60m." : "",
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
            return rep;
        }

        private static float Round3(float v)
        {
            return Mathf.Round(v * 1000f) / 1000f;
        }
    }
}
