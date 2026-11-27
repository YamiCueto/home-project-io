using UnityEngine;
using UnityEngine.InputSystem;

namespace HomeProject.Interaction
{
    public class OrbitalInspectionCamera : MonoBehaviour
    {
        [SerializeField] private Vector3 targetCenter = new Vector3(-4.0f, 2.5f, -5.5f);
        [SerializeField] private float distance = 16.0f;
        [SerializeField] private float orbitSpeed = 0.25f;
        [SerializeField] private float zoomSpeed = 0.02f;

        private Camera cam;
        private float yaw = 35f;
        private float pitch = 24f;
        private bool active;

        private void Awake()
        {
            cam = GetComponent<Camera>();
            UpdateOrbitTransform();
        }

        public void SetActive(bool isActive)
        {
            active = isActive;
            if (cam != null)
            {
                cam.enabled = isActive;
            }
            if (isActive)
            {
                UpdateOrbitTransform();
            }
        }

        private void Update()
        {
            if (!active)
            {
                return;
            }

            if (Mouse.current != null)
            {
                if (Mouse.current.leftButton.isPressed || Mouse.current.rightButton.isPressed)
                {
                    Vector2 delta = Mouse.current.delta.ReadValue();
                    yaw += delta.x * orbitSpeed;
                    pitch = Mathf.Clamp(pitch - delta.y * orbitSpeed, 5f, 80f);
                }

                float scroll = Mouse.current.scroll.ReadValue().y;
                if (Mathf.Abs(scroll) > 0.01f)
                {
                    distance = Mathf.Clamp(distance - scroll * zoomSpeed, 6f, 35f);
                }
            }

            UpdateOrbitTransform();
        }

        private void UpdateOrbitTransform()
        {
            Quaternion rot = Quaternion.Euler(pitch, yaw, 0f);
            transform.position = targetCenter - (rot * Vector3.forward) * distance;
            transform.LookAt(targetCenter);
        }
    }
}
