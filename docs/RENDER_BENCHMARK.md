# Benchmark de Renderizado — HOME PROJECT (Hito 5)

- **GPU:** `NVIDIA GeForce RTX 5070 Ti Laptop GPU`
- **Motor:** Cycles (`GPU Compute`) · **Backend:** `OPTIX` · **Denoiser:** `OPTIX` · **Adaptive Sampling:** Activo
- **Gestión de color:** `AgX` (`AgX - Medium High Contrast`)

| Archivo | Escenario | Resolución | Muestras | Tiempo (`s`) |
| :--- | :--- | :---: | :---: | :---: |
| `exterior/01_ESQUINA_DIA_4K.png` | Día (Cielo físico Nishita) | `3840 × 2160` | `64` | `6,83` |
| `exterior/02_ESQUINA_ATARDECER_4K.png` | Atardecer (Golden Hour + luces int.) | `3840 × 2160` | `64` | `6,81` |
| `exterior/03_FRONTAL_NOCHE.png` | Noche (Iluminación arquitectónica) | `2560 × 1440` | `48` | `2,54` |
| `exterior/04_AEREA_FOTOVOLTAICA.png` | Aérea diurna (Cubierta solar) | `2560 × 1440` | `48` | `2,17` |
| `interior/05_SALA_CONTEMPORANEA.png` | Interior Sala (Día + luz interior) | `2560 × 1440` | `64` | `7,50` |
| `interior/06_COCINA_COMEDOR.png` | Interior Cocina y Comedor | `2560 × 1440` | `64` | `7,03` |
| `interior/07_SUITE_PRINCIPAL.png` | Interior Suite Principal | `2560 × 1440` | `64` | `7,27` |
| `architectural/08_CORTE_ISOMETRICO_CONJUNTO.png` | Presentación isométrica | `2560 × 1440` | `48` | `2,81` |
| **Total (8 renders finales)** | — | `4K + 1440p` | — | **`42,96 s`** |
