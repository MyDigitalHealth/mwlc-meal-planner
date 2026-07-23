import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'My Weight Loss Clinic Portal',
  description: 'Secure patient and clinician access to weight-loss profiles and meal plans.',
  robots: { index: false, follow: false, nocache: true },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
