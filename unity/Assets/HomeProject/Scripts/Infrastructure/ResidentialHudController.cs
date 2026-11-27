using HomeProject.Interaction;
using UnityEngine;

namespace HomeProject.Infrastructure
{
    public class ResidentialHudController : MonoBehaviour
    {
        private ResidentialFirstPersonController player;
        private float smoothedDeltaTime = 0.016f;
        private float minFps = 9999f;
        private float fpsSum;
        private int frameSamples;

        public float CurrentFps => smoothedDeltaTime > 0.0001f ? 1.0f / smoothedDeltaTime : 0f;
        public float CurrentFrameTimeMs => smoothedDeltaTime * 1000f;
        public float AverageFps => frameSamples > 0 ? fpsSum / frameSamples : 0f;
        public float MinFps => frameSamples > 0 ? minFps : 0f;

        private void Awake()
        {
            player = Object.FindFirstObjectByType<ResidentialFirstPersonController>();
        }

        private void Update()
        {
            smoothedDeltaTime += (Time.unscaledDeltaTime - smoothedDeltaTime) * 0.1f;
            if (Time.unscaledDeltaTime > 0.0001f)
            {
                float instFps = 1.0f / Time.unscaledDeltaTime;
                fpsSum += instFps;
                frameSamples++;
                if (instFps < minFps)
                {
                    minFps = instFps;
                }
            }
        }

        private void OnGUI()
        {
            if (player == null)
            {
                player = Object.FindFirstObjectByType<ResidentialFirstPersonController>();
                if (player == null) return;
            }

            GUIStyle boxStyle = new GUIStyle(GUI.skin.box);
            boxStyle.alignment = TextAnchor.UpperLeft;
            boxStyle.fontSize = 13;
            boxStyle.padding = new RectOffset(10, 10, 8, 8);

            string mode = player.IsOrbitalMode ? "Inspeccion Orbital" : (player.IsPaused ? "Pausado" : "Primera Persona");
            string info = "HOME PROJECT — Recorrido Residencial\n" +
                          "Modo: " + mode + "\n" +
                          "Ubicacion: " + player.CurrentZoneName + "\n" +
                          "Altura: " + player.CurrentElevationY.ToString("F2") + " m\n" +
                          "Rendimiento: " + CurrentFps.ToString("F0") + " FPS (" + CurrentFrameTimeMs.ToString("F1") + " ms)";

            GUI.Box(new Rect(14, 14, 320, 108), info, boxStyle);

            if (!player.IsOrbitalMode && player.LastHoveredDoor != null)
            {
                string prompt = player.LastHoveredDoor.IsOpen ? "[E] Cerrar puerta" : "[E] Abrir puerta";
                GUI.Box(new Rect(Screen.width * 0.5f - 85, Screen.height * 0.5f + 24, 170, 28), prompt, boxStyle);
            }

            string controls = "WASD: Caminar | Raton: Orientar | E: Puerta | V: Modo Orbital | R: Inicio | Esc: Pausa";
            GUI.Box(new Rect(14, Screen.height - 42, 620, 28), controls, boxStyle);
        }
    }
}
