using System;
using System.Collections;
using System.IO;
using HomeProject.Core;
using HomeProject.Infrastructure;
using HomeProject.Interaction;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace HomeProject.Tests.PlayMode
{
    [Serializable]
    public class PlayModeMetricsReport
    {
        public int screen_width;
        public int screen_height;
        public float average_fps;
        public float min_fps;
        public float frame_time_ms;
        public float stair_top_y;
        public float stair_bottom_y;
        public bool closed_door_blocked;
        public bool open_door_entered_sala;
        public bool wall_blocked;
        public bool spawn_reset_passed;
    }

    public class HomeProjectPlayModeTests
    {
        [UnityTest]
        public IEnumerator FullFirstPersonNavigationAndPhysicsVerification()
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

            HomeProjectSystemInitializer sys = UnityEngine.Object.FindAnyObjectByType<HomeProjectSystemInitializer>();
            Assert.IsNotNull(sys);
            Assert.IsTrue(sys.IsInitialized);

            ResidentialFirstPersonController player = UnityEngine.Object.FindAnyObjectByType<ResidentialFirstPersonController>();
            Assert.IsNotNull(player, "ResidentialFirstPersonController missing in PlayMode.");

            ResidentialHudController hud = UnityEngine.Object.FindAnyObjectByType<ResidentialHudController>();
            Assert.IsNotNull(hud, "ResidentialHudController missing in PlayMode.");

            for (int i = 0; i < 15; i++)
            {
                yield return null;
            }
            Assert.IsTrue(player.IsGrounded, "Player did not settle onto ground with gravity.");

            GameObject frontDoorGo = GameObject.Find("P1_M_Sur_Sala_Puerta1");
            Assert.IsNotNull(frontDoorGo);
            InteractiveDoor frontDoor = frontDoorGo.GetComponent<InteractiveDoor>();
            Assert.IsNotNull(frontDoor);
            frontDoor.SetOpen(false, true);

            player.TeleportTo(new Vector3(-1.12f, 0.08f, -0.50f), 180f);
            player.SetInputOverride(true, new Vector2(0f, 1f), Vector2.zero);
            yield return WalkForSeconds(1.2f);
            bool closedDoorBlocked = player.transform.position.z > -1.70f;
            Assert.IsTrue(closedDoorBlocked, "Closed front door failed to block player! z=" + player.transform.position.z);

            frontDoor.SetOpen(true, true);
            yield return WalkForSeconds(1.2f);
            bool enteredSala = player.transform.position.z < -2.0f && player.CurrentZoneName == "Sala";
            Assert.IsTrue(enteredSala, "Player could not enter Sala after opening door. z=" + player.transform.position.z + ", zone=" + player.CurrentZoneName);

            player.TeleportTo(new Vector3(-1.2f, 0.08f, -3.0f), 90f);
            yield return WalkForSeconds(1.0f);
            bool wallBlocked = player.transform.position.x < -0.10f;
            Assert.IsTrue(wallBlocked, "Player penetrated West wall! x=" + player.transform.position.x);

            player.TeleportTo(new Vector3(-2.75f, 0.08f, -5.22f), -90f);
            yield return WalkForSeconds(3.2f);
            float stairTopY = player.transform.position.y;
            Assert.Greater(stairTopY, 2.50f, "Player failed to climb stairs to P2! y=" + stairTopY);

            player.TeleportTo(new Vector3(-7.10f, 2.95f, -5.22f), 90f);
            yield return WalkForSeconds(3.2f);
            float stairBottomY = player.transform.position.y;
            Assert.Less(stairBottomY, 1.50f, "Player failed to descend stairs cleanly! y=" + stairBottomY);

            player.SetInputOverride(false, Vector2.zero, Vector2.zero);
            player.ResetToSpawn();
            yield return null;
            bool spawnReset = Vector3.Distance(player.transform.position, new Vector3(-1.12f, 0.08f, 1.80f)) < 0.05f;
            Assert.IsTrue(spawnReset, "ResetToSpawn did not return player to spawn.");

            player.SetOrbitalMode(true);
            yield return null;
            Assert.IsTrue(player.IsOrbitalMode);
            player.SetOrbitalMode(false);
            yield return null;
            Assert.IsFalse(player.IsOrbitalMode);

            PlayModeMetricsReport metrics = new PlayModeMetricsReport
            {
                screen_width = Screen.width,
                screen_height = Screen.height,
                average_fps = Mathf.Round(hud.AverageFps * 10f) / 10f,
                min_fps = Mathf.Round(hud.MinFps * 10f) / 10f,
                frame_time_ms = Mathf.Round(hud.CurrentFrameTimeMs * 100f) / 100f,
                stair_top_y = Mathf.Round(stairTopY * 1000f) / 1000f,
                stair_bottom_y = Mathf.Round(stairBottomY * 1000f) / 1000f,
                closed_door_blocked = closedDoorBlocked,
                open_door_entered_sala = enteredSala,
                wall_blocked = wallBlocked,
                spawn_reset_passed = spawnReset
            };

            string outPath = Path.GetFullPath(Path.Combine(Application.dataPath, "../../validation/HITO_08_2_PLAYMODE_METRICS.json"));
            Directory.CreateDirectory(Path.GetDirectoryName(outPath));
            File.WriteAllText(outPath, JsonUtility.ToJson(metrics, true));
        }

        private static IEnumerator WalkForSeconds(float seconds)
        {
            float elapsed = 0f;
            while (elapsed < seconds)
            {
                elapsed += Time.deltaTime;
                yield return null;
            }
        }
    }
}
