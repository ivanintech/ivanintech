import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sobre mí',
  description: 'Trayectoria, formación y áreas de especialización de Iván In Tech.',
  alternates: { canonical: '/sobre-mi' },
  openGraph: {
    title: `Sobre mí | Iván In Tech`,
    description: 'Trayectoria, formación y áreas de especialización de Iván In Tech.',
    url: '/sobre-mi',
    type: 'website',
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
