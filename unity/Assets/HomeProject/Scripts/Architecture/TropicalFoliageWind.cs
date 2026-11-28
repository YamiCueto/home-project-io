using UnityEngine;

namespace HomeProject.Architecture
{
    public class TropicalFoliageWind : MonoBehaviour
    {
        [SerializeField] private float swayAmplitudeDegrees = 1.35f;
        [SerializeField] private float swaySpeed = 1.45f;

        private Transform[] targets;
        private Quaternion[] baseRotations;
        private float phaseOffset;

        private void Awake()
        {
            phaseOffset = (transform.position.x * 0.73f) + (transform.position.z * 0.41f);
            int childCount = transform.childCount;
            if (childCount > 0)
            {
                targets = new Transform[childCount];
                baseRotations = new Quaternion[childCount];
                for (int i = 0; i < childCount; i++)
                {
                    targets[i] = transform.GetChild(i);
                    baseRotations[i] = targets[i].localRotation;
                }
            }
            else
            {
                targets = new[] { transform };
                baseRotations = new[] { transform.localRotation };
            }
        }

        private void Update()
        {
            float t = Time.time * swaySpeed + phaseOffset;
            float angleX = Mathf.Sin(t) * swayAmplitudeDegrees + Mathf.Sin(t * 2.13f) * (swayAmplitudeDegrees * 0.35f);
            float angleZ = Mathf.Cos(t * 0.87f) * swayAmplitudeDegrees + Mathf.Cos(t * 1.91f) * (swayAmplitudeDegrees * 0.30f);
            Quaternion sway = Quaternion.Euler(angleX, 0f, angleZ);

            for (int i = 0; i < targets.Length; i++)
            {
                if (targets[i] != null)
                {
                    targets[i].localRotation = baseRotations[i] * sway;
                }
            }
        }
    }
}
