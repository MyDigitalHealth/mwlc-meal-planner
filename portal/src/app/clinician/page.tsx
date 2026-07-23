import { requireRole } from '@/lib/auth/require-role';

export default async function ClinicianDashboard() {
  const { supabase, user, profile } = await requireRole(['clinician','admin']);
  const { data: assignments } = await supabase
    .from('clinician_patient_assignments')
    .select('patient_id,patients(id,preferred_name,external_reference,updated_at)')
    .eq('clinician_user_id', user.id)
    .eq('active', true)
    .order('assigned_at', { ascending: false });

  return <><header className="portal-header"><div className="portal-brand"><span>Clinician portal</span>My Weight Loss Clinic</div><form action="/auth/signout" method="post"><button type="submit">Sign out</button></form></header><main className="portal-shell"><p className="eyebrow">Clinical workspace</p><h1>{profile.display_name || 'Assigned patients'}</h1><section className="card"><h2>Patient list</h2><div className="list">{assignments?.length ? assignments.map((row:any)=><div className="list-item" key={row.patient_id}><div><strong>{row.patients?.preferred_name || 'Patient'}</strong><div className="muted">Reference: {row.patients?.external_reference || 'Not recorded'}</div></div><a className="button" href={`/clinician/patients/${row.patient_id}`}>Open profile</a></div>) : <p className="muted">No active patient assignments.</p>}</div></section></main></>;
}
