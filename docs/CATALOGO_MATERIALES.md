# Catálogo de Materiales PBR — HOME PROJECT (Hito 3)

## 1. Origen y Compatibilidad
- **Método:** Materiales PBR procedurales generados mediante nodos estándar de Blender (`Principled BSDF` + `ShaderNodeTexNoise`, `ShaderNodeTexBrick`, `ShaderNodeTexWave`, `ShaderNodeBump`), utilizados como alternativa determinista y libre de licencias ante la ausencia de `api_key` configurada en BlenderKit.
- **Compatibilidad Unity:** Todos los materiales emplean el shader `Principled BSDF` con parámetros físicos estándar (*Base Color*, *Metallic*, *Roughness*, *Normal/Bump*, *Transmission*), listos para horneado (*bake*) de mapas `Albedo`, `Normal` y `Metallic/Roughness` previo a la exportación FBX.

---

## 2. Materiales Arquitectónicos Aplicados (`HOME_PROJECT_HITO_03.blend`)

| Identificador | Uso Principal | Roughness | Metallic | Relieve / Textura |
| :--- | :--- | :---: | :---: | :--- |
| `MAT_estuco_blanco` | Muros exteriores y pretiles | `0,78` | `0,00` | Micro-estuco (`Noise + Bump 0,06`) |
| `MAT_concreto_arq` | Columnas, vigas, marcos P2 y piso garaje | `0,72` | `0,00` | Concreto visto (`Noise + Bump 0,14`) |
| `MAT_piedra_natural` | Pilares decorativos de fachada frontal y esquina | `0,85` | `0,00` | Mampostería (`Brick + Bump 0,30`) |
| `MAT_madera_ext` | Puerta principal y celosías verticales laterales | `0,45` | `0,00` | Veta de madera (`Wave + ColorRamp + Bump 0,12`) |
| `MAT_aluminio_negro` | Perfilería de ventanas, aleros solares y barandas | `0,28` | `0,88` | Aluminio anodizado negro |
| `MAT_antracita` | Portón vehicular seccional (4 paneles) | `0,38` | `0,45` | Acabado satinado gris antracita (`Bump 0,05`) |
| `MAT_vidrio_arq` | Ventanales panorámicos y baranda de balcón | `0,03` | `0,00` | `Transmission Weight 0,92`, `IOR 1,52` |
| `MAT_porcelanato_ext` | Terraza frontal, pisos interiores y balcón | `0,35` | `0,00` | Modulación cerámica (`Brick + Bump 0,05`) |
| `MAT_solar_panel` | Reserva fotovoltaica en cubierta | `0,15` | `0,35` | Azul fotovoltaico oscuro |
| `MAT_follaje_tropical` | Vegetación tropical en macetas privadas | `0,55` | `0,00` | Orgánico (`Noise + Bump 0,08`) |
