"""Gradio interface for the seven agent pipeline.

The verifier rejection moment is the hero visual. When the first verdict fails
the UI shows a red banner naming the unsupported claim, then displays the
optimizer hint, then the revised assessment that passed verification.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SRC = Path(__file__).resolve().parent / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import gradio as gr  # noqa: E402

from maitri.orchestrator import Orchestrator  # noqa: E402


DEFAULT_NOTE = (
    "32 year old woman, second pregnancy, about 30 weeks. "
    "Severe persistent headache for 24 hours, blurred vision, swelling of the face. "
    "Blood pressure today 168 over 112. No active bleeding. "
    "Speaks Hindi. From Saharsa block. LMP 2025-10-22."
)


_TIER_COLOR = {"green": "#1b7a3e", "amber": "#b07c00", "red": "#b00020"}


def _tier_html(tier: str) -> str:
    color = _TIER_COLOR.get(tier, "#444")
    return (
        f"<div style='padding:14px 18px;border-radius:12px;background:{color};"
        f"color:white;font-weight:600;font-size:20px;letter-spacing:0.04em;"
        f"text-transform:uppercase'>Tier {tier}</div>"
    )


def _verifier_banner(accepted: bool, claim_ids: list[str], rationale: str) -> str:
    if accepted:
        return (
            "<div style='padding:12px 16px;border-radius:10px;background:#1b7a3e;"
            "color:white;font-weight:500'>"
            "Verifier accepted the draft. All cited claims supported by evidence.</div>"
        )
    return (
        "<div style='padding:12px 16px;border-radius:10px;background:#b00020;"
        "color:white;font-weight:600;border:2px solid #ffd9df'>"
        "Verifier rejected the draft. Unsupported claims: "
        f"{', '.join(claim_ids) or 'unspecified'}<br/>"
        f"<span style='font-weight:400'>{rationale}</span></div>"
    )


def _format_claims(claims: list[dict]) -> str:
    if not claims:
        return "<em>No claims produced.</em>"
    rows = []
    for c in claims:
        rows.append(
            f"<div style='margin:8px 0;padding:10px;border-left:3px solid #444;background:#f6f6f6'>"
            f"<div style='font-size:12px;color:#666'>{c.get('claim_id','?')} cites "
            f"{', '.join(c.get('cites', []) or [])}</div>"
            f"<div>{c.get('text','')}</div></div>"
        )
    return "\n".join(rows)


def _format_referral(referral: dict[str, Any]) -> str:
    return (
        "<div style='padding:16px;border:1px solid #ddd;border-radius:12px'>"
        f"<h3 style='margin:0 0 8px'>Referral Packet</h3>"
        f"<div><b>Facility:</b> {referral.get('facility_name','')}</div>"
        f"<div><b>Distance:</b> {referral.get('facility_distance_km','')} km</div>"
        f"<div><b>Phone:</b> {referral.get('facility_phone','')}</div>"
        f"<div><b>Capabilities:</b> {', '.join(referral.get('facility_capabilities', []) or [])}</div>"
        f"<div style='margin-top:8px'><b>Transport:</b> {referral.get('transport_advice','')}</div>"
        f"<div><b>Cost:</b> {referral.get('cost_advice','')}</div>"
        f"<div><b>Voucher:</b> {referral.get('voucher_eligibility','')}</div>"
        f"<div style='margin-top:8px;font-size:12px;color:#666'>"
        f"Signed token: {referral.get('signed_token','')}</div>"
        "</div>"
    )


def _format_audit(case_id: str, audit_calls: int, notes: list[str], safety_rules: list[str]) -> str:
    return (
        "<div style='padding:12px;border:1px solid #ddd;border-radius:10px;font-family:monospace;font-size:12px'>"
        f"<div><b>Case id:</b> {case_id}</div>"
        f"<div><b>Audit calls logged:</b> {audit_calls}</div>"
        f"<div><b>Safety rules fired:</b> {', '.join(safety_rules) or 'none'}</div>"
        f"<div><b>Notes:</b> {', '.join(notes) or 'none'}</div>"
        "</div>"
    )


def _run(
    raw_text: str,
    age: int,
    systolic: int,
    diastolic: int,
    hemoglobin: float,
    severe_headache: bool,
    blurred_vision: bool,
    swelling: bool,
    bleeding: bool,
    convulsions: bool,
    fever: bool,
    reduced_fetal_movement: bool,
    lmp_date: str,
    force_demo_hallucination: bool,
) -> tuple[str, str, str, str, str, str, str, str, str]:
    structured: dict[str, Any] = {
        "age_years": int(age),
        "systolic_bp": int(systolic) if systolic else None,
        "diastolic_bp": int(diastolic) if diastolic else None,
        "hemoglobin_g_dl": float(hemoglobin) if hemoglobin else None,
        "severe_headache": bool(severe_headache),
        "blurred_vision": bool(blurred_vision),
        "swelling_face_or_hands": bool(swelling),
        "bleeding": bool(bleeding),
        "convulsions": bool(convulsions),
        "fever": bool(fever),
        "fetal_movements_normal": (None if not reduced_fetal_movement else False),
        "lmp_date": lmp_date or None,
        "language_preference": "hi",
        "district": "Saharsa",
    }
    orch = Orchestrator()
    trace = orch.run(
        raw_text=raw_text,
        structured={k: v for k, v in structured.items() if v not in (None, "")},
        force_demo_hallucination=force_demo_hallucination,
    )

    initial = trace.initial_assessment
    final = trace.final_assessment
    first = trace.first_verdict
    referral = trace.referral
    formatted = trace.deliverable.formatted if trace.deliverable else None

    tier_html = _tier_html(final.tier.value if final else "green")
    headline_html = f"<div style='font-size:18px;margin-top:8px'><b>{final.headline if final else ''}</b></div>"
    initial_claims_html = _format_claims([c.model_dump() for c in (initial.claims if initial else [])])
    banner_html = _verifier_banner(
        accepted=first.accepted if first else False,
        claim_ids=first.unsupported_claim_ids if first else [],
        rationale=first.rationale if first else "",
    )
    optimizer_hint_html = (
        f"<div style='padding:10px;background:#fffbe6;border-left:3px solid #b07c00'>"
        f"<b>Optimizer hint to specialist:</b><br/>{trace.optimizer_hint or 'No rewrite was needed.'}"
        "</div>"
    )
    final_claims_html = _format_claims([c.model_dump() for c in (final.claims if final else [])])
    referral_html = _format_referral(referral.model_dump() if referral else {})

    chw = formatted.chw_card_en if formatted else ""
    mother = formatted.mother_message_hi if formatted else ""
    family = formatted.family_message_hi if formatted else ""

    audit_html = _format_audit(
        case_id=trace.case_id,
        audit_calls=len(trace.audit_call_ids),
        notes=trace.notes,
        safety_rules=trace.safety_rule_ids,
    )

    return (
        tier_html + headline_html,
        initial_claims_html,
        banner_html,
        optimizer_hint_html,
        final_claims_html,
        referral_html,
        chw,
        f"माँ के लिए:\n{mother}\n\nपरिवार के लिए:\n{family}",
        audit_html,
    )


def build_app() -> gr.Blocks:
    with gr.Blocks(title="Maitri maternal referral co pilot") as demo:
        gr.HTML(
            "<div style='padding:14px 18px;border-radius:14px;"
            "background:linear-gradient(90deg,#0f4a3a,#1b7a3e);color:white'>"
            "<h1 style='margin:0;font-size:26px'>Maitri</h1>"
            "<div>Safety verified maternal referral co pilot, built on Gemma 4. "
            "Watch the verifier reject an unsupported claim and the system recover.</div>"
            "</div>"
        )
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Patient snapshot")
                raw_text = gr.Textbox(label="Free text from the community health worker",
                                      value=DEFAULT_NOTE, lines=5)
                with gr.Row():
                    age = gr.Number(value=32, label="Age years", precision=0)
                    systolic = gr.Number(value=168, label="Systolic BP", precision=0)
                    diastolic = gr.Number(value=112, label="Diastolic BP", precision=0)
                with gr.Row():
                    hemoglobin = gr.Number(value=10.4, label="Hemoglobin g/dL")
                    lmp = gr.Textbox(value="2025-10-22", label="LMP ISO date")
                with gr.Row():
                    severe_headache = gr.Checkbox(value=True, label="Severe headache")
                    blurred_vision = gr.Checkbox(value=True, label="Blurred vision")
                    swelling = gr.Checkbox(value=True, label="Facial swelling")
                with gr.Row():
                    bleeding = gr.Checkbox(value=False, label="Bleeding")
                    convulsions = gr.Checkbox(value=False, label="Convulsions")
                    fever = gr.Checkbox(value=False, label="Fever")
                reduced_fetal = gr.Checkbox(value=False, label="Reduced fetal movement")
                force_halluc = gr.Checkbox(
                    value=True,
                    label="Demo mode: force one unsupported claim to showcase the verifier",
                )
                run_btn = gr.Button("Run Maitri", variant="primary")

            with gr.Column(scale=2):
                tier_out = gr.HTML()
                gr.Markdown("### Specialist initial draft")
                initial_claims_out = gr.HTML()
                gr.Markdown("### Verifier")
                banner_out = gr.HTML()
                gr.Markdown("### Optimizer rewrite hint")
                optimizer_out = gr.HTML()
                gr.Markdown("### Final claims after verification")
                final_claims_out = gr.HTML()
                gr.Markdown("### Referral and Facility")
                referral_out = gr.HTML()
                gr.Markdown("### Community health worker card")
                chw_out = gr.Textbox(lines=4, show_label=False)
                gr.Markdown("### Mother and family messages")
                family_out = gr.Textbox(lines=6, show_label=False)
                gr.Markdown("### Audit summary")
                audit_out = gr.HTML()

        run_btn.click(
            _run,
            inputs=[
                raw_text, age, systolic, diastolic, hemoglobin,
                severe_headache, blurred_vision, swelling, bleeding,
                convulsions, fever, reduced_fetal, lmp, force_halluc,
            ],
            outputs=[
                tier_out, initial_claims_out, banner_out, optimizer_out,
                final_claims_out, referral_out, chw_out, family_out, audit_out,
            ],
            api_name="run",
        )
    return demo


if __name__ == "__main__":
    build_app().launch(server_name="0.0.0.0", server_port=7860, share=False, theme=gr.themes.Soft())
