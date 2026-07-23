begin;

create extension if not exists pgcrypto;

create type public.portal_role as enum ('patient','clinician','admin');
create type public.assessment_status as enum ('draft','completed','clinician_reviewed','archived');

create table public.organisations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique,
  created_at timestamptz not null default now()
);

create table public.user_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  organisation_id uuid references public.organisations(id) on delete restrict,
  role public.portal_role not null default 'patient',
  display_name text,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.patients (
  id uuid primary key default gen_random_uuid(),
  organisation_id uuid not null references public.organisations(id) on delete restrict,
  user_id uuid unique references auth.users(id) on delete set null,
  external_reference text,
  preferred_name text,
  date_of_birth date,
  created_by uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (organisation_id, external_reference)
);

create table public.clinician_patient_assignments (
  id uuid primary key default gen_random_uuid(),
  organisation_id uuid not null references public.organisations(id) on delete cascade,
  clinician_user_id uuid not null references auth.users(id) on delete cascade,
  patient_id uuid not null references public.patients(id) on delete cascade,
  active boolean not null default true,
  assigned_by uuid references auth.users(id) on delete set null,
  assigned_at timestamptz not null default now(),
  unique (clinician_user_id, patient_id)
);

create table public.weight_loss_assessments (
  id uuid primary key default gen_random_uuid(),
  organisation_id uuid not null references public.organisations(id) on delete cascade,
  patient_id uuid not null references public.patients(id) on delete cascade,
  created_by uuid not null references auth.users(id) on delete restrict,
  status public.assessment_status not null default 'draft',
  questionnaire_version text not null,
  responses jsonb not null default '{}'::jsonb,
  metabolic_result jsonb,
  phenotype_result jsonb,
  completed_at timestamptz,
  reviewed_by uuid references auth.users(id) on delete set null,
  reviewed_at timestamptz,
  supersedes_assessment_id uuid references public.weight_loss_assessments(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.meal_plans (
  id uuid primary key default gen_random_uuid(),
  organisation_id uuid not null references public.organisations(id) on delete cascade,
  patient_id uuid not null references public.patients(id) on delete cascade,
  source_assessment_id uuid references public.weight_loss_assessments(id) on delete set null,
  created_by uuid not null references auth.users(id) on delete restrict,
  status public.assessment_status not null default 'draft',
  planner_version text not null,
  profile_input jsonb not null default '{}'::jsonb,
  plan_result jsonb,
  approved_by uuid references auth.users(id) on delete set null,
  approved_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.documents (
  id uuid primary key default gen_random_uuid(),
  organisation_id uuid not null references public.organisations(id) on delete cascade,
  patient_id uuid not null references public.patients(id) on delete cascade,
  assessment_id uuid references public.weight_loss_assessments(id) on delete cascade,
  meal_plan_id uuid references public.meal_plans(id) on delete cascade,
  storage_path text not null unique,
  file_name text not null,
  mime_type text not null,
  patient_visible boolean not null default false,
  created_by uuid not null references auth.users(id) on delete restrict,
  created_at timestamptz not null default now(),
  check ((assessment_id is not null)::int + (meal_plan_id is not null)::int = 1)
);

create table public.consents (
  id uuid primary key default gen_random_uuid(),
  organisation_id uuid not null references public.organisations(id) on delete cascade,
  patient_id uuid not null references public.patients(id) on delete cascade,
  consent_type text not null,
  consent_version text not null,
  granted boolean not null,
  recorded_by uuid not null references auth.users(id) on delete restrict,
  recorded_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create table public.audit_events (
  id bigint generated always as identity primary key,
  organisation_id uuid references public.organisations(id) on delete set null,
  actor_user_id uuid references auth.users(id) on delete set null,
  patient_id uuid references public.patients(id) on delete set null,
  action text not null,
  entity_type text not null,
  entity_id uuid,
  request_id text,
  ip_hash text,
  user_agent_hash text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index on public.patients (organisation_id, user_id);
create index on public.clinician_patient_assignments (clinician_user_id, patient_id) where active;
create index on public.weight_loss_assessments (patient_id, created_at desc);
create index on public.meal_plans (patient_id, created_at desc);
create index on public.audit_events (organisation_id, created_at desc);

create or replace function public.current_profile()
returns public.user_profiles
language sql
stable
security definer
set search_path = public
as $$
  select p from public.user_profiles p where p.user_id = auth.uid() and p.is_active = true;
$$;

create or replace function public.current_role()
returns public.portal_role
language sql
stable
security definer
set search_path = public
as $$
  select role from public.user_profiles where user_id = auth.uid() and is_active = true;
$$;

create or replace function public.current_organisation_id()
returns uuid
language sql
stable
security definer
set search_path = public
as $$
  select organisation_id from public.user_profiles where user_id = auth.uid() and is_active = true;
$$;

create or replace function public.can_access_patient(target_patient_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.patients p
    where p.id = target_patient_id
      and p.organisation_id = public.current_organisation_id()
      and (
        p.user_id = auth.uid()
        or public.current_role() = 'admin'
        or (
          public.current_role() = 'clinician'
          and exists (
            select 1 from public.clinician_patient_assignments a
            where a.patient_id = p.id
              and a.clinician_user_id = auth.uid()
              and a.active = true
          )
        )
      )
  );
$$;

alter table public.organisations enable row level security;
alter table public.user_profiles enable row level security;
alter table public.patients enable row level security;
alter table public.clinician_patient_assignments enable row level security;
alter table public.weight_loss_assessments enable row level security;
alter table public.meal_plans enable row level security;
alter table public.documents enable row level security;
alter table public.consents enable row level security;
alter table public.audit_events enable row level security;

create policy organisations_select on public.organisations for select
using (id = public.current_organisation_id());

create policy profiles_self_select on public.user_profiles for select
using (user_id = auth.uid());

create policy profiles_admin_select on public.user_profiles for select
using (public.current_role() = 'admin' and organisation_id = public.current_organisation_id());

create policy patients_select on public.patients for select
using (public.can_access_patient(id));

create policy patients_admin_insert on public.patients for insert
with check (public.current_role() = 'admin' and organisation_id = public.current_organisation_id());

create policy patients_admin_update on public.patients for update
using (public.current_role() = 'admin' and organisation_id = public.current_organisation_id())
with check (public.current_role() = 'admin' and organisation_id = public.current_organisation_id());

create policy assignments_clinician_select on public.clinician_patient_assignments for select
using (
  organisation_id = public.current_organisation_id()
  and (clinician_user_id = auth.uid() or public.current_role() = 'admin')
);

create policy assignments_admin_write on public.clinician_patient_assignments for all
using (public.current_role() = 'admin' and organisation_id = public.current_organisation_id())
with check (public.current_role() = 'admin' and organisation_id = public.current_organisation_id());

create policy assessments_select on public.weight_loss_assessments for select
using (public.can_access_patient(patient_id));

create policy assessments_patient_insert on public.weight_loss_assessments for insert
with check (
  public.current_role() = 'patient'
  and created_by = auth.uid()
  and exists (select 1 from public.patients p where p.id = patient_id and p.user_id = auth.uid())
  and organisation_id = public.current_organisation_id()
);

create policy assessments_clinician_insert on public.weight_loss_assessments for insert
with check (
  public.current_role() in ('clinician','admin')
  and created_by = auth.uid()
  and public.can_access_patient(patient_id)
  and organisation_id = public.current_organisation_id()
);

create policy assessments_patient_update_draft on public.weight_loss_assessments for update
using (
  status = 'draft'
  and created_by = auth.uid()
  and exists (select 1 from public.patients p where p.id = patient_id and p.user_id = auth.uid())
)
with check (status in ('draft','completed') and created_by = auth.uid());

create policy assessments_clinician_update on public.weight_loss_assessments for update
using (public.current_role() in ('clinician','admin') and public.can_access_patient(patient_id))
with check (public.current_role() in ('clinician','admin') and public.can_access_patient(patient_id));

create policy meal_plans_select on public.meal_plans for select
using (public.can_access_patient(patient_id));

create policy meal_plans_write on public.meal_plans for insert
with check (
  created_by = auth.uid()
  and public.can_access_patient(patient_id)
  and organisation_id = public.current_organisation_id()
);

create policy meal_plans_update on public.meal_plans for update
using (created_by = auth.uid() or public.current_role() in ('clinician','admin'))
with check (public.can_access_patient(patient_id));

create policy documents_select on public.documents for select
using (
  public.can_access_patient(patient_id)
  and (public.current_role() in ('clinician','admin') or patient_visible = true)
);

create policy documents_clinician_write on public.documents for insert
with check (
  public.current_role() in ('clinician','admin')
  and created_by = auth.uid()
  and public.can_access_patient(patient_id)
);

create policy consents_select on public.consents for select
using (public.can_access_patient(patient_id));

create policy consents_insert on public.consents for insert
with check (
  recorded_by = auth.uid()
  and public.can_access_patient(patient_id)
  and organisation_id = public.current_organisation_id()
);

create policy audit_admin_select on public.audit_events for select
using (public.current_role() = 'admin' and organisation_id = public.current_organisation_id());

revoke insert, update, delete on public.audit_events from authenticated;

create or replace function public.log_audit_event(
  p_action text,
  p_entity_type text,
  p_entity_id uuid default null,
  p_patient_id uuid default null,
  p_request_id text default null,
  p_ip_hash text default null,
  p_user_agent_hash text default null,
  p_metadata jsonb default '{}'::jsonb
) returns bigint
language plpgsql
security definer
set search_path = public
as $$
declare new_id bigint;
begin
  if auth.uid() is null then raise exception 'authentication required'; end if;
  if p_patient_id is not null and not public.can_access_patient(p_patient_id) then raise exception 'forbidden'; end if;
  insert into public.audit_events (
    organisation_id, actor_user_id, patient_id, action, entity_type, entity_id,
    request_id, ip_hash, user_agent_hash, metadata
  ) values (
    public.current_organisation_id(), auth.uid(), p_patient_id, p_action, p_entity_type,
    p_entity_id, p_request_id, p_ip_hash, p_user_agent_hash, p_metadata
  ) returning id into new_id;
  return new_id;
end;
$$;

grant execute on function public.log_audit_event(text,text,uuid,uuid,text,text,text,jsonb) to authenticated;

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('patient-documents','patient-documents',false,10485760,array['application/pdf'])
on conflict (id) do nothing;

create policy patient_documents_read on storage.objects for select
using (
  bucket_id = 'patient-documents'
  and exists (
    select 1 from public.documents d
    where d.storage_path = name
      and public.can_access_patient(d.patient_id)
      and (public.current_role() in ('clinician','admin') or d.patient_visible = true)
  )
);

create policy patient_documents_clinician_insert on storage.objects for insert
with check (
  bucket_id = 'patient-documents'
  and public.current_role() in ('clinician','admin')
);

commit;
