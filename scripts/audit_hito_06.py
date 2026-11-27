from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(bpy.data.filepath).resolve().parents[1] if bpy.data.filepath else Path.cwd()
V2_BLEND = ROOT / "models" / "HOME_PROJECT_HITO_05_V2.blend"
H6_BLEND = ROOT / "models" / "HOME_PROJECT_HITO_06.blend"

Z_P1 = 0.00
Z_P2 = 2.90
EYE_H = 1.65

WALKTHROUGH_WAYPOINTS = [
    (0, (9.0, -5.5, Z_P1 + 2.2), (4.0, 2.5, Z_P1 + 1.6)),
    (96, (1.12, -1.0, Z_P1 + EYE_H), (1.12, 2.5, Z_P1 + 1.5)),
    (192, (1.12, 2.5, Z_P1 + EYE_H), (2.60, 4.2, Z_P1 + 1.4)),
    (288, (2.60, 4.2, Z_P1 + EYE_H), (2.60, 6.8, Z_P1 + 1.4)),
    (384, (2.60, 7.2, Z_P1 + EYE_H), (1.80, 9.5, Z_P1 + 1.2)),
    (480, (2.60, 7.2, Z_P1 + EYE_H), (5.50, 7.0, Z_P1 + 1.3)),
    (576, (2.60, 5.22, Z_P1 + EYE_H), (6.80, 5.22, Z_P2 + 0.8)),
    (720, (7.35, 5.22, Z_P2 + EYE_H), (7.35, 6.20, Z_P2 + 1.5)),
    (816, (5.50, 6.20, Z_P2 + EYE_H), (2.60, 6.20, Z_P2 + 1.5)),
    (864, (2.60, 6.20, Z_P2 + EYE_H), (2.60, 4.00, Z_P2 + 1.4)),
    (912, (2.60, 4.00, Z_P2 + EYE_H), (2.20, 0.80, Z_P2 + 1.2)),
    (1008, (3.40, 6.20, Z_P2 + EYE_H), (1.20, 8.80, Z_P2 + 1.2)),
    (1152, (4.60, 6.20, Z_P2 + EYE_H), (6.80, 8.80, Z_P2 + 1.2)),
]

def main():
    bpy.ops.wm.open_mainfile(filepath=str(V2_BLEND))
    scene = bpy.context.scene
    c_p1 = bpy.data.collections["07_Propuesta_Primera_Planta"]
    if not bpy.data.objects.get("P1_Piso_P1_Pasillo_Huesped"):
        import bmesh
        mesh = bpy.data.meshes.new("P1_Piso_P1_Pasillo_Huesped")
        obj = bpy.data.objects.new("P1_Piso_P1_Pasillo_Huesped", mesh)
        c_p1.objects.link(obj)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x = v.co.x * 0.95 + 2.625
            v.co.y = v.co.y * 1.40 + 7.35
            v.co.z = v.co.z * 0.04 + 0.02
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()
        obj.data.materials.append(bpy.data.materials["MAT_porcelanato_ext"])

    closet_v = bpy.data.objects.get("P2_Mob_Closet_Vestidor")
    if closet_v:
        for v in closet_v.data.vertices:
            if v.co.y < 3.58:
                v.co.y = 3.58
    c_rv = bpy.data.collections.get("13_Recorrido_Virtual")
    if not c_rv:
        c_rv = bpy.data.collections.new("13_Recorrido_Virtual")
        scene.collection.children.link(c_rv)

    anim_cam = bpy.data.objects.get("Cam_Recorrido_Anim")
    if not anim_cam:
        cdata = bpy.data.cameras.new("Cam_Recorrido_Anim")
        cdata.lens = 24.0
        anim_cam = bpy.data.objects.new("Cam_Recorrido_Anim", cdata)
        c_rv.objects.link(anim_cam)

    anim_cam.animation_data_clear()
    scene.frame_start = 0
    scene.frame_end = 1152
    scene.render.fps = 24
    for frame, loc, tgt in WALKTHROUGH_WAYPOINTS:
        anim_cam.location = loc
        direction = Vector(tgt) - Vector(loc)
        anim_cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        anim_cam.keyframe_insert(data_path="location", frame=frame)
        anim_cam.keyframe_insert(data_path="rotation_euler", frame=frame)

    for img in bpy.data.images:
        if img.source == "FILE" and not img.packed_file:
            p = Path(bpy.path.abspath(img.filepath))
            if p.exists():
                img.pack()

    bpy.ops.wm.save_as_mainfile(filepath=str(H6_BLEND))
    print("HITO_06_MODEL_SAVED:", str(H6_BLEND))

main()
