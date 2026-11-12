import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Recursos',
  description: 'Enlaces y recursos sobre IA, desarrollo y datos seleccionados por Iván.',
  alternates: { canonical: '/recursos' },
  openGraph: {
    title: `Recursos | Iván In Tech`,
    description: 'Enlaces y recursos sobre IA, desarrollo y datos seleccionados por Iván.',
    url: '/recursos',
    type: 'website',
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
