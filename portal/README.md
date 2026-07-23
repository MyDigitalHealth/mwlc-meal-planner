# MWLC Patient Portal

Secure Next.js + Supabase foundation for persistent patient profiles, clinician access and administrator controls.

## Current scope

- Passwordless email magic-link authentication using PKCE
- Patient, clinician and administrator role routing
- Organisation-scoped patient records
- Clinician-patient assignments
- Versioned weight-loss assessments and meal plans
- Private PDF storage
- Row Level Security on all health-data tables
- Append-only audit events
- Responsive patient, clinician and administrator dashboards

## Required environment variables

Copy `.env.example` to `.env.local`. Configure values in Vercel project settings; never commit them.

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` — server-only; reserved for invitation/admin workflows
- `NEXT_PUBLIC_SITE_URL`
- `AUDIT_HASH_SECRET`

## Supabase setup

1. Create a dedicated Supabase project in the required region.
2. Apply `supabase/migrations/202607230001_patient_portal.sql`.
3. Configure Auth Site URL and permitted redirect URLs:
   - local: `http://localhost:3000/auth/callback`
   - production: `https://<portal-domain>/auth/callback`
4. Disable open public sign-ups. Accounts must be invited or provisioned by an administrator.
5. Configure branded SMTP and short magic-link expiry.
6. Require MFA/AAL2 for clinician and administrator routes before production.
7. Store all secrets in Supabase/Vercel secret stores only.

## Initial organisation bootstrap

The first organisation and administrator must be created through a controlled migration or one-time server-side script. Do not expose a public “become an administrator” flow.

## Production gates

- Move this workspace to a private repository before adding operational configuration.
- Add RLS integration tests using separate patient, clinician and administrator JWTs.
- Add rate limiting and bot challenge to login and invitation endpoints.
- Add security-event alerts and log drains without patient content.
- Complete penetration testing and restore testing.
- Review privacy collection notice, consent language and retention policy.

## Development

```bash
npm install
npm run typecheck
npm run lint
npm run build
npm run dev
```

The existing clinical calculators remain separate until authenticated persistence and authorisation tests pass.
