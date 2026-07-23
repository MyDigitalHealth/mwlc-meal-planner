import { redirect } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';

export default async function DashboardRouter() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data: profile, error } = await supabase
    .from('user_profiles')
    .select('role,is_active')
    .eq('user_id', user.id)
    .single();

  if (error || !profile?.is_active) redirect('/login?error=account_unavailable');
  if (profile.role === 'admin') redirect('/admin');
  if (profile.role === 'clinician') redirect('/clinician');
  redirect('/patient');
}
