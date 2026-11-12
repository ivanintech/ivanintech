import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Portafolio',
  description: 'Proyectos de IA, desarrollo web y datos de Iván In Tech.',
  alternates: { canonical: '/portfolio' },
  openGraph: {
    title: `Portafolio | Iván In Tech`,
    description: 'Proyectos de IA, desarrollo web y datos de Iván In Tech.',
    url: '/portfolio',
    type: 'website',
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
