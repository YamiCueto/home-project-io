using System.Collections.Generic;
using HomeProject.Architecture;
using HomeProject.Core;
using UnityEditor;
using UnityEngine;

namespace HomeProject.Editor
{
    public static class ColliderAuditService
    {
        public static void ConfigureColliders()
        {
            int colLayer = EnsureLayer(HomeProjectConstants.CollisionLayerName);
            GameObject root = GameObject.Find(HomeProjectConstants.HomeProjectRootName);
            if (root == null)
            {
                return;
            }

            Transform colGroup = root.transform.Find(HomeProjectConstants.GroupCollisionGeometry);
            if (colGroup != null)
            {
                ConfigureColliderGroup(colGroup, colLayer);
            }

            ConfigureFurnitureAndDoorColliders(root.transform);
        }

        private static void ConfigureColliderGroup(Transform colGroup, int colLayer)
        {
            MeshFilter[] filters = colGroup.GetComponentsInChildren<MeshFilter>(true);
            for (int i = 0; i < filters.Length; i++)
            {
                GameObject go = filters[i].gameObject;
                if (colLayer >= 0)
                {
                    go.layer = colLayer;
                }

                MeshRenderer mr = go.GetComponent<MeshRenderer>();
                if (mr != null)
                {
                    mr.enabled = false;
                    EditorUtility.SetDirty(mr);
                    PrefabUtility.RecordPrefabInstancePropertyModifications(mr);
                }

                Mesh mesh = filters[i].sharedMesh;
                if (mesh == null)
                {
                    continue;
                }

                Collider existing = go.GetComponent<Collider>();
                if (mesh.vertexCount <= 24 && mesh.triangles.Length <= 36)
                {
                    if (existing != null && !(existing is BoxCollider))
                    {
                        Object.DestroyImmediate(existing);
                        existing = null;
                    }

                    BoxCollider box = existing as BoxCollider;
                    if (box == null)
                    {
                        box = go.AddComponent<BoxCollider>();
                    }

                    box.center = mesh.bounds.center;
                    box.size = mesh.bounds.size;
                }
                else
                {
                    if (existing != null && !(existing is MeshCollider))
                    {
                        Object.DestroyImmediate(existing);
                        existing = null;
                    }

                    MeshCollider mc = existing as MeshCollider;
                    if (mc == null)
                    {
                        mc = go.AddComponent<MeshCollider>();
                    }

                    mc.sharedMesh = mesh;
                    mc.convex = false;
                }
            }
        }

        private static void ConfigureFurnitureAndDoorColliders(Transform homeRoot)
        {
            string[] groups = { HomeProjectConstants.GroupFurniture, HomeProjectConstants.GroupInteractiveDoors, HomeProjectConstants.GroupVehicles };
            for (int g = 0; g < groups.Length; g++)
            {
                Transform group = homeRoot.Find(groups[g]);
                if (group == null)
                {
                    continue;
                }

                MeshFilter[] filters = group.GetComponentsInChildren<MeshFilter>(true);
                for (int i = 0; i < filters.Length; i++)
                {
                    GameObject go = filters[i].gameObject;
                    Mesh mesh = filters[i].sharedMesh;
                    if (mesh == null || go.GetComponent<Collider>() != null)
                    {
                        continue;
                    }

                    if (groups[g] == HomeProjectConstants.GroupInteractiveDoors)
                    {
                        BoxCollider box = go.AddComponent<BoxCollider>();
                        box.center = mesh.bounds.center;
                        box.size = mesh.bounds.size;
                    }
                    else
                    {
                        MeshCollider mc = go.AddComponent<MeshCollider>();
                        mc.sharedMesh = mesh;
                        mc.convex = false;
                    }
                }
            }
        }

        public static int EnsureLayer(string layerName)
        {
            int existing = LayerMask.NameToLayer(layerName);
            if (existing >= 0)
            {
                return existing;
            }

            Object[] assets = AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset");
            if (assets == null || assets.Length == 0)
            {
                return 0;
            }

            SerializedObject tagManager = new SerializedObject(assets[0]);
            SerializedProperty layers = tagManager.FindProperty("layers");
            for (int i = 8; i < layers.arraySize; i++)
            {
                SerializedProperty sp = layers.GetArrayElementAtIndex(i);
                if (string.IsNullOrEmpty(sp.stringValue))
                {
                    sp.stringValue = layerName;
                    tagManager.ApplyModifiedProperties();
                    return i;
                }
            }

            return 0;
        }
    }
}
