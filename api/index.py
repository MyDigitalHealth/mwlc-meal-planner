"""Vercel entry point for the Phase 2 adaptive questionnaire review."""
from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
BASE_ARCHIVE = REPOSITORY_ROOT / "source.zip"
HELPER_DIR = REPOSITORY_ROOT / "app"
EXTRACT_DIR = Path("/tmp/mwlc_meal_planner_phase2_normal")
MARKER = EXTRACT_DIR / ".ready-0.6.0"


def _replace_required(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Phase 2 bootstrap could not find {label}")
    return text.replace(old, new, 1)


def _prepare_application() -> None:
    if MARKER.exists():
        return
    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    # source.zip remains the licensed photography and established Sprint 0
    # application asset bundle. Phase 2 logic is applied as normal UTF-8 source.
    with zipfile.ZipFile(BASE_ARCHIVE) as bundle:
        bundle.extractall(EXTRACT_DIR)

    app_dir = EXTRACT_DIR / "app"
    shutil.copy2(app_dir / "engine.py", app_dir / "base_engine.py")
    shutil.copy2(app_dir / "questions.py", app_dir / "base_questions.py")
    shutil.copy2(HELPER_DIR / "phase2_models.py", app_dir / "models.py")
    shutil.copy2(HELPER_DIR / "phase2_engine.py", app_dir / "engine.py")
    shutil.copy2(HELPER_DIR / "phase2_questions.py", app_dir / "questions.py")

    rules_path = app_dir / "data" / "clinical_rules.json"
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    rules["ruleset_version"] = "2026.2"
    rules["phenotype"] = {
        "screening_label": "MWLC Acosta-Informed Screening Profile v1.0",
        "timeframe": "past four weeks",
        "response_scale": {
            "Never": 0,
            "Rarely": 1,
            "Sometimes": 2,
            "Often": 3,
            "Almost always": 4,
        },
        "adaptive_trigger": {"core_sum_at_least": 5, "any_core_at_least": 3},
        "bands": [
            {"minimum": 70, "level": "high", "label": "High current signal"},
            {"minimum": 40, "level": "moderate", "label": "Moderate current signal"},
            {"minimum": 0, "level": "lower", "label": "Lower current signal"},
        ],
        "intervention_threshold": 40,
        "minimum_priority_domains": 0,
        "disclaimer": "Acosta-informed questionnaire screening only; it does not reproduce objective satiation, gastric emptying or resting-energy-expenditure testing.",
    }
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    main_path = app_dir / "main.py"
    main_text = main_path.read_text(encoding="utf-8")
    main_text = main_text.replace('version="0.5.0"', 'version="0.6.0"')
    main_text = main_text.replace(
        '"phenotype_note": "Acosta-informed multidomain screening; not a replacement for formal physiological phenotype testing.",',
        '"phenotype_note": "MWLC Acosta-Informed Screening Profile v1.0; adaptive 12-20 item questionnaire, not formal physiological phenotype testing.",\n'
        '        "phenotype_timeframe": "past four weeks",\n'
        '        "phenotype_response_scale": {"Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Almost always": 4},',
    )
    main_path.write_text(main_text, encoding="utf-8")

    js_path = app_dir / "static" / "app.js"
    js = js_path.read_text(encoding="utf-8")
    old_visibility = """  function questionVisible(question) {
    if (!question.show_if) return true;
    const value = state.answers[question.show_if.field];
    if (Object.prototype.hasOwnProperty.call(question.show_if, 'contains')) {
      return Array.isArray(value) ? value.includes(question.show_if.contains) : String(value || '').includes(question.show_if.contains);
    }
    return true;
  }
"""
    new_visibility = """  const phenotypeCoreFields = {
    hungry_brain: ['hb_recognise_enough', 'hb_large_portion_needed', 'hb_second_serving'],
    hungry_gut: ['hg_hunger_returns', 'hg_grazing_needed', 'hg_late_hunger'],
    emotional_hunger: ['eh_emotional_eating', 'eh_environment_cues', 'eh_strong_cravings'],
    slow_burn: ['sb_sedentary_time', 'sb_low_incidental_movement', 'sb_fatigue_limits_activity'],
  };

  function questionVisible(question) {
    if (question.adaptive_if) {
      const fields = phenotypeCoreFields[question.adaptive_if.domain] || [];
      const values = fields.map(field => state.answers[field]);
      if (values.some(value => value === undefined || value === null)) return false;
      return values.reduce((sum, value) => sum + Number(value), 0) >= 5 || values.some(value => Number(value) >= 3);
    }
    if (question.show_if_any) {
      const value = state.answers[question.show_if_any.field];
      const selected = Array.isArray(value) ? value : [value];
      return selected.some(item => question.show_if_any.values.includes(item));
    }
    if (!question.show_if) return true;
    const value = state.answers[question.show_if.field];
    if (Object.prototype.hasOwnProperty.call(question.show_if, 'contains')) {
      return Array.isArray(value) ? value.includes(question.show_if.contains) : String(value || '').includes(question.show_if.contains);
    }
    if (Object.prototype.hasOwnProperty.call(question.show_if, 'not_equals')) return value !== question.show_if.not_equals;
    if (Object.prototype.hasOwnProperty.call(question.show_if, 'equals')) return value === question.show_if.equals;
    return true;
  }
"""
    js = _replace_required(js, old_visibility, new_visibility, "question visibility function")

    scale_marker = "    if (q.type === 'scale') {\n"
    matrix_block = """    if (q.type === 'matrix') {
      wrapper.className = 'matrix-wrap';
      q.rows.forEach(row => {
        const group = document.createElement('fieldset');
        group.className = 'matrix-row';
        const legend = document.createElement('legend');
        legend.textContent = row.label;
        group.appendChild(legend);
        q.options.forEach(option => {
          const label = document.createElement('label');
          label.className = 'option-pill matrix-option';
          const input = document.createElement('input');
          input.type = 'radio'; input.name = `matrix_${row.id}`; input.value = option;
          const span = document.createElement('span'); span.textContent = option;
          label.append(input, span); group.appendChild(label);
        });
        wrapper.appendChild(group);
      });
      wrapper.appendChild(submitButton());
      return wrapper;
    }
"""
    js = _replace_required(js, scale_marker, matrix_block + scale_marker, "scale renderer")

    old_read = """    if (q.type === 'multi') {
      return [...form.querySelectorAll('input[name="answer"]:checked')].map(el => el.value);
    }
    const input = form.querySelector('[name="answer"]');
"""
    new_read = """    if (q.type === 'multi') {
      return [...form.querySelectorAll('input[name="answer"]:checked')].map(el => el.value);
    }
    if (q.type === 'matrix') {
      const result = {};
      for (const row of q.rows) {
        const selected = form.querySelector(`input[name="matrix_${row.id}"]:checked`);
        if (!selected) throw new Error('Please answer each comparison row.');
        result[row.id] = selected.value;
      }
      return result;
    }
    const input = form.querySelector('[name="answer"]');
"""
    js = _replace_required(js, old_read, new_read, "answer reader")
    js = js.replace(
        "    if (Array.isArray(value)) return value.join(', ');\n    return String(value);",
        "    if (Array.isArray(value)) return value.join(', ');\n    if (value && typeof value === 'object') return Object.entries(value).map(([key, item]) => `${key.replaceAll('_', ' ')}: ${item}`).join('; ');\n    return String(value);",
        1,
    )
    old_card = """        <p><strong>${escapeHtml(item.level_label)}</strong><br>${escapeHtml(item.summary)}</p>
        <ul>${actionItems}</ul>
"""
    new_card = """        <p><strong>${escapeHtml(item.level_label)}</strong> · ${item.questions_answered || 3} questions<br>${escapeHtml(item.summary)}</p>
        ${item.key === 'slow_burn' ? `<p class="evidence-line"><strong>${escapeHtml(item.evidence_label || '')}</strong><br>${escapeHtml(item.evidence_note || '')}</p>` : ''}
        ${item.recalled_context ? `<p class="recalled-line">${escapeHtml(item.recalled_context)}</p>` : ''}
        <ul>${actionItems}</ul>
"""
    js = _replace_required(js, old_card, new_card, "phenotype result card")
    js_path.write_text(js, encoding="utf-8")

    styles_path = app_dir / "static" / "styles.css"
    with styles_path.open("a", encoding="utf-8") as styles:
        styles.write("\n.matrix-wrap{display:grid;gap:14px}.matrix-row{border:1px solid #d9e1ea;border-radius:12px;padding:12px;display:flex;flex-wrap:wrap;gap:8px}.matrix-row legend{font-weight:700;color:#152744;padding:0 6px}.matrix-option{font-size:.82rem}.evidence-line,.recalled-line{font-size:.77rem!important;padding:8px;border-radius:8px;background:#f5f7fa}.recalled-line{background:#fff8e8}\n")

    MARKER.write_text("0.6.0", encoding="utf-8")


_prepare_application()
sys.path.insert(0, str(EXTRACT_DIR))
from app.main import app  # noqa: E402

__all__ = ["app"]
