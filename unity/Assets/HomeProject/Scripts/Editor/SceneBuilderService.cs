using System.Collections.Generic;
using HomeProject.Core;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
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
            SetupSystems(systemsRoot);
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

        private static void SetupSystems(GameObject systemsRoot)
        {
            Transform sys = GetOrCreateChild(systemsRoot.transform, "HomeProjectSystems");
            if (sys.GetComponent<HomeProjectSystemInitializer>() == null)
            {
                sys.gameObject.AddComponent<HomeProjectSystemInitializer>();
            }
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
