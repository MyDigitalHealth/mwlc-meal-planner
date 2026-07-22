"""Phase 2 review entry point layered over the verified Sprint 0 release."""
from __future__ import annotations

import base64
import hashlib
import io
import json
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "source.zip"
SPRINT0_PARTS = ROOT / "artifacts" / "sprint0_parts"
HELPERS = ROOT / "app"
RUNTIME = Path("/tmp/mwlc_phase2_over_sprint0")
MARKER = RUNTIME / ".ready-0.6.0"
SPRINT0_SHA256 = "8dc512007b3865feb565eb8b30663e608bdc22802ff394842d52976326849eba"


def required_replace(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Missing Phase 2 patch target: {label}")
    return text.replace(old, new, 1)


def prepare() -> None:
    if MARKER.exists():
        return
    if RUNTIME.exists():
        shutil.rmtree(RUNTIME)
    RUNTIME.mkdir(parents=True, exist_ok=True)

    # Start with the established photography and brand assets.
    with zipfile.ZipFile(ARCHIVE) as bundle:
        bundle.extractall(RUNTIME)

    # Apply the exact verified Sprint 0 application release before Phase 2.
    encoded = b"".join(path.read_bytes().strip() for path in sorted(SPRINT0_PARTS.glob("part*")))
    payload = base64.b64decode(encoded, validate=True)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != SPRINT0_SHA256:
        raise RuntimeError(f"Sprint 0 checksum mismatch: expected {SPRINT0_SHA256}, got {digest}")
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:xz") as package:
        package.extractall(RUNTIME)

    app_dir = RUNTIME / "app"
    shutil.copy2(app_dir / "engine.py", app_dir / "base_engine.py")
    shutil.copy2(app_dir / "questions.py", app_dir / "base_questions.py")
    shutil.copy2(HELPERS / "phase2_models.py", app_dir / "models.py")
    shutil.copy2(HELPERS / "phase2_engine.py", app_dir / "engine.py")
    shutil.copy2(HELPERS / "phase2_questions.py", app_dir / "questions.py")

    # Version the inherited clinical rules without removing Sprint 0 guardrails.
    rules_path = app_dir / "data" / "clinical_rules.json"
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    rules["ruleset_version"] = "2026.2"
    rules["phenotype"] = {
        "screening_label": "MWLC Acosta-Informed Screening Profile v1.0",
        "timeframe": "past four weeks",
        "response_scale": {"Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Almost always": 4},
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
    js = required_replace(js, """  function questionVisible(question) {
    if (!question.show_if) return true;
    const value = state.answers[question.show_if.field];
    if (Object.prototype.hasOwnProperty.call(question.show_if, 'contains')) {
      return Array.isArray(value) ? value.includes(question.show_if.contains) : String(value || '').includes(question.show_if.contains);
    }
    return true;
  }
""", """  const phenotypeCoreFields = {
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
    if (Object.prototype.hasOwnProperty.call(question.show_if, 'not_equals')) return Number(value) !== Number(question.show_if.not_equals);
    return true;
  }
""", "adaptive visibility")

    scale_marker = "    if (q.type === 'scale') {\n"
    matrix = """    if (q.type === 'matrix') {
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
    js = required_replace(js, scale_marker, matrix + scale_marker, "matrix renderer")
    js = required_replace(js, """    if (q.type === 'multi') {
      return [...form.querySelectorAll('input[name="answer"]:checked')].map(el => el.value);
    }
    const input = form.querySelector('[name="answer"]');
""", """    if (q.type === 'multi') {
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
""", "matrix answer reader")
    js = js.replace(
        "    if (Array.isArray(value)) return value.join(', ');\n    return String(value);",
        "    if (Array.isArray(value)) return value.join(', ');\n    if (value && typeof value === 'object') return Object.entries(value).map(([key, item]) => `${key.replaceAll('_', ' ')}: ${item}`).join('; ');\n    return String(value);",
        1,
    )
    js = required_replace(js, """        <p><strong>${escapeHtml(item.level_label)}</strong><br>${escapeHtml(item.summary)}</p>
        <ul>${actionItems}</ul>
""", """        <p><strong>${escapeHtml(item.level_label)}</strong> · ${item.questions_answered || 3} questions<br>${escapeHtml(item.summary)}</p>
        ${item.key === 'slow_burn' ? `<p class="evidence-line"><strong>${escapeHtml(item.evidence_label || '')}</strong><br>${escapeHtml(item.evidence_note || '')}</p>` : ''}
        ${item.recalled_context ? `<p class="recalled-line">${escapeHtml(item.recalled_context)}</p>` : ''}
        <ul>${actionItems}</ul>
""", "phenotype result card")
    js_path.write_text(js, encoding="utf-8")

    with (app_dir / "static" / "styles.css").open("a", encoding="utf-8") as styles:
        styles.write("\n.matrix-wrap{display:grid;gap:14px}.matrix-row{border:1px solid #d9e1ea;border-radius:12px;padding:12px;display:flex;flex-wrap:wrap;gap:8px}.matrix-row legend{font-weight:700;color:#152744;padding:0 6px}.matrix-option{font-size:.82rem}.evidence-line,.recalled-line{font-size:.77rem!important;padding:8px;border-radius:8px;background:#f5f7fa}.recalled-line{background:#fff8e8}\n")

    MARKER.write_text("0.6.0", encoding="utf-8")


prepare()
sys.path.insert(0, str(RUNTIME))
from app.main import app  # noqa: E402

app.version = "0.6.0"

@app.get("/api/phase2")
def phase2_metadata() -> dict:
    from app.questions import PHENOTYPE_QUESTIONS
    return {
        "app_version": "0.6.0",
        "ruleset_version": "2026.2",
        "base_release": "Sprint 0 verified overlay",
        "profile": "MWLC Acosta-Informed Screening Profile v1.0",
        "timeframe": "past four weeks",
        "core_questions": 12,
        "maximum_questions": 20,
        "adaptive_trigger": {"core_sum_at_least": 5, "any_core_at_least": 3},
        "response_scale": {"Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Almost always": 4},
        "question_count_including_context_fields": len(PHENOTYPE_QUESTIONS),
    }

__all__ = ["app"]
