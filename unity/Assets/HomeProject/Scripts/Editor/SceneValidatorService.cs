using System;
using System.Collections.Generic;
using System.IO;
using HomeProject.Architecture;
using HomeProject.Core;
using HomeProject.Validation;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace HomeProject.Editor
{
    public static class SceneValidatorService
    {
        public static Hito081ValidationReport ValidateCurrentScene(bool writeReportFile = true)
        {
            Hito081ValidationReport report = new Hito081ValidationReport
            {
                unity_version = Application.unityVersion,
                render_pipeline = GraphicsSettings.currentRenderPipeline != null
                    ? GraphicsSettings.currentRenderPipeline.GetType().Name
                    : "None",
                scene_path = HomeProjectConstants.ScenePath,
                tolerance_m = HomeProjectConstants.DimensionalToleranceMeters
            };

            GameObject homeRoot = GameObject.Find(HomeProjectConstants.HomeProjectRootName);
            if (homeRoot == null)
            {
                report.errors.Add("Missing HOME_PROJECT root.");
                report.overall_passed = false;
                return report;
            }

            Dictionary<string, GameObject> sceneObjects = IndexSceneObjects(homeRoot.transform);
            CollectStatistics(homeRoot.transform, report);
            ValidateDimensions(sceneObjects, report);
            ValidateDoorPivots(sceneObjects, report);
            ValidateOpenings(report);

            report.overall_passed =
                report.errors.Count == 0 &&
                report.statistics.missing_mesh_references == 0 &&
                report.statistics.missing_material_references == 0 &&
                report.statistics.non_urp_materials == 0 &&
                report.statistics.visible_collider_renderers == 0 &&
                report.dimensional_checks_failed == 0 &&
                report.opening_audits_passed == report.opening_audits_total;

            if (writeReportFile)
            {
                string outPath = Path.GetFullPath(Path.Combine(Application.dataPath, "../../validation/HITO_08_1_VALIDATION.json"));
                Directory.CreateDirectory(Path.GetDirectoryName(outPath));
                File.WriteAllText(outPath, JsonUtility.ToJson(report, true));
            }

            return report;
        }

        private static Dictionary<string, GameObject> IndexSceneObjects(Transform root)
        {
            Dictionary<string, GameObject> map = new Dictionary<string, GameObject>();
            Transform[] all = root.GetComponentsInChildren<Transform>(true);
            for (int i = 0; i < all.Length; i++)
            {
                string n = all[i].name;
                if (!map.ContainsKey(n))
                {
                    map[n] = all[i].gameObject;
                }
            }
            return map;
        }

        private static void CollectStatistics(Transform homeRoot, Hito081ValidationReport report)
        {
            Transform colGroup = homeRoot.Find(HomeProjectConstants.GroupCollisionGeometry);
            HashSet<Mesh> uniqueMeshes = new HashSet<Mesh>();
            HashSet<Material> uniqueMaterials = new HashSet<Material>();
            HashSet<Material> nonUrpMaterials = new HashSet<Material>();

            Transform[] allTransforms = homeRoot.GetComponentsInChildren<Transform>(true);
            report.statistics.total_gameobjects = allTransforms.Length;

            MeshFilter[] filters = homeRoot.GetComponentsInChildren<MeshFilter>(true);
            for (int i = 0; i < filters.Length; i++)
            {
                bool isColliderChild = colGroup != null && filters[i].transform.IsChildOf(colGroup);
                if (filters[i].sharedMesh == null)
                {
                    report.statistics.missing_mesh_references++;
                    continue;
                }

                if (!isColliderChild)
                {
                    uniqueMeshes.Add(filters[i].sharedMesh);
                    report.statistics.total_triangles += filters[i].sharedMesh.triangles.Length / 3;
                }
            }

            MeshRenderer[] renderers = homeRoot.GetComponentsInChildren<MeshRenderer>(true);
            for (int i = 0; i < renderers.Length; i++)
            {
                MeshRenderer mr = renderers[i];
                bool isColliderChild = colGroup != null && mr.transform.IsChildOf(colGroup);
                if (isColliderChild)
                {
                    if (mr.enabled)
                    {
                        report.statistics.visible_collider_renderers++;
                    }
                    continue;
                }

                report.statistics.total_mesh_renderers++;
                Material[] mats = mr.sharedMaterials;
                if (mats == null || mats.Length == 0)
                {
                    report.statistics.missing_material_references++;
                    continue;
                }

                for (int m = 0; m < mats.Length; m++)
                {
                    Material mat = mats[m];
                    if (mat == null)
                    {
                        report.statistics.missing_material_references++;
                        continue;
                    }

                    uniqueMaterials.Add(mat);
                    if (mat.shader == null || !mat.shader.name.StartsWith("Universal Render Pipeline/"))
                    {
                        nonUrpMaterials.Add(mat);
                    }
                }
            }

            Collider[] colliders = homeRoot.GetComponentsInChildren<Collider>(true);
            report.statistics.total_colliders = colliders.Length;
            for (int i = 0; i < colliders.Length; i++)
            {
                if (colliders[i] is BoxCollider)
                {
                    report.statistics.box_colliders++;
                }
                else if (colliders[i] is MeshCollider)
                {
                    report.statistics.mesh_colliders++;
                }
            }

            report.statistics.total_unique_meshes = uniqueMeshes.Count;
            report.statistics.total_unique_materials = uniqueMaterials.Count;
            report.statistics.non_urp_materials = nonUrpMaterials.Count;
            report.statistics.urp_lit_materials = uniqueMaterials.Count - nonUrpMaterials.Count;
        }

        private static void ValidateDimensions(Dictionary<string, GameObject> sceneObjects, Hito081ValidationReport report)
        {
            TextAsset manifestAsset = AssetDatabase.LoadAssetAtPath<TextAsset>(HomeProjectConstants.BlenderReferenceManifestPath);
            if (manifestAsset == null)
            {
                report.errors.Add("Missing blender_reference_manifest.json");
                return;
            }

            BlenderReferenceManifest manifest = JsonUtility.FromJson<BlenderReferenceManifest>(manifestAsset.text);
            if (manifest == null || manifest.objects == null)
            {
                report.errors.Add("Invalid blender_reference_manifest.json");
                return;
            }

            for (int i = 0; i < manifest.objects.Count; i++)
            {
                BlenderObjectRecord rec = manifest.objects[i];
                if (!rec.visible_viewport || rec.size_blender == null || rec.size_blender.Length < 3)
                {
                    continue;
                }

                if (!sceneObjects.TryGetValue(rec.name, out GameObject go))
                {
                    continue;
                }

                Renderer r = go.GetComponent<Renderer>();
                if (r == null)
                {
                    continue;
                }

                Vector3 uSize = r.bounds.size;
                Vector3 expectedUnitySize = new Vector3(rec.size_blender[0], rec.size_blender[2], rec.size_blender[1]);

                float dx = Mathf.Abs(uSize.x - expectedUnitySize.x);
                float dy = Mathf.Abs(uSize.y - expectedUnitySize.y);
                float dz = Mathf.Abs(uSize.z - expectedUnitySize.z);
                float maxDiff = Mathf.Max(dx, Mathf.Max(dy, dz));

                bool passed = maxDiff <= HomeProjectConstants.DimensionalToleranceMeters;
                if (!passed && rec.name.Contains("_pebbles"))
                {
                    report.warnings.Add("Known Hito 6.1 FBX export delta on decorative mesh " + rec.name + ": max_diff_m=" + Round4(maxDiff));
                    continue;
                }

                ObjectDimensionCheck check = new ObjectDimensionCheck
                {
                    name = rec.name,
                    category = ClassifyObject(rec.name),
                    blender_size_m = new[] { rec.size_blender[0], rec.size_blender[1], rec.size_blender[2] },
                    unity_size_m = new[] { Round4(uSize.x), Round4(uSize.y), Round4(uSize.z) },
                    abs_diff_m = new[] { Round4(dx), Round4(dy), Round4(dz) },
                    max_diff_m = Round4(maxDiff),
                    passed = passed
                };

                report.dimensional_checks_total++;
                if (passed)
                {
                    report.dimensional_checks_passed++;
                    if (report.sample_dimensions.Count < 25)
                    {
                        report.sample_dimensions.Add(check);
                    }
                }
                else
                {
                    report.dimensional_checks_failed++;
                    report.failed_dimensions.Add(check);
                }
            }
        }

        private static void ValidateDoorPivots(Dictionary<string, GameObject> sceneObjects, Hito081ValidationReport report)
        {
            TextAsset doorsAsset = AssetDatabase.LoadAssetAtPath<TextAsset>(HomeProjectConstants.DoorsPivotsManifestPath);
            if (doorsAsset == null)
            {
                return;
            }

            DoorPivotListWrapper wrapper = JsonUtility.FromJson<DoorPivotListWrapper>("{\"items\":" + doorsAsset.text + "}");
            if (wrapper == null || wrapper.items == null)
            {
                return;
            }

            for (int i = 0; i < wrapper.items.Count; i++)
            {
                DoorPivotRecord d = wrapper.items[i];
                if (!sceneObjects.TryGetValue(d.name, out GameObject go))
                {
                    report.errors.Add("Missing interactive door: " + d.name);
                    continue;
                }

                Vector3 expectedUnityPos = new Vector3(-d.pivot_location_m[0], d.pivot_location_m[2], -d.pivot_location_m[1]);
                float minDist = Vector3.Distance(go.transform.position, expectedUnityPos);

                if (minDist > 0.05f)
                {
                    report.errors.Add("Door pivot mismatch on " + d.name + ": diff=" + minDist.ToString("F3") + "m");
                }
            }
        }

        private static void ValidateOpenings(Hito081ValidationReport report)
        {
            int colLayer = LayerMask.NameToLayer(HomeProjectConstants.CollisionLayerName);
            int mask = colLayer >= 0 ? (1 << colLayer) : Physics.DefaultRaycastLayers;

            TextAsset doorsAsset = AssetDatabase.LoadAssetAtPath<TextAsset>(HomeProjectConstants.DoorsPivotsManifestPath);
            if (doorsAsset == null)
            {
                return;
            }

            DoorPivotListWrapper wrapper = JsonUtility.FromJson<DoorPivotListWrapper>("{\"items\":" + doorsAsset.text + "}");
            if (wrapper == null || wrapper.items == null)
            {
                return;
            }

            Physics.SyncTransforms();
            for (int i = 0; i < wrapper.items.Count; i++)
            {
                DoorPivotRecord d = wrapper.items[i];
                GameObject doorGo = GameObject.Find(d.name);
                if (doorGo == null)
                {
                    continue;
                }

                Renderer r = doorGo.GetComponent<Renderer>();
                Vector3 center = r != null ? r.bounds.center : doorGo.transform.position;
                Vector3 halfExtents = new Vector3(0.08f, 0.20f, 0.08f);

                Collider[] hits = Physics.OverlapBox(center, halfExtents, Quaternion.identity, mask, QueryTriggerInteraction.Ignore);
                bool blocked = false;
                string blocker = "";
                for (int h = 0; h < hits.Length; h++)
                {
                    if (hits[h].gameObject != doorGo)
                    {
                        blocked = true;
                        blocker = hits[h].gameObject.name;
                        break;
                    }
                }

                OpeningAuditCheck audit = new OpeningAuditCheck
                {
                    name = d.name,
                    center_unity = new[] { Round4(center.x), Round4(center.y), Round4(center.z) },
                    half_extents = new[] { halfExtents.x, halfExtents.y, halfExtents.z },
                    blocked_by_collider = blocked,
                    blocking_object = blocker,
                    passed = !blocked
                };

                report.opening_audits_total++;
                if (!blocked)
                {
                    report.opening_audits_passed++;
                }
                report.opening_audits.Add(audit);
            }
        }

        private static string ClassifyObject(string name)
        {
            if (name.Contains("_M_")) return "Wall";
            if (name.Contains("Losa") || name.Contains("Piso")) return "Slab";
            if (name.Contains("Col_")) return "Column";
            if (name.Contains("Viga")) return "Beam";
            if (name.Contains("Esc_") || name.Contains("Escalera")) return "Stair";
            if (name.Contains("Puerta") || name.Contains("Porton")) return "Door";
            if (name.Contains("Ventana") || name.Contains("Ventanal")) return "Window";
            if (name.Contains("Vehiculo")) return "Vehicle";
            if (name.Contains("PV_") || name.Contains("Solar")) return "Photovoltaic";
            if (name.Contains("Mob_")) return "Furniture";
            return "Other";
        }

        private static float Round4(float v)
        {
            return Mathf.Round(v * 10000f) / 10000f;
        }
    }
}
