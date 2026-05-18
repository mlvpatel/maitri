"""JSON schemas for Gemma 4 native function calling and a dispatcher."""

from __future__ import annotations

from typing import Any, Callable

from .climate_query import query_climate_risk
from .drug_safety import lookup_drug_safety_in_pregnancy
from .facility_lookup import lookup_facility_readiness
from .gestational_age import compute_gestational_age
from .transport_cost import estimate_transport_cost
from .voucher_check import check_voucher_eligibility


SPECIALIST_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "compute_gestational_age",
            "description": "Compute weeks plus days since LMP and the trimester.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lmp_date_iso": {"type": "string", "description": "ISO date of last menstrual period"},
                    "today_iso": {"type": "string", "description": "Optional reference date"},
                },
                "required": ["lmp_date_iso"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_climate_risk",
            "description": "Return current climate and disease risk for a geography and week.",
            "parameters": {
                "type": "object",
                "properties": {
                    "geo": {"type": "string"},
                    "week": {"type": "integer"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_drug_safety_in_pregnancy",
            "description": "Return pregnancy category and advice for a drug.",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string"},
                },
                "required": ["drug_name"],
            },
        },
    },
]


REFERRAL_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "lookup_facility_readiness",
            "description": "List facilities matching the required maternal care capabilities sorted by distance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "capability_required": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Capabilities such as maternal_emergency, obstetric_surgery, ultrasound, blood_bank.",
                    },
                    "open_only": {"type": "boolean"},
                    "exclude_high_cost": {"type": "boolean"},
                    "max_distance_km": {"type": "number"},
                },
                "required": ["capability_required"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_transport_cost",
            "description": "Estimate transport cost in INR over a road distance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "distance_km": {"type": "number"},
                    "when_iso": {"type": "string"},
                },
                "required": ["distance_km"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_voucher_eligibility",
            "description": "Return eligible Indian cash transfer schemes for the patient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "age_years": {"type": "integer"},
                    "para": {"type": "integer"},
                    "bpl_category": {"type": "boolean"},
                    "institutional_delivery": {"type": "boolean"},
                },
                "required": ["age_years", "para"],
            },
        },
    },
]


DISPATCH: dict[str, Callable[..., Any]] = {
    "compute_gestational_age": compute_gestational_age,
    "query_climate_risk": query_climate_risk,
    "lookup_drug_safety_in_pregnancy": lookup_drug_safety_in_pregnancy,
    "lookup_facility_readiness": lookup_facility_readiness,
    "estimate_transport_cost": estimate_transport_cost,
    "check_voucher_eligibility": check_voucher_eligibility,
}


def dispatch_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    fn = DISPATCH.get(name)
    if fn is None:
        return {"error": f"unknown tool: {name}"}
    try:
        result = fn(**arguments)
        return result if isinstance(result, dict) else {"result": result}
    except Exception as exc:  # noqa: BLE001 -- tool errors must not crash the agent
        return {"error": str(exc), "tool": name, "arguments": arguments}
