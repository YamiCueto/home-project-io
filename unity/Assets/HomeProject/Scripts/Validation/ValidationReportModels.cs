using System;
using System.Collections.Generic;

namespace HomeProject.Validation
{
    [Serializable]
    public class ObjectTransformCheck
    {
        public string name;
        public string category;
        public float[] blender_size_m;
        public float[] unity_size_m;
        public float max_size_diff_m;
        public float center_pos_diff_m;
        public bool passed;
    }

    [Serializable]
    public class ExplicitExceptionRecord
    {
        public string object_name;
        public float magnitude_m;
        public string justification;
    }

    [Serializable]
    public class CapsuleSweepAudit
    {
        public string name;
        public float[] start_unity;
        public float[] end_unity;
        public float capsule_radius_m;
        public float capsule_height_m;
        public bool blocked;
        public string blocking_object;
        public bool passed;
    }

    [Serializable]
    public class FloorRaycastAudit
    {
        public string zone_name;
        public float[] origin_unity;
        public bool hit;
        public string hit_object;
        public float hit_y;
        public bool passed;
    }

    [Serializable]
    public class SceneStatistics
    {
        public int total_gameobjects;
        public int total_mesh_renderers;
        public int total_unique_meshes;
        public int total_triangles;
        public int total_unique_materials;
        public int urp_lit_materials;
        public int non_urp_materials;
        public int total_colliders;
        public int box_colliders;
        public int mesh_colliders;
        public int visible_collider_renderers;
        public int missing_mesh_references;
        public int missing_material_references;
        public int missing_expected_objects;
        public int duplicate_object_names;
    }

    [Serializable]
    public class Hito081ValidationReport
    {
        public string milestone = "Hito 8.2";
        public string unity_version;
        public string render_pipeline;
        public string scene_path;
        public float tolerance_m;
        public bool overall_passed;
        public SceneStatistics statistics = new SceneStatistics();
        public int dimensional_checks_total;
        public int dimensional_checks_passed;
        public int dimensional_checks_failed;
        public int pivot_checks_total;
        public int pivot_checks_passed;
        public int capsule_audits_total;
        public int capsule_audits_passed;
        public int floor_raycasts_total;
        public int floor_raycasts_passed;
        public List<string> missing_objects = new List<string>();
        public List<string> duplicate_names = new List<string>();
        public List<ExplicitExceptionRecord> explicit_exceptions = new List<ExplicitExceptionRecord>();
        public List<ObjectTransformCheck> failed_transforms = new List<ObjectTransformCheck>();
        public List<CapsuleSweepAudit> capsule_audits = new List<CapsuleSweepAudit>();
        public List<FloorRaycastAudit> floor_raycasts = new List<FloorRaycastAudit>();
        public List<string> errors = new List<string>();
        public List<string> warnings = new List<string>();
    }

    [Serializable]
    public class NegativeTestCaseResult
    {
        public string test_id;
        public string description;
        public bool fault_detected;
        public string detector_message;
        public bool scene_restored;
        public bool passed;
    }

    [Serializable]
    public class Hito081NegativeTestsReport
    {
        public string milestone = "Hito 8.2";
        public int total_cases;
        public int passed_cases;
        public bool all_detected;
        public List<NegativeTestCaseResult> cases = new List<NegativeTestCaseResult>();
    }
}
