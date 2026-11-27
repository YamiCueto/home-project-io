using UnityEngine;

namespace HomeProject.Core
{
    public static class ResidentialZoneTracker
    {
        public static string GetZoneName(Vector3 unityPos)
        {
            float bx = -unityPos.x;
            float by = -unityPos.z;
            float bz = unityPos.y;

            if (by < 0.0f || bx < 0.0f || bx > 8.0f || by > 11.25f)
            {
                return "Exterior / Contexto Urbano";
            }

            if (bz < 2.65f)
            {
                if (by < 1.70f && bx < 4.55f) return "Acceso Peatonal";
                if (bx >= 4.55f && by <= 4.75f) return "Garaje";
                if (bx < 4.55f && by <= 4.70f) return "Sala";
                if (bx < 2.15f && by > 4.70f && by <= 6.70f) return "Bano Social";
                if (bx >= 3.10f && bx <= 6.85f && by >= 4.75f && by <= 5.75f) return "Escalera";
                if (bx < 5.65f && by > 5.75f && by <= 8.10f) return "Comedor";
                if (bx >= 5.65f && by > 5.75f && by <= 8.10f) return "Cocina";
                if (bx < 4.55f && by > 8.10f) return "Habitacion de Huespedes";
                if (bx >= 4.55f && by > 8.10f) return "Lavanderia / Patio";
                return "Primera Planta";
            }

            if (by <= 4.70f)
            {
                if (bx < 4.55f) return "Habitacion Principal";
                if (bx >= 4.55f && by < 1.50f) return "Balcon";
                if (bx >= 4.55f && bx < 6.00f) return "Vestidor";
                return "Bano Principal";
            }

            if (by <= 6.70f)
            {
                if (bx < 2.10f) return "Bano Compartido";
                return "Corredor Superior";
            }

            if (bx < 4.00f) return "Habitacion Hija 1";
            return "Habitacion Hija 2";
        }
    }
}
