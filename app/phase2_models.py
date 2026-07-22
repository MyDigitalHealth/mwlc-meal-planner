from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


PHENOTYPE_FIELD_NAMES = (
    "hb_recognise_enough", "hb_large_portion_needed", "hb_second_serving",
    "hb_continue_after_hunger", "hb_food_gone",
    "hg_hunger_returns", "hg_grazing_needed", "hg_late_hunger",
    "hg_meal_not_hold", "hg_fullness_fades",
    "eh_emotional_eating", "eh_environment_cues", "eh_strong_cravings",
    "eh_food_reward", "eh_loss_control",
    "sb_sedentary_time", "sb_low_incidental_movement", "sb_fatigue_limits_activity",
    "sb_strength_limits_activity", "sb_no_resistance_training",
)


class PatientProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    patient_initials: str = Field(default="Patient", max_length=40)
    primary_goal: str = "Lose weight"
    age: int = Field(ge=16, le=100)
    sex: str
    height_cm: float = Field(gt=100, lt=230)
    current_weight_kg: float = Field(gt=35, lt=350)
    goal_weight_kg: float = Field(gt=35, lt=300)
    expected_12_week_weight_kg: float | None = Field(default=None, gt=35, lt=350)

    medications: list[str] = Field(default_factory=list)
    mounjaro_dose: str | None = None
    conditions: list[str] = Field(default_factory=list)

    dietary_style: str = "No preference"
    allergies: list[str] = Field(default_factory=list)
    protein_preferences: list[str] = Field(default_factory=list)
    food_exclusions: list[str] = Field(default_factory=list)
    seafood_frequency: str = "Flexible"
    red_meat_frequency: str = "Maximum 2 meals/week"
    dinner_portion_preference: str = "Standard evening meal"
    meal_repetition_preference: str = "Some repetition is fine"
    dislikes: str = ""
    favourite_foods: str = ""

    current_intake: str = ""
    hunger_score: int = Field(default=3, ge=1, le=5)
    craving_triggers: list[str] = Field(default_factory=list)

    hb_recognise_enough: int = Field(default=2, ge=0, le=4)
    hb_large_portion_needed: int = Field(default=2, ge=0, le=4)
    hb_second_serving: int = Field(default=2, ge=0, le=4)
    hb_continue_after_hunger: int | None = Field(default=None, ge=0, le=4)
    hb_food_gone: int | None = Field(default=None, ge=0, le=4)

    hg_hunger_returns: int = Field(default=2, ge=0, le=4)
    hg_grazing_needed: int = Field(default=2, ge=0, le=4)
    hg_late_hunger: int = Field(default=2, ge=0, le=4)
    hg_meal_not_hold: int | None = Field(default=None, ge=0, le=4)
    hg_fullness_fades: int | None = Field(default=None, ge=0, le=4)

    eh_emotional_eating: int = Field(default=2, ge=0, le=4)
    eh_environment_cues: int = Field(default=2, ge=0, le=4)
    eh_strong_cravings: int = Field(default=2, ge=0, le=4)
    eh_food_reward: int | None = Field(default=None, ge=0, le=4)
    eh_loss_control: int | None = Field(default=None, ge=0, le=4)

    sb_sedentary_time: int = Field(default=2, ge=0, le=4)
    sb_low_incidental_movement: int = Field(default=2, ge=0, le=4)
    sb_fatigue_limits_activity: int = Field(default=2, ge=0, le=4)
    sb_strength_limits_activity: int | None = Field(default=None, ge=0, le=4)
    sb_no_resistance_training: int | None = Field(default=None, ge=0, le=4)

    phenotype_medication_comparison: dict[str, str] = Field(default_factory=dict)

    measured_ree_kcal: int | None = Field(default=None, ge=500, le=5000)
    predicted_ree_kcal: int | None = Field(default=None, ge=500, le=5000)
    ree_method: str = ""
    ree_date: str = ""
    ree_below_expected_confirmed: bool = False
    body_composition_summary: str = ""
    average_daily_steps: int | None = Field(default=None, ge=0, le=100000)
    grip_strength_value: float | None = Field(default=None, ge=0, le=200)
    grip_strength_units: str = "kg"
    resistance_training_sessions: int | None = Field(default=None, ge=0, le=14)
    occupational_activity: str = "Not recorded"
    prolonged_inactivity: str = ""

    activity_level: str = "Light activity"
    meals_per_day: str = "3 meals"
    confidence: int = Field(default=5, ge=1, le=10)
    biggest_barrier: str = "Cravings"
    water_intake: str = "1-2 litres"
    alcohol_intake: str = "None"
    success_goal: str = "Improve weight trend"
    cooking_time: str = "15-30 minutes"
    weekly_budget: str = "Moderate"
    renal_or_fluid_restriction: str = "No"
    diabetes_status: str = "No"
    gi_symptoms: str = "None"
    eating_disorder_history: str = "No"
    practitioner_notes: str = ""

    clinician_energy_override: int | None = Field(default=None, ge=1200, le=3500)
    clinician_protein_override: int | None = Field(default=None, ge=50, le=300)
    weight_expectation_override_acknowledged: bool = False
    weight_expectation_override_reason: str = Field(default="", max_length=500)
    weight_expectation_override_practitioner_initials: str = Field(default="", max_length=12)
    weight_expectation_monitoring_confirmed: bool = False
    approved_by_practitioner: bool = False

    @model_validator(mode="before")
    @classmethod
    def migrate_sprint0_phenotype_fields(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        data = dict(value)
        legacy_map = {
            "hb_large_portions": "hb_large_portion_needed",
            "hb_difficulty_stopping": "hb_recognise_enough",
            "hb_second_helpings": "hb_second_serving",
            "hg_hungry_soon": "hg_hunger_returns",
            "hg_need_snacks": "hg_grazing_needed",
            "eh_eat_emotions": "eh_emotional_eating",
            "eh_food_cravings": "eh_strong_cravings",
            "sb_low_activity": "sb_sedentary_time",
            "sb_low_energy": "sb_fatigue_limits_activity",
            "sb_low_strength": "sb_strength_limits_activity",
        }
        for old, new in legacy_map.items():
            if new not in data and old in data and data[old] is not None:
                data[new] = max(0, min(4, int(data[old]) - 1))
        for name in ("hg_fullness_fades", "eh_loss_control"):
            if name in data and data[name] is not None and int(data[name]) > 4:
                data[name] = 4
        return data

    @field_validator("patient_initials", mode="before")
    @classmethod
    def clean_initials(cls, value: Any) -> str:
        text = str(value or "Patient").strip()
        return text[:40] or "Patient"

    @field_validator(
        "medications", "conditions", "allergies", "craving_triggers",
        "protein_preferences", "food_exclusions", mode="before",
    )
    @classmethod
    def normalise_lists(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return [str(item) for item in value]

    @field_validator("measured_ree_kcal", "predicted_ree_kcal", "average_daily_steps", "grip_strength_value", "resistance_training_sessions", mode="before")
    @classmethod
    def zero_to_none(cls, value: Any) -> Any:
        if value in (None, "", 0, "0"):
            return None
        return value

    @field_validator("phenotype_medication_comparison", mode="before")
    @classmethod
    def normalise_comparison(cls, value: Any) -> dict[str, str]:
        if not isinstance(value, dict):
            return {}
        allowed = {"Improved", "Stayed about the same", "Worsened", "Unsure or cannot recall"}
        return {str(k): str(v) for k, v in value.items() if str(v) in allowed}

    @field_validator(
        "weight_expectation_override_reason", "weight_expectation_override_practitioner_initials",
        "ree_method", "ree_date", "body_composition_summary", "prolonged_inactivity", mode="before",
    )
    @classmethod
    def clean_text(cls, value: Any, info) -> str:
        limits = {
            "weight_expectation_override_practitioner_initials": 12,
            "weight_expectation_override_reason": 500,
            "ree_method": 100,
            "ree_date": 30,
            "body_composition_summary": 500,
            "prolonged_inactivity": 500,
        }
        return str(value or "").strip()[:limits.get(info.field_name, 500)]

    @model_validator(mode="after")
    def validate_weights(self) -> "PatientProfile":
        if self.primary_goal.lower().startswith("lose"):
            if self.goal_weight_kg >= self.current_weight_kg:
                raise ValueError("Goal weight must be below current weight for a weight-loss plan.")
            if self.expected_12_week_weight_kg is not None and self.expected_12_week_weight_kg > self.current_weight_kg:
                raise ValueError("The 12-week expected weight cannot be above current weight for a weight-loss plan.")
        return self


class PreviewRequest(BaseModel):
    profile: PatientProfile


class GenerateRequest(BaseModel):
    profile: PatientProfile
