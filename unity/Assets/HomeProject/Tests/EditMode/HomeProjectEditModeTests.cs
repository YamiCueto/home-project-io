using System.Collections.Generic;
using HomeProject.Core;
using HomeProject.Editor;
using HomeProject.Validation;
using NUnit.Framework;
using UnityEditor;
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
        public void SceneValidationPassesDimensionalAndMaterialChecks()
        {
            Hito081ValidationReport report = SceneValidatorService.ValidateCurrentScene(false);
            Assert.AreEqual(0, report.errors.Count, "Validation errors: " + string.Join("; ", report.errors));
            Assert.AreEqual(0, report.statistics.missing_mesh_references, "Missing mesh references found.");
            Assert.AreEqual(0, report.statistics.missing_material_references, "Missing material references found.");
            Assert.AreEqual(0, report.statistics.non_urp_materials, "Non-URP materials found.");
            Assert.AreEqual(0, report.statistics.visible_collider_renderers, "Visible collider renderers found.");
            Assert.Greater(report.dimensional_checks_total, 100, "Too few dimensional checks executed.");
            Assert.AreEqual(0, report.dimensional_checks_failed, "Dimensional tolerance failures detected.");
            Assert.AreEqual(report.opening_audits_total, report.opening_audits_passed, "Blocked openings detected.");
        }

        [Test]
        public void NegativeTestsDetectAllControlledFaults()
        {
            Hito081NegativeTestsReport neg = NegativeTestsRunner.RunAllNegativeTests();
            Assert.IsTrue(neg.all_detected, "Not all negative faults were detected: " + neg.passed_cases + "/" + neg.total_cases);
        }
    }
}
