import bpy
import bmesh
import math
from pathlib import Path
from mathutils import Vector


def remove_obj(name):
    obj = bpy.data.objects.get(name)
    if obj:
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data and data.users == 0:
            bpy.data.meshes.remove(data)


def get_mat(name, fallback_rgba=(0.8, 0.8, 0.8, 1.0), metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = fallback_rgba
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def make_box(name, x0, x1, y0, y1, z0, z1, mat, cols):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = [
        bm.verts.new((x0, y0, z0)),
        bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)),
        bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)),
        bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)),
        bm.verts.new((x0, y1, z1)),
    ]
    for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
        bm.faces.new([verts[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    for c in cols:
        if c and obj.name not in c.objects:
            c.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def make_sloped_rail(name, p0, p1, half_w, half_h, mat, cols):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    verts = [
        bm.verts.new((x0, y0 - half_w, z0 - half_h)),
        bm.verts.new((x0, y0 + half_w, z0 - half_h)),
        bm.verts.new((x0, y0 + half_w, z0 + half_h)),
        bm.verts.new((x0, y0 - half_w, z0 + half_h)),
        bm.verts.new((x1, y1 - half_w, z1 - half_h)),
        bm.verts.new((x1, y1 + half_w, z1 - half_h)),
        bm.verts.new((x1, y1 + half_w, z1 + half_h)),
        bm.verts.new((x1, y1 - half_w, z1 + half_h)),
    ]
    for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
        bm.faces.new([verts[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    for c in cols:
        if c and obj.name not in c.objects:
            c.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def decimate_tree_clean(src, base_name, c_urb, c_sem, loc, scl, rot_deg):
    import random
    random.seed(42)
    bm_full = bmesh.new()
    bm_full.from_mesh(src.data)
    mat_names = [m.name if m else "" for m in src.data.materials]
    leaf_mat_indices = {i for i, mn in enumerate(mat_names) if "leaves" in mn.lower()}

    for suffix, keep_prob, bark_ratio in [("_LOD0", 0.14, 0.08), ("_LOD1", 0.06, 0.03), ("_LOD2", 0.025, 0.015)]:
        bm_bark = bm_full.copy()
        del_leaves = [f for f in bm_bark.faces if f.material_index in leaf_mat_indices]
        if del_leaves:
            bmesh.ops.delete(bm_bark, geom=del_leaves, context="FACES")
        m_bark = bpy.data.meshes.new(f"_TMP_B_{base_name}{suffix}")
        bm_bark.to_mesh(m_bark)
        bm_bark.free()
        o_bark = bpy.data.objects.new(f"_TMP_B_{base_name}{suffix}", m_bark)
        for m in src.data.materials:
            o_bark.data.materials.append(m)
        c_urb.objects.link(o_bark)
        mod = o_bark.modifiers.new("Decimate", "DECIMATE")
        mod.ratio = bark_ratio
        with bpy.context.temp_override(object=o_bark, active_object=o_bark, selected_objects=[o_bark]):
            bpy.ops.object.modifier_apply(modifier="Decimate")

        bm_leaf = bm_full.copy()
        del_non_leaf = [f for f in bm_leaf.faces if f.material_index not in leaf_mat_indices]
        if del_non_leaf:
            bmesh.ops.delete(bm_leaf, geom=del_non_leaf, context="FACES")
        drop_faces = [f for f in bm_leaf.faces if random.random() > keep_prob]
        if drop_faces:
            bmesh.ops.delete(bm_leaf, geom=drop_faces, context="FACES")
        bm_join = bmesh.new()
        bm_join.from_mesh(o_bark.data)
        m_leaf_tmp = bpy.data.meshes.new("_TMP_L")
        bm_leaf.to_mesh(m_leaf_tmp)
        bm_leaf.free()
        bm_join.from_mesh(m_leaf_tmp)
        bpy.data.meshes.remove(m_leaf_tmp)

        m_final = bpy.data.meshes.new(base_name + suffix)
        bm_join.to_mesh(m_final)
        bm_join.free()
        obj = bpy.data.objects.new(base_name + suffix, m_final)
        for m in src.data.materials:
            obj.data.materials.append(m)
        c_urb.objects.link(obj)
        if obj.name not in c_sem.objects:
            c_sem.objects.link(obj)
        obj.location = Vector(loc)
        obj.scale = Vector((scl, scl, scl))
        obj.rotation_euler = (0.0, 0.0, math.radians(rot_deg))
        remove_obj(o_bark.name)

    bm_full.free()


def build_tropical_trees(root):
    for n in ["Arbol_Urbano_Copa_1", "Arbol_Urbano_Copa_2", "Arbol_Urbano_Tronco_1", "Arbol_Urbano_Tronco_2"]:
        remove_obj(n)
    for o in list(bpy.data.objects):
        if o.name.startswith("Arbol_Tropical_"):
            remove_obj(o.name)

    cache = root / "models" / "_polyhaven_trees_cache.blend"
    with bpy.data.libraries.load(str(cache), link=False) as (data_from, data_to):
        data_to.objects = [n for n in data_from.objects if n in ("tree_small_02_LOD0", "island_tree_02_LOD0")]

    c_urb = bpy.data.collections.get("17_Contexto_Urbano") or bpy.context.scene.collection
    c_sem = bpy.data.collections.get("Contexto_Urbano") or bpy.context.scene.collection

    specs = [
        ("Arbol_Tropical_01", "tree_small_02_LOD0", (-2.05, -1.15, 0.0), 0.92, 18.0),
        ("Arbol_Tropical_02", "island_tree_02_LOD0", (10.25, 10.95, 0.0), 0.88, 135.0),
        ("Arbol_Tropical_03", "tree_small_02_LOD0", (9.15, 4.40, 0.0), 0.72, -72.0),
    ]

    for base_name, src_name, loc, scl, rot_deg in specs:
        src = bpy.data.objects.get(src_name)
        if src:
            decimate_tree_clean(src, base_name, c_urb, c_sem, loc, scl, rot_deg)

    for o in list(bpy.data.objects):
        if o.name.startswith("_TMP_") or o.name in ("tree_small_02_LOD0", "island_tree_02_LOD0"):
            remove_obj(o.name)


def make_local_box(mesh_name, obj_name, origin, x0, x1, y0, y1, z0, z1, mat, cols):
    mesh = bpy.data.meshes.new(mesh_name)
    bm = bmesh.new()
    verts = [
        bm.verts.new((x0, y0, z0)),
        bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)),
        bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)),
        bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)),
        bm.verts.new((x0, y1, z1)),
    ]
    for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
        bm.faces.new([verts[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(obj_name, mesh)
    obj.location = origin
    for c in cols:
        if c and obj.name not in c.objects:
            c.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def make_stair_segment(name, origin, length_dir, mat_rail, mat_tread, mat_hinge, cols):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    L = 1.12 * length_dir
    x_a, x_b = (0.0, L) if length_dir < 0 else (0.0, L)
    x_min, x_max = min(x_a, x_b), max(x_a, x_b)

    def add_bm_box(bx0, bx1, by0, by1, bz0, bz1, mat_idx):
        v = [
            bm.verts.new((bx0, by0, bz0)),
            bm.verts.new((bx1, by0, bz0)),
            bm.verts.new((bx1, by1, bz0)),
            bm.verts.new((bx0, by1, bz0)),
            bm.verts.new((bx0, by0, bz1)),
            bm.verts.new((bx1, by0, bz1)),
            bm.verts.new((bx1, by1, bz1)),
            bm.verts.new((bx0, by1, bz1)),
        ]
        for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
            face = bm.faces.new([v[i] for i in f])
            face.material_index = mat_idx

    add_bm_box(x_min, x_max, -0.27, -0.24, -0.025, 0.025, 0)
    add_bm_box(x_min, x_max, 0.24, 0.27, -0.025, 0.025, 0)
    for k in range(4):
        tx = (0.14 + k * 0.26) * length_dir
        tx0, tx1 = min(tx - 0.045, tx + 0.045), max(tx - 0.045, tx + 0.045)
        add_bm_box(tx0, tx1, -0.24, 0.24, -0.015, 0.015, 1)
    add_bm_box(-0.025, 0.025, -0.275, -0.235, -0.03, 0.03, 2)
    add_bm_box(-0.025, 0.025, 0.235, 0.275, -0.03, 0.03, 2)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = origin
    for c in cols:
        if c and obj.name not in c.objects:
            c.objects.link(obj)
    obj.data.materials.append(mat_rail)
    obj.data.materials.append(mat_tread)
    obj.data.materials.append(mat_hinge)
    return obj


def build_p2_rooftop_access():
    c_p2 = bpy.data.collections.get("08_Propuesta_Segunda_Planta") or bpy.context.scene.collection
    c_arch = bpy.data.collections.get("Arquitectura") or bpy.context.scene.collection
    c_doors = bpy.data.collections.get("Puertas_Y_Ventanas") or bpy.context.scene.collection

    m_concreto = get_mat("MAT_hormigon", (0.68, 0.68, 0.66, 1.0), 0.0, 0.8)
    m_imp = get_mat("MAT_impermeabilizante", (0.28, 0.30, 0.32, 1.0), 0.05, 0.72)
    m_alum = get_mat("MAT_aluminio", (0.76, 0.78, 0.80, 1.0), 0.85, 0.25)
    m_negro = get_mat("MAT_aluminio_negro", (0.10, 0.11, 0.12, 1.0), 0.5, 0.4)
    m_acero = get_mat("MAT_acero_tecnico", (0.42, 0.45, 0.48, 1.0), 0.75, 0.35)

    remove_obj("Zona_Paneles_Solares_Base")
    make_box("Zona_Paneles_Solares_Base", 1.20, 6.60, 2.20, 5.50, 5.88, 5.94, m_imp, [c_p2, c_arch])
    remove_obj("Solar_Canalizacion")
    c_inst = bpy.data.collections.get("Instalaciones")
    make_box("Solar_Canalizacion", 5.15, 5.23, 4.00, 9.75, 5.88, 5.94, m_alum, [c_p2, c_inst] if c_inst else [c_p2])
    remove_obj("Inst_Zona_Ampliacion_Solar")
    m_zona_amp = bpy.data.materials.get("MAT_zona_ampliacion") or m_imp
    make_box("Inst_Zona_Ampliacion_Solar", 1.20, 5.70, 6.25, 8.20, 5.88, 5.94, m_zona_amp, [c_p2, c_inst] if c_inst else [c_p2])

    for n in [
        "Cubierta_Plana_Superior", "Cubierta_Pendiente_Drenaje",
        "Escotilla_Techo_Marco", "Escotilla_Techo_Puerta1", "Escotilla_Techo_Cierre",
        "Escotilla_Techo_Junta", "Escotilla_Techo_Compuerta", "Escotilla_Techo_Cordel", "Escotilla_Techo_Tirador",
        "Esc_Techo_Tramo_1", "Esc_Techo_Tramo_2", "Esc_Techo_Tramo_3",
        "Esc_Techo_Baranda_Norte", "Esc_Techo_Baranda_Sur",
        "Cubierta_Canal_Drenaje", "Cubierta_Sumidero_NE",
        "Cubierta_Solapa_Oeste", "Cubierta_Solapa_Este", "Cubierta_Solapa_Sur", "Cubierta_Solapa_Norte",
        "Baranda_Cubierta_Sur", "Baranda_Cubierta_Norte", "Baranda_Cubierta_Este", "Baranda_Cubierta_Oeste",
        "Baranda_Escotilla_Oeste", "Baranda_Escotilla_Sur", "Baranda_Escotilla_Norte", "Baranda_Escotilla_Este", "Cubierta_Descanso_Escotilla",
        "P2_M_Corredor_Norte_Ret", "P2_Piso_P2_Bypass_Esc_Techo",
    ]:
        remove_obj(n)
    for o in list(bpy.data.objects):
        if o.name.startswith(("Cubierta_Plana_Seg_", "Cubierta_Pend_Seg_", "Esc_Techo_Peldano_")):
            remove_obj(o.name)

    ox0, ox1, oy0, oy1 = 5.45, 6.75, 5.80, 6.60

    make_box("Cubierta_Plana_Seg_Oeste", 0.0, ox0, 0.0, 10.0, 5.60, 5.80, m_concreto, [c_p2, c_arch])
    make_box("Cubierta_Plana_Seg_Este", ox1, 8.0, 0.0, 10.0, 5.60, 5.80, m_concreto, [c_p2, c_arch])
    make_box("Cubierta_Plana_Seg_Sur", ox0, ox1, 0.0, oy0, 5.60, 5.80, m_concreto, [c_p2, c_arch])
    make_box("Cubierta_Plana_Seg_Norte", ox0, ox1, oy1, 10.0, 5.60, 5.80, m_concreto, [c_p2, c_arch])

    make_box("Cubierta_Pend_Seg_Oeste", 0.15, ox0, 0.15, 9.85, 5.80, 5.88, m_imp, [c_p2, c_arch])
    make_box("Cubierta_Pend_Seg_Este", ox1, 7.85, 0.15, 9.85, 5.80, 5.88, m_imp, [c_p2, c_arch])
    make_box("Cubierta_Pend_Seg_Sur", ox0, ox1, 0.15, oy0, 5.80, 5.88, m_imp, [c_p2, c_arch])
    make_box("Cubierta_Pend_Seg_Norte", ox0, ox1, oy1, 9.85, 5.80, 5.88, m_imp, [c_p2, c_arch])

    make_box("Cubierta_Canal_Drenaje", 7.60, 7.85, 0.25, 9.75, 5.86, 5.89, m_negro, [c_p2, c_arch])
    make_box("Cubierta_Sumidero_NE", 7.62, 7.84, 9.55, 9.80, 5.84, 5.90, m_alum, [c_p2, c_arch])
    make_box("Cubierta_Solapa_Oeste", 0.15, 0.22, 0.15, 9.85, 5.88, 5.96, m_negro, [c_p2, c_arch])
    make_box("Cubierta_Solapa_Este", 7.78, 7.85, 0.15, 9.85, 5.88, 5.96, m_negro, [c_p2, c_arch])
    make_box("Cubierta_Solapa_Sur", 0.15, 7.85, 0.15, 0.22, 5.88, 5.96, m_negro, [c_p2, c_arch])
    make_box("Cubierta_Solapa_Norte", 0.15, 7.85, 9.78, 9.85, 5.88, 5.96, m_negro, [c_p2, c_arch])

    mesh_marco = bpy.data.meshes.new("Escotilla_Techo_Marco")
    bm_m = bmesh.new()
    for bx0, bx1, by0, by1 in [
        (ox0 - 0.06, ox0, oy0 - 0.06, oy1 + 0.06),
        (ox1, ox1 + 0.06, oy0 - 0.06, oy1 + 0.06),
        (ox0, ox1, oy0 - 0.06, oy0),
        (ox0, ox1, oy1, oy1 + 0.06),
    ]:
        mv = [
            bm_m.verts.new((bx0, by0, 5.88)),
            bm_m.verts.new((bx1, by0, 5.88)),
            bm_m.verts.new((bx1, by1, 5.88)),
            bm_m.verts.new((bx0, by1, 5.88)),
            bm_m.verts.new((bx0, by0, 6.03)),
            bm_m.verts.new((bx1, by0, 6.03)),
            bm_m.verts.new((bx1, by1, 6.03)),
            bm_m.verts.new((bx0, by1, 6.03)),
        ]
        for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
            bm_m.faces.new([mv[i] for i in f])
    bmesh.ops.recalc_face_normals(bm_m, faces=bm_m.faces)
    bm_m.to_mesh(mesh_marco)
    bm_m.free()
    marco = bpy.data.objects.new("Escotilla_Techo_Marco", mesh_marco)
    c_p2.objects.link(marco)
    c_arch.objects.link(marco)
    marco.data.materials.append(m_negro)

    make_box("Escotilla_Techo_Junta", ox0 - 0.03, ox1 + 0.03, oy0 - 0.03, oy1 + 0.03, 6.02, 6.04, m_negro, [c_p2, c_arch])
    mesh_lid = bpy.data.meshes.new("Escotilla_Techo_Puerta1")
    bm = bmesh.new()
    verts = [
        bm.verts.new((-0.03, -(oy1 - oy0) - 0.06, -0.02)),
        bm.verts.new((ox1 - ox0 + 0.03, -(oy1 - oy0) - 0.06, -0.02)),
        bm.verts.new((ox1 - ox0 + 0.03, 0.03, -0.02)),
        bm.verts.new((-0.03, 0.03, -0.02)),
        bm.verts.new((-0.03, -(oy1 - oy0) - 0.06, 0.04)),
        bm.verts.new((ox1 - ox0 + 0.03, -(oy1 - oy0) - 0.06, 0.04)),
        bm.verts.new((ox1 - ox0 + 0.03, 0.03, 0.04)),
        bm.verts.new((-0.03, 0.03, 0.04)),
    ]
    for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
        bm.faces.new([verts[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh_lid)
    bm.free()
    lid = bpy.data.objects.new("Escotilla_Techo_Puerta1", mesh_lid)
    c_p2.objects.link(lid)
    c_doors.objects.link(lid)
    lid.location = (ox0, oy1, 6.04)
    lid.data.materials.append(m_alum)
    make_box("Escotilla_Techo_Cierre", ox0 + 0.05, ox0 + 0.25, oy0 - 0.04, oy0 + 0.02, 5.96, 6.05, m_acero, [c_p2, c_arch])

    m_techo = bpy.data.materials.get("MAT_blanco_calido") or m_concreto
    make_local_box("Escotilla_Techo_Compuerta", "Escotilla_Techo_Compuerta", (6.73, 6.20, 5.60), -1.26, 0.0, -0.38, 0.38, -0.02, 0.02, m_techo, [c_p2, c_arch])
    make_local_box("Escotilla_Techo_Cordel", "Escotilla_Techo_Cordel", (5.58, 6.20, 5.58), -0.008, 0.008, -0.008, 0.008, -0.90, 0.0, m_negro, [c_p2, c_arch])
    make_local_box("Escotilla_Techo_Tirador", "Escotilla_Techo_Tirador", (5.58, 6.20, 4.65), -0.03, 0.03, -0.015, 0.015, -0.03, 0.03, m_alum, [c_p2, c_arch])

    make_stair_segment("Esc_Techo_Tramo_1", (6.70, 6.20, 5.64), -1.0, m_alum, m_acero, m_negro, [c_p2, c_arch])
    make_stair_segment("Esc_Techo_Tramo_2", (5.58, 6.20, 5.71), 1.0, m_alum, m_acero, m_negro, [c_p2, c_arch])
    make_stair_segment("Esc_Techo_Tramo_3", (6.70, 6.20, 5.78), -1.0, m_alum, m_acero, m_negro, [c_p2, c_arch])

    make_box("Baranda_Cubierta_Sur", 0.05, 7.95, 0.05, 0.10, 6.88, 6.94, m_negro, [c_p2, c_arch])
    make_box("Baranda_Cubierta_Norte", 0.05, 7.95, 9.90, 9.95, 6.88, 6.94, m_negro, [c_p2, c_arch])
    make_box("Baranda_Cubierta_Oeste", 0.05, 0.10, 0.10, 9.90, 6.88, 6.94, m_negro, [c_p2, c_arch])
    make_box("Baranda_Cubierta_Este", 7.90, 7.95, 0.10, 9.90, 6.88, 6.94, m_negro, [c_p2, c_arch])
    for idx, (px, py) in enumerate([(0.08, 0.08), (4.0, 0.08), (7.92, 0.08), (0.08, 5.0), (7.92, 5.0), (0.08, 9.92), (4.0, 9.92), (7.92, 9.92)], 1):
        make_box(f"Baranda_Cubierta_Poste_{idx:02d}", px - 0.025, px + 0.025, py - 0.025, py + 0.025, 6.35, 6.90, m_negro, [c_p2, c_arch])

    make_box("Baranda_Escotilla_Oeste", ox0 - 0.08, ox0 - 0.03, oy0 - 0.08, oy1 + 0.08, 6.85, 6.91, m_negro, [c_p2, c_arch])
    make_box("Baranda_Escotilla_Este", ox1 + 0.03, ox1 + 0.08, oy0 - 0.08, oy1 + 0.08, 6.85, 6.91, m_negro, [c_p2, c_arch])
    make_box("Baranda_Escotilla_Norte", ox0 - 0.03, ox1 + 0.08, oy1 + 0.03, oy1 + 0.08, 6.85, 6.91, m_negro, [c_p2, c_arch])
    for idx, (px, py) in enumerate([(ox0 - 0.055, oy0 - 0.055), (ox0 - 0.055, oy1 + 0.055), (ox1 + 0.055, oy0 - 0.055), (ox1 + 0.055, oy1 + 0.055)], 1):
        make_box(f"Baranda_Escotilla_Poste_{idx:02d}", px - 0.025, px + 0.025, py - 0.025, py + 0.025, 5.88, 6.90, m_negro, [c_p2, c_arch])

    c_inst = bpy.data.collections.get("Instalaciones")
    for o in bpy.data.objects:
        if o.type == "MESH" and ("Solar" in o.name):
            if c_inst and o.name in c_inst.objects:
                c_inst.objects.unlink(o)
            if o.name not in c_arch.objects:
                c_arch.objects.link(o)
            o.hide_viewport = False
            o.hide_render = False


def main():
    root = Path(r"C:\Users\YAMI\Documents\projects\home-project")
    src = root / "models" / "HOME_PROJECT_HITO_08_3_2.blend"
    dst = root / "models" / "HOME_PROJECT_HITO_08_3_3.blend"

    bpy.ops.wm.open_mainfile(filepath=str(src))
    build_tropical_trees(root)
    build_p2_rooftop_access()
    bpy.ops.wm.save_as_mainfile(filepath=str(dst))
    print(f"HITO_08_3_3_SAVED: {dst}")


if __name__ == "__main__":
    main()
