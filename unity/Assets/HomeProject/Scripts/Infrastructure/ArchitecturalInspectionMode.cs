using System.Collections.Generic;
using HomeProject.Core;
using HomeProject.Interaction;
using UnityEngine;
using UnityEngine.InputSystem;

namespace HomeProject.Infrastructure
{
    public enum InspectionMode
    {
        ArchitectureOnly = 0,
        FullFurnished = 1
    }

    public class ArchitecturalInspectionMode : MonoBehaviour
    {
        private static readonly string[] NonArchPrefixes =
        {
            "Veh_",
            "Inst_",
            "PH_Plant",
            "P1_Mob_",
            "P2_Mob_",
            "P1_PH_",
            "P2_PH_",
            "Aplique_"
        };

        private static readonly string[] NonArchSubstrings =
        {
            "Cortina",
            "Tapete",
            "Espejo",
            "Solar",
            "Closet",
            "Inodoro",
            "Lavabo",
            "Ducha",
            "Mampara",
            "Grifo",
            "Lavadora",
            "Lavadero",
            "Estufa",
            "Campana",
            "Nevecon",
            "TV_65",
            "Barra_Apoyo"
        };

        private readonly List<Renderer> managedRenderers = new List<Renderer>();
        private readonly List<Collider> managedColliders = new List<Collider>();
        private readonly List<GameObject> managedObjects = new List<GameObject>();
        private bool initialized;

        public InspectionMode CurrentMode { get; private set; } = InspectionMode.ArchitectureOnly;
        public int ToggleCount { get; private set; }
        public string LastBlockedReason { get; private set; } = string.Empty;
        public int ManagedObjectCount => managedObjects.Count;

        public int ActiveManagedRendererCount
        {
            get
            {
                int count = 0;
                for (int i = 0; i < managedRenderers.Count; i++)
                {
                    if (managedRenderers[i] != null && managedRenderers[i].enabled)
                    {
                        count++;
                    }
                }
                return count;
            }
        }

        public int ActiveManagedColliderCount
        {
            get
            {
                int count = 0;
                for (int i = 0; i < managedColliders.Count; i++)
                {
                    if (managedColliders[i] != null && managedColliders[i].enabled)
                    {
                        count++;
                    }
                }
                return count;
            }
        }

        private void Awake()
        {
            EnsureInitialized();
            ApplyMode(InspectionMode.ArchitectureOnly);
        }

        private void Update()
        {
            foreach (InputDevice dev in InputSystem.devices)
            {
                if (dev is Keyboard kb && kb.enabled && kb.mKey.wasPressedThisFrame)
                {
                    ToggleMode();
                    break;
                }
            }
        }

        public void EnsureInitialized()
        {
            if (initialized)
            {
                return;
            }

            managedRenderers.Clear();
            managedColliders.Clear();
            managedObjects.Clear();

            GameObject root = GameObject.Find(HomeProjectConstants.HomeProjectRootName);
            if (root != null)
            {
                HashSet<GameObject> seen = new HashSet<GameObject>();
                CollectGroup(root.transform.Find(HomeProjectConstants.GroupFurniture), seen);
                CollectGroup(root.transform.Find(HomeProjectConstants.GroupVehicles), seen);
                CollectGroup(root.transform.Find(HomeProjectConstants.GroupInstallations), seen);
                CollectByName(root.transform.Find(HomeProjectConstants.GroupArchitecture), seen);
                CollectByName(root.transform.Find(HomeProjectConstants.GroupUrbanContext), seen);
            }

            initialized = true;
        }

        private void CollectGroup(Transform group, HashSet<GameObject> seen)
        {
            if (group == null)
            {
                return;
            }

            Transform[] all = group.GetComponentsInChildren<Transform>(true);
            for (int i = 0; i < all.Length; i++)
            {
                GameObject go = all[i].gameObject;
                if (go == group.gameObject || seen.Contains(go))
                {
                    continue;
                }
                seen.Add(go);
                RegisterObject(go);
            }
        }

        private void CollectByName(Transform group, HashSet<GameObject> seen)
        {
            if (group == null)
            {
                return;
            }

            Transform[] all = group.GetComponentsInChildren<Transform>(true);
            for (int i = 0; i < all.Length; i++)
            {
                GameObject go = all[i].gameObject;
                if (go == group.gameObject || seen.Contains(go))
                {
                    continue;
                }
                if (IsNonArchitecturalName(go.name))
                {
                    seen.Add(go);
                    RegisterObject(go);
                }
            }
        }

        private static bool IsNonArchitecturalName(string objectName)
        {
            for (int i = 0; i < NonArchPrefixes.Length; i++)
            {
                if (objectName.StartsWith(NonArchPrefixes[i]))
                {
                    return true;
                }
            }
            for (int i = 0; i < NonArchSubstrings.Length; i++)
            {
                if (objectName.Contains(NonArchSubstrings[i]))
                {
                    return true;
                }
            }
            return false;
        }

        private void RegisterObject(GameObject go)
        {
            bool added = false;
            Renderer[] rends = go.GetComponents<Renderer>();
            for (int i = 0; i < rends.Length; i++)
            {
                managedRenderers.Add(rends[i]);
                added = true;
            }
            Collider[] cols = go.GetComponents<Collider>();
            for (int i = 0; i < cols.Length; i++)
            {
                managedColliders.Add(cols[i]);
                added = true;
            }
            if (added)
            {
                managedObjects.Add(go);
            }
        }

        public bool ToggleMode()
        {
            InspectionMode next = CurrentMode == InspectionMode.ArchitectureOnly
                ? InspectionMode.FullFurnished
                : InspectionMode.ArchitectureOnly;
            return SetMode(next);
        }

        public bool SetMode(InspectionMode mode)
        {
            EnsureInitialized();
            LastBlockedReason = string.Empty;

            if (mode == InspectionMode.FullFurnished && WouldOverlapPlayer(out string blockingObject))
            {
                LastBlockedReason = "Bloqueado por interseccion con jugador: " + blockingObject;
                return false;
            }

            ApplyMode(mode);
            ToggleCount++;
            return true;
        }

        private bool WouldOverlapPlayer(out string blockingObject)
        {
            blockingObject = string.Empty;
            ResidentialFirstPersonController player = Object.FindAnyObjectByType<ResidentialFirstPersonController>();
            if (player == null)
            {
                return false;
            }

            CharacterController cc = player.GetComponent<CharacterController>();
            if (cc == null)
            {
                return false;
            }

            Bounds playerBounds = cc.bounds;
            for (int i = 0; i < managedColliders.Count; i++)
            {
                Collider col = managedColliders[i];
                if (col == null || col.gameObject.name.Contains("Tapete"))
                {
                    continue;
                }

                bool wasEnabled = col.enabled;
                if (!wasEnabled)
                {
                    col.enabled = true;
                }
                bool intersects = col.bounds.Intersects(playerBounds);
                if (!wasEnabled)
                {
                    col.enabled = false;
                }

                if (intersects)
                {
                    blockingObject = col.gameObject.name;
                    return true;
                }
            }

            return false;
        }

        private void ApplyMode(InspectionMode mode)
        {
            CurrentMode = mode;
            bool showFurnished = mode == InspectionMode.FullFurnished;

            for (int i = 0; i < managedRenderers.Count; i++)
            {
                if (managedRenderers[i] != null)
                {
                    managedRenderers[i].enabled = showFurnished;
                }
            }

            for (int i = 0; i < managedColliders.Count; i++)
            {
                if (managedColliders[i] != null)
                {
                    managedColliders[i].enabled = showFurnished;
                }
            }
        }
    }
}
