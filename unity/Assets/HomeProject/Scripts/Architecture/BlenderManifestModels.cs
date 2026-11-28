using System;
using System.Collections.Generic;

namespace HomeProject.Architecture
{
    [Serializable]
    public class BlenderReferenceManifest
    {
        public string blend_file;
        public List<BlenderObjectRecord> objects = new List<BlenderObjectRecord>();
    }

    [Serializable]
    public class BlenderObjectRecord
    {
        public string name;
        public List<string> collections = new List<string>();
        public float[] location_blender;
        public float[] rotation_euler_deg_blender;
        public float[] scale_blender;
        public float[] world_center_blender;
        public float[] world_min_blender;
        public float[] world_max_blender;
        public float[] size_blender;
        public int triangles;
        public List<string> materials = new List<string>();
        public bool visible_viewport;
        public bool visible_render;
    }

    [Serializable]
    public class BlenderMaterialListWrapper
    {
        public List<BlenderMaterialDetail> items = new List<BlenderMaterialDetail>();
    }

    [Serializable]
    public class BlenderMaterialDetail
    {
        public string name;
        public float[] base_color;
        public float metallic;
        public float roughness;
        public float ior;
        public float alpha;
        public float transmission;
        public float[] emission_color;
        public float emission_strength;
    }

    [Serializable]
    public class DoorPivotListWrapper
    {
        public List<DoorPivotRecord> items = new List<DoorPivotRecord>();
    }

    [Serializable]
    public class DoorPivotRecord
    {
        public string name;
        public float[] pivot_location_m;
        public float[] dimensions_m;
    }
}
