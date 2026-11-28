using HomeProject.Validation;
using UnityEditor;
using UnityEngine;

namespace HomeProject.Editor
{
    public static class HomeProjectMenu
    {
        [MenuItem("Tools/Home Project/1. Import Architecture from Blender", false, 10)]
        public static void ImportFromBlender()
        {
            FbxImportConfigurator.ConfigureTexturesAndFbx();
            Debug.Log("Home Project: FBX & Texture importers configured.");
        }

        [MenuItem("Tools/Home Project/2. Rebuild Scene", false, 20)]
        public static void RebuildScene()
        {
            SceneBuilderService.BuildOrUpdateMainScene();
            Debug.Log("Home Project: Main scene rebuilt.");
        }

        [MenuItem("Tools/Home Project/3. Rebuild URP Materials", false, 30)]
        public static void RebuildMaterials()
        {
            UrpMaterialBuilderService.BuildAllMaterials();
            Debug.Log("Home Project: URP materials rebuilt.");
        }

        [MenuItem("Tools/Home Project/4. Configure Colliders", false, 40)]
        public static void ConfigureColliders()
        {
            ColliderAuditService.ConfigureColliders();
            Debug.Log("Home Project: Colliders configured.");
        }

        [MenuItem("Tools/Home Project/5. Configure URP Graphics & Cameras", false, 50)]
        public static void ConfigureGraphicsAndCameras()
        {
            UrpGraphicsAndLightingService.ConfigureGraphicsLightingAndCameras();
            Debug.Log("Home Project: URP Graphics, Lighting and Cameras configured.");
        }

        [MenuItem("Tools/Home Project/6. Run Validations", false, 60)]
        public static void RunValidations()
        {
            Hito081ValidationReport report = SceneValidatorService.ValidateCurrentScene(true);
            Hito081NegativeTestsReport neg = NegativeTestsRunner.RunAllNegativeTests();
            Debug.Log("Home Project Validation: overall_passed=" + report.overall_passed +
                      ", dims=" + report.dimensional_checks_passed + "/" + report.dimensional_checks_total +
                      ", negative_tests=" + neg.passed_cases + "/" + neg.total_cases);
        }

        [MenuItem("Tools/Home Project/7. Generate Technical Report & Renders", false, 70)]
        public static void GenerateReportAndRenders()
        {
            EvidenceCaptureService.CaptureAllRenders();
            EvidenceCaptureService.CaptureHito082Renders();
            Debug.Log("Home Project: Game camera renders captured.");
        }

        [MenuItem("Tools/Home Project/Run Full Pipeline", false, 100)]
        public static void RunFullPipeline()
        {
            ImportFromBlender();
            RebuildScene();
            RebuildMaterials();
            ConfigureColliders();
            ConfigureGraphicsAndCameras();
            UnityEditor.SceneManagement.EditorSceneManager.MarkAllScenesDirty();
            UnityEditor.SceneManagement.EditorSceneManager.SaveOpenScenes();
            RunValidations();
        }
    }
}
