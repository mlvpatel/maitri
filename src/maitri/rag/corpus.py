"""Minimal evidence corpus drawn from public maternal care guidelines.

Each chunk is verifiable against the cited source. Evidence is what the Verifier
checks Specialist claims against. Keeping the corpus small for the hackathon
ensures every chunk is exactly known at audit time.
"""

from __future__ import annotations

from ..schemas import EvidenceChunk


CHUNKS: list[EvidenceChunk] = [
    EvidenceChunk(
        chunk_id="WHO-ANC-2016-S1",
        source="WHO recommendations on antenatal care for a positive pregnancy experience",
        title="Severe hypertension referral",
        year=2016,
        section="Section 1.2",
        text=(
            "Blood pressure at or above 160 mmHg systolic or 110 mmHg diastolic during pregnancy "
            "should be treated as severe hypertension and the woman referred to a facility capable "
            "of obstetric emergency care."
        ),
    ),
    EvidenceChunk(
        chunk_id="WHO-ANC-2016-S2",
        source="WHO recommendations on antenatal care for a positive pregnancy experience",
        title="Pre eclampsia warning signs",
        year=2016,
        section="Section 1.3",
        text=(
            "Severe persistent headache combined with visual disturbance, right upper quadrant pain, "
            "or rapid swelling of the face and hands suggests pre eclampsia and requires immediate "
            "evaluation."
        ),
    ),
    EvidenceChunk(
        chunk_id="FIGO-PE-2019-S3",
        source="FIGO initiative on pre eclampsia",
        title="Magnesium sulphate for severe pre eclampsia",
        year=2019,
        section="Management",
        text=(
            "Magnesium sulphate remains the first line agent for prevention and treatment of "
            "eclamptic seizures in women with severe pre eclampsia. Calcium gluconate must be "
            "available as antidote."
        ),
    ),
    EvidenceChunk(
        chunk_id="WHO-ANEMIA-2011-S1",
        source="WHO hemoglobin concentrations for the diagnosis of anaemia",
        title="Severe anemia in pregnancy",
        year=2011,
        section="Table 1",
        text=(
            "Hemoglobin concentration below 7 g per dL during pregnancy is classified as severe anemia "
            "and may require transfusion. Hemoglobin between 7 and 10 g per dL is moderate anemia."
        ),
    ),
    EvidenceChunk(
        chunk_id="RMNCH-IN-2013-S4",
        source="Indian Ministry of Health Reproductive Maternal Newborn Child and Adolescent Health programme",
        title="JSY conditional cash transfer",
        year=2013,
        section="JSY scheme",
        text=(
            "Janani Suraksha Yojana provides a conditional cash incentive to pregnant women aged "
            "19 years and above on completion of an institutional delivery."
        ),
    ),
    EvidenceChunk(
        chunk_id="WHO-APH-2018-S1",
        source="WHO recommendations on antepartum hemorrhage",
        title="Antepartum bleeding",
        year=2018,
        section="Section 2.1",
        text=(
            "Any bleeding from the genital tract after 24 weeks of gestation is antepartum hemorrhage "
            "and must be evaluated urgently at a facility capable of obstetric emergency care."
        ),
    ),
    EvidenceChunk(
        chunk_id="WHO-FETMOVE-2018-S1",
        source="WHO recommendations for routine antenatal care",
        title="Reduced fetal movement",
        year=2018,
        section="Self monitoring",
        text=(
            "After 28 weeks of gestation, a perception of reduced or absent fetal movement requires "
            "same day clinical evaluation."
        ),
    ),
    EvidenceChunk(
        chunk_id="WHO-IFA-2016-S5",
        source="WHO recommendations on antenatal care for a positive pregnancy experience",
        title="Iron and folic acid supplementation",
        year=2016,
        section="Section 1.5",
        text=(
            "Daily oral iron and folic acid supplementation with 30 to 60 mg of elemental iron and "
            "400 micrograms of folic acid is recommended for all pregnant women."
        ),
    ),
    EvidenceChunk(
        chunk_id="WHO-INFECT-2016-S6",
        source="WHO recommendations on antenatal care",
        title="Fever in pregnancy",
        year=2016,
        section="Section 1.6",
        text=(
            "Temperature at or above 38 degrees Celsius in a pregnant woman warrants prompt evaluation "
            "for sepsis, urinary tract infection, malaria, and other intercurrent infections."
        ),
    ),
    EvidenceChunk(
        chunk_id="WHO-NUTR-2016-S7",
        source="WHO recommendations on antenatal care",
        title="Recommended pregnancy weight gain",
        year=2016,
        section="Section 1.4",
        text=(
            "Total recommended weight gain in pregnancy for a woman with normal pre pregnancy BMI is "
            "between 11.5 and 16 kilograms."
        ),
    ),
]


def all_chunks() -> list[EvidenceChunk]:
    return list(CHUNKS)
