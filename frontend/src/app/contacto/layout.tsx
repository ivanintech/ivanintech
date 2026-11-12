import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Contacto',
  description: 'Hablemos de tu proyecto de IA o desarrollo web.',
  alternates: { canonical: '/contacto' },
  openGraph: {
    title: `Contacto | Iván In Tech`,
    description: 'Hablemos de tu proyecto de IA o desarrollo web.',
    url: '/contacto',
    type: 'website',
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
