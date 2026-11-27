using UnityEngine;

namespace HomeProject.Interaction
{
    public class InteractiveDoor : MonoBehaviour
    {
        [SerializeField] private float openAngleDegrees = 88f;
        [SerializeField] private float slideHeightMeters = 2.15f;
        [SerializeField] private float transitionSpeed = 4.5f;

        private Quaternion closedRotation;
        private Quaternion openRotation;
        private Vector3 closedLocalPosition;
        private Vector3 openLocalPosition;
        private Collider doorCollider;
        private bool isGaragePanel;
        private bool initialized;
        private float currentProgress;

        public bool IsOpen { get; private set; }
        public bool IsTransitioning => !Mathf.Approximately(currentProgress, IsOpen ? 1f : 0f);

        private void Awake()
        {
            EnsureInitialized();
        }

        public void EnsureInitialized()
        {
            if (initialized)
            {
                return;
            }

            closedRotation = transform.localRotation;
            closedLocalPosition = transform.localPosition;
            doorCollider = GetComponent<Collider>();
            isGaragePanel = gameObject.name.Contains("Porton");

            if (isGaragePanel)
            {
                Vector3 parentUp = transform.parent != null ? transform.parent.InverseTransformDirection(Vector3.up) : Vector3.up;
                openLocalPosition = closedLocalPosition + parentUp * slideHeightMeters;
                openRotation = closedRotation;
            }
            else
            {
                openLocalPosition = closedLocalPosition;
                float dir = (gameObject.name.Contains("Bano_Este") ||
                             gameObject.name.Contains("Bano_Comp_Este") ||
                             gameObject.name.Contains("Banda_Norte") ||
                             gameObject.name.Contains("Banda_Sur")) ? -1f : 1f;
                Vector3 localVerticalAxis = transform.InverseTransformDirection(Vector3.up);
                openRotation = closedRotation * Quaternion.AngleAxis(openAngleDegrees * dir, localVerticalAxis);
            }

            initialized = true;
        }

        private void Update()
        {
            float target = IsOpen ? 1f : 0f;
            if (!Mathf.Approximately(currentProgress, target))
            {
                currentProgress = Mathf.MoveTowards(currentProgress, target, transitionSpeed * Time.deltaTime);
                if (doorCollider != null)
                {
                    doorCollider.isTrigger = !Mathf.Approximately(currentProgress, target);
                }
                ApplyProgress();
            }
            else if (doorCollider != null && doorCollider.isTrigger)
            {
                doorCollider.isTrigger = false;
            }
        }

        public void Toggle()
        {
            if (isGaragePanel && transform.parent != null)
            {
                bool nextState = !IsOpen;
                InteractiveDoor[] siblings = transform.parent.GetComponentsInChildren<InteractiveDoor>(true);
                for (int i = 0; i < siblings.Length; i++)
                {
                    if (siblings[i].gameObject.name.Contains("Porton"))
                    {
                        siblings[i].SetOpen(nextState, false);
                    }
                }
                return;
            }
            SetOpen(!IsOpen, false);
        }

        public void SetOpen(bool open, bool immediate = false)
        {
            EnsureInitialized();
            IsOpen = open;
            if (immediate)
            {
                currentProgress = open ? 1f : 0f;
                if (doorCollider != null)
                {
                    doorCollider.isTrigger = false;
                }
                ApplyProgress();
                Physics.SyncTransforms();
            }
        }

        private void ApplyProgress()
        {
            transform.localPosition = Vector3.Lerp(closedLocalPosition, openLocalPosition, currentProgress);
            transform.localRotation = Quaternion.Slerp(closedRotation, openRotation, currentProgress);
        }
    }
}
