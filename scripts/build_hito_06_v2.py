from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(bpy.data.filepath).resolve().parents[1] if bpy.data.filepath else Path.cwd()
H6_BLEND = ROOT / "models" / "HOME_PROJECT_HITO_06.blend"
H6_V2_BLEND = ROOT / "models" / "HOME_PROJECT_HITO_06_V2.blend"

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
    obj.data.materials.append(mat)
    return obj

def main():
    bpy.ops.wm.open_mainfile(filepath=str(H6_BLEND))
    c_p1 = bpy.data.collections["07_Propuesta_Primera_Planta"]
    c_veh = bpy.data.collections["10_Vehiculos"]

    if not bpy.data.objects.get("Cubierta_P1_Huespedes"):
        mesh = bpy.data.meshes.new("Cubierta_P1_Huespedes")
        obj = bpy.data.objects.new("Cubierta_P1_Huespedes", mesh)
        c_p1.objects.link(obj)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x = v.co.x * 4.55 + 2.275
            v.co.y = v.co.y * 1.25 + 10.625
            v.co.z = v.co.z * 0.20 + 2.80
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()
        obj.data.materials.append(bpy.data.materials["MAT_concreto_arq"])

    m_car = bpy.data.materials["MAT_vehicle_car"]
    for v in bpy.data.collections["10_Vehiculos"].objects:
        if "Swift" in v.name and "Puerta" not in v.name:
            v.location.x += 0.30
            v.location.y -= 0.10
        elif "VStrom" in v.name:
            v.location.x += 0.10
            v.location.y += 0.87

    if not bpy.data.objects.get("Veh_Swift_Puerta_Cond"):
        create_hinged_panel("Veh_Swift_Puerta_Cond", 6.785, 2.42, 0.25, -0.90, 0.04, 0.95, "Y", m_car, c_veh)
    if not bpy.data.objects.get("Veh_Swift_Puerta_Pas"):
        create_hinged_panel("Veh_Swift_Puerta_Pas", 5.05, 2.42, 0.25, -0.90, 0.04, 0.95, "Y", m_car, c_veh)

    swing_map = {
        "P1_M_Sur_Sala_Puerta1": -1,
        "P1_M_Sep_Sala_Garaje_Puerta1": 1,
        "P1_M_Bano_Sur_Puerta1": 1,
        "P1_M_Bano_Este_Puerta1": -1,
        "P1_M_Huesped_Norte_Cocina_Puerta1": 1,
        "P1_M_Huesped_Norte_Cocina_Puerta3": 1,
        "P2_M_Master_Este_Puerta1": 1,
        "P2_M_Master_Este_Puerta3": 1,
        "P2_M_Vest_Bano_Puerta1": 1,
        "P2_M_Banda_Sur_Puerta1": 1,
        "P2_M_Bano_Comp_Este_Puerta1": -1,
        "P2_M_Banda_Norte_Puerta1": 1,
        "P2_M_Banda_Norte_Puerta3": 1,
    }
    for d in bpy.data.objects:
        if "_Puerta" in d.name and d.type == "MESH" and not d.name.startswith("Veh_"):
            d["swing_dir"] = swing_map.get(d.name, 1)

    viga_06 = bpy.data.objects.get("Viga_P1_06")
    if viga_06:
        bm = bmesh.new()
        bm.from_mesh(viga_06.data)
        for v in bm.verts:
            if (viga_06.matrix_world @ v.co).y > 4.72:
                v.co = viga_06.matrix_world.inverted() @ Vector(((viga_06.matrix_world @ v.co).x, 4.72, (viga_06.matrix_world @ v.co).z))
        bm.to_mesh(viga_06.data)
        bm.free()
        viga_06.data.update()

    for o in bpy.data.collections["11_Mobiliario"].objects:
        if o.name.startswith(("P2_Mob_Cama_Master", "P2_Mob_LED_Cabecero", "P2_PH_Nightstand", "P2_Mob_Tapete_Master")):
            o.location.y -= 0.95

    anim_cam = bpy.data.objects.get("Cam_Recorrido_Anim")
    if anim_cam:
        anim_cam.location = (1.42, 2.20, 1.65)
        anim_cam.keyframe_insert(data_path="location", frame=192)
        anim_cam.location = (2.60, 2.20, 1.65)
        anim_cam.keyframe_insert(data_path="location", frame=240)
        anim_cam.location = (2.60, 4.15, 4.55)
        anim_cam.keyframe_insert(data_path="location", frame=888)
        anim_cam.location = (0.45, 4.15, 4.55)
        anim_cam.keyframe_insert(data_path="location", frame=900)
        anim_cam.location = (0.45, 3.00, 4.55)
        anim_cam.keyframe_insert(data_path="location", frame=912)
        anim_cam.location = (0.45, 4.15, 4.55)
        anim_cam.keyframe_insert(data_path="location", frame=940)
        anim_cam.location = (2.60, 4.15, 4.55)
        anim_cam.keyframe_insert(data_path="location", frame=960)
        anim_cam.location = (2.60, 6.20, 4.55)
        anim_cam.keyframe_insert(data_path="location", frame=980)

    bpy.ops.wm.save_as_mainfile(filepath=str(H6_V2_BLEND))
    print("HITO_06_V2_MODEL_SAVED:", str(H6_V2_BLEND))

if __name__ == "__main__":
    main()
