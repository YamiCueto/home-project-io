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
        private bool isGaragePanel;
        private bool initialized;
        private float currentProgress;

        public bool IsOpen { get; private set; }

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
            isGaragePanel = gameObject.name.Contains("Porton");

            if (isGaragePanel)
            {
                openLocalPosition = closedLocalPosition + new Vector3(0f, slideHeightMeters, 0f);
                openRotation = closedRotation;
            }
            else
            {
                openLocalPosition = closedLocalPosition;
                Vector3 localVerticalAxis = transform.InverseTransformDirection(Vector3.up);
                openRotation = closedRotation * Quaternion.AngleAxis(openAngleDegrees, localVerticalAxis);
            }

            initialized = true;
        }

        private void Update()
        {
            float target = IsOpen ? 1f : 0f;
            if (!Mathf.Approximately(currentProgress, target))
            {
                currentProgress = Mathf.MoveTowards(currentProgress, target, transitionSpeed * Time.deltaTime);
                ApplyProgress();
            }
        }

        public void Toggle()
        {
            SetOpen(!IsOpen, false);
        }

        public void SetOpen(bool open, bool immediate = false)
        {
            EnsureInitialized();
            IsOpen = open;
            if (immediate)
            {
                currentProgress = open ? 1f : 0f;
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
