using System.IO;
using HomeProject.Core;
using HomeProject.Validation;
using UnityEditor;
using UnityEngine;

namespace HomeProject.Editor
{
    public static class NegativeTestsRunner
    {
        public static Hito081NegativeTestsReport RunAllNegativeTests()
        {
            Hito081NegativeTestsReport report = new Hito081NegativeTestsReport();

            report.cases.Add(TestWrongScale());
            report.cases.Add(TestMissingAsset());
            report.cases.Add(TestIncompatibleShader());
            report.cases.Add(TestColliderBlockingDoor());
            report.cases.Add(TestVisibleCollider());
            report.cases.Add(TestWrongPivot());
            report.cases.Add(TestFloorMisalignment());
            report.cases.Add(TestDuplicateObjectName());
            report.cases.Add(TestMissingWalkableSurface());

            report.total_cases = report.cases.Count;
            for (int i = 0; i < report.cases.Count; i++)
            {
                if (report.cases[i].passed)
                {
                    report.passed_cases++;
                }
            }
            report.all_detected = report.passed_cases == report.total_cases;

            string outPath = Path.GetFullPath(Path.Combine(Application.dataPath, "../../validation/HITO_08_3_1_NEGATIVE_TESTS.json"));
            Directory.CreateDirectory(Path.GetDirectoryName(outPath));
            File.WriteAllText(outPath, JsonUtility.ToJson(report, true));
            return report;
        }

        private static NegativeTestCaseResult TestWrongScale()
        {
            GameObject target = GameObject.Find("P1_M_Oeste_S0");
            if (target == null)
            {
                return FailedSetup("NEG_01_WRONG_SCALE", "Target P1_M_Oeste_S0 not found");
            }

            Vector3 origScale = target.transform.localScale;
            target.transform.localScale = new Vector3(2f, 2f, 2f);
            Hito081ValidationReport val = SceneValidatorService.ValidateCurrentScene(false);
            target.transform.localScale = origScale;

            bool detected = val.dimensional_checks_failed > 0;
            return new NegativeTestCaseResult
            {
                test_id = "NEG_01_WRONG_SCALE",
                description = "Escalar P1_M_Oeste_S0 a (2,2,2) debe fallar validacion dimensional",
                fault_detected = detected,
                detector_message = "dimensional_checks_failed=" + val.dimensional_checks_failed,
                scene_restored = target.transform.localScale == origScale,
                passed = detected
            };
        }

        private static NegativeTestCaseResult TestMissingAsset()
        {
            GameObject target = GameObject.Find("P1_M_Oeste_S0");
            MeshFilter mf = target != null ? target.GetComponent<MeshFilter>() : null;
            if (mf == null)
            {
                return FailedSetup("NEG_02_MISSING_ASSET", "MeshFilter not found");
            }

            Mesh origMesh = mf.sharedMesh;
            mf.sharedMesh = null;
            Hito081ValidationReport val = SceneValidatorService.ValidateCurrentScene(false);
            mf.sharedMesh = origMesh;

            bool detected = val.statistics.missing_mesh_references > 0;
            return new NegativeTestCaseResult
            {
                test_id = "NEG_02_MISSING_ASSET",
                description = "Remover sharedMesh en P1_M_Oeste_S0 debe detectarse como referencia faltante",
                fault_detected = detected,
                detector_message = "missing_mesh_references=" + val.statistics.missing_mesh_references,
                scene_restored = mf.sharedMesh == origMesh,
                passed = detected
            };
        }

        private static NegativeTestCaseResult TestIncompatibleShader()
        {
            GameObject target = GameObject.Find("P1_M_Oeste_S0");
            MeshRenderer mr = target != null ? target.GetComponent<MeshRenderer>() : null;
            Shader standard = Shader.Find("Standard");
            if (mr == null || standard == null)
            {
                return FailedSetup("NEG_03_INCOMPATIBLE_SHADER", "Renderer or Standard shader not found");
            }

            Material[] origMats = mr.sharedMaterials;
            Material badMat = new Material(standard);
            mr.sharedMaterials = new[] { badMat };
            Hito081ValidationReport val = SceneValidatorService.ValidateCurrentScene(false);
            mr.sharedMaterials = origMats;
            Object.DestroyImmediate(badMat);

            bool detected = val.statistics.non_urp_materials > 0;
            return new NegativeTestCaseResult
            {
                test_id = "NEG_03_INCOMPATIBLE_SHADER",
                description = "Asignar shader Built-In Standard debe detectarse como material no-URP",
                fault_detected = detected,
                detector_message = "non_urp_materials=" + val.statistics.non_urp_materials,
                scene_restored = mr.sharedMaterials.Length == origMats.Length,
                passed = detected
            };
        }

        private static NegativeTestCaseResult TestColliderBlockingDoor()
        {
            GameObject door = GameObject.Find("P1_M_Sur_Sala_Puerta1");
            if (door == null)
            {
                return FailedSetup("NEG_04_COLLIDER_BLOCKING_DOOR", "Door P1_M_Sur_Sala_Puerta1 not found");
            }

            Renderer r = door.GetComponent<Renderer>();
            GameObject blocker = new GameObject("_TMP_DOOR_BLOCKER");
            blocker.layer = LayerMask.NameToLayer(HomeProjectConstants.CollisionLayerName);
            blocker.transform.position = r != null ? r.bounds.center : door.transform.position;
            BoxCollider bc = blocker.AddComponent<BoxCollider>();
            bc.size = new Vector3(1.0f, 2.0f, 1.0f);
            Physics.SyncTransforms();

            Hito081ValidationReport val = SceneValidatorService.ValidateCurrentScene(false);
            Object.DestroyImmediate(blocker);
            Physics.SyncTransforms();

            bool detected = val.capsule_audits_passed < val.capsule_audits_total;
            return new NegativeTestCaseResult
            {
                test_id = "NEG_04_COLLIDER_BLOCKING_DOOR",
                description = "Collider bloqueando puerta principal debe detectarse en barrido volumetrico de capsula",
                fault_detected = detected,
                detector_message = "capsule_audits_passed=" + val.capsule_audits_passed + "/" + val.capsule_audits_total,
                scene_restored = GameObject.Find("_TMP_DOOR_BLOCKER") == null,
                passed = detected
            };
        }

        private static NegativeTestCaseResult TestVisibleCollider()
        {
            GameObject colRoot = GameObject.Find(HomeProjectConstants.HomeProjectRootName + "/" + HomeProjectConstants.GroupCollisionGeometry);
            MeshRenderer mr = colRoot != null ? colRoot.GetComponentInChildren<MeshRenderer>(true) : null;
            if (mr == null)
            {
                return FailedSetup("NEG_05_VISIBLE_COLLIDER", "Collider MeshRenderer not found");
            }

            bool origEnabled = mr.enabled;
            mr.enabled = true;
            Hito081ValidationReport val = SceneValidatorService.ValidateCurrentScene(false);
            mr.enabled = origEnabled;

            bool detected = val.statistics.visible_collider_renderers > 0;
            return new NegativeTestCaseResult
            {
                test_id = "NEG_05_VISIBLE_COLLIDER",
                description = "Habilitar MeshRenderer en CollisionGeometry debe detectarse como collider visible",
                fault_detected = detected,
                detector_message = "visible_collider_renderers=" + val.statistics.visible_collider_renderers,
                scene_restored = mr.enabled == origEnabled,
                passed = detected
            };
        }

        private static NegativeTestCaseResult TestWrongPivot()
        {
            GameObject door = GameObject.Find("P1_M_Sur_Sala_Puerta1");
            if (door == null)
            {
                return FailedSetup("NEG_06_WRONG_PIVOT", "Door P1_M_Sur_Sala_Puerta1 not found");
            }

            Vector3 origPos = door.transform.position;
            door.transform.position = origPos + new Vector3(0.05f, 0f, 0f);
            Hito081ValidationReport val = SceneValidatorService.ValidateCurrentScene(false);
            door.transform.position = origPos;

            bool detected = val.pivot_checks_passed < val.pivot_checks_total;
            return new NegativeTestCaseResult
            {
                test_id = "NEG_06_WRONG_PIVOT",
                description = "Desplazar pivote de puerta 0.05m (> 0.02m) debe detectarse en validacion de pivotes",
                fault_detected = detected,
                detector_message = "pivot_checks_passed=" + val.pivot_checks_passed + "/" + val.pivot_checks_total,
                scene_restored = door.transform.position == origPos,
                passed = detected
            };
        }

        private static NegativeTestCaseResult TestFloorMisalignment()
        {
            GameObject p2 = GameObject.Find("P2_Losa_Seg_1");
            if (p2 == null)
            {
                return FailedSetup("NEG_07_FLOOR_MISALIGNMENT", "P2_Losa_Seg_1 not found");
            }

            Vector3 origPos = p2.transform.position;
            p2.transform.position = origPos + new Vector3(0f, 0.25f, 0f);
            Hito081ValidationReport val = SceneValidatorService.ValidateCurrentScene(false);
            p2.transform.position = origPos;

            bool detected = val.dimensional_checks_failed > 0;
            return new NegativeTestCaseResult
            {
                test_id = "NEG_07_FLOOR_MISALIGNMENT",
                description = "Desplazar losa P2 verticalmente 0.25m debe detectarse en validacion posicional",
                fault_detected = detected,
                detector_message = "dimensional_checks_failed=" + val.dimensional_checks_failed,
                scene_restored = p2.transform.position == origPos,
                passed = detected
            };
        }

        private static NegativeTestCaseResult TestDuplicateObjectName()
        {
            GameObject arch = GameObject.Find(HomeProjectConstants.HomeProjectRootName + "/" + HomeProjectConstants.GroupArchitecture);
            if (arch == null)
            {
                return FailedSetup("NEG_08_DUPLICATE_OBJECT_NAME", "Architecture group not found");
            }

            GameObject dup = new GameObject("P1_M_Oeste_S0");
            dup.transform.SetParent(arch.transform, false);
            Hito081ValidationReport val = SceneValidatorService.ValidateCurrentScene(false);
            Object.DestroyImmediate(dup);

            bool detected = val.statistics.duplicate_object_names > 0;
            return new NegativeTestCaseResult
            {
                test_id = "NEG_08_DUPLICATE_OBJECT_NAME",
                description = "Introducir objeto con nombre duplicado debe detectarse en UNI-01",
                fault_detected = detected,
                detector_message = "duplicate_object_names=" + val.statistics.duplicate_object_names,
                scene_restored = true,
                passed = detected
            };
        }

        private static NegativeTestCaseResult TestMissingWalkableSurface()
        {
            GameObject salaFloor = GameObject.Find("P1_Piso_P1_Sala");
            Collider col = salaFloor != null ? salaFloor.GetComponent<Collider>() : null;
            if (col == null)
            {
                return FailedSetup("NEG_09_MISSING_SURFACE", "P1_Piso_P1_Sala collider not found");
            }

            bool origEnabled = col.enabled;
            col.enabled = false;
            Physics.SyncTransforms();
            Hito081ValidationReport val = SceneValidatorService.ValidateCurrentScene(false);
            col.enabled = origEnabled;
            Physics.SyncTransforms();

            bool detected = val.floor_raycasts_passed < val.floor_raycasts_total;
            return new NegativeTestCaseResult
            {
                test_id = "NEG_09_MISSING_SURFACE",
                description = "Deshabilitar collider de piso transitable debe detectarse en UNI-05",
                fault_detected = detected,
                detector_message = "floor_raycasts_passed=" + val.floor_raycasts_passed + "/" + val.floor_raycasts_total,
                scene_restored = col.enabled == origEnabled,
                passed = detected
            };
        }

        private static NegativeTestCaseResult FailedSetup(string id, string msg)
        {
            return new NegativeTestCaseResult
            {
                test_id = id,
                description = msg,
                fault_detected = false,
                detector_message = msg,
                scene_restored = true,
                passed = false
            };
        }
    }
}
