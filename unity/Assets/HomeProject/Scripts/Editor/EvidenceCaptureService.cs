using System.IO;
using HomeProject.Core;
using UnityEditor;
using UnityEngine;

namespace HomeProject.Editor
{
    public static class EvidenceCaptureService
    {
        public static void CaptureAllRenders()
        {
            string outDir = Path.GetFullPath(Path.Combine(Application.dataPath, "../../renders/hito_08_1"));
            Directory.CreateDirectory(outDir);

            RenderNamedCamera("02_Perspectiva_Esquinera", Path.Combine(outDir, "01_EXTERIOR_ESQUINA.png"));
            RenderNamedCamera("03_Vista_Aerea", Path.Combine(outDir, "02_VISTA_AEREA.png"));
            RenderNamedCamera("04_Sala", Path.Combine(outDir, "03_SALA.png"));
            RenderNamedCamera("05_Cocina_Comedor", Path.Combine(outDir, "04_COCINA.png"));
            RenderNamedCamera("09_Hab_Principal", Path.Combine(outDir, "05_HAB_PRINCIPAL.png"));
            RenderNamedCamera("08_Escalera", Path.Combine(outDir, "06_ESCALERA.png"));
            RenderNamedCamera("07_Garaje", Path.Combine(outDir, "07_GARAJE.png"));
            CaptureCollidersPreview(Path.Combine(outDir, "09_COLLIDERS.png"));
        }

        private static void RenderNamedCamera(string cameraName, string outputPath)
        {
            GameObject camGo = GameObject.Find(HomeProjectConstants.CamerasRootName + "/" + cameraName);
            if (camGo == null)
            {
                Debug.LogWarning("Camera not found: " + cameraName);
                return;
            }

            Camera cam = camGo.GetComponent<Camera>();
            if (cam == null)
            {
                return;
            }

            int width = 1920;
            int height = 1080;
            RenderTexture rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            RenderTexture prevTarget = cam.targetTexture;
            RenderTexture prevActive = RenderTexture.active;
            bool prevEnabled = cam.enabled;

            cam.enabled = true;
            cam.targetTexture = rt;
            cam.Render();

            RenderTexture.active = rt;
            Texture2D tex = new Texture2D(width, height, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            tex.Apply();

            File.WriteAllBytes(outputPath, tex.EncodeToPNG());

            cam.targetTexture = prevTarget;
            cam.enabled = prevEnabled;
            RenderTexture.active = prevActive;
            Object.DestroyImmediate(rt);
            Object.DestroyImmediate(tex);
        }

        private static void CaptureCollidersPreview(string outputPath)
        {
            GameObject colRoot = GameObject.Find(HomeProjectConstants.HomeProjectRootName + "/" + HomeProjectConstants.GroupCollisionGeometry);
            if (colRoot == null)
            {
                return;
            }

            MeshRenderer[] renderers = colRoot.GetComponentsInChildren<MeshRenderer>(true);
            Shader urpLit = Shader.Find(HomeProjectConstants.UrpLitShaderName);
            Material previewMat = new Material(urpLit);
            previewMat.SetColor("_BaseColor", new Color(0.1f, 0.85f, 0.95f, 1.0f));
            Material[][] origMats = new Material[renderers.Length][];

            for (int i = 0; i < renderers.Length; i++)
            {
                origMats[i] = renderers[i].sharedMaterials;
                renderers[i].sharedMaterial = previewMat;
                renderers[i].enabled = true;
            }

            RenderNamedCamera("02_Perspectiva_Esquinera", outputPath);

            for (int i = 0; i < renderers.Length; i++)
            {
                renderers[i].sharedMaterials = origMats[i];
                renderers[i].enabled = false;
            }
            Object.DestroyImmediate(previewMat);
        }
    }
}
