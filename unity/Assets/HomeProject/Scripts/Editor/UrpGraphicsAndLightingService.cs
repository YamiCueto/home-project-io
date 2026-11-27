using System;
using System.Collections.Generic;
using HomeProject.Core;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace HomeProject.Editor
{
    public static class UrpGraphicsAndLightingService
    {
        public static void ConfigureGraphicsLightingAndCameras()
        {
            ConfigureUrpAssets();
            GameObject lightingRoot = GameObject.Find(HomeProjectConstants.LightingRootName);
            GameObject camerasRoot = GameObject.Find(HomeProjectConstants.CamerasRootName);
            GameObject archGroup = GameObject.Find(HomeProjectConstants.HomeProjectRootName + "/" + HomeProjectConstants.GroupArchitecture);

            Bounds houseBounds = ComputeBounds(archGroup);
            if (lightingRoot != null)
            {
                ConfigureLighting(lightingRoot.transform, houseBounds);
            }

            if (camerasRoot != null)
            {
                ConfigureCameras(camerasRoot.transform, houseBounds);
            }
        }

        private static void ConfigureUrpAssets()
        {
            UniversalRenderPipelineAsset urpAsset = GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
            if (urpAsset == null)
            {
                urpAsset = QualitySettings.renderPipeline as UniversalRenderPipelineAsset;
            }

            if (urpAsset == null)
            {
                return;
            }

            urpAsset.supportsHDR = true;
            urpAsset.shadowDistance = 65.0f;
            urpAsset.shadowCascadeCount = 4;
            urpAsset.msaaSampleCount = 4;

            SerializedObject urpSo = new SerializedObject(urpAsset);
            SerializedProperty mainShadowRes = urpSo.FindProperty("m_MainLightShadowmapResolution");
            if (mainShadowRes != null)
            {
                mainShadowRes.intValue = 4096;
            }
            urpSo.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(urpAsset);

            SerializedProperty rendererDataList = urpSo.FindProperty("m_RendererDataList");
            if (rendererDataList != null && rendererDataList.arraySize > 0)
            {
                UniversalRendererData rendererData = rendererDataList.GetArrayElementAtIndex(0).objectReferenceValue as UniversalRendererData;
                if (rendererData != null)
                {
                    rendererData.renderingMode = RenderingMode.ForwardPlus;
                    EnsureSsaoFeature(rendererData);
                    EditorUtility.SetDirty(rendererData);
                }
            }

            AssetDatabase.SaveAssets();
        }

        private static void EnsureSsaoFeature(UniversalRendererData rendererData)
        {
            for (int i = 0; i < rendererData.rendererFeatures.Count; i++)
            {
                if (rendererData.rendererFeatures[i] != null &&
                    rendererData.rendererFeatures[i].GetType().Name.Contains("ScreenSpaceAmbientOcclusion"))
                {
                    rendererData.rendererFeatures[i].SetActive(true);
                    return;
                }
            }

            Type ssaoType = typeof(UniversalRendererData).Assembly.GetType("UnityEngine.Rendering.Universal.ScreenSpaceAmbientOcclusion");
            if (ssaoType == null)
            {
                return;
            }

            ScriptableRendererFeature feature = ScriptableObject.CreateInstance(ssaoType) as ScriptableRendererFeature;
            if (feature == null)
            {
                return;
            }

            feature.name = "ScreenSpaceAmbientOcclusion";
            AssetDatabase.AddObjectToAsset(feature, rendererData);
            rendererData.rendererFeatures.Add(feature);
            rendererData.SetDirty();
        }

        private static void ConfigureLighting(Transform lightingRoot, Bounds houseBounds)
        {
            Transform sunTf = GetOrCreateChild(lightingRoot, "Sun_DirectionalLight");
            Light sun = sunTf.GetComponent<Light>();
            if (sun == null) sun = sunTf.gameObject.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1.0f, 0.96f, 0.89f);
            sun.intensity = 2.4f;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 0.85f;
            sunTf.position = houseBounds.center + new Vector3(0f, 12f, 0f);
            sunTf.rotation = Quaternion.Euler(52f, -38f, 0f);

            Transform probeTf = GetOrCreateChild(lightingRoot, "Main_ReflectionProbe");
            ReflectionProbe probe = probeTf.GetComponent<ReflectionProbe>();
            if (probe == null) probe = probeTf.gameObject.AddComponent<ReflectionProbe>();
            probe.mode = ReflectionProbeMode.Realtime;
            probe.refreshMode = ReflectionProbeRefreshMode.OnAwake;
            probe.size = new Vector3(14f, 8f, 16f);
            probe.center = Vector3.zero;
            probeTf.position = houseBounds.center;

            Transform lpTf = GetOrCreateChild(lightingRoot, "Interior_LightProbes");
            LightProbeGroup lpg = lpTf.GetComponent<LightProbeGroup>();
            if (lpg == null) lpg = lpTf.gameObject.AddComponent<LightProbeGroup>();
            List<Vector3> positions = new List<Vector3>();
            Vector3 min = houseBounds.min;
            Vector3 max = houseBounds.max;
            for (int x = 0; x < 3; x++)
            {
                for (int y = 0; y < 2; y++)
                {
                    for (int z = 0; z < 4; z++)
                    {
                        float px = Mathf.Lerp(min.x + 1f, max.x - 1f, x / 2f);
                        float py = y == 0 ? 1.5f : 4.2f;
                        float pz = Mathf.Lerp(min.z + 1f, max.z - 1f, z / 3f);
                        positions.Add(new Vector3(px, py, pz));
                    }
                }
            }
            lpg.probePositions = positions.ToArray();

            Transform volTf = GetOrCreateChild(lightingRoot, "Global_Volume");
            Volume vol = volTf.GetComponent<Volume>();
            if (vol == null) vol = volTf.gameObject.AddComponent<Volume>();
            vol.isGlobal = true;
            vol.priority = 1.0f;
            vol.sharedProfile = GetOrCreateVolumeProfile();
        }

        private static VolumeProfile GetOrCreateVolumeProfile()
        {
            string profilePath = HomeProjectConstants.SettingsPath + "/HomeProject_VolumeProfile.asset";
            VolumeProfile profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(profilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                AssetDatabase.CreateAsset(profile, profilePath);
            }

            if (!profile.TryGet<Tonemapping>(out Tonemapping tonemapping))
            {
                tonemapping = profile.Add<Tonemapping>(true);
            }
            tonemapping.mode.overrideState = true;
            tonemapping.mode.value = TonemappingMode.ACES;

            if (!profile.TryGet<Bloom>(out Bloom bloom))
            {
                bloom = profile.Add<Bloom>(true);
            }
            bloom.threshold.overrideState = true;
            bloom.threshold.value = 1.05f;
            bloom.intensity.overrideState = true;
            bloom.intensity.value = 0.28f;

            EditorUtility.SetDirty(profile);
            AssetDatabase.SaveAssets();
            return profile;
        }

        private static void ConfigureCameras(Transform camerasRoot, Bounds b)
        {
            Vector3 c = b.center;
            CreateOrUpdateCamera(camerasRoot, "Main Camera", new Vector3(-13.5f, 4.8f, 8.5f), new Vector3(-4.0f, 2.5f, -4.5f), 50f, true);
            CreateOrUpdateCamera(camerasRoot, "01_Fachada_Frontal", new Vector3(-4.0f, 2.2f, 9.0f), new Vector3(-4.0f, 2.5f, -1.0f), 50f, false);
            CreateOrUpdateCamera(camerasRoot, "02_Perspectiva_Esquinera", new Vector3(-13.5f, 4.8f, 8.5f), new Vector3(-4.0f, 2.5f, -4.5f), 48f, false);
            CreateOrUpdateCamera(camerasRoot, "03_Vista_Aerea", new Vector3(-15.0f, 16.0f, 10.0f), c, 45f, false);
            CreateOrUpdateCamera(camerasRoot, "04_Sala", new Vector3(-1.0f, 1.65f, -4.2f), new Vector3(-3.8f, 1.3f, -2.0f), 60f, false);
            CreateOrUpdateCamera(camerasRoot, "05_Cocina_Comedor", new Vector3(-3.8f, 1.65f, -7.8f), new Vector3(-6.8f, 1.3f, -6.5f), 60f, false);
            CreateOrUpdateCamera(camerasRoot, "06_Hab_Huespedes", new Vector3(-1.2f, 1.65f, -8.8f), new Vector3(-3.8f, 1.2f, -10.2f), 60f, false);
            CreateOrUpdateCamera(camerasRoot, "07_Garaje", new Vector3(-6.2f, 1.65f, -0.5f), new Vector3(-6.2f, 1.2f, -4.0f), 60f, false);
            CreateOrUpdateCamera(camerasRoot, "08_Escalera", new Vector3(-3.3f, 1.65f, -5.2f), new Vector3(-6.5f, 2.6f, -5.2f), 60f, false);
            CreateOrUpdateCamera(camerasRoot, "09_Hab_Principal", new Vector3(-1.0f, 4.59f, -1.2f), new Vector3(-4.0f, 4.0f, -3.5f), 60f, false);
            CreateOrUpdateCamera(camerasRoot, "10_Hab_Hija_1", new Vector3(-1.0f, 4.59f, -7.4f), new Vector3(-3.2f, 4.0f, -9.8f), 60f, false);
            CreateOrUpdateCamera(camerasRoot, "11_Hab_Hija_2", new Vector3(-5.0f, 4.59f, -7.4f), new Vector3(-7.0f, 4.0f, -9.8f), 60f, false);
            CreateOrUpdateCamera(camerasRoot, "12_Cubierta_FV", new Vector3(-11.5f, 9.5f, 4.0f), new Vector3(-4.0f, 6.0f, -5.5f), 50f, false);
        }

        private static void CreateOrUpdateCamera(Transform parent, string camName, Vector3 pos, Vector3 lookAt, float fov, bool isMain)
        {
            Transform tf = GetOrCreateChild(parent, camName);
            Camera cam = tf.GetComponent<Camera>();
            if (cam == null) cam = tf.gameObject.AddComponent<Camera>();
            cam.fieldOfView = fov;
            cam.nearClipPlane = 0.05f;
            cam.farClipPlane = 250.0f;
            cam.enabled = isMain;
            tf.tag = isMain ? "MainCamera" : "Untagged";
            tf.position = pos;
            tf.LookAt(lookAt);

            UniversalAdditionalCameraData uac = tf.GetComponent<UniversalAdditionalCameraData>();
            if (uac == null) uac = tf.gameObject.AddComponent<UniversalAdditionalCameraData>();
            uac.renderPostProcessing = true;
            uac.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
        }

        private static Bounds ComputeBounds(GameObject root)
        {
            if (root == null)
            {
                return new Bounds(new Vector3(-4f, 3f, -5.5f), new Vector3(8.5f, 6.4f, 11.7f));
            }

            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length == 0)
            {
                return new Bounds(new Vector3(-4f, 3f, -5.5f), new Vector3(8.5f, 6.4f, 11.7f));
            }

            Bounds bounds = renderers[0].bounds;
            for (int i = 1; i < renderers.Length; i++)
            {
                bounds.Encapsulate(renderers[i].bounds);
            }
            return bounds;
        }

        private static Transform GetOrCreateChild(Transform parent, string name)
        {
            Transform existing = parent.Find(name);
            if (existing != null)
            {
                return existing;
            }

            GameObject go = new GameObject(name);
            go.transform.SetParent(parent, false);
            return go.transform;
        }
    }
}
