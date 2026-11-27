using System.Collections.Generic;
using HomeProject.Interaction;
using UnityEngine;

namespace HomeProject.Infrastructure
{
    public class ResidentialHudController : MonoBehaviour
    {
        private const int WarmupFrames = 60;

        private ResidentialFirstPersonController player;
        private readonly List<float> frameTimesMs = new List<float>();
        private float smoothedDeltaTime = 0.016f;
        private int totalFrames;

        public float CurrentFps => smoothedDeltaTime > 0.0001f ? 1.0f / smoothedDeltaTime : 0f;
        public float CurrentFrameTimeMs => smoothedDeltaTime * 1000f;

        private void Awake()
        {
            player = Object.FindAnyObjectByType<ResidentialFirstPersonController>();
        }

        private void Update()
        {
            float dt = Time.unscaledDeltaTime;
            if (dt <= 0.0001f)
            {
                return;
            }

            smoothedDeltaTime += (dt - smoothedDeltaTime) * 0.1f;
            totalFrames++;
            if (totalFrames > WarmupFrames)
            {
                frameTimesMs.Add(dt * 1000f);
            }
        }

        public void GetPerformanceSummary(out float avgFps, out float avgFrameMs, out float p95FrameMs, out float p99FrameMs, out float onePercentLowFps)
        {
            if (frameTimesMs.Count == 0)
            {
                avgFps = CurrentFps;
                avgFrameMs = CurrentFrameTimeMs;
                p95FrameMs = avgFrameMs;
                p99FrameMs = avgFrameMs;
                onePercentLowFps = avgFps;
                return;
            }

            List<float> sorted = new List<float>(frameTimesMs);
            sorted.Sort();

            float sum = 0f;
            for (int i = 0; i < sorted.Count; i++)
            {
                sum += sorted[i];
            }

            avgFrameMs = sum / sorted.Count;
            avgFps = avgFrameMs > 0.001f ? 1000f / avgFrameMs : 0f;

            int p95Idx = Mathf.Clamp(Mathf.CeilToInt(sorted.Count * 0.95f) - 1, 0, sorted.Count - 1);
            int p99Idx = Mathf.Clamp(Mathf.CeilToInt(sorted.Count * 0.99f) - 1, 0, sorted.Count - 1);
            p95FrameMs = sorted[p95Idx];
            p99FrameMs = sorted[p99Idx];

            int topOnePercentCount = Mathf.Max(1, Mathf.CeilToInt(sorted.Count * 0.01f));
            float slowSum = 0f;
            for (int i = sorted.Count - topOnePercentCount; i < sorted.Count; i++)
            {
                slowSum += sorted[i];
            }
            float slowAvgMs = slowSum / topOnePercentCount;
            onePercentLowFps = slowAvgMs > 0.001f ? 1000f / slowAvgMs : 0f;
        }

        private void OnGUI()
        {
            if (player == null)
            {
                player = Object.FindAnyObjectByType<ResidentialFirstPersonController>();
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
