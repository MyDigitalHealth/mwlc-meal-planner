from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class PatientProfile(BaseModel):
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

    # Acosta-informed screening questions. These are subjective proxies, not
    # replacements for objective satiation, gastric emptying or REE testing.
    hb_large_portions: int = Field(default=3, ge=1, le=5)
    hb_difficulty_stopping: int = Field(default=3, ge=1, le=5)
    hb_second_helpings: int = Field(default=3, ge=1, le=5)
    hg_hungry_soon: int = Field(default=3, ge=1, le=5)
    hg_fullness_fades: int = Field(default=3, ge=1, le=5)
    hg_need_snacks: int = Field(default=3, ge=1, le=5)
    eh_eat_emotions: int = Field(default=3, ge=1, le=5)
    eh_food_cravings: int = Field(default=3, ge=1, le=5)
    eh_loss_control: int = Field(default=3, ge=1, le=5)
    sb_low_activity: int = Field(default=3, ge=1, le=5)
    sb_low_energy: int = Field(default=3, ge=1, le=5)
    sb_low_strength: int = Field(default=3, ge=1, le=5)

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

    @field_validator("patient_initials", mode="before")
    @classmethod
    def clean_initials(cls, value: Any) -> str:
        text = str(value or "Patient").strip()
        return text[:40] or "Patient"

    @field_validator(
        "medications",
        "conditions",
        "allergies",
        "craving_triggers",
        "protein_preferences",
        "food_exclusions",
        mode="before",
    )
    @classmethod
    def normalise_lists(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return [str(item) for item in value]

    @field_validator("weight_expectation_override_reason", "weight_expectation_override_practitioner_initials", mode="before")
    @classmethod
    def clean_override_reason(cls, value: Any, info) -> str:
        limit = 12 if info.field_name == "weight_expectation_override_practitioner_initials" else 500
        return str(value or "").strip()[:limit]

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
