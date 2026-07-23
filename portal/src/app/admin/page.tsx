import { requireRole } from '@/lib/auth/require-role';

export default async function AdminDashboard() {
  const { supabase, profile } = await requireRole(['admin']);
  const [{ count: users }, { count: patients }, { count: auditEvents }] = await Promise.all([
    supabase.from('user_profiles').select('*', { count: 'exact', head: true }),
    supabase.from('patients').select('*', { count: 'exact', head: true }),
    supabase.from('audit_events').select('*', { count: 'exact', head: true }),
  ]);

  return <><header className="portal-header"><div className="portal-brand"><span>Administrator portal</span>My Weight Loss Clinic</div><form action="/auth/signout" method="post"><button type="submit">Sign out</button></form></header><main className="portal-shell"><p className="eyebrow">Organisation administration</p><h1>{profile.display_name || 'Portal administration'}</h1><div className="dashboard-grid"><section className="card"><h2>Portal users</h2><div className="metric">{users || 0}</div></section><section className="card"><h2>Patients</h2><div className="metric">{patients || 0}</div></section><section className="card"><h2>Audit events</h2><div className="metric">{auditEvents || 0}</div></section></div><section className="card" style={{marginTop:16}}><h2>Security controls</h2><p className="muted">Role assignment, clinician-patient access, invitation management and audit review are restricted to administrators. Clinician MFA enforcement will be applied through Supabase Auth assurance levels before production.</p></section></main></>;
}
