from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(bpy.data.filepath).resolve().parents[1] if bpy.data.filepath else Path.cwd()
H6_V2_BLEND = ROOT / "models" / "HOME_PROJECT_HITO_06_V2.blend"
H6_V3_BLEND = ROOT / "models" / "HOME_PROJECT_HITO_06_V3.blend"

def make_box(name, x0, x1, y0, y1, z0, z1, mat, col):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = v.co.x * (x1 - x0) + (x0 + x1) * 0.5
        v.co.y = v.co.y * (y1 - y0) + (y0 + y1) * 0.5
        v.co.z = v.co.z * (z1 - z0) + (z0 + z1) * 0.5
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        obj.data.materials.append(mat)
    return obj

def create_hinged_panel(name, hx, hy, z0, length, thick, height, axis, mat, col):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        if axis == "Y":
            v.co.x = v.co.x * thick
            v.co.y = (v.co.y + 0.5) * length
        else:
            v.co.x = (v.co.x + 0.5) * length
            v.co.y = v.co.y * thick
        v.co.z = (v.co.z + 0.5) * height
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj.location = (hx, hy, z0)
    if mat:
        obj.data.materials.append(mat)
    return obj

def remove_obj(name):
    o = bpy.data.objects.get(name)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

def main():
    bpy.ops.wm.open_mainfile(filepath=str(H6_V2_BLEND))
    c_p1 = bpy.data.collections["07_Propuesta_Primera_Planta"]
    c_p2 = bpy.data.collections["08_Propuesta_Segunda_Planta"]
    c_fach = bpy.data.collections["14_Fachadas_Y_Vegetacion"]
    c_inst = bpy.data.collections["16_Instalaciones_Domotica"]

    m_stucco = bpy.data.materials.get("MAT_estuco_blanco")
    m_piedra = bpy.data.materials.get("MAT_piedra_natural")
    m_antracita = bpy.data.materials.get("MAT_antracita")
    m_aluminio = bpy.data.materials.get("MAT_aluminio_negro")
    m_madera = bpy.data.materials.get("MAT_madera_ext")
    m_domotica = bpy.data.materials.get("MAT_equipo_domotica")
    m_vidrio = bpy.data.materials.get("MAT_vidrio_arq")
    m_porcelanato = bpy.data.materials.get("MAT_porcelanato_ext")

    remove_obj("Fach_Murete_Peatonal")
    remove_obj("Fach_Remate_Murete")
    make_box("Fach_Murete_Peatonal_Izq", 0.42, 0.62, 0.00, 0.10, 0.00, 0.95, m_stucco, c_fach)
    make_box("Fach_Murete_Peatonal_Der", 1.62, 4.38, 0.00, 0.10, 0.00, 0.95, m_stucco, c_fach)
    make_box("Fach_Remate_Murete_Izq", 0.42, 0.62, -0.01, 0.11, 0.95, 1.01, m_piedra, c_fach)
    make_box("Fach_Remate_Murete_Der", 1.62, 4.38, -0.01, 0.11, 0.95, 1.01, m_piedra, c_fach)

    gate = create_hinged_panel("Fach_Porton_Peatonal_Puerta1", 0.62, 0.05, 0.02, 0.98, 0.05, 1.02, "X", m_antracita, c_fach)
    gate["swing_dir"] = -1
    make_box("Inst_Cerradura_Peatonal", 1.50, 1.56, 0.01, 0.09, 0.86, 1.02, m_domotica, c_inst)

    for obj in bpy.data.collections["11_Mobiliario"].objects:
        if obj.name.startswith(("P1_Mob_Mesa_Comedor", "P1_Mob_Mesa_Pata", "P1_PH_Chair_1", "P1_PH_Chair_2", "P1_PH_Chair_3", "P1_PH_Chair_4", "P1_PH_Chair_5")):
            obj.location.x -= 0.35
            obj.location.y -= 0.15
            if "Chair_3" in obj.name or "Chair_4" in obj.name:
                obj.location.y -= 0.58
        elif obj.name == "P1_Mob_Cocina_Barra":
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            for v in bm.verts:
                w = obj.matrix_world @ v.co
                if w.y > 6.75:
                    w.y = 6.75
                    v.co = obj.matrix_world.inverted() @ w
            bm.to_mesh(obj.data)
            bm.free()
            obj.data.update()
        elif obj.name == "P1_Mob_Nevecon":
            obj.location.x += 1.43
            obj.location.y -= 1.45
        elif obj.name.startswith(("P2_Mob_Cama_Master", "P2_Mob_LED_Cabecero", "P2_PH_Nightstand_")):
            obj.location.x -= 0.15

    for obj in bpy.data.objects:
        if obj.name.startswith("Veh_VStrom"):
            obj.location.y -= 0.55

    remove_obj("P1_Piso_P1_Paso_Garaje")
    make_box("P1_Piso_P1_Paso_Garaje", 6.85, 7.85, 4.75, 5.80, 0.00, 0.04, m_porcelanato, c_p1)
    remove_obj("P1_M_Norte_Garaje_S0")
    remove_obj("P1_M_Norte_Garaje_Lint1")
    remove_obj("P1_M_Norte_Garaje_Puerta1")
    make_box("P1_M_Norte_Garaje_S0", 4.60, 6.95, 4.66, 4.76, 0.00, 2.70, m_stucco, c_p1)
    make_box("P1_M_Norte_Garaje_Lint1", 6.95, 7.85, 4.66, 4.76, 2.10, 2.70, m_stucco, c_p1)
    g_door = create_hinged_panel("P1_M_Norte_Garaje_Puerta1", 6.95, 4.71, 0.04, 0.85, 0.05, 2.06, "X", m_madera, c_p1)
    g_door["swing_dir"] = -1

    for name in ("Esc_Baranda_P2_Oeste", "Esc_Baranda_P2_Norte", "Esc_Vidrio_P2_Oeste", "Esc_Vidrio_P2_Norte", "Esc_Pasamanos_Norte"):
        remove_obj(name)
    for i in range(1, 16):
        remove_obj(f"Esc_Poste_{i:02d}")

    make_box("Esc_Baranda_P2_Oeste", 3.08, 3.13, 4.75, 5.70, 3.80, 3.85, m_aluminio, c_p2)
    make_box("Esc_Vidrio_P2_Oeste", 3.09, 3.12, 4.75, 5.70, 2.90, 3.80, m_vidrio, c_p2)
    make_box("Esc_Baranda_P2_Norte", 3.10, 6.85, 5.68, 5.73, 3.80, 3.85, m_aluminio, c_p2)
    make_box("Esc_Vidrio_P2_Norte", 3.10, 6.85, 5.69, 5.72, 2.90, 3.80, m_vidrio, c_p2)

    mesh_hr = bpy.data.meshes.new("Esc_Pasamanos_Norte")
    obj_hr = bpy.data.objects.new("Esc_Pasamanos_Norte", mesh_hr)
    c_p1.objects.link(obj_hr)
    bm = bmesh.new()
    verts_top = [
        bm.verts.new((3.10, 5.66, 0.90)),
        bm.verts.new((6.85, 5.66, 3.62)),
        bm.verts.new((6.85, 5.71, 3.62)),
        bm.verts.new((3.10, 5.71, 0.90)),
        bm.verts.new((3.10, 5.66, 0.95)),
        bm.verts.new((6.85, 5.66, 3.67)),
        bm.verts.new((6.85, 5.71, 3.67)),
        bm.verts.new((3.10, 5.71, 0.95)),
    ]
    faces_idx = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    for fi in faces_idx:
        bm.faces.new([verts_top[k] for k in fi])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh_hr)
    bm.free()
    if m_aluminio:
        obj_hr.data.materials.append(m_aluminio)

    for idx in (1, 4, 8, 12, 15):
        px = 3.10 + (idx - 0.5) * 0.25
        pz_base = (idx - 1) * 0.18125
        make_box(f"Esc_Poste_{idx:02d}", px - 0.02, px + 0.02, 5.66, 5.71, pz_base, pz_base + 0.92, m_aluminio, c_p1)

    bpy.ops.wm.save_as_mainfile(filepath=str(H6_V3_BLEND))
    print("HITO_06_V3_MODEL_SAVED:", str(H6_V3_BLEND))

if __name__ == "__main__":
    main()
