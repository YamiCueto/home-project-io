using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace HomeProject.Interaction
{
    public enum AtticStairState
    {
        Closed = 0,
        Opening = 1,
        Open = 2,
        Closing = 3
    }

    public class RetractableAtticStair : MonoBehaviour
    {
        [SerializeField] private float transitionDuration = 1.15f;

        private Transform compuerta;
        private Transform cordel;
        private Transform tirador;
        private Transform tramo1;
        private Transform tramo2;
        private Transform tramo3;
        private InteractiveDoor topHatch;

        private Vector3 compuertaClosedPos;
        private Quaternion compuertaClosedRot;
        private Vector3 cordelLocalOffset;
        private Vector3 tiradorLocalOffset;

        private Vector3 tramo1ClosedPos;
        private Quaternion tramo1ClosedRot;
        private Vector3 tramo2ClosedPos;
        private Quaternion tramo2ClosedRot;
        private Vector3 tramo3ClosedPos;
        private Quaternion tramo3ClosedRot;

        private readonly List<Renderer> segmentRenderers = new List<Renderer>();
        private readonly List<Collider> segmentColliders = new List<Collider>();
        private readonly List<BoxCollider> stepColliders = new List<BoxCollider>();
        private Coroutine activeRoutine;
        private float normalizedProgress;

        public AtticStairState CurrentState { get; private set; } = AtticStairState.Closed;
        public string LastBlockedReason { get; private set; } = "";
        public float NormalizedProgress => normalizedProgress;

        private void Awake()
        {
            InitializeReferences();
            SetProgressImmediate(0f, AtticStairState.Closed);
        }

        public void InitializeReferences()
        {
            if (compuerta != null)
            {
                return;
            }

            compuerta = FindTarget("Escotilla_Techo_Compuerta");
            cordel = FindTarget("Escotilla_Techo_Cordel");
            tirador = FindTarget("Escotilla_Techo_Tirador");
            tramo1 = FindTarget("Esc_Techo_Tramo_1");
            tramo2 = FindTarget("Esc_Techo_Tramo_2");
            tramo3 = FindTarget("Esc_Techo_Tramo_3");

            GameObject hatchGo = GameObject.Find("Escotilla_Techo_Puerta1");
            if (hatchGo != null)
            {
                topHatch = hatchGo.GetComponent<InteractiveDoor>();
            }

            GameObject juntaGo = GameObject.Find("Escotilla_Techo_Junta");
            if (juntaGo != null)
            {
                Collider jc = juntaGo.GetComponent<Collider>();
                if (jc != null) jc.enabled = false;
            }

            if (compuerta != null)
            {
                compuertaClosedPos = compuerta.position;
                compuertaClosedRot = compuerta.rotation;
                if (cordel != null) cordelLocalOffset = compuerta.InverseTransformPoint(cordel.position);
                if (tirador != null) tiradorLocalOffset = compuerta.InverseTransformPoint(tirador.position);
            }

            if (tramo1 != null)
            {
                tramo1ClosedPos = tramo1.position;
                tramo1ClosedRot = tramo1.rotation;
                CollectSegmentComponents(tramo1);
            }
            if (tramo2 != null)
            {
                tramo2ClosedPos = tramo2.position;
                tramo2ClosedRot = tramo2.rotation;
                CollectSegmentComponents(tramo2);
            }
            if (tramo3 != null)
            {
                tramo3ClosedPos = tramo3.position;
                tramo3ClosedRot = tramo3.rotation;
                CollectSegmentComponents(tramo3);
            }

            if (stepColliders.Count == 0)
            {
                GameObject rampGo = new GameObject("Esc_Techo_Rampa_Collider");
                rampGo.transform.SetParent(transform, false);
                rampGo.transform.position = new Vector3(-6.30f, 4.19f, -6.20f);
                rampGo.transform.rotation = Quaternion.Euler(0f, 0f, -73.4f);
                BoxCollider ramp = rampGo.AddComponent<BoxCollider>();
                ramp.size = new Vector3(3.25f, 0.16f, 0.74f);
                stepColliders.Add(ramp);
            }
        }

        private static Transform FindTarget(string name)
        {
            GameObject go = GameObject.Find(name);
            return go != null ? go.transform : null;
        }

        private void CollectSegmentComponents(Transform root)
        {
            Renderer[] rends = root.GetComponentsInChildren<Renderer>(true);
            for (int i = 0; i < rends.Length; i++)
            {
                segmentRenderers.Add(rends[i]);
            }
            Collider[] cols = root.GetComponentsInChildren<Collider>(true);
            for (int i = 0; i < cols.Length; i++)
            {
                segmentColliders.Add(cols[i]);
            }
        }

        public bool IsPlayerOnStair()
        {
            ResidentialFirstPersonController player = Object.FindAnyObjectByType<ResidentialFirstPersonController>();
            if (player == null)
            {
                return false;
            }
            CharacterController cc = player.GetComponent<CharacterController>();
            Bounds pb = cc != null ? cc.bounds : new Bounds(player.transform.position + Vector3.up * 0.9f, new Vector3(0.6f, 1.8f, 0.6f));
            Bounds stairBounds = new Bounds(new Vector3(-5.95f, 4.50f, -6.20f), new Vector3(1.65f, 2.90f, 0.90f));
            return pb.Intersects(stairBounds);
        }

        public bool Toggle()
        {
            LastBlockedReason = "";
            if (CurrentState == AtticStairState.Closed || CurrentState == AtticStairState.Closing)
            {
                return Open();
            }
            return Close();
        }

        public bool Open()
        {
            InitializeReferences();
            LastBlockedReason = "";
            if (CurrentState == AtticStairState.Open || CurrentState == AtticStairState.Opening)
            {
                return true;
            }
            if (activeRoutine != null)
            {
                StopCoroutine(activeRoutine);
            }
            activeRoutine = StartCoroutine(AnimateTo(1f));
            return true;
        }

        public bool Close()
        {
            InitializeReferences();
            LastBlockedReason = "";
            if (IsPlayerOnStair())
            {
                LastBlockedReason = "No se puede plegar la escalera mientras el usuario esta sobre ella.";
                return false;
            }
            if ((CurrentState == AtticStairState.Closed || CurrentState == AtticStairState.Closing) && activeRoutine != null)
            {
                return true;
            }
            if (CurrentState == AtticStairState.Closed)
            {
                return true;
            }
            if (activeRoutine != null)
            {
                StopCoroutine(activeRoutine);
            }
            activeRoutine = StartCoroutine(AnimateTo(0f));
            return true;
        }

        public void SetStateImmediate(AtticStairState state)
        {
            InitializeReferences();
            if (activeRoutine != null)
            {
                StopCoroutine(activeRoutine);
                activeRoutine = null;
            }
            float p = state == AtticStairState.Open ? 1f : (state == AtticStairState.Opening ? 0.55f : (state == AtticStairState.Closing ? 0.40f : 0f));
            SetProgressImmediate(p, state);
        }

        private IEnumerator AnimateTo(float target)
        {
            bool opening = target > normalizedProgress;
            CurrentState = opening ? AtticStairState.Opening : AtticStairState.Closing;

            if (opening && topHatch != null)
            {
                topHatch.SetOpen(true, false);
            }

            float start = normalizedProgress;
            float elapsed = 0f;
            float dur = Mathf.Max(0.2f, transitionDuration * Mathf.Abs(target - start));

            while (elapsed < dur)
            {
                if (!opening && IsPlayerOnStair())
                {
                    LastBlockedReason = "Plegado detenido: usuario detectado sobre la escalera.";
                    activeRoutine = StartCoroutine(AnimateTo(1f));
                    yield break;
                }

                elapsed += Time.deltaTime;
                float u = Mathf.Clamp01(elapsed / dur);
                SetProgressImmediate(Mathf.Lerp(start, target, u), CurrentState);
                yield return null;
            }

            SetProgressImmediate(target, opening ? AtticStairState.Open : AtticStairState.Closed);
            if (!opening && topHatch != null)
            {
                topHatch.SetOpen(false, false);
            }
            activeRoutine = null;
        }

        public void SetProgressImmediate(float t, AtticStairState state)
        {
            InitializeReferences();
            normalizedProgress = Mathf.Clamp01(t);
            CurrentState = state;

            if (topHatch != null)
            {
                if (state == AtticStairState.Open || state == AtticStairState.Opening)
                {
                    if (!topHatch.IsOpen) topHatch.SetOpen(true, true);
                }
                else if (state == AtticStairState.Closed)
                {
                    if (topHatch.IsOpen) topHatch.SetOpen(false, true);
                }
            }

            float hatchFactor = Mathf.Clamp01(normalizedProgress / 0.35f);
            float stairFactor = Mathf.Clamp01((normalizedProgress - 0.20f) / 0.80f);

            if (compuerta != null)
            {
                compuerta.position = compuertaClosedPos;
                compuerta.rotation = Quaternion.AngleAxis(-88f * hatchFactor, Vector3.forward) * compuertaClosedRot;
                if (cordel != null)
                {
                    cordel.position = compuerta.TransformPoint(cordelLocalOffset);
                    cordel.rotation = Quaternion.identity;
                }
                if (tirador != null)
                {
                    tirador.position = compuerta.TransformPoint(tiradorLocalOffset);
                    tirador.rotation = Quaternion.identity;
                }
            }

            bool showStair = state != AtticStairState.Closed && stairFactor > 0.01f;
            for (int i = 0; i < segmentRenderers.Count; i++)
            {
                if (segmentRenderers[i] != null)
                {
                    segmentRenderers[i].enabled = showStair;
                }
            }
            for (int i = 0; i < segmentColliders.Count; i++)
            {
                if (segmentColliders[i] != null)
                {
                    segmentColliders[i].enabled = false;
                }
            }

            for (int i = 0; i < stepColliders.Count; i++)
            {
                if (stepColliders[i] != null)
                {
                    stepColliders[i].enabled = state == AtticStairState.Open;
                }
            }

            if (tramo1 != null && tramo2 != null && tramo3 != null)
            {
                if (!showStair)
                {
                    tramo1.position = tramo1ClosedPos;
                    tramo1.rotation = tramo1ClosedRot;
                    tramo2.position = tramo2ClosedPos;
                    tramo2.rotation = tramo2ClosedRot;
                    tramo3.position = tramo3ClosedPos;
                    tramo3.rotation = tramo3ClosedRot;
                }
                else
                {
                    float deployAngle = -52.9f * stairFactor;
                    float foldAngle2 = -232.9f * stairFactor;

                    tramo1.position = tramo1ClosedPos;
                    tramo1.rotation = Quaternion.AngleAxis(deployAngle, Vector3.forward) * tramo1ClosedRot;
                    Vector3 end1 = tramo1ClosedPos + Quaternion.AngleAxis(deployAngle, Vector3.forward) * new Vector3(1.12f, 0f, 0f);

                    tramo2.position = end1;
                    tramo2.rotation = Quaternion.AngleAxis(foldAngle2, Vector3.forward) * tramo2ClosedRot;
                    Vector3 end2 = end1 + Quaternion.AngleAxis(foldAngle2, Vector3.forward) * new Vector3(-1.12f, 0f, 0f);

                    tramo3.position = end2;
                    tramo3.rotation = Quaternion.AngleAxis(deployAngle, Vector3.forward) * tramo3ClosedRot;
                }
            }
        }
    }
}
