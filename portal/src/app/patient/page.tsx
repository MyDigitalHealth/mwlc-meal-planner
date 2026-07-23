import { redirect } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';

export default async function PatientDashboard() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data: patient } = await supabase
    .from('patients')
    .select('id,preferred_name')
    .eq('user_id', user.id)
    .single();
  if (!patient) redirect('/login?error=patient_record_missing');

  const [{ data: assessments }, { data: plans }] = await Promise.all([
    supabase.from('weight_loss_assessments').select('id,status,questionnaire_version,created_at,completed_at').eq('patient_id', patient.id).order('created_at', { ascending: false }).limit(10),
    supabase.from('meal_plans').select('id,status,planner_version,created_at,approved_at').eq('patient_id', patient.id).order('created_at', { ascending: false }).limit(10),
  ]);

  return <><header className="portal-header"><div className="portal-brand"><span>Patient portal</span>My Weight Loss Clinic</div><form action="/auth/signout" method="post"><button type="submit">Sign out</button></form></header><main className="portal-shell"><p className="eyebrow">Welcome back</p><h1>{patient.preferred_name || 'Your health profile'}</h1><div className="dashboard-grid"><section className="card"><h2>Weight-loss profiles</h2><div className="metric">{assessments?.length || 0}</div><p className="muted">Saved assessments and results.</p></section><section className="card"><h2>Meal plans</h2><div className="metric">{plans?.length || 0}</div><p className="muted">Generated and clinician-approved plans.</p></section><section className="card"><h2>Privacy</h2><p className="muted">Only you and authorised members of your clinical team can access these records.</p></section></div><section className="card" style={{marginTop:16}}><h2>Recent activity</h2><div className="list">{assessments?.length ? assessments.map(item=><div className="list-item" key={item.id}><div><strong>Weight-loss profile</strong><div className="muted">{new Date(item.created_at).toLocaleDateString('en-AU')}</div></div><span className="badge">{item.status}</span></div>) : <p className="muted">No saved profile yet.</p>}</div></section></main></>;
}
