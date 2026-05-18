"""Gradio interface for the seven agent pipeline.

The Run Maitri button drives a streaming handler. Each agent phase yields a
partial UI update so the verifier rejection moment is visible the instant it
happens, not at the end of the full run.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Any

_SRC = Path(__file__).resolve().parent / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import gradio as gr  # noqa: E402

from maitri.gemma_client import GemmaClient  # noqa: E402
from maitri.orchestrator import CaseTrace, Orchestrator  # noqa: E402


DEFAULT_NOTE = (
    "32 year old woman, second pregnancy, about 30 weeks. "
    "Severe persistent headache for 24 hours, blurred vision, swelling of the face. "
    "Blood pressure today 168 over 112. No active bleeding. "
    "Speaks Hindi. From Saharsa block. LMP 2025-10-22."
)


_TIER_COLOR = {"green": "#1b7a3e", "amber": "#b07c00", "red": "#b00020"}
_NEUTRAL = "<em style='color:#888'>pending</em>"


def _tier_html(tier: str | None) -> str:
    if not tier:
        return _NEUTRAL
    color = _TIER_COLOR.get(tier, "#444")
    return (
        f"<div style='padding:14px 18px;border-radius:12px;background:{color};"
        f"color:white;font-weight:600;font-size:20px;letter-spacing:0.04em;"
        f"text-transform:uppercase'>Tier {tier}</div>"
    )


def _verifier_banner(accepted: bool | None, claim_ids: list[str] | None, rationale: str) -> str:
    if accepted is None:
        return _NEUTRAL
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
        f"{', '.join(claim_ids or []) or 'unspecified'}<br/>"
        f"<span style='font-weight:400'>{rationale}</span></div>"
    )


def _format_claims(claims: list[dict] | None) -> str:
    if claims is None:
        return _NEUTRAL
    if not claims:
        return "<em>No claims produced.</em>"
    rows = []
    for c in claims:
        rows.append(
            "<div style='margin:8px 0;padding:10px;border-left:3px solid #444;background:#f6f6f6'>"
            f"<div style='font-size:12px;color:#666'>{c.get('claim_id','?')} cites "
            f"{', '.join(c.get('cites', []) or [])}</div>"
            f"<div>{c.get('text','')}</div></div>"
        )
    return "\n".join(rows)


def _format_referral(referral: dict[str, Any] | None) -> str:
    if not referral:
        return _NEUTRAL
    return (
        "<div style='padding:16px;border:1px solid #ddd;border-radius:12px'>"
        "<h3 style='margin:0 0 8px'>Referral Packet</h3>"
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


def _format_audit(trace: CaseTrace) -> str:
    timings = trace.timings_ms or {}
    rows = "".join(f"<tr><td>{k}</td><td>{v} ms</td></tr>" for k, v in timings.items())
    timings_table = (
        "<table style='border-collapse:collapse;font-family:monospace;font-size:12px'>"
        "<thead><tr><th style='text-align:left;padding-right:18px'>phase</th><th>latency</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    ) if rows else _NEUTRAL
    return (
        "<div style='padding:12px;border:1px solid #ddd;border-radius:10px;font-family:monospace;font-size:12px'>"
        f"<div><b>Case id:</b> {trace.case_id}</div>"
        f"<div><b>Current phase:</b> {trace.phase}</div>"
        f"<div><b>Audit calls logged:</b> {len(trace.audit_call_ids)}</div>"
        f"<div><b>Safety rules fired:</b> {', '.join(trace.safety_rule_ids) or 'none'}</div>"
        f"<div><b>Notes:</b> {', '.join(trace.notes) or 'none'}</div>"
        f"<div style='margin-top:8px'>{timings_table}</div>"
        "</div>"
    )


def _render(trace: CaseTrace) -> tuple[str, ...]:
    initial = trace.initial_assessment
    revised = trace.revised_assessment
    final = trace.final_assessment
    first = trace.first_verdict
    referral = trace.referral
    formatted = trace.deliverable.formatted if trace.deliverable else None

    final_tier = (final or initial).tier.value if (final or initial) else None
    headline = (final or initial).headline if (final or initial) else ""
    tier_html = _tier_html(final_tier) + (f"<div style='font-size:18px;margin-top:8px'><b>{headline}</b></div>" if headline else "")

    initial_claims_html = _format_claims(
        [c.model_dump() for c in initial.claims] if initial else None
    )

    banner_html = _verifier_banner(
        accepted=first.accepted if first else None,
        claim_ids=first.unsupported_claim_ids if first else None,
        rationale=first.rationale if first else "",
    )

    optimizer_text = trace.optimizer_hint
    if optimizer_text:
        optimizer_html = (
            "<div style='padding:10px;background:#fffbe6;border-left:3px solid #b07c00'>"
            f"<b>Optimizer hint to specialist:</b><br/>{optimizer_text}</div>"
        )
    elif first and first.accepted:
        optimizer_html = "<em style='color:#888'>No rewrite was needed.</em>"
    else:
        optimizer_html = _NEUTRAL

    final_source = revised if revised else (final if final else None)
    final_claims_html = _format_claims(
        [c.model_dump() for c in final_source.claims] if final_source else None
    )

    referral_html = _format_referral(referral.model_dump() if referral else None)

    chw = formatted.chw_card_en if formatted else ""
    if formatted:
        family_combo = f"माँ के लिए:\n{formatted.mother_message_hi}\n\nपरिवार के लिए:\n{formatted.family_message_hi}"
    else:
        family_combo = ""

    audit_html = _format_audit(trace)

    return (
        tier_html or _NEUTRAL,
        initial_claims_html,
        banner_html,
        optimizer_html,
        final_claims_html,
        referral_html,
        chw,
        family_combo,
        audit_html,
    )


def _run_streaming(
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
):
    structured: dict[str, Any] = {
        "age_years": int(age) if age else None,
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
    for trace in orch.run_streaming(
        raw_text=raw_text,
        structured={k: v for k, v in structured.items() if v not in (None, "")},
        force_demo_hallucination=force_demo_hallucination,
    ):
        yield _render(trace)


def _prewarm_in_background() -> None:
    def _go() -> None:
        try:
            with GemmaClient() as client:
                client.chat(
                    messages=[{"role": "user", "content": "ping"}],
                    agent="prewarm",
                    temperature=0.0,
                    max_tokens=2,
                )
        except Exception:  # noqa: BLE001 -- prewarm must never block startup
            pass

    threading.Thread(target=_go, daemon=True).start()


def build_app() -> gr.Blocks:
    with gr.Blocks(title="Maitri maternal referral co pilot", theme=gr.themes.Soft()) as demo:
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
                raw_text = gr.Textbox(
                    label="Free text from the community health worker",
                    value=DEFAULT_NOTE,
                    lines=5,
                )
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
                gr.Markdown("### Audit summary with per agent latency")
                audit_out = gr.HTML()

        run_btn.click(
            _run_streaming,
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
    _prewarm_in_background()
    build_app().launch(server_name="0.0.0.0", server_port=7860, share=False)
