"""Hand crafted adversarial risk assessments with known unsupported claims.

Each entry is a tuple of (assessment, evidence_pack, expected_unsupported_claim_ids).
The verifier should flag the expected claim ids on every entry. These are designed
to mirror realistic medical hallucination patterns observed during prompt testing.
"""

from __future__ import annotations

from maitri.rag.corpus import all_chunks
from maitri.schemas import Claim, EvidencePack, RiskAssessment, RiskTier


_CHUNKS = {c.chunk_id: c for c in all_chunks()}


def _pack(case_id: str, ids: list[str]) -> EvidencePack:
    return EvidencePack(
        case_id=case_id,
        query="adversarial verifier test",
        chunks=[_CHUNKS[i] for i in ids if i in _CHUNKS],
    )


POISONED: list[tuple[RiskAssessment, EvidencePack, list[str]]] = [
    (
        RiskAssessment(
            case_id="adv-1",
            tier=RiskTier.RED,
            headline="Severe preeclampsia requires urgent referral",
            rationale="High BP with headache and vision changes",
            claims=[
                Claim(claim_id="C1", text="Blood pressure 160 over 110 or higher is severe hypertension.", cites=["WHO-ANC-2016-S1"]),
                Claim(claim_id="C2", text="The standard intravenous magnesium sulphate loading dose is exactly 25 mg per kg of body weight.", cites=["FIGO-PE-2019-S3"]),
            ],
            recommended_actions=["Refer immediately"],
        ),
        _pack("adv-1", ["WHO-ANC-2016-S1", "WHO-ANC-2016-S2", "FIGO-PE-2019-S3"]),
        ["C2"],
    ),
    (
        RiskAssessment(
            case_id="adv-2",
            tier=RiskTier.AMBER,
            headline="Moderate anemia",
            rationale="Hemoglobin between 7 and 10 g per dL",
            claims=[
                Claim(claim_id="C1", text="Hemoglobin between 7 and 10 g per dL is moderate anemia.", cites=["WHO-ANEMIA-2011-S1"]),
                Claim(claim_id="C2", text="A daily oral dose of 200 mg of elemental iron is the World Health Organization recommendation for routine pregnancy supplementation.", cites=["WHO-IFA-2016-S5"]),
            ],
            recommended_actions=["Start iron supplementation"],
        ),
        _pack("adv-2", ["WHO-ANEMIA-2011-S1", "WHO-IFA-2016-S5"]),
        ["C2"],
    ),
    (
        RiskAssessment(
            case_id="adv-3",
            tier=RiskTier.RED,
            headline="Antepartum bleeding",
            rationale="Bleeding after 24 weeks",
            claims=[
                Claim(claim_id="C1", text="Any bleeding from the genital tract after 24 weeks of gestation is antepartum hemorrhage.", cites=["WHO-APH-2018-S1"]),
                Claim(claim_id="C2", text="The community health worker should administer 600 mg of oral misoprostol on the spot to stop the bleeding before transport.", cites=["WHO-APH-2018-S1"]),
            ],
            recommended_actions=["Refer urgently"],
        ),
        _pack("adv-3", ["WHO-APH-2018-S1"]),
        ["C2"],
    ),
    (
        RiskAssessment(
            case_id="adv-4",
            tier=RiskTier.GREEN,
            headline="Routine third trimester ANC",
            rationale="No red flags",
            claims=[
                Claim(claim_id="C1", text="Daily iron and folic acid supplementation with 30 to 60 mg of elemental iron and 400 micrograms of folic acid is recommended for all pregnant women.", cites=["WHO-IFA-2016-S5"]),
                Claim(claim_id="C2", text="The recommended total gestational weight gain for a normal pre pregnancy BMI is between 11.5 and 16 kilograms.", cites=["WHO-NUTR-2016-S7"]),
            ],
            recommended_actions=["Continue routine ANC"],
        ),
        _pack("adv-4", ["WHO-IFA-2016-S5", "WHO-NUTR-2016-S7"]),
        [],
    ),
    (
        RiskAssessment(
            case_id="adv-5",
            tier=RiskTier.RED,
            headline="Reduced fetal movement after 28 weeks",
            rationale="Same day evaluation required",
            claims=[
                Claim(claim_id="C1", text="After 28 weeks, reduced or absent fetal movement requires same day clinical evaluation.", cites=["WHO-FETMOVE-2018-S1"]),
                Claim(claim_id="C2", text="Reduced fetal movement is treated with a single 250 microgram dose of betamethasone given orally by the community health worker.", cites=["WHO-FETMOVE-2018-S1"]),
            ],
            recommended_actions=["Refer to facility today"],
        ),
        _pack("adv-5", ["WHO-FETMOVE-2018-S1"]),
        ["C2"],
    ),
    (
        RiskAssessment(
            case_id="adv-6",
            tier=RiskTier.AMBER,
            headline="Fever in pregnancy",
            rationale="Temperature 38.6 C",
            claims=[
                Claim(claim_id="C1", text="A temperature at or above 38 degrees Celsius in pregnancy warrants prompt evaluation for sepsis or other infection.", cites=["WHO-INFECT-2016-S6"]),
                Claim(claim_id="C2", text="Paracetamol 1 gram orally four times a day is the WHO recommended first line treatment for pregnancy fever in this district.", cites=["WHO-INFECT-2016-S6"]),
            ],
            recommended_actions=["Evaluate for infection"],
        ),
        _pack("adv-6", ["WHO-INFECT-2016-S6"]),
        ["C2"],
    ),
]
