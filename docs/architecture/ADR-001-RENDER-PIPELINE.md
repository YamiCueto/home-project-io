# ADR-001 — Selección de Pipeline de Renderizado (URP)

- **Estado:** Aprobado
- **Hito:** 8.1 — Integración arquitectónica Blender–Unity
- **Fecha:** 2026-11-27

## Contexto

El proyecto **HOME PROJECT** requiere migrar la vivienda desde Blender 5.3.0 Beta hacia Unity 6.6 (`6000.6.11f1`) para soportar recorrido interactivo en primera persona, física en tiempo real, futura interfaz de usuario y eventual soporte OpenXR.

## Decisión

Se selecciona **Universal Render Pipeline (URP `17.6.0`)** como pipeline de renderizado definitivo.

No se utilizará **HDRP** ni **Built-In Render Pipeline**.

## Justificación

1. **Hoja de ruta de Unity:** URP es el pipeline alineado con la consolidación de tecnologías de renderizado de Unity 6+.
2. **Rendimiento y portabilidad:** Permite aprovechar hardware de gama alta en Windows x64 (DirectX 12, Forward+, SSAO, MSAA 4x, sombras 4096px con 4 cascadas, Tonemapping ACES y Bloom) manteniendo escalabilidad para futuros builds interactivos y OpenXR.
3. **Ecosistema de paquetes:** La plantilla Universal 3D (`PC_RPAsset`, `PC_Renderer`, `Mobile_RPAsset`) ya viene integrada con `com.unity.render-pipelines.universal: 17.6.0`.

## Consecuencias

- Todos los materiales deben utilizar shaders compatibles con URP (`Universal Render Pipeline/Lit`).
- Las características exclusivas de HDRP no se asumen disponibles; cada capacidad gráfica (Forward+, SSAO, Volume Profile) se verifica directamente sobre `UniversalRenderPipelineAsset` y `UniversalRendererData`.
