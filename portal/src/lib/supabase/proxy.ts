import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({ request });
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  if (!url || !key) return response;

  const supabase = createServerClient(url, key, {
    cookies: {
      getAll: () => request.cookies.getAll(),
      setAll: (items) => {
        items.forEach(({ name, value }) => request.cookies.set(name, value));
        response = NextResponse.next({ request });
        items.forEach(({ name, value, options }) => response.cookies.set(name, value, options));
      },
    },
  });

  const { data: { user } } = await supabase.auth.getUser();
  const path = request.nextUrl.pathname;
  const protectedPath = path.startsWith('/patient') || path.startsWith('/clinician') || path.startsWith('/admin');
  if (protectedPath && !user) {
    const destination = request.nextUrl.clone();
    destination.pathname = '/login';
    destination.searchParams.set('next', path);
    return NextResponse.redirect(destination);
  }
  if (user && path === '/login') {
    const destination = request.nextUrl.clone();
    destination.pathname = '/dashboard';
    destination.search = '';
    return NextResponse.redirect(destination);
  }
  return response;
}
