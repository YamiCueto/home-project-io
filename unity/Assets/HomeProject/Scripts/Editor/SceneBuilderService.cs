using System.Collections.Generic;
using HomeProject.Core;
using HomeProject.Infrastructure;
using HomeProject.Interaction;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace HomeProject.Editor
{
    public static class SceneBuilderService
    {
        public static Scene BuildOrUpdateMainScene()
        {
            Scene scene = OpenOrCreateMainScene();

            GameObject homeRoot = GetOrCreateRoot(scene, HomeProjectConstants.HomeProjectRootName);
            GameObject lightingRoot = GetOrCreateRoot(scene, HomeProjectConstants.LightingRootName);
            GameObject camerasRoot = GetOrCreateRoot(scene, HomeProjectConstants.CamerasRootName);
            GameObject systemsRoot = GetOrCreateRoot(scene, HomeProjectConstants.SystemsRootName);

            Transform archGroup = GetOrCreateChild(homeRoot.transform, HomeProjectConstants.GroupArchitecture);
            Transform furnGroup = GetOrCreateChild(homeRoot.transform, HomeProjectConstants.GroupFurniture);
            Transform vehGroup = GetOrCreateChild(homeRoot.transform, HomeProjectConstants.GroupVehicles);
            Transform doorsGroup = GetOrCreateChild(homeRoot.transform, HomeProjectConstants.GroupInteractiveDoors);
            Transform instGroup = GetOrCreateChild(homeRoot.transform, HomeProjectConstants.GroupInstallations);
            Transform urbanGroup = GetOrCreateChild(homeRoot.transform, HomeProjectConstants.GroupUrbanContext);
            Transform colGroup = GetOrCreateChild(homeRoot.transform, HomeProjectConstants.GroupCollisionGeometry);

            InstantiateFbxPackage(HomeProjectConstants.ArchitectureFbxPath, archGroup, "architecture_pkg");
            InstantiateFbxPackage(HomeProjectConstants.FurnitureFbxPath, furnGroup, "furniture_pkg");
            InstantiateFbxPackage(HomeProjectConstants.InteractiveDoorsFbxPath, doorsGroup, "interactive_doors_pkg");
            InstantiateFbxPackage(HomeProjectConstants.InstallationsFbxPath, instGroup, "installations_pkg");
            InstantiateFbxPackage(HomeProjectConstants.UrbanContextFbxPath, urbanGroup, "urban_context_pkg");
            InstantiateFbxPackage(HomeProjectConstants.CollidersFbxPath, colGroup, "colliders_pkg");

            OrganizeVehicles(furnGroup, urbanGroup, vehGroup);
            SetupInteractiveDoors(doorsGroup);
            SetupSystems(systemsRoot, camerasRoot);
            RemoveStrayDefaultObjects(scene, homeRoot, lightingRoot, camerasRoot, systemsRoot);

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, HomeProjectConstants.ScenePath);
            EnsureSceneInBuildSettings(HomeProjectConstants.ScenePath);
            return scene;
        }

        private static void EnsureSceneInBuildSettings(string scenePath)
        {
            List<EditorBuildSettingsScene> scenes = new List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
            for (int i = 0; i < scenes.Count; i++)
            {
                if (scenes[i].path == scenePath)
                {
                    if (!scenes[i].enabled)
                    {
                        scenes[i].enabled = true;
                        EditorBuildSettings.scenes = scenes.ToArray();
                    }
                    return;
                }
            }
            scenes.Insert(0, new EditorBuildSettingsScene(scenePath, true));
            EditorBuildSettings.scenes = scenes.ToArray();
        }

        private static Scene OpenOrCreateMainScene()
        {
            if (System.IO.File.Exists(HomeProjectConstants.ScenePath))
            {
                return EditorSceneManager.OpenScene(HomeProjectConstants.ScenePath, OpenSceneMode.Single);
            }

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            EditorSceneManager.SaveScene(scene, HomeProjectConstants.ScenePath);
            return scene;
        }

        private static GameObject GetOrCreateRoot(Scene scene, string name)
        {
            GameObject[] roots = scene.GetRootGameObjects();
            for (int i = 0; i < roots.Length; i++)
            {
                if (roots[i].name == name)
                {
                    return roots[i];
                }
            }

            GameObject go = new GameObject(name);
            SceneManager.MoveGameObjectToScene(go, scene);
            return go;
        }

        private static Transform GetOrCreateChild(Transform parent, string name)
        {
            Transform existing = parent.Find(name);
            if (existing != null)
            {
                return existing;
            }

            GameObject go = new GameObject(name);
            go.transform.SetParent(parent, false);
            return go.transform;
        }

        private static void InstantiateFbxPackage(string fbxPath, Transform parent, string instanceName)
        {
            Transform existing = parent.Find(instanceName);
            if (existing != null)
            {
                Object.DestroyImmediate(existing.gameObject);
            }

            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(fbxPath);
            if (prefab == null)
            {
                Debug.LogError("Missing FBX asset: " + fbxPath);
                return;
            }

            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
            instance.name = instanceName;
            instance.transform.localPosition = Vector3.zero;
            instance.transform.localRotation = Quaternion.identity;
            instance.transform.localScale = Vector3.one;
        }

        private static void OrganizeVehicles(Transform furnGroup, Transform urbanGroup, Transform vehGroup)
        {
            List<Transform> toMove = new List<Transform>();
            CollectVehicleTransforms(furnGroup, toMove);
            CollectVehicleTransforms(urbanGroup, toMove);

            for (int i = 0; i < toMove.Count; i++)
            {
                Transform t = toMove[i];
                if (t.parent != vehGroup)
                {
                    t.SetParent(vehGroup, true);
                }
            }
        }

        private static void CollectVehicleTransforms(Transform root, List<Transform> results)
        {
            Transform[] all = root.GetComponentsInChildren<Transform>(true);
            for (int i = 0; i < all.Length; i++)
            {
                string n = all[i].name;
                if (n.StartsWith("Vehiculo_") || n.StartsWith("Vehicle_"))
                {
                    results.Add(all[i]);
                }
            }
        }

        private static void SetupInteractiveDoors(Transform doorsGroup)
        {
            MeshRenderer[] renderers = doorsGroup.GetComponentsInChildren<MeshRenderer>(true);
            for (int i = 0; i < renderers.Length; i++)
            {
                if (renderers[i].gameObject.GetComponent<InteractiveDoor>() == null)
                {
                    renderers[i].gameObject.AddComponent<InteractiveDoor>();
                }
            }
        }

        private static void SetupSystems(GameObject systemsRoot, GameObject camerasRoot)
        {
            Transform sys = GetOrCreateChild(systemsRoot.transform, "HomeProjectSystems");
            if (sys.GetComponent<HomeProjectSystemInitializer>() == null)
            {
                sys.gameObject.AddComponent<HomeProjectSystemInitializer>();
            }
            if (sys.GetComponent<ArchitecturalInspectionMode>() == null)
            {
                sys.gameObject.AddComponent<ArchitecturalInspectionMode>();
            }

            Transform hud = GetOrCreateChild(systemsRoot.transform, "ResidentialHud");
            if (hud.GetComponent<ResidentialHudController>() == null)
            {
                hud.gameObject.AddComponent<ResidentialHudController>();
            }

            Transform orb = GetOrCreateChild(camerasRoot.transform, "Orbital_Inspection_Camera");
            Camera orbCam = orb.GetComponent<Camera>();
            if (orbCam == null) orbCam = orb.gameObject.AddComponent<Camera>();
            orbCam.enabled = false;
            orbCam.fieldOfView = 48f;
            orbCam.nearClipPlane = 0.05f;
            orbCam.farClipPlane = 250f;
            UniversalAdditionalCameraData orbUac = orb.GetComponent<UniversalAdditionalCameraData>();
            if (orbUac == null) orbUac = orb.gameObject.AddComponent<UniversalAdditionalCameraData>();
            orbUac.renderPostProcessing = true;
            if (orb.GetComponent<OrbitalInspectionCamera>() == null)
            {
                orb.gameObject.AddComponent<OrbitalInspectionCamera>();
            }

            Transform playerTf = GetOrCreateChild(systemsRoot.transform, "ResidentialPlayer");
            playerTf.position = new Vector3(-1.12f, 0.08f, 1.80f);
            playerTf.rotation = Quaternion.Euler(0f, 180f, 0f);
            CharacterController cc = playerTf.GetComponent<CharacterController>();
            if (cc == null) cc = playerTf.gameObject.AddComponent<CharacterController>();
            ResidentialFirstPersonController fps = playerTf.GetComponent<ResidentialFirstPersonController>();
            if (fps == null) fps = playerTf.gameObject.AddComponent<ResidentialFirstPersonController>();
            fps.ConfigureCharacterController();

            Transform pCamTf = GetOrCreateChild(playerTf, "PlayerCamera");
            pCamTf.localPosition = new Vector3(0f, 1.65f, 0f);
            pCamTf.localRotation = Quaternion.identity;
            pCamTf.tag = "MainCamera";
            Camera pCam = pCamTf.GetComponent<Camera>();
            if (pCam == null) pCam = pCamTf.gameObject.AddComponent<Camera>();
            pCam.enabled = true;
            pCam.fieldOfView = 60f;
            pCam.nearClipPlane = 0.05f;
            pCam.farClipPlane = 250f;
            UniversalAdditionalCameraData pUac = pCamTf.GetComponent<UniversalAdditionalCameraData>();
            if (pUac == null) pUac = pCamTf.gameObject.AddComponent<UniversalAdditionalCameraData>();
            pUac.renderPostProcessing = true;
            pUac.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
        }

        private static void RemoveStrayDefaultObjects(Scene scene, params GameObject[] keepRoots)
        {
            HashSet<GameObject> keep = new HashSet<GameObject>(keepRoots);
            GameObject[] roots = scene.GetRootGameObjects();
            for (int i = 0; i < roots.Length; i++)
            {
                if (!keep.Contains(roots[i]))
                {
                    Object.DestroyImmediate(roots[i]);
                }
            }
        }
    }
}
