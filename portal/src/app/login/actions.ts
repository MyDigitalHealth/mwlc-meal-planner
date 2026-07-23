'use server';

import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import { z } from 'zod';
import { createClient } from '@/lib/supabase/server';

const schema = z.object({ email: z.string().trim().email().max(254), next: z.string().optional() });

export async function sendMagicLink(formData: FormData) {
  const parsed = schema.safeParse({ email: formData.get('email'), next: formData.get('next') });
  if (!parsed.success) redirect('/login?error=invalid_email');

  const headerStore = await headers();
  const origin = process.env.NEXT_PUBLIC_SITE_URL || headerStore.get('origin');
  if (!origin) throw new Error('Site URL is not configured.');
  const safeNext = parsed.data.next?.startsWith('/') && !parsed.data.next.startsWith('//') ? parsed.data.next : '/dashboard';
  const supabase = await createClient();
  const { error } = await supabase.auth.signInWithOtp({
    email: parsed.data.email.toLowerCase(),
    options: {
      shouldCreateUser: false,
      emailRedirectTo: `${origin}/auth/callback?next=${encodeURIComponent(safeNext)}`,
    },
  });

  // Avoid disclosing whether an email exists.
  if (error) console.error('[magic-link]', error.code);
  redirect('/login?sent=1');
}
