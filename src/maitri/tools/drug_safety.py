"""Small pregnancy drug safety table for the demo. WHO Essential Medicines anchored."""

from __future__ import annotations


_TABLE = {
    "paracetamol": {"category": "A", "advice": "Safe at therapeutic doses."},
    "iron-folic-acid": {"category": "A", "advice": "Recommended for antenatal supplementation."},
    "methyldopa": {"category": "B", "advice": "Preferred antihypertensive in pregnancy."},
    "labetalol": {"category": "C", "advice": "Use under clinician supervision."},
    "magnesium-sulphate": {"category": "B", "advice": "First line for severe preeclampsia and eclampsia."},
    "misoprostol": {"category": "X", "advice": "Contraindicated during pregnancy except for specific obstetric indications under supervision."},
    "ibuprofen": {"category": "C-D", "advice": "Avoid in third trimester."},
    "warfarin": {"category": "X", "advice": "Contraindicated in pregnancy. Use heparin if anticoagulation needed."},
}


def lookup_drug_safety_in_pregnancy(drug_name: str) -> dict:
    key = drug_name.strip().lower().replace(" ", "-")
    info = _TABLE.get(key)
    if not info:
        return {"drug": drug_name, "category": "unknown", "advice": "No entry in local table. Consult a clinician."}
    return {"drug": drug_name, **info}
