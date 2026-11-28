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

            Dictionary<string, GameObject> sceneObjects = IndexSceneObjects(homeRoot.transform, report);
            CollectStatistics(homeRoot.transform, report);
            ValidateTransformsAndDimensions(sceneObjects, report);
            ValidateDoorPivots(sceneObjects, report);
            ValidateCapsuleOpenings(report);
            ValidateFloorRaycasts(report);

            report.overall_passed =
                report.errors.Count == 0 &&
                report.statistics.missing_expected_objects == 0 &&
                report.statistics.duplicate_object_names == 0 &&
                report.statistics.missing_mesh_references == 0 &&
                report.statistics.missing_material_references == 0 &&
                report.statistics.non_urp_materials == 0 &&
                report.statistics.visible_collider_renderers == 0 &&
                report.dimensional_checks_failed == 0 &&
                report.pivot_checks_passed == report.pivot_checks_total &&
                report.capsule_audits_passed == report.capsule_audits_total &&
                report.floor_raycasts_passed == report.floor_raycasts_total;

            if (writeReportFile)
            {
                string json = JsonUtility.ToJson(report, true);
                string outPath = Path.GetFullPath(Path.Combine(Application.dataPath, "../../validation/HITO_08_3_1_VALIDATION.json"));
                Directory.CreateDirectory(Path.GetDirectoryName(outPath));
                File.WriteAllText(outPath, json);
                string outPath2 = Path.GetFullPath(Path.Combine(Application.dataPath, "../../validation/HITO_08_3_2_VALIDATION.json"));
                File.WriteAllText(outPath2, json);
            }

            return report;
        }

        private static Dictionary<string, GameObject> IndexSceneObjects(Transform root, Hito081ValidationReport report)
        {
            Dictionary<string, GameObject> map = new Dictionary<string, GameObject>();
            Transform colGroup = root.Find(HomeProjectConstants.GroupCollisionGeometry);
            Transform[] all = root.GetComponentsInChildren<Transform>(true);

            for (int i = 0; i < all.Length; i++)
            {
                Transform t = all[i];
                if (t == root || t.parent == root || t.name.EndsWith("_pkg"))
                {
                    continue;
                }
                if (colGroup != null && t.IsChildOf(colGroup))
                {
                    continue;
                }

                string n = t.name;
                if (map.ContainsKey(n))
                {
                    report.statistics.duplicate_object_names++;
                    report.duplicate_names.Add(n);
                }
                else
                {
                    map[n] = t.gameObject;
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

        private static void ValidateTransformsAndDimensions(Dictionary<string, GameObject> sceneObjects, Hito081ValidationReport report)
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
                if (!rec.visible_viewport || !rec.visible_render || rec.size_blender == null || rec.size_blender.Length < 3)
                {
                    continue;
                }

                if (!sceneObjects.TryGetValue(rec.name, out GameObject go))
                {
                    report.statistics.missing_expected_objects++;
                    report.missing_objects.Add(rec.name);
                    continue;
                }

                Renderer r = go.GetComponent<Renderer>();
                if (r == null)
                {
                    report.errors.Add("Missing Renderer on expected object: " + rec.name);
                    continue;
                }

                Vector3 uSize = r.bounds.size;
                Vector3 expectedSize = new Vector3(rec.size_blender[0], rec.size_blender[2], rec.size_blender[1]);
                float maxSizeDiff = Mathf.Max(
                    Mathf.Abs(uSize.x - expectedSize.x),
                    Mathf.Max(Mathf.Abs(uSize.y - expectedSize.y), Mathf.Abs(uSize.z - expectedSize.z)));

                float centerDiff = 0f;
                if (rec.world_center_blender != null && rec.world_center_blender.Length >= 3)
                {
                    Vector3 expectedCenter = new Vector3(-rec.world_center_blender[0], rec.world_center_blender[2], -rec.world_center_blender[1]);
                    centerDiff = Vector3.Distance(r.bounds.center, expectedCenter);
                }

                bool isPebbleException = rec.name.Contains("_pebbles");
                if (isPebbleException && maxSizeDiff > HomeProjectConstants.DimensionalToleranceMeters)
                {
                    report.explicit_exceptions.Add(new ExplicitExceptionRecord
                    {
                        object_name = rec.name,
                        magnitude_m = Round4(maxSizeDiff),
                        justification = "Sub-malla decorativa de guijarros en maceta heredada del export FBX de Hito 6.1; no afecta estructura ni navegabilidad."
                    });
                    continue;
                }

                bool passed = maxSizeDiff <= HomeProjectConstants.DimensionalToleranceMeters &&
                              centerDiff <= HomeProjectConstants.DimensionalToleranceMeters;

                report.dimensional_checks_total++;
                if (passed)
                {
                    report.dimensional_checks_passed++;
                }
                else
                {
                    report.dimensional_checks_failed++;
                    report.failed_transforms.Add(new ObjectTransformCheck
                    {
                        name = rec.name,
                        category = ClassifyObject(rec.name),
                        blender_size_m = new[] { rec.size_blender[0], rec.size_blender[1], rec.size_blender[2] },
                        unity_size_m = new[] { Round4(uSize.x), Round4(uSize.y), Round4(uSize.z) },
                        max_size_diff_m = Round4(maxSizeDiff),
                        center_pos_diff_m = Round4(centerDiff),
                        passed = false
                    });
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
                report.pivot_checks_total++;
                if (!sceneObjects.TryGetValue(d.name, out GameObject go))
                {
                    report.errors.Add("Missing interactive door: " + d.name);
                    continue;
                }

                Vector3 expectedUnityPos = new Vector3(-d.pivot_location_m[0], d.pivot_location_m[2], -d.pivot_location_m[1]);
                float dist = Vector3.Distance(go.transform.position, expectedUnityPos);

                if (dist <= HomeProjectConstants.DimensionalToleranceMeters)
                {
                    report.pivot_checks_passed++;
                }
                else
                {
                    report.errors.Add("Door pivot mismatch on " + d.name + ": diff=" + dist.ToString("F4") + "m");
                }
            }
        }

        private static void ValidateCapsuleOpenings(Hito081ValidationReport report)
        {
            int colLayer = LayerMask.NameToLayer(HomeProjectConstants.CollisionLayerName);
            int mask = colLayer >= 0 ? (1 << colLayer) : Physics.DefaultRaycastLayers;
            Physics.SyncTransforms();

            float radius = 0.30f;
            float height = 1.80f;

            (string name, Vector3 start, Vector3 end)[] sweeps =
            {
                ("Acceso_Peatonal_Exterior_a_Sala", new Vector3(-1.12f, 0.05f, 1.2f), new Vector3(-1.12f, 0.05f, -2.5f)),
                ("Sala_a_Bano_Social", new Vector3(-2.60f, 0.05f, -4.1f), new Vector3(-2.60f, 0.05f, -5.2f)),
                ("Sala_a_Garaje", new Vector3(-4.0f, 0.05f, -4.12f), new Vector3(-5.1f, 0.05f, -4.12f)),
                ("Pasillo_a_Hab_Huespedes", new Vector3(-2.62f, 0.05f, -7.5f), new Vector3(-2.62f, 0.05f, -8.8f)),
                ("Cocina_a_Lavanderia", new Vector3(-6.65f, 0.05f, -7.5f), new Vector3(-6.65f, 0.05f, -8.8f)),
                ("Master_a_Vestidor", new Vector3(-4.0f, 2.95f, -3.05f), new Vector3(-5.2f, 2.95f, -3.05f)),
                ("Corredor_P2_a_Hija_1", new Vector3(-3.4f, 2.95f, -6.1f), new Vector3(-3.4f, 2.95f, -7.3f)),
                ("Corredor_P2_a_Hija_2", new Vector3(-4.6f, 2.95f, -6.1f), new Vector3(-4.6f, 2.95f, -7.3f))
            };

            for (int i = 0; i < sweeps.Length; i++)
            {
                Vector3 p1 = sweeps[i].start + Vector3.up * (radius + 0.05f);
                Vector3 p2 = sweeps[i].start + Vector3.up * (height - radius);
                Vector3 dir = sweeps[i].end - sweeps[i].start;
                float dist = dir.magnitude;

                bool blocked = Physics.CapsuleCast(p1, p2, radius, dir.normalized, out RaycastHit hit, dist, mask, QueryTriggerInteraction.Ignore);
                CapsuleSweepAudit audit = new CapsuleSweepAudit
                {
                    name = sweeps[i].name,
                    start_unity = new[] { sweeps[i].start.x, sweeps[i].start.y, sweeps[i].start.z },
                    end_unity = new[] { sweeps[i].end.x, sweeps[i].end.y, sweeps[i].end.z },
                    capsule_radius_m = radius,
                    capsule_height_m = height,
                    blocked = blocked,
                    blocking_object = blocked ? hit.collider.gameObject.name : "",
                    passed = !blocked
                };

                report.capsule_audits_total++;
                if (!blocked)
                {
                    report.capsule_audits_passed++;
                }
                report.capsule_audits.Add(audit);
            }
        }

        private static void ValidateFloorRaycasts(Hito081ValidationReport report)
        {
            Physics.SyncTransforms();
            (string zone, Vector3 origin, string expectedPrefix)[] checks =
            {
                ("Anden_Frontal", new Vector3(-2.0f, 1.0f, 0.75f), "Anden_Frontal"),
                ("Sala_P1", new Vector3(-1.12f, 1.5f, -2.0f), "P1_Piso_P1_Sala"),
                ("Garaje_P1", new Vector3(-4.85f, 1.5f, -2.4f), "P1_Piso_P1_Garaje"),
                ("Cocina_P1", new Vector3(-6.7f, 1.5f, -6.9f), "P1_Piso_P1_Cocina"),
                ("Huespedes_P1", new Vector3(-2.3f, 1.5f, -9.6f), "P1_Piso_P1_Habitacion_Huespedes"),
                ("Escalera_Peldano_08", new Vector3(-4.97f, 2.5f, -5.22f), "P1_Esc_Peldano"),
                ("Desembarco_P2", new Vector3(-7.3f, 4.0f, -5.2f), "P2_Piso_P2_Llegada_Escalera"),
                ("Master_P2", new Vector3(-3.8f, 4.0f, -1.0f), "P2_Piso_P2_Habitacion_Principal")
            };

            for (int i = 0; i < checks.Length; i++)
            {
                bool hit = Physics.Raycast(checks[i].origin, Vector3.down, out RaycastHit hitInfo, 3.0f, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
                string hitName = hit ? hitInfo.collider.gameObject.name : "";
                bool passed = hit && hitName.StartsWith(checks[i].expectedPrefix);

                report.floor_raycasts_total++;
                if (passed)
                {
                    report.floor_raycasts_passed++;
                }

                report.floor_raycasts.Add(new FloorRaycastAudit
                {
                    zone_name = checks[i].zone,
                    origin_unity = new[] { checks[i].origin.x, checks[i].origin.y, checks[i].origin.z },
                    hit = hit,
                    hit_object = hitName,
                    hit_y = hit ? Round4(hitInfo.point.y) : 0f,
                    passed = passed
                });
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
