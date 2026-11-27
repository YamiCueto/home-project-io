using System;
using System.Collections.Generic;

namespace HomeProject.Validation
{
    [Serializable]
    public class ObjectDimensionCheck
    {
        public string name;
        public string category;
        public float[] blender_size_m;
        public float[] unity_size_m;
        public float[] abs_diff_m;
        public float max_diff_m;
        public bool passed;
    }

    [Serializable]
    public class OpeningAuditCheck
    {
        public string name;
        public float[] center_unity;
        public float[] half_extents;
        public bool blocked_by_collider;
        public string blocking_object;
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
    }

    [Serializable]
    public class Hito081ValidationReport
    {
        public string milestone = "Hito 8.1";
        public string unity_version;
        public string render_pipeline;
        public string scene_path;
        public float tolerance_m;
        public bool overall_passed;
        public SceneStatistics statistics = new SceneStatistics();
        public int dimensional_checks_total;
        public int dimensional_checks_passed;
        public int dimensional_checks_failed;
        public int opening_audits_total;
        public int opening_audits_passed;
        public List<ObjectDimensionCheck> failed_dimensions = new List<ObjectDimensionCheck>();
        public List<ObjectDimensionCheck> sample_dimensions = new List<ObjectDimensionCheck>();
        public List<OpeningAuditCheck> opening_audits = new List<OpeningAuditCheck>();
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
        public string milestone = "Hito 8.1";
        public int total_cases;
        public int passed_cases;
        public bool all_detected;
        public List<NegativeTestCaseResult> cases = new List<NegativeTestCaseResult>();
    }
}
