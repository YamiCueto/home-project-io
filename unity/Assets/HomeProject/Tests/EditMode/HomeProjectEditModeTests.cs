using HomeProject.Core;
using HomeProject.Editor;
using HomeProject.Infrastructure;
using HomeProject.Interaction;
using HomeProject.Validation;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace HomeProject.Tests.EditMode
{
    public class HomeProjectEditModeTests
    {
        [OneTimeSetUp]
        public void OpenMainScene()
        {
            EditorSceneManager.OpenScene(HomeProjectConstants.ScenePath, OpenSceneMode.Single);
        }

        [Test]
        public void SixFbxPackagesAreImportedAndInstantiated()
        {
            string[] expected =
            {
                "HOME_PROJECT/Architecture/architecture_pkg",
                "HOME_PROJECT/Furniture/furniture_pkg",
                "HOME_PROJECT/InteractiveDoors/interactive_doors_pkg",
                "HOME_PROJECT/Installations/installations_pkg",
                "HOME_PROJECT/UrbanContext/urban_context_pkg",
                "HOME_PROJECT/CollisionGeometry/colliders_pkg"
            };

            for (int i = 0; i < expected.Length; i++)
            {
                GameObject go = GameObject.Find(expected[i]);
                Assert.IsNotNull(go, "Missing FBX instance: " + expected[i]);
                Assert.AreEqual(Vector3.one, go.transform.localScale, "Unexpected scale on " + expected[i]);
            }
        }

        [Test]
        public void UrpIsActiveRenderPipeline()
        {
            Assert.IsNotNull(GraphicsSettings.currentRenderPipeline, "Active render pipeline is null.");
            Assert.IsInstanceOf<UniversalRenderPipelineAsset>(GraphicsSettings.currentRenderPipeline);
        }

        [Test]
        public void PlayerControllerAndInteractiveDoorsConfigured()
        {
            ResidentialFirstPersonController fps = Object.FindAnyObjectByType<ResidentialFirstPersonController>();
            Assert.IsNotNull(fps, "ResidentialFirstPersonController missing.");
            CharacterController cc = fps.GetComponent<CharacterController>();
            Assert.IsNotNull(cc, "CharacterController missing.");
            Assert.AreEqual(1.80f, cc.height, 0.01f);
            Assert.AreEqual(0.30f, cc.radius, 0.01f);
            Assert.AreEqual(0.25f, cc.stepOffset, 0.01f);

            OrbitalInspectionCamera orbital = Object.FindAnyObjectByType<OrbitalInspectionCamera>(FindObjectsInactive.Include);
            Assert.IsNotNull(orbital, "OrbitalInspectionCamera missing.");

            ResidentialHudController hud = Object.FindAnyObjectByType<ResidentialHudController>();
            Assert.IsNotNull(hud, "ResidentialHudController missing.");

            ArchitecturalInspectionMode inspection = Object.FindAnyObjectByType<ArchitecturalInspectionMode>();
            Assert.IsNotNull(inspection, "ArchitecturalInspectionMode missing.");

            InteractiveDoor[] doors = Object.FindObjectsByType<InteractiveDoor>();
            Assert.AreEqual(19, doors.Length, "Expected 19 InteractiveDoor components.");

            string[] treeNames = { "Arbol_Tropical_01", "Arbol_Tropical_02", "Arbol_Tropical_03" };
            for (int i = 0; i < treeNames.Length; i++)
            {
                GameObject tree = GameObject.Find(treeNames[i]);
                Assert.IsNotNull(tree, "Missing tropical tree: " + treeNames[i]);
                Assert.IsNotNull(tree.GetComponent<LODGroup>(), "Missing LODGroup on " + treeNames[i]);
                Assert.IsNotNull(tree.GetComponent<CapsuleCollider>(), "Missing CapsuleCollider on " + treeNames[i]);
                Assert.IsNotNull(tree.GetComponent<HomeProject.Architecture.TropicalFoliageWind>(), "Missing TropicalFoliageWind on " + treeNames[i]);
            }
        }

        [Test]
        public void SceneValidationPassesAuditAndDimensionalChecks()
        {
            Hito081ValidationReport report = SceneValidatorService.ValidateCurrentScene(false);
            Assert.AreEqual(0, report.errors.Count, "Validation errors: " + string.Join("; ", report.errors));
            Assert.AreEqual(0, report.statistics.missing_expected_objects, "Missing expected objects.");
            Assert.AreEqual(0, report.statistics.duplicate_object_names, "Duplicate object names.");
            Assert.AreEqual(0, report.statistics.missing_mesh_references, "Missing mesh references found.");
            Assert.AreEqual(0, report.statistics.missing_material_references, "Missing material references found.");
            Assert.AreEqual(0, report.statistics.non_urp_materials, "Non-URP materials found.");
            Assert.AreEqual(0, report.statistics.visible_collider_renderers, "Visible collider renderers found.");
            Assert.GreaterOrEqual(report.dimensional_checks_total, 300, "Too few dimensional checks executed.");
            Assert.AreEqual(0, report.dimensional_checks_failed, "Dimensional/transform tolerance failures detected.");
            Assert.AreEqual(report.pivot_checks_total, report.pivot_checks_passed, "Door pivot tolerance failures.");
            Assert.AreEqual(report.capsule_audits_total, report.capsule_audits_passed, "Capsule opening sweeps blocked.");
            Assert.AreEqual(report.floor_raycasts_total, report.floor_raycasts_passed, "Floor raycast surface failures.");
        }

        [Test]
        public void NegativeTestsDetectAllControlledFaults()
        {
            Hito081NegativeTestsReport neg = NegativeTestsRunner.RunAllNegativeTests();
            Assert.IsTrue(neg.all_detected, "Not all negative faults were detected: " + neg.passed_cases + "/" + neg.total_cases);
        }
    }
}
