using System.Collections;
using HomeProject.Core;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace HomeProject.Tests.PlayMode
{
    public class HomeProjectPlayModeTests
    {
        [UnityTest]
        public IEnumerator MainSceneLoadsInitializesAndPassesPhysicsAudits()
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

            HomeProjectSystemInitializer sys = Object.FindFirstObjectByType<HomeProjectSystemInitializer>();
            Assert.IsNotNull(sys, "HomeProjectSystemInitializer missing in PlayMode.");
            Assert.IsTrue(sys.IsInitialized, "SystemInitializer did not initialize.");

            GameObject salaFloor = GameObject.Find("P1_Piso_P1_Sala");
            Assert.IsNotNull(salaFloor, "P1_Piso_P1_Sala not found.");
            Renderer floorRenderer = salaFloor.GetComponent<Renderer>();
            Assert.IsNotNull(floorRenderer, "P1_Piso_P1_Sala renderer missing.");

            Vector3 rayOrigin = floorRenderer.bounds.center + new Vector3(0f, 1.5f, 0f);
            bool hitFloor = Physics.Raycast(rayOrigin, Vector3.down, out RaycastHit hitInfo, 3.0f);
            Assert.IsTrue(hitFloor, "Downward raycast over Sala failed to hit walkable/collision surface.");

            GameObject door = GameObject.Find("P1_M_Sur_Sala_Puerta1");
            Assert.IsNotNull(door, "Main door P1_M_Sur_Sala_Puerta1 not found.");
            Renderer doorRenderer = door.GetComponent<Renderer>();
            int colLayer = LayerMask.NameToLayer(HomeProjectConstants.CollisionLayerName);
            int mask = colLayer >= 0 ? (1 << colLayer) : Physics.DefaultRaycastLayers;
            Collider[] blocking = Physics.OverlapBox(
                doorRenderer.bounds.center,
                new Vector3(0.12f, 0.35f, 0.12f),
                Quaternion.identity,
                mask,
                QueryTriggerInteraction.Ignore);
            Assert.AreEqual(0, blocking.Length, "Main door opening blocked by CollisionGeometry collider.");
        }
    }
}
