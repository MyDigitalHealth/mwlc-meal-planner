# My Weight Loss Clinic - 7-Day Meal Planner Chatbot

A working practitioner-facing prototype that:

1. asks the consultation questions one at a time in a chat-style interface;
2. calculates energy, protein, fibre, fluid and sodium targets with deterministic code;
3. applies clinical blockers and warnings before generation;
4. previews a complete seven-day menu; and
5. creates a branded 45-page PDF containing photographs, recipes, per-meal macros, a shopping list, preparation plan, behavioural tools and trackers.

The application does **not** require an LLM or send patient data to an external AI service. The conversational experience is handled in the browser; calculations and PDF generation run on the application server. Consult data is not persisted by this prototype.

## Deploy to Vercel

Import this repository into Vercel and deploy with the included `vercel.json`. No environment variables are required for the prototype.

## Run locally

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Clinical guardrails

Automatic generation is blocked for recorded food allergies, vegetarian/vegan/dairy-free requirements, coeliac/gluten-free needs, renal or prescribed fluid restrictions, higher-risk diabetes medication scenarios, persistent vomiting or inability to maintain fluids, and active or uncertain eating-disorder risk. Generation also requires practitioner approval.

## Production hardening recommended

Before live clinical use, add practitioner authentication, role-based access, audit logging, privacy and security review, clinical-governance approval, secure document delivery, ruleset versioning, and confirmed commercial licences for all photography and brand assets.

## Photography

The included images are retained to demonstrate output quality. Confirm provenance and licensing before commercial deployment.
