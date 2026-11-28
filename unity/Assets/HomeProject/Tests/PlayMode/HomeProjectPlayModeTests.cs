using System;
using System.Collections;
using System.IO;
using HomeProject.Core;
using HomeProject.Infrastructure;
using HomeProject.Interaction;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace HomeProject.Tests.PlayMode
{
    [Serializable]
    public class Hito083PerformanceReport
    {
        public string milestone = "Hito 8.3";
        public int screen_width;
        public int screen_height;
        public int warmup_frames = 60;
        public string render_pipeline = "URP 17.6.0 (Forward+, HDR, MSAA 4x, SSAO, Shadows 4096)";
        public float average_fps;
        public float average_frame_time_ms;
        public float p95_frame_time_ms;
        public float p99_frame_time_ms;
        public float one_percent_low_fps;
    }

    public class HomeProjectPlayModeTests
    {
        private IEnumerator LoadMainScene()
        {
            #if UNITY_EDITOR
            yield return UnityEditor.SceneManagement.EditorSceneManager.LoadSceneInPlayMode(
                HomeProjectConstants.ScenePath,
                new LoadSceneParameters(LoadSceneMode.Single));
            #else
            SceneManager.LoadScene("HomeProject_Main", LoadSceneMode.Single);
            yield return null;
            #endif
            yield return null;
        }

        private static int CountEnabledCameras()
        {
            Camera[] cams = UnityEngine.Object.FindObjectsByType<Camera>(FindObjectsInactive.Include);
            int count = 0;
            for (int i = 0; i < cams.Length; i++)
            {
                if (cams[i].enabled)
                {
                    count++;
                }
            }
            return count;
        }

        [UnityTest]
        public IEnumerator OrbitalModeSingleActiveCameraRotationAndZoom()
        {
            yield return LoadMainScene();

            ResidentialFirstPersonController player = UnityEngine.Object.FindAnyObjectByType<ResidentialFirstPersonController>();
            OrbitalInspectionCamera orbital = UnityEngine.Object.FindAnyObjectByType<OrbitalInspectionCamera>(FindObjectsInactive.Include);
            Assert.IsNotNull(player);
            Assert.IsNotNull(orbital);

            Assert.AreEqual(1, CountEnabledCameras(), "Expected exactly 1 active camera in FPS mode.");
            Assert.IsFalse(orbital.IsActive);

            player.SetOrbitalMode(true);
            yield return null;
            Assert.AreEqual(1, CountEnabledCameras(), "Expected exactly 1 active camera in Orbital mode.");
            Assert.IsTrue(orbital.IsActive);

            Vector3 posBefore = orbital.transform.position;
            float distBefore = orbital.Distance;
            orbital.ApplyOrbitInput(25f, 10f, -3f);
            yield return null;
            Assert.AreNotEqual(posBefore, orbital.transform.position, "Orbital camera did not rotate.");
            Assert.Less(orbital.Distance, distBefore, "Orbital camera did not zoom in.");

            orbital.ApplyOrbitInput(-10f, -5f, 4f);
            yield return null;
            Assert.Greater(orbital.Distance, distBefore - 3f, "Orbital camera did not zoom out.");

            player.SetOrbitalMode(false);
            yield return null;
            Assert.AreEqual(1, CountEnabledCameras(), "Expected exactly 1 active camera after returning to FPS.");
        }

        private static IEnumerator PressSyntheticKey(Key key)
        {
            Application.runInBackground = true;
            InputSystem.settings.backgroundBehavior = InputSettings.BackgroundBehavior.IgnoreFocus;
            Keyboard kb = InputSystem.AddDevice<Keyboard>();
            kb.MakeCurrent();
            yield return null;
            yield return null;
            InputSystem.QueueStateEvent(kb, new KeyboardState());
            yield return null;
            InputSystem.QueueStateEvent(kb, new KeyboardState(key));
            yield return null;
            yield return null;
            yield return null;
            yield return null;
            InputSystem.QueueStateEvent(kb, new KeyboardState());
            yield return null;
            InputSystem.RemoveDevice(kb);
        }

        [UnityTest]
        public IEnumerator InputSystemEKeyOpensDoorAndWindowBlocksPlayer()
        {
            yield return LoadMainScene();

            ResidentialFirstPersonController player = UnityEngine.Object.FindAnyObjectByType<ResidentialFirstPersonController>();
            GameObject doorGo = GameObject.Find("P1_M_Sur_Sala_Puerta1");
            Assert.IsNotNull(player);
            Assert.IsNotNull(doorGo);
            InteractiveDoor door = doorGo.GetComponent<InteractiveDoor>();
            door.SetOpen(false, true);

            player.TeleportTo(new Vector3(-1.12f, 0.08f, -1.10f), 180f);
            yield return null;

            yield return PressSyntheticKey(Key.E);

            Assert.IsTrue(door.IsOpen, "Pressing E via InputSystem did not open P1_M_Sur_Sala_Puerta1.");

            GameObject winGlass = GameObject.Find("P2_M_Sur_Win1_Glass");
            Assert.IsNotNull(winGlass, "Window glass P2_M_Sur_Win1_Glass missing.");
            Assert.IsNotNull(winGlass.GetComponent<Collider>(), "Window glass must have a Collider.");
        }

        [UnityTest]
        public IEnumerator ArchitecturalInspectionModeTogglesAndPreventsPlayerOverlap()
        {
            yield return LoadMainScene();

            ArchitecturalInspectionMode inspection = UnityEngine.Object.FindAnyObjectByType<ArchitecturalInspectionMode>();
            ResidentialFirstPersonController player = UnityEngine.Object.FindAnyObjectByType<ResidentialFirstPersonController>();
            Assert.IsNotNull(inspection, "ArchitecturalInspectionMode missing in scene.");
            Assert.IsNotNull(player);

            Assert.AreEqual(InspectionMode.ArchitectureOnly, inspection.CurrentMode, "Scene must start in ArchitectureOnly.");
            Assert.AreEqual(0, inspection.ActiveManagedRendererCount, "Non-architectural renderers must be hidden in ArchitectureOnly.");
            Assert.AreEqual(0, inspection.ActiveManagedColliderCount, "Non-architectural colliders must be disabled in ArchitectureOnly.");

            GameObject wall = GameObject.Find("P1_M_Oeste_S0");
            Assert.IsNotNull(wall);
            Assert.IsTrue(wall.GetComponent<Collider>() != null && wall.GetComponent<Collider>().enabled, "Architectural colliders must stay active.");

            GameObject tree = GameObject.Find("Arbol_Tropical_01_LOD0");
            Assert.IsNotNull(tree, "Arbol_Tropical_01_LOD0 missing.");
            Assert.IsTrue(tree.GetComponent<Renderer>().enabled, "Tropical trees must stay visible in ArchitectureOnly.");

            GameObject solar = GameObject.Find("Solar_Panel_01");
            if (solar == null)
            {
                foreach (MeshRenderer mr in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsInactive.Include))
                {
                    if (mr.gameObject.name.StartsWith("Solar_"))
                    {
                        solar = mr.gameObject;
                        break;
                    }
                }
            }
            Assert.IsNotNull(solar, "Solar panel object missing.");
            Assert.IsTrue(solar.GetComponent<Renderer>().enabled, "Solar panels must stay visible in ArchitectureOnly.");

            string renderDir = Path.GetFullPath(Path.Combine(Application.dataPath, "../../renders/hito_08_3_3"));
            Directory.CreateDirectory(renderDir);
            player.TeleportTo(new Vector3(-3.20f, 0.08f, -2.15f), 240f);
            yield return null;
            CaptureCameraFrame(player.PlayerCamera, Path.Combine(renderDir, "COMPARATIVA_ARCHITECTURE_ONLY.png"));

            yield return PressSyntheticKey(Key.M);

            Assert.AreEqual(InspectionMode.FullFurnished, inspection.CurrentMode,
                "Pressing M did not switch to FullFurnished. Blocked: " + inspection.LastBlockedReason);
            Assert.Greater(inspection.ActiveManagedRendererCount, 0, "FullFurnished must restore non-architectural renderers.");
            Assert.Greater(inspection.ActiveManagedColliderCount, 0, "FullFurnished must restore non-architectural colliders.");
            CaptureCameraFrame(player.PlayerCamera, Path.Combine(renderDir, "COMPARATIVA_FULL_FURNISHED.png"));

            Assert.IsTrue(inspection.SetMode(InspectionMode.ArchitectureOnly));
            Assert.AreEqual(0, inspection.ActiveManagedRendererCount);
            Assert.AreEqual(0, inspection.ActiveManagedColliderCount);

            player.TeleportTo(new Vector3(-5.88f, 0.08f, -2.25f), 180f);
            yield return null;
            bool switched = inspection.SetMode(InspectionMode.FullFurnished);
            Assert.IsFalse(switched, "Switching to FullFurnished must be blocked when player overlaps vehicle/furniture volume.");
            Assert.AreEqual(InspectionMode.ArchitectureOnly, inspection.CurrentMode);
            Assert.IsFalse(string.IsNullOrEmpty(inspection.LastBlockedReason));
        }

        [UnityTest]
        [Timeout(300000)]
        public IEnumerator ContinuousAutonomousTourVisitsAll18ZonesAndMeasuresPerformance()
        {
            yield return LoadMainScene();

            ResidentialFirstPersonController player = UnityEngine.Object.FindAnyObjectByType<ResidentialFirstPersonController>();
            ResidentialHudController hud = UnityEngine.Object.FindAnyObjectByType<ResidentialHudController>();
            Assert.IsNotNull(player);
            Assert.IsNotNull(hud);

            string renderDir = Path.GetFullPath(Path.Combine(Application.dataPath, "../../renders/hito_08_3_3"));
            Directory.CreateDirectory(renderDir);

            int shotIndex = 1;
            ResidentialNavigationAgent agent = new ResidentialNavigationAgent(player);
            yield return agent.ExecuteContinuousTour(zoneName =>
            {
                string safeName = zoneName.Replace(" / ", "_").Replace(" ", "_");
                string fileName = shotIndex.ToString("D2") + "_ZONA_" + safeName + ".png";
                CaptureCameraFrame(player.PlayerCamera, Path.Combine(renderDir, fileName));
                shotIndex++;
            });

            NavigationTraceReport traceReport = agent.BuildReport();
            string tracePath = Path.GetFullPath(Path.Combine(Application.dataPath, "../../validation/HITO_08_3_3_NAVIGATION_TRACE.json"));
            Directory.CreateDirectory(Path.GetDirectoryName(tracePath));
            File.WriteAllText(tracePath, JsonUtility.ToJson(traceReport, true));

            hud.GetPerformanceSummary(out float avgFps, out float avgFrameMs, out float p95Ms, out float p99Ms, out float onePercentLow);
            Hito083PerformanceReport perf = new Hito083PerformanceReport
            {
                screen_width = Screen.width,
                screen_height = Screen.height,
                average_fps = Mathf.Round(avgFps * 10f) / 10f,
                average_frame_time_ms = Mathf.Round(avgFrameMs * 100f) / 100f,
                p95_frame_time_ms = Mathf.Round(p95Ms * 100f) / 100f,
                p99_frame_time_ms = Mathf.Round(p99Ms * 100f) / 100f,
                one_percent_low_fps = Mathf.Round(onePercentLow * 10f) / 10f
            };
            string perfPath = Path.GetFullPath(Path.Combine(Application.dataPath, "../../validation/HITO_08_3_3_PERFORMANCE.json"));
            File.WriteAllText(perfPath, JsonUtility.ToJson(perf, true));

            Assert.AreEqual(0, traceReport.teleport_count, "Teleports prohibited during autonomous tour.");
            Assert.IsTrue(traceReport.exterior_entry_passed, "Exterior pedestrian entry failed.");
            Assert.IsTrue(traceReport.exterior_return_passed, "Return to exterior failed.");
            Assert.AreEqual(18, traceReport.zones_visited_count,
                "Unreachable zones: " + string.Join(", ", traceReport.unreachable_zones));
            Assert.IsTrue(traceReport.all_zones_visited, "Not all 18 zones were visited.");
        }

        [UnityTest]
        public IEnumerator RooftopHatchAndFallProtectionWorkCorrectly()
        {
            yield return LoadMainScene();

            RetractableAtticStair attic = UnityEngine.Object.FindAnyObjectByType<RetractableAtticStair>();
            ResidentialFirstPersonController player = UnityEngine.Object.FindAnyObjectByType<ResidentialFirstPersonController>();
            Assert.IsNotNull(attic, "RetractableAtticStair missing.");
            Assert.IsNotNull(player);

            string renderDir = Path.GetFullPath(Path.Combine(Application.dataPath, "../../renders/hito_08_3_3"));
            Directory.CreateDirectory(renderDir);

            Assert.AreEqual(AtticStairState.Closed, attic.CurrentState, "Stair must start Closed.");
            GameObject tramo1 = GameObject.Find("Esc_Techo_Tramo_1");
            Assert.IsNotNull(tramo1, "Esc_Techo_Tramo_1 missing.");
            Assert.IsFalse(tramo1.GetComponent<Renderer>().enabled, "Retractable stair segments must be hidden when Closed.");

            player.TeleportTo(new Vector3(-4.10f, 2.96f, -6.20f), 270f);
            yield return null;
            CaptureCameraFrame(player.PlayerCamera, Path.Combine(renderDir, "ESCALERA_RETRACTIL_1_CLOSED.png"));

            attic.SetStateImmediate(AtticStairState.Opening);
            yield return null;
            Assert.AreEqual(AtticStairState.Opening, attic.CurrentState);
            Assert.IsTrue(tramo1.GetComponent<Renderer>().enabled, "Stair segments must become visible while Opening.");
            CaptureCameraFrame(player.PlayerCamera, Path.Combine(renderDir, "ESCALERA_RETRACTIL_2_OPENING.png"));

            attic.SetStateImmediate(AtticStairState.Open);
            yield return null;
            Assert.AreEqual(AtticStairState.Open, attic.CurrentState);
            CaptureCameraFrame(player.PlayerCamera, Path.Combine(renderDir, "ESCALERA_RETRACTIL_3_OPEN.png"));

            player.TeleportTo(new Vector3(-5.70f, 4.30f, -6.20f), 270f);
            yield return null;
            bool closedWhileOnStair = attic.Close();
            Assert.IsFalse(closedWhileOnStair, "Closing must be blocked while player is on the stair.");
            Assert.AreEqual(AtticStairState.Open, attic.CurrentState);
            Assert.IsFalse(string.IsNullOrEmpty(attic.LastBlockedReason));

            player.TeleportTo(new Vector3(-4.10f, 2.96f, -6.20f), 270f);
            yield return null;
            attic.SetStateImmediate(AtticStairState.Closing);
            yield return null;
            Assert.AreEqual(AtticStairState.Closing, attic.CurrentState);
            CaptureCameraFrame(player.PlayerCamera, Path.Combine(renderDir, "ESCALERA_RETRACTIL_4_CLOSING.png"));

            attic.SetStateImmediate(AtticStairState.Open);
            attic.Close();
            float waitS = Time.unscaledTime;
            while (attic.CurrentState != AtticStairState.Closed && Time.unscaledTime - waitS < 3.0f)
            {
                yield return null;
            }
            Assert.AreEqual(AtticStairState.Closed, attic.CurrentState, "Stair failed to return to Closed.");
            Assert.IsFalse(tramo1.GetComponent<Renderer>().enabled, "Stair segments must hide again when Closed.");

            player.TeleportTo(new Vector3(-4.95f, 2.96f, -6.20f), 270f);
            yield return null;
            yield return PressSyntheticKey(Key.E);
            Assert.IsTrue(attic.CurrentState == AtticStairState.Opening || attic.CurrentState == AtticStairState.Open,
                "Pressing E near the pull cord did not trigger Opening.");

            string[] guardrailNames =
            {
                "Baranda_Cubierta_Oeste",
                "Baranda_Cubierta_Este",
                "Baranda_Cubierta_Sur",
                "Baranda_Cubierta_Norte",
                "Baranda_Escotilla_Oeste"
            };
            for (int i = 0; i < guardrailNames.Length; i++)
            {
                GameObject rail = GameObject.Find(guardrailNames[i]);
                Assert.IsNotNull(rail, "Missing rooftop guardrail: " + guardrailNames[i]);
                Collider col = rail.GetComponent<Collider>();
                Assert.IsNotNull(col, "Missing collider on guardrail: " + guardrailNames[i]);
                Assert.IsTrue(col.enabled, "Collider disabled on guardrail: " + guardrailNames[i]);
            }
        }

        private static void CaptureCameraFrame(Camera cam, string path)
        {
            if (cam == null) return;
            int w = 1280;
            int h = 720;
            RenderTexture rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32);
            RenderTexture prev = cam.targetTexture;
            RenderTexture prevActive = RenderTexture.active;
            cam.targetTexture = rt;
            cam.Render();
            RenderTexture.active = rt;
            Texture2D tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
            tex.Apply();
            File.WriteAllBytes(path, tex.EncodeToPNG());
            cam.targetTexture = prev;
            RenderTexture.active = prevActive;
            UnityEngine.Object.Destroy(rt);
            UnityEngine.Object.Destroy(tex);
        }
    }
}
