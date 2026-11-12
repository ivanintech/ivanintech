import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Noticias IA',
  description: 'Radar diario de noticias de inteligencia artificial, filtradas y puntuadas.',
  alternates: { canonical: '/noticias' },
  openGraph: {
    title: `Noticias IA | Iván In Tech`,
    description: 'Radar diario de noticias de inteligencia artificial, filtradas y puntuadas.',
    url: '/noticias',
    type: 'website',
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
