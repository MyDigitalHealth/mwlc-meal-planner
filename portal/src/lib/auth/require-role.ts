import { redirect } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';

export type PortalRole = 'patient' | 'clinician' | 'admin';

export async function requireRole(allowed: PortalRole[]) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data: profile } = await supabase
    .from('user_profiles')
    .select('role,organisation_id,is_active,display_name')
    .eq('user_id', user.id)
    .single();

  if (!profile?.is_active || !allowed.includes(profile.role as PortalRole)) redirect('/dashboard');
  return { supabase, user, profile };
}
