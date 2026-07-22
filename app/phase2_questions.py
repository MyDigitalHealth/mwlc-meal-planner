from __future__ import annotations

from copy import deepcopy

from app import base_questions as _base

FREQUENCY_LABELS = {"0": "Never", "2": "Sometimes", "4": "Almost always"}

OLD_PHENOTYPE_IDS = {
    "hb_large_portions", "hb_difficulty_stopping", "hb_second_helpings",
    "hg_hungry_soon", "hg_fullness_fades", "hg_need_snacks",
    "eh_eat_emotions", "eh_food_cravings", "eh_loss_control",
    "sb_low_activity", "sb_low_energy", "sb_low_strength",
}

PHENOTYPE_QUESTIONS = [
    {
        "id": "phenotype_intro",
        "prompt": "Before we continue: think about the patient's experience over the past four weeks.",
        "help": "Answer based on what is happening now, including the effects of any appetite-modifying medication.",
        "type": "single", "options": ["Continue"], "default": "Continue",
    },
    {"id": "hb_recognise_enough", "prompt": "How often was it difficult to recognise that enough food had been eaten?", "help": "Thinking about the past four weeks - Hungry brain core item 1 of 3.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS},
    {"id": "hb_large_portion_needed", "prompt": "How often was a larger portion than expected needed before feeling comfortably satisfied?", "help": "Thinking about the past four weeks - Hungry brain core item 2 of 3.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS},
    {"id": "hb_second_serving", "prompt": "How often was a second serving taken before feeling satisfied?", "help": "Thinking about the past four weeks - Hungry brain core item 3 of 3.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS},
    {"id": "hb_continue_after_hunger", "prompt": "How often did eating continue after physical hunger had eased?", "help": "Hungry brain adaptive follow-up 1 of 2.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS, "adaptive_if": {"domain": "hungry_brain"}},
    {"id": "hb_food_gone", "prompt": "How often did a meal end mainly because the food was gone rather than because comfortable fullness was reached?", "help": "Hungry brain adaptive follow-up 2 of 2.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS, "adaptive_if": {"domain": "hungry_brain"}},

    {"id": "hg_hunger_returns", "prompt": "How often did physical hunger return within two or three hours of an adequate meal?", "help": "Thinking about the past four weeks - Hungry gut core item 1 of 3.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS},
    {"id": "hg_grazing_needed", "prompt": "How often was it difficult to reach the next planned meal without grazing because of physical hunger?", "help": "Thinking about the past four weeks - Hungry gut core item 2 of 3.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS},
    {"id": "hg_late_hunger", "prompt": "How often was there strong late-afternoon or evening physical hunger despite adequate meals earlier in the day?", "help": "Thinking about the past four weeks - Hungry gut core item 3 of 3.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS},
    {"id": "hg_meal_not_hold", "prompt": "How often did a meal initially satisfy but fail to hold until the next planned meal?", "help": "Hungry gut adaptive follow-up 1 of 2.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS, "adaptive_if": {"domain": "hungry_gut"}},
    {"id": "hg_fullness_fades", "prompt": "How often did fullness fade sooner than expected after eating?", "help": "Hungry gut adaptive follow-up 2 of 2.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS, "adaptive_if": {"domain": "hungry_gut"}},

    {"id": "eh_emotional_eating", "prompt": "How often did eating occur in response to stress, boredom, loneliness, frustration or low mood?", "help": "Thinking about the past four weeks - Emotional or hedonic hunger core item 1 of 3.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS},
    {"id": "eh_environment_cues", "prompt": "How often did television, social situations, particular places or other cues trigger thoughts about food?", "help": "Thinking about the past four weeks - Emotional or hedonic hunger core item 2 of 3.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS},
    {"id": "eh_strong_cravings", "prompt": "How often were there strong cravings for particular highly rewarding foods?", "help": "Thinking about the past four weeks - Emotional or hedonic hunger core item 3 of 3.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS},
    {"id": "eh_food_reward", "prompt": "How often was food used as a reward, comfort or way of changing how the patient felt?", "help": "Emotional or hedonic hunger adaptive follow-up 1 of 2.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS, "adaptive_if": {"domain": "emotional_hunger"}},
    {"id": "eh_loss_control", "prompt": "How often was there a sense of being out of control once a trigger food was started?", "help": "Emotional or hedonic hunger adaptive follow-up 2 of 2. This is not an eating-disorder diagnosis.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS, "adaptive_if": {"domain": "emotional_hunger"}},

    {"id": "sb_sedentary_time", "prompt": "How often was most of the waking day spent sitting or physically inactive?", "help": "Thinking about the past four weeks - Slow burn questionnaire signal core item 1 of 3.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS},
    {"id": "sb_low_incidental_movement", "prompt": "How often did a usual day involve very little walking or incidental movement?", "help": "Thinking about the past four weeks - Slow burn questionnaire signal core item 2 of 3.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS},
    {"id": "sb_fatigue_limits_activity", "prompt": "How often did fatigue limit everyday movement or planned physical activity?", "help": "Thinking about the past four weeks - Slow burn core item 3 of 3. Fatigue alone cannot create high evidence strength.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS},
    {"id": "sb_strength_limits_activity", "prompt": "How often did low strength or physical capacity limit daily activities or exercise?", "help": "Slow burn adaptive follow-up 1 of 2.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS, "adaptive_if": {"domain": "slow_burn"}},
    {"id": "sb_no_resistance_training", "prompt": "How often was there no resistance or muscle-strengthening activity during the week?", "help": "Slow burn adaptive follow-up 2 of 2.", "type": "scale", "min": 0, "max": 4, "labels": FREQUENCY_LABELS, "adaptive_if": {"domain": "slow_burn"}},

    {
        "id": "phenotype_medication_comparison",
        "prompt": "Compared with before starting appetite-modifying medication, how has each pattern changed?",
        "help": "This is recalled pre-treatment context and may be affected by recall bias. It does not alter the current numerical scores.",
        "type": "matrix",
        "rows": [
            {"id": "hungry_brain", "label": "Hungry brain / reduced satiation"},
            {"id": "hungry_gut", "label": "Hungry gut / reduced duration of satiety"},
            {"id": "emotional_hunger", "label": "Emotional or hedonic hunger"},
            {"id": "slow_burn", "label": "Slow burn questionnaire signal"},
        ],
        "options": ["Improved", "Stayed about the same", "Worsened", "Unsure or cannot recall"],
        "show_if_any": {"field": "medications", "values": ["Mounjaro", "Wegovy/Ozempic", "Saxenda", "Phentermine/Duromine", "Topiramate"]},
    },
    {"id": "average_daily_steps", "prompt": "Optional: measured average daily step count?", "help": "Enter 0 when unavailable. Objective fields strengthen slow-burn interpretation but do not diagnose metabolism.", "type": "number", "min": 0, "max": 100000, "step": 100, "default": 0},
    {"id": "resistance_training_sessions", "prompt": "Optional: resistance-training sessions per week?", "type": "number", "min": 0, "max": 14, "default": 0},
    {"id": "occupational_activity", "prompt": "Optional clinician-supported occupational activity assessment?", "type": "single", "options": ["Not recorded", "Sedentary", "Mixed", "Active", "Highly active"], "default": "Not recorded"},
    {"id": "measured_ree_kcal", "prompt": "Optional: measured resting energy expenditure?", "help": "Enter 0 when not measured. High evidence strength also requires a predicted value and practitioner confirmation.", "type": "number", "min": 0, "max": 5000, "default": 0, "suffix": "kcal/day"},
    {"id": "predicted_ree_kcal", "prompt": "Optional: predicted or expected resting energy expenditure?", "type": "number", "min": 0, "max": 5000, "default": 0, "suffix": "kcal/day", "show_if": {"field": "measured_ree_kcal", "not_equals": 0}},
    {"id": "ree_method", "prompt": "Optional: REE test method or laboratory reference?", "type": "text", "placeholder": "e.g. indirect calorimetry", "show_if": {"field": "measured_ree_kcal", "not_equals": 0}},
    {"id": "ree_below_expected_confirmed", "prompt": "Has the practitioner interpreted the measured REE as below the relevant expected range?", "type": "single", "options": ["No", "Yes"], "default": "No", "show_if": {"field": "measured_ree_kcal", "not_equals": 0}},
]

QUESTIONS = [deepcopy(item) for item in _base.QUESTIONS if item.get("id") not in OLD_PHENOTYPE_IDS]
insert_at = next(
    (index for index, item in enumerate(QUESTIONS) if item.get("id") == "craving_triggers"),
    len(QUESTIONS),
)
QUESTIONS[insert_at:insert_at] = deepcopy(PHENOTYPE_QUESTIONS)

DEMO_PROFILE = deepcopy(_base.DEMO_PROFILE)
for old_id in OLD_PHENOTYPE_IDS:
    DEMO_PROFILE.pop(old_id, None)
DEMO_PROFILE.update({
    "phenotype_intro": "Continue",
    "hb_recognise_enough": 3,
    "hb_large_portion_needed": 3,
    "hb_second_serving": 2,
    "hb_continue_after_hunger": 3,
    "hb_food_gone": 2,
    "hg_hunger_returns": 3,
    "hg_grazing_needed": 3,
    "hg_late_hunger": 2,
    "hg_meal_not_hold": 3,
    "hg_fullness_fades": 3,
    "eh_emotional_eating": 3,
    "eh_environment_cues": 3,
    "eh_strong_cravings": 4,
    "eh_food_reward": 3,
    "eh_loss_control": 3,
    "sb_sedentary_time": 3,
    "sb_low_incidental_movement": 3,
    "sb_fatigue_limits_activity": 2,
    "sb_strength_limits_activity": 2,
    "sb_no_resistance_training": 3,
    "phenotype_medication_comparison": {
        "hungry_brain": "Improved",
        "hungry_gut": "Improved",
        "emotional_hunger": "Stayed about the same",
        "slow_burn": "Stayed about the same",
    },
    "average_daily_steps": 4500,
    "resistance_training_sessions": 1,
    "occupational_activity": "Sedentary",
    "measured_ree_kcal": 0,
    "predicted_ree_kcal": 0,
    "ree_method": "",
    "ree_below_expected_confirmed": "No",
})

for _name in dir(_base):
    if not _name.startswith("_") and _name not in globals():
        globals()[_name] = getattr(_base, _name)
