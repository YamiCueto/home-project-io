using System.Collections.Generic;
using System.IO;
using HomeProject.Architecture;
using HomeProject.Core;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace HomeProject.Editor
{
    public static class UrpMaterialBuilderService
    {
        private static readonly Dictionary<string, string> TextureSetMap = new Dictionary<string, string>
        {
            { "asphalt_02_material_Calle_Frontal", "asphalt_02" },
            { "asphalt_02_material_Calle_Lateral", "asphalt_02" },
            { "concrete_pavement_03_material_Anden_Frontal", "concrete_pavement_03" },
            { "concrete_pavement_03_material_Anden_Lateral", "concrete_pavement_03" },
            { "dark_wood_material_P1_Mob_Mesa_Comedor_Sobre", "dark_wood" },
            { "dining_chair_02", "dining_chair_02" },
            { "modern_coffee_table_01", "modern_coffee_table_01" },
            { "potted_plant_01_leaves", "potted_plant_01_leaves" },
            { "potted_plant_01_pot", "potted_plant_01_pot" },
            { "potted_plant_02_leaves", "potted_plant_02_leaves" },
            { "potted_plant_02_pot", "potted_plant_02_pot" },
            { "side_table_01", "side_table_01" },
            { "MAT_antracita", "MAT_antracita" },
            { "MAT_concreto_arq", "MAT_concreto_arq" },
            { "MAT_cuarzo_blanco", "MAT_cuarzo_blanco" },
            { "MAT_estuco_blanco", "MAT_estuco_blanco" },
            { "MAT_follaje_tropical", "MAT_follaje_tropical" },
            { "MAT_madera_ext", "MAT_madera_ext" },
            { "MAT_piedra_natural", "MAT_piedra_natural" },
            { "MAT_porcelanato_ext", "MAT_porcelanato_ext" },
            { "tree_small_02_trunk", "tree_small_02" },
            { "tree_small_02_branches", "tree_small_02_branch" },
            { "tree_small_02_leaves", "tree_small_02_leaves" },
            { "island_tree_02", "island_tree_02" },
            { "island_tree_02_branches", "island_tree_02_branches" },
            { "island_tree_02_leaves", "island_tree_02_leaves" }
        };

        public static Dictionary<string, Material> BuildAllMaterials()
        {
            if (!Directory.Exists(HomeProjectConstants.MaterialsPath))
            {
                Directory.CreateDirectory(HomeProjectConstants.MaterialsPath);
            }

            Shader urpLit = Shader.Find(HomeProjectConstants.UrpLitShaderName);
            Dictionary<string, Material> result = new Dictionary<string, Material>();
            if (urpLit == null)
            {
                Debug.LogError("URP Lit shader not found.");
                return result;
            }

            TextAsset detailJson = AssetDatabase.LoadAssetAtPath<TextAsset>(HomeProjectConstants.BlenderMaterialsDetailPath);
            if (detailJson == null)
            {
                Debug.LogError("Missing blender_materials_detail.json");
                return result;
            }

            BlenderMaterialListWrapper wrapper = JsonUtility.FromJson<BlenderMaterialListWrapper>("{\"items\":" + detailJson.text + "}");
            if (wrapper == null || wrapper.items == null)
            {
                return result;
            }

            for (int i = 0; i < wrapper.items.Count; i++)
            {
                BlenderMaterialDetail detail = wrapper.items[i];
                string matAssetPath = Path.Combine(HomeProjectConstants.MaterialsPath, detail.name + ".mat").Replace("\\", "/");
                Material mat = AssetDatabase.LoadAssetAtPath<Material>(matAssetPath);
                if (mat == null)
                {
                    mat = new Material(urpLit);
                    AssetDatabase.CreateAsset(mat, matAssetPath);
                }
                else if (mat.shader != urpLit)
                {
                    mat.shader = urpLit;
                }

                ConfigureMaterial(mat, detail);
                EditorUtility.SetDirty(mat);
                result[detail.name] = mat;
            }

            AssetDatabase.SaveAssets();
            RemapFbxMaterials(result);
            ApplyMaterialsToScene(result);
            AssetDatabase.SaveAssets();
            return result;
        }

        private static void ConfigureMaterial(Material mat, BlenderMaterialDetail detail)
        {
            Color baseColor = ToColor(detail.base_color, Color.white);
            bool hasTextureSet = TextureSetMap.TryGetValue(detail.name, out string prefix);

            Texture2D baseMap = null;
            Texture2D normalMap = null;
            Texture2D msMap = null;

            if (hasTextureSet)
            {
                baseMap = FindBaseMap(prefix);
                normalMap = FindNormalMap(prefix);
                msMap = LoadTexture(prefix + "_MetallicSmoothness.png");
            }

            if (baseMap != null)
            {
                mat.SetTexture("_BaseMap", baseMap);
                mat.SetColor("_BaseColor", Color.white);
            }
            else
            {
                mat.SetTexture("_BaseMap", null);
                mat.SetColor("_BaseColor", baseColor);
            }

            if (msMap != null)
            {
                mat.SetTexture("_MetallicGlossMap", msMap);
                mat.SetFloat("_Metallic", 1.0f);
                mat.SetFloat("_Smoothness", 1.0f);
                mat.EnableKeyword("_METALLICSPECGLOSSMAP");
            }
            else
            {
                mat.SetTexture("_MetallicGlossMap", null);
                mat.DisableKeyword("_METALLICSPECGLOSSMAP");
                mat.SetFloat("_Metallic", Mathf.Clamp01(detail.metallic));
                mat.SetFloat("_Smoothness", Mathf.Clamp01(1.0f - detail.roughness));
            }

            if (normalMap != null)
            {
                mat.SetTexture("_BumpMap", normalMap);
                mat.SetFloat("_BumpScale", 1.0f);
                mat.EnableKeyword("_NORMALMAP");
            }
            else
            {
                mat.SetTexture("_BumpMap", null);
                mat.DisableKeyword("_NORMALMAP");
            }

            if (detail.emission_strength > 0.01f)
            {
                Color emColor = ToColor(detail.emission_color, Color.white);
                float intensity = Mathf.Clamp(detail.emission_strength, 0.5f, 4.0f);
                mat.EnableKeyword("_EMISSION");
                mat.SetColor("_EmissionColor", emColor * intensity);
                mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
            }
            else
            {
                mat.DisableKeyword("_EMISSION");
                mat.SetColor("_EmissionColor", Color.black);
            }

            bool isGlass = detail.name == "MAT_vidrio_arq" || detail.transmission > 0.5f || detail.alpha < 0.99f;
            bool isAlphaClip = detail.name == "potted_plant_01_leaves" ||
                               detail.name == "potted_plant_02_leaves" ||
                               detail.name == "tree_small_02_leaves" ||
                               detail.name == "island_tree_02_leaves";

            if (isGlass)
            {
                mat.SetFloat("_Surface", 1.0f);
                mat.SetFloat("_Blend", 0.0f);
                mat.SetFloat("_AlphaClip", 0.0f);
                mat.SetOverrideTag("RenderType", "Transparent");
                mat.SetInt("_SrcBlend", (int)BlendMode.SrcAlpha);
                mat.SetInt("_DstBlend", (int)BlendMode.OneMinusSrcAlpha);
                mat.SetInt("_ZWrite", 0);
                mat.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
                mat.renderQueue = (int)RenderQueue.Transparent;
                Color glassColor = baseColor;
                glassColor.a = 0.28f;
                mat.SetColor("_BaseColor", glassColor);
                mat.SetFloat("_Smoothness", 0.95f);
            }
            else if (isAlphaClip)
            {
                mat.SetFloat("_Surface", 0.0f);
                mat.SetFloat("_AlphaClip", 1.0f);
                mat.SetFloat("_Cutoff", 0.45f);
                mat.SetFloat("_Cull", 0.0f);
                mat.EnableKeyword("_ALPHATEST_ON");
                mat.DisableKeyword("_SURFACE_TYPE_TRANSPARENT");
                mat.SetOverrideTag("RenderType", "TransparentCutout");
                mat.SetInt("_ZWrite", 1);
                mat.renderQueue = (int)RenderQueue.AlphaTest;
            }
            else
            {
                mat.SetFloat("_Surface", 0.0f);
                mat.SetFloat("_AlphaClip", 0.0f);
                mat.DisableKeyword("_ALPHATEST_ON");
                mat.DisableKeyword("_SURFACE_TYPE_TRANSPARENT");
                mat.SetOverrideTag("RenderType", "Opaque");
                mat.SetInt("_SrcBlend", (int)BlendMode.One);
                mat.SetInt("_DstBlend", (int)BlendMode.Zero);
                mat.SetInt("_ZWrite", 1);
                mat.renderQueue = (int)RenderQueue.Geometry;
            }
        }

        private static void RemapFbxMaterials(Dictionary<string, Material> materials)
        {
            string[] fbxPaths =
            {
                HomeProjectConstants.ArchitectureFbxPath,
                HomeProjectConstants.InteractiveDoorsFbxPath,
                HomeProjectConstants.FurnitureFbxPath,
                HomeProjectConstants.InstallationsFbxPath,
                HomeProjectConstants.UrbanContextFbxPath
            };

            for (int i = 0; i < fbxPaths.Length; i++)
            {
                ModelImporter importer = AssetImporter.GetAtPath(fbxPaths[i]) as ModelImporter;
                if (importer == null)
                {
                    continue;
                }

                bool changed = false;
                foreach (KeyValuePair<string, Material> kvp in materials)
                {
                    AssetImporter.SourceAssetIdentifier id = new AssetImporter.SourceAssetIdentifier(typeof(Material), kvp.Key);
                    Dictionary<AssetImporter.SourceAssetIdentifier, Object> existing = importer.GetExternalObjectMap();
                    if (!existing.TryGetValue(id, out Object currentObj) || currentObj != kvp.Value)
                    {
                        importer.AddRemap(id, kvp.Value);
                        changed = true;
                    }
                }

                if (changed)
                {
                    importer.SaveAndReimport();
                }
            }
        }

        private static void ApplyMaterialsToScene(Dictionary<string, Material> materials)
        {
            GameObject root = GameObject.Find(HomeProjectConstants.HomeProjectRootName);
            if (root == null)
            {
                return;
            }

            MeshRenderer[] renderers = root.GetComponentsInChildren<MeshRenderer>(true);
            for (int i = 0; i < renderers.Length; i++)
            {
                MeshRenderer mr = renderers[i];
                if (mr.transform.IsChildOf(root.transform.Find(HomeProjectConstants.GroupCollisionGeometry)))
                {
                    continue;
                }

                Material[] mats = mr.sharedMaterials;
                bool modified = false;
                for (int m = 0; m < mats.Length; m++)
                {
                    if (mats[m] == null)
                    {
                        continue;
                    }

                    string matName = mats[m].name;
                    if (materials.TryGetValue(matName, out Material persistent))
                    {
                        if (mats[m] != persistent)
                        {
                            mats[m] = persistent;
                            modified = true;
                        }
                    }
                }

                if (modified)
                {
                    mr.sharedMaterials = mats;
                }
            }
        }

        private static Texture2D FindBaseMap(string prefix)
        {
            string[] candidates =
            {
                prefix + "_diff_alpha.png",
                prefix + "_Diffuse.png",
                prefix + "_diff.png",
                prefix + "_BaseColor.png"
            };
            for (int i = 0; i < candidates.Length; i++)
            {
                Texture2D tex = LoadTexture(candidates[i]);
                if (tex != null)
                {
                    return tex;
                }
            }
            return null;
        }

        private static Texture2D FindNormalMap(string prefix)
        {
            string[] candidates =
            {
                prefix + "_nor_gl.png",
                prefix + "_gl_normal.png"
            };
            for (int i = 0; i < candidates.Length; i++)
            {
                Texture2D tex = LoadTexture(candidates[i]);
                if (tex != null)
                {
                    return tex;
                }
            }
            return null;
        }

        private static Texture2D LoadTexture(string fileName)
        {
            string path = Path.Combine(HomeProjectConstants.TexturesPath, fileName).Replace("\\", "/");
            Texture2D tex = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (tex != null)
            {
                return tex;
            }
            string foliagePath = Path.Combine(HomeProjectConstants.TexturesPath, "Foliage", fileName).Replace("\\", "/");
            return AssetDatabase.LoadAssetAtPath<Texture2D>(foliagePath);
        }

        private static Color ToColor(float[] arr, Color fallback)
        {
            if (arr == null || arr.Length < 3)
            {
                return fallback;
            }
            float a = arr.Length >= 4 ? arr[3] : 1.0f;
            return new Color(arr[0], arr[1], arr[2], a);
        }
    }
}
