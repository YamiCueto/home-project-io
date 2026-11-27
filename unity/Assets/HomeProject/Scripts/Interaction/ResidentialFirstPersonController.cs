using HomeProject.Core;
using UnityEngine;
using UnityEngine.InputSystem;

namespace HomeProject.Interaction
{
    [RequireComponent(typeof(CharacterController))]
    public class ResidentialFirstPersonController : MonoBehaviour
    {
        [SerializeField] private float playerHeight = 1.80f;
        [SerializeField] private float cameraEyeHeight = 1.65f;
        [SerializeField] private float playerRadius = 0.30f;
        [SerializeField] private float walkSpeed = 1.60f;
        [SerializeField] private float gravity = -9.81f;
        [SerializeField] private float stepOffset = 0.25f;
        [SerializeField] private float mouseSensitivity = 0.14f;
        [SerializeField] private float interactDistance = 2.4f;
        [SerializeField] private Vector3 spawnPosition = new Vector3(-1.12f, 0.08f, 1.80f);
        [SerializeField] private float spawnYaw = 180f;

        private CharacterController controller;
        private Camera playerCamera;
        private OrbitalInspectionCamera orbitalCamera;
        private float verticalVelocity;
        private float pitch;
        private float yaw;
        private float smoothedCameraY;
        private bool inputOverrideActive;
        private Vector2 overrideMove;
        private Vector2 overrideLook;

        public bool IsPaused { get; private set; }
        public bool IsOrbitalMode { get; private set; }
        public bool IsGrounded => controller != null && controller.isGrounded;
        public string CurrentZoneName => ResidentialZoneTracker.GetZoneName(transform.position);
        public float CurrentElevationY => transform.position.y;
        public float CurrentYaw => yaw;
        public InteractiveDoor LastHoveredDoor { get; private set; }
        public int CollisionCount { get; private set; }
        public string LastHitObject { get; private set; }
        public Camera PlayerCamera => playerCamera;

        private void Awake()
        {
            controller = GetComponent<CharacterController>();
            ConfigureCharacterController();
            playerCamera = GetComponentInChildren<Camera>(true);
            orbitalCamera = Object.FindAnyObjectByType<OrbitalInspectionCamera>(FindObjectsInactive.Include);
            yaw = spawnYaw;
            smoothedCameraY = transform.position.y + cameraEyeHeight;
            ApplyCameraTransform(true);
        }

        private void Start()
        {
            SetOrbitalMode(false);
        }

        private void OnDisable()
        {
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }

        private void OnApplicationFocus(bool hasFocus)
        {
            if (hasFocus)
            {
                UpdateCursorLock();
            }
        }

        private void OnControllerColliderHit(ControllerColliderHit hit)
        {
            if (hit.normal.y < 0.5f)
            {
                CollisionCount++;
                LastHitObject = hit.collider != null ? hit.collider.gameObject.name : "";
            }
        }

        public void ConfigureCharacterController()
        {
            if (controller == null)
            {
                controller = GetComponent<CharacterController>();
            }
            controller.height = playerHeight;
            controller.radius = playerRadius;
            controller.center = new Vector3(0f, playerHeight * 0.5f, 0f);
            controller.stepOffset = stepOffset;
            controller.slopeLimit = 50f;
            controller.skinWidth = 0.02f;
        }

        private void Update()
        {
            HandleSystemShortcuts();

            if (transform.position.y < -1.0f)
            {
                ResetToSpawn();
                return;
            }

            if (IsPaused || IsOrbitalMode)
            {
                return;
            }

            HandleLook();
            HandleMovement();
            HandleDoorHoverAndInteract();
        }

        private void HandleSystemShortcuts()
        {
            Keyboard kb = Keyboard.current;
            if (kb == null)
            {
                return;
            }

            if (kb.escapeKey.wasPressedThisFrame)
            {
                IsPaused = !IsPaused;
                UpdateCursorLock();
            }

            if (kb.rKey.wasPressedThisFrame)
            {
                ResetToSpawn();
            }

            if (kb.vKey.wasPressedThisFrame)
            {
                SetOrbitalMode(!IsOrbitalMode);
            }
        }

        private void HandleLook()
        {
            Vector2 delta = Vector2.zero;
            if (inputOverrideActive)
            {
                delta = overrideLook;
            }
            else if (Mouse.current != null && Cursor.lockState == CursorLockMode.Locked)
            {
                delta = Mouse.current.delta.ReadValue() * mouseSensitivity;
            }

            yaw += delta.x;
            pitch = Mathf.Clamp(pitch - delta.y, -80f, 80f);
            ApplyCameraTransform(false);
        }

        private void HandleMovement()
        {
            Vector2 moveInput = Vector2.zero;
            if (inputOverrideActive)
            {
                moveInput = overrideMove;
            }
            else if (Keyboard.current != null)
            {
                if (Keyboard.current.wKey.isPressed) moveInput.y += 1f;
                if (Keyboard.current.sKey.isPressed) moveInput.y -= 1f;
                if (Keyboard.current.dKey.isPressed) moveInput.x += 1f;
                if (Keyboard.current.aKey.isPressed) moveInput.x -= 1f;
            }

            if (moveInput.sqrMagnitude > 1f)
            {
                moveInput.Normalize();
            }

            Vector3 forward = Quaternion.Euler(0f, yaw, 0f) * Vector3.forward;
            Vector3 right = Quaternion.Euler(0f, yaw, 0f) * Vector3.right;
            Vector3 horizontal = (forward * moveInput.y + right * moveInput.x) * walkSpeed;

            if (controller.isGrounded && verticalVelocity < 0f)
            {
                verticalVelocity = -2.0f;
            }
            else
            {
                verticalVelocity += gravity * Time.deltaTime;
            }

            Vector3 motion = (horizontal + Vector3.up * verticalVelocity) * Time.deltaTime;
            controller.Move(motion);
            ApplyCameraTransform(false);
        }

        private void HandleDoorHoverAndInteract()
        {
            LastHoveredDoor = null;
            if (playerCamera == null)
            {
                return;
            }

            Ray ray = new Ray(playerCamera.transform.position, playerCamera.transform.forward);
            if (Physics.Raycast(ray, out RaycastHit hit, interactDistance, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore))
            {
                InteractiveDoor door = hit.collider.GetComponentInParent<InteractiveDoor>();
                if (door != null)
                {
                    LastHoveredDoor = door;
                    if (Keyboard.current != null && Keyboard.current.eKey.wasPressedThisFrame)
                    {
                        door.Toggle();
                    }
                }
            }
        }

        public void ResetToSpawn()
        {
            TeleportTo(spawnPosition, spawnYaw);
        }

        public void TeleportTo(Vector3 position, float newYaw)
        {
            if (controller == null)
            {
                controller = GetComponent<CharacterController>();
            }
            controller.enabled = false;
            transform.position = position;
            verticalVelocity = 0f;
            yaw = newYaw;
            pitch = 0f;
            smoothedCameraY = position.y + cameraEyeHeight;
            ApplyCameraTransform(true);
            controller.enabled = true;
            Physics.SyncTransforms();
        }

        public void SetInputOverride(bool active, Vector2 move, Vector2 look)
        {
            inputOverrideActive = active;
            overrideMove = move;
            overrideLook = look;
        }

        public void SetOrbitalMode(bool orbital)
        {
            IsOrbitalMode = orbital;

            Camera[] allCams = Object.FindObjectsByType<Camera>(FindObjectsInactive.Include);
            for (int i = 0; i < allCams.Length; i++)
            {
                if (allCams[i] != playerCamera && (orbitalCamera == null || allCams[i].gameObject != orbitalCamera.gameObject))
                {
                    allCams[i].enabled = false;
                }
            }

            if (playerCamera != null)
            {
                playerCamera.enabled = !orbital;
            }
            if (orbitalCamera != null)
            {
                orbitalCamera.SetActive(orbital);
            }
            UpdateCursorLock();
        }

        private void ApplyCameraTransform(bool immediate)
        {
            transform.rotation = Quaternion.Euler(0f, yaw, 0f);
            if (playerCamera != null)
            {
                float targetY = transform.position.y + cameraEyeHeight;
                if (immediate)
                {
                    smoothedCameraY = targetY;
                }
                else
                {
                    smoothedCameraY = Mathf.Lerp(smoothedCameraY, targetY, Mathf.Clamp01(Time.deltaTime * 18f));
                }

                float localY = smoothedCameraY - transform.position.y;
                playerCamera.transform.localPosition = new Vector3(0f, localY, 0f);
                playerCamera.transform.localRotation = Quaternion.Euler(pitch, 0f, 0f);
            }
        }

        private void UpdateCursorLock()
        {
            bool shouldLock = !IsPaused && !IsOrbitalMode && !Application.isBatchMode;
            if (shouldLock && !inputOverrideActive)
            {
                Cursor.lockState = CursorLockMode.Locked;
                Cursor.visible = false;
            }
            else
            {
                Cursor.lockState = CursorLockMode.None;
                Cursor.visible = true;
            }
        }
    }
}
