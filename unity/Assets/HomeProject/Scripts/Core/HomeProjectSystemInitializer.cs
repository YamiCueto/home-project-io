using UnityEngine;

namespace HomeProject.Core
{
    public class HomeProjectSystemInitializer : MonoBehaviour
    {
        [SerializeField] private bool hideCollisionRenderersOnAwake = true;
        public bool IsInitialized { get; private set; }
        public int DisabledColliderRenderers { get; private set; }

        private void Awake()
        {
            Initialize();
        }

        public void Initialize()
        {
            DisabledColliderRenderers = 0;
            if (hideCollisionRenderersOnAwake)
            {
                GameObject root = GameObject.Find(HomeProjectConstants.HomeProjectRootName);
                if (root != null)
                {
                    Transform colliders = root.transform.Find(HomeProjectConstants.GroupCollisionGeometry);
                    if (colliders != null)
                    {
                        MeshRenderer[] renderers = colliders.GetComponentsInChildren<MeshRenderer>(true);
                        for (int i = 0; i < renderers.Length; i++)
                        {
                            if (renderers[i].enabled)
                            {
                                renderers[i].enabled = false;
                                DisabledColliderRenderers++;
                            }
                        }
                    }
                }
            }
            IsInitialized = true;
        }
    }
}
