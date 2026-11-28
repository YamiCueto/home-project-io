using System.IO;
using HomeProject.Core;
using UnityEditor;
using UnityEngine;

namespace HomeProject.Editor
{
    public static class FbxImportConfigurator
    {
        private static readonly string[] AllFbxPaths =
        {
            HomeProjectConstants.ArchitectureFbxPath,
            HomeProjectConstants.InteractiveDoorsFbxPath,
            HomeProjectConstants.FurnitureFbxPath,
            HomeProjectConstants.InstallationsFbxPath,
            HomeProjectConstants.UrbanContextFbxPath,
            HomeProjectConstants.CollidersFbxPath
        };

        public static void ConfigureTexturesAndFbx()
        {
            ConfigureTextureImporters();
            ConfigureFbxImporters();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
        }

        public static void ConfigureTextureImporters()
        {
            if (!Directory.Exists(HomeProjectConstants.TexturesPath))
            {
                return;
            }

            string[] guids = AssetDatabase.FindAssets("t:Texture2D", new[] { HomeProjectConstants.TexturesPath });
            for (int i = 0; i < guids.Length; i++)
            {
                string path = AssetDatabase.GUIDToAssetPath(guids[i]);
                TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null)
                {
                    continue;
                }

                string lower = Path.GetFileName(path).ToLowerInvariant();
                bool changed = false;

                if (lower.Contains("_nor_gl") || lower.Contains("_gl_normal") || lower.Contains("normal"))
                {
                    if (importer.textureType != TextureImporterType.NormalMap)
                    {
                        importer.textureType = TextureImporterType.NormalMap;
                        changed = true;
                    }
                }
                else if (lower.Contains("_metallicsmoothness") || lower.Contains("_rough") || lower.Contains("_metal"))
                {
                    if (importer.sRGBTexture)
                    {
                        importer.sRGBTexture = false;
                        changed = true;
                    }
                }

                if (importer.maxTextureSize < 2048)
                {
                    importer.maxTextureSize = 2048;
                    changed = true;
                }

                if (changed)
                {
                    importer.SaveAndReimport();
                }
            }
        }

        public static void ConfigureFbxImporters()
        {
            for (int i = 0; i < AllFbxPaths.Length; i++)
            {
                string fbxPath = AllFbxPaths[i];
                ModelImporter importer = AssetImporter.GetAtPath(fbxPath) as ModelImporter;
                if (importer == null)
                {
                    continue;
                }

                bool changed = false;

                if (!Mathf.Approximately(importer.globalScale, 1.0f))
                {
                    importer.globalScale = 1.0f;
                    changed = true;
                }

                if (!importer.useFileScale)
                {
                    importer.useFileScale = true;
                    changed = true;
                }

                if (!importer.isReadable)
                {
                    importer.isReadable = true;
                    changed = true;
                }

                bool isArch = fbxPath == HomeProjectConstants.ArchitectureFbxPath;
                if (isArch && !importer.generateSecondaryUV)
                {
                    importer.generateSecondaryUV = true;
                    changed = true;
                }

                bool isCollider = fbxPath == HomeProjectConstants.CollidersFbxPath;
                ModelImporterMaterialImportMode targetMatMode = isCollider
                    ? ModelImporterMaterialImportMode.None
                    : ModelImporterMaterialImportMode.ImportStandard;

                if (importer.materialImportMode != targetMatMode)
                {
                    importer.materialImportMode = targetMatMode;
                    changed = true;
                }

                if (changed)
                {
                    importer.SaveAndReimport();
                }
            }
        }
    }
}
