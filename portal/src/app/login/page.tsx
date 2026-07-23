import { sendMagicLink } from './actions';

export default async function LoginPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const params = await searchParams;
  const sent = params.sent === '1';
  const error = typeof params.error === 'string' ? params.error : null;
  const next = typeof params.next === 'string' ? params.next : '/dashboard';

  return (
    <main className="auth-shell">
      <section className="auth-card" aria-labelledby="login-title">
        <div className="brand-mark">MW</div>
        <p className="eyebrow">My Weight Loss Clinic</p>
        <h1 id="login-title">Secure profile access</h1>
        <p className="muted">Enter the email address registered with the clinic. We will send a single-use sign-in link.</p>
        {sent ? <div className="notice success">Check your email. The link expires and can only be used to establish an authenticated session.</div> : null}
        {error ? <div className="notice error">That link could not be used. Request a new secure sign-in link.</div> : null}
        <form action={sendMagicLink}>
          <input type="hidden" name="next" value={next} />
          <label htmlFor="email">Email address</label>
          <input id="email" name="email" type="email" autoComplete="email" required maxLength={254} placeholder="name@example.com" />
          <button type="submit">Email my secure link</button>
        </form>
        <p className="fine">For privacy, the same confirmation is shown whether or not an address is registered.</p>
      </section>
    </main>
  );
}
