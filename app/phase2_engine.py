from __future__ import annotations

from typing import Any

from app import base_engine as _base
from app.phase2_models import PatientProfile

PHENOTYPE_DEFINITIONS = {
    "hungry_brain": {
        "name": "Hungry brain",
        "clinical_label": "Reduced satiation / meal termination",
        "core": ["hb_recognise_enough", "hb_large_portion_needed", "hb_second_serving"],
        "followup": ["hb_continue_after_hunger", "hb_food_gone"],
        "summary": "A higher current questionnaire signal suggests that larger portions or more eating time may be needed before comfortable satisfaction is recognised.",
        "actions": [
            "Pre-plate the planned portion and keep serving dishes off the table.",
            "Begin with protein and high-volume vegetables, then pause before seconds.",
            "Use slower meal pacing and a deliberate meal-ending cue.",
            "Review response to appetite-modifying medication rather than relying on willpower alone.",
        ],
    },
    "hungry_gut": {
        "name": "Hungry gut",
        "clinical_label": "Reduced duration of satiety",
        "core": ["hg_hunger_returns", "hg_grazing_needed", "hg_late_hunger"],
        "followup": ["hg_meal_not_hold", "hg_fullness_fades"],
        "summary": "A higher current questionnaire signal suggests that an adequate meal may not sustain physical satiety until the next planned eating occasion.",
        "actions": [
            "Build each meal around protein, fibre-rich foods, vegetables and measured healthy fat.",
            "Use regular meal timing and a planned high-protein bridge snack when clinically appropriate.",
            "Avoid long unplanned fasting periods that predictably amplify late-day hunger.",
            "Review rapid return of hunger, gastrointestinal symptoms and medication timing clinically.",
        ],
    },
    "emotional_hunger": {
        "name": "Emotional hunger",
        "clinical_label": "Hedonic, cue-driven and emotional eating",
        "core": ["eh_emotional_eating", "eh_environment_cues", "eh_strong_cravings"],
        "followup": ["eh_food_reward", "eh_loss_control"],
        "summary": "A higher current questionnaire signal suggests that emotion, reward and environmental cues may drive eating independently of physical hunger.",
        "actions": [
            "Map the trigger, emotion, usual food and consequence for recurring episodes.",
            "Use an urge-delay strategy and a pre-selected alternative response.",
            "Change the environment around television, alcohol, takeaway apps and trigger foods.",
            "Consider psychological or eating-behaviour support when episodes are frequent or distressing.",
        ],
    },
    "slow_burn": {
        "name": "Slow burn",
        "clinical_label": "Reduced energy-expenditure questionnaire signal",
        "core": ["sb_sedentary_time", "sb_low_incidental_movement", "sb_fatigue_limits_activity"],
        "followup": ["sb_strength_limits_activity", "sb_no_resistance_training"],
        "summary": "A higher questionnaire signal suggests that low movement, limited strength or reduced muscle stimulus may be important barriers; it does not establish low resting energy expenditure.",
        "actions": [
            "Progress daily movement from the measured or estimated baseline.",
            "Add progressive resistance training scaled to current capacity and medical status.",
            "Protect protein intake and lean mass while avoiding unnecessarily aggressive restriction.",
            "Consider objective assessment when the result would change clinical management.",
        ],
    },
}

APPETITE_MODIFYING_MEDICATIONS = {
    "mounjaro", "wegovy", "ozempic", "saxenda", "phentermine", "duromine", "topiramate"
}


def _followup_triggered(core_values: list[int]) -> bool:
    return sum(core_values) >= 5 or any(value >= 3 for value in core_values)


def _slow_burn_evidence(profile: PatientProfile) -> tuple[str, str, list[str]]:
    support: list[str] = []
    if profile.average_daily_steps:
        support.append(f"Average steps: {profile.average_daily_steps:,}/day")
    if profile.resistance_training_sessions is not None:
        support.append(f"Resistance training: {profile.resistance_training_sessions}/week")
    if profile.body_composition_summary:
        support.append("Body-composition information recorded")
    if profile.grip_strength_value is not None:
        support.append(f"Grip strength: {profile.grip_strength_value:g} {profile.grip_strength_units}")
    if profile.occupational_activity not in {"", "Not recorded"}:
        support.append(f"Occupational activity: {profile.occupational_activity}")
    if profile.prolonged_inactivity:
        support.append("Prolonged inactivity history recorded")

    if (
        profile.measured_ree_kcal is not None
        and profile.predicted_ree_kcal is not None
        and profile.ree_below_expected_confirmed
    ):
        support.append(
            f"Measured REE: {profile.measured_ree_kcal} vs expected {profile.predicted_ree_kcal} kcal/day"
        )
        return (
            "high",
            "High evidence strength: measured REE has been interpreted by the practitioner as below the relevant expected range.",
            support,
        )
    if support:
        return (
            "moderate",
            "Moderate evidence strength: the questionnaire is supported by clinician-supported or objective activity, body-composition or functional information.",
            support,
        )
    return (
        "low",
        "Low evidence strength: questionnaire responses only. Fatigue or perceived low metabolism cannot confirm reduced resting energy expenditure.",
        support,
    )


def score_phenotypes(profile: PatientProfile) -> dict[str, Any]:
    results: dict[str, Any] = {}
    comparison = profile.phenotype_medication_comparison or {}
    taking_appetite_medication = any(
        any(token in medication.casefold() for token in APPETITE_MODIFYING_MEDICATIONS)
        for medication in profile.medications
    )

    for key, definition in PHENOTYPE_DEFINITIONS.items():
        core_values = [int(getattr(profile, item)) for item in definition["core"]]
        triggered = _followup_triggered(core_values)
        followup_values = [getattr(profile, item) for item in definition["followup"]]
        answered_followups = [int(value) for value in followup_values if value is not None]
        if triggered and len(answered_followups) == 2:
            values = core_values + answered_followups
            denominator = 20
        else:
            values = core_values
            denominator = 12

        score = round(sum(values) / denominator * 100)
        if score >= 70:
            level, label = "high", "High current signal"
        elif score >= 40:
            level, label = "moderate", "Moderate current signal"
        else:
            level, label = "lower", "Lower current signal"

        evidence_strength = "questionnaire"
        evidence_label = "Questionnaire signal"
        evidence_note = "Questionnaire-derived signal; not a physiological diagnosis."
        evidence_support: list[str] = []
        if key == "slow_burn":
            evidence_strength, evidence_note, evidence_support = _slow_burn_evidence(profile)
            evidence_label = f"{evidence_strength.title()} evidence strength"

        medication_change = comparison.get(key) if taking_appetite_medication else None
        recalled_context = None
        if medication_change:
            recalled_context = (
                f"Patient recalls this pattern has {medication_change.casefold()} compared with before medication. "
                "This is recalled context, may be affected by recall bias and is not a measured baseline score."
            )

        results[key] = {
            "key": key,
            "name": definition["name"],
            "clinical_label": definition["clinical_label"],
            "score": score,
            "level": level,
            "level_label": label,
            "summary": definition["summary"],
            "actions": definition["actions"],
            "item_scores": values,
            "core_scores": core_values,
            "followup_triggered": triggered,
            "followup_answered": len(answered_followups),
            "questions_answered": len(values),
            "medication_change": medication_change,
            "recalled_context": recalled_context,
            "evidence_strength": evidence_strength,
            "evidence_label": evidence_label,
            "evidence_note": evidence_note,
            "evidence_support": evidence_support,
        }

    ranked = sorted(results.values(), key=lambda item: item["score"], reverse=True)
    for rank, item in enumerate(ranked, start=1):
        results[item["key"]]["rank"] = rank

    return {
        "profile_name": "MWLC Acosta-Informed Screening Profile v1.0",
        "domains": results,
        "ranked": [results[item["key"]] for item in ranked],
        "priority_keys": [item["key"] for item in ranked if item["score"] >= 40],
        "screening_note": (
            "This is an Acosta-informed questionnaire profile based on current four-week symptoms. "
            "It does not reproduce formal physiological phenotype testing. Emotional-hunger scoring is not an eating-disorder diagnosis. "
            "Recalled pre-treatment context may be affected by recall bias."
        ),
        "ruleset_version": "2026.2",
    }


# Patch the mature Sprint 0 engine so every existing plan, safety and PDF pathway
# uses the adaptive Phase 2 score without duplicating the rest of the engine.
_base.score_phenotypes = score_phenotypes
_base.PHENOTYPE_DEFINITIONS = PHENOTYPE_DEFINITIONS

for _name in dir(_base):
    if not _name.startswith("_") and _name not in globals():
        globals()[_name] = getattr(_base, _name)

globals()["score_phenotypes"] = score_phenotypes
