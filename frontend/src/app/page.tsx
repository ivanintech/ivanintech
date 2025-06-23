import { Suspense } from 'react';
import Link from 'next/link';
import { FaBrain, FaCode, FaCube, FaQuoteLeft } from 'react-icons/fa';
import { AnimatedSection } from '@/components/ui/animated-section';
import { ProjectCardSkeleton } from '@/components/portfolio/project-card-skeleton';
import { Skeleton } from '@/components/ui/skeleton';
import { PhilosophySection } from '@/components/home/PhilosophySection';
import { FeaturedProjectsList } from '@/components/home/FeaturedProjectsList';
import { LatestBlogPostsList } from '@/components/home/LatestBlogPostsList';
import { HeroSection } from '@/components/home/HeroSection';
import { HeroBackgroundCarousel } from '@/components/home/HeroBackgroundCarousel';

const SectionTitle = ({ children }: { children: React.ReactNode }) => (
  <h2 className="text-3xl md:text-4xl font-semibold text-center mb-12">
    {children}
  </h2>
);

const testimonials = [
  {
    id: 't1',
    quote: "Iván tiene una habilidad única para entender problemas complejos y traducirlos en soluciones de IA efectivas. Su visión tecnológica y gestión del producto fueron clave.",
    name: "Pablo Motos",
    title: "CEO & Fundador, El Hormiguero",
  },
  {
    id: 't2',
    quote: "Trabajar con Iván en el desarrollo 3D fue excepcional. Aporta creatividad, rigor técnico y una comunicación fluida.",
    name: "Pedro Sánchez",
    title: "Director Técnico, La que te cuento",
  },
];

export default function HomePage() {
  return (
    <main className="flex flex-col items-center">
      <HeroSection>
        <HeroBackgroundCarousel />
      </HeroSection>

      {/* Featured Projects */}
      <AnimatedSection className="w-full py-16 md:py-24 bg-muted/30 dark:bg-muted/5">
        <div className="container mx-auto px-4">
          <SectionTitle>Proyectos Destacados</SectionTitle>
          <Suspense fallback={<FeaturedProjectsSkeleton />}>
            <FeaturedProjectsList />
          </Suspense>
          <div className="text-center mt-12">
            <Link href="/portfolio" className="text-primary hover:underline font-medium">
              Ver todos los proyectos →
            </Link>
          </div>
        </div>
      </AnimatedSection>

      {/* Focus Areas */}
      <AnimatedSection className="w-full py-16 md:py-24">
        <div className="container mx-auto px-4">
          <SectionTitle>Áreas de Enfoque</SectionTitle>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="border border-border rounded-lg p-6 bg-background shadow-sm">
              <FaBrain className="w-10 h-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Inteligencia Artificial</h3>
              <p className="text-muted-foreground text-sm">Desde modelos predictivos y NLP hasta <strong className="font-medium text-foreground/80 dark:text-gray-300">IA Generativa</strong> (Langchain, LLMs) para soluciones de impacto.</p>
            </div>
            <div className="border border-border rounded-lg p-6 bg-background shadow-sm">
              <FaCode className="w-10 h-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Desarrollo Web Moderno</h3>
              <p className="text-muted-foreground text-sm">Aplicaciones full-stack robustas y escalables con <strong className="font-medium text-foreground/80 dark:text-gray-300">FastAPI, Next.js, React</strong> y TypeScript.</p>
            </div>
            <div className="border border-border rounded-lg p-6 bg-background shadow-sm">
              <FaCube className="w-10 h-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Datos y Gemelos Digitales</h3>
              <p className="text-muted-foreground text-sm">Experiencia en <strong className="font-medium text-foreground/80 dark:text-gray-300">analítica de datos, KPIs</strong> y el potencial de los <strong className="font-medium text-foreground/80 dark:text-gray-300">Gemelos Digitales</strong>.</p>
            </div>
          </div>
        </div>
      </AnimatedSection>

      {/* Latest Blog Posts */}
      <AnimatedSection className="w-full py-16 md:py-24 bg-muted/30 dark:bg-muted/5">
        <div className="container mx-auto px-4">
          <SectionTitle>Del Blog (Actividad en LinkedIn)</SectionTitle>
          <Suspense fallback={<LatestBlogPostsSkeleton />}>
            <LatestBlogPostsList />
          </Suspense>
          <div className="text-center mt-12">
            <Link href="/blog" className="text-primary hover:underline font-medium">
              Ver toda la actividad de LinkedIn →
            </Link>
          </div>
        </div>
      </AnimatedSection>

      {/* Philosophy */}
      <PhilosophySection />

      {/* Testimonials */}
      <AnimatedSection className="w-full py-16 md:py-24">
        <div className="container mx-auto px-4">
          <SectionTitle>Lo que dicen de mi trabajo</SectionTitle>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {testimonials.map((testimonial) => (
              <div key={testimonial.id} className="border border-border rounded-lg p-6 bg-background shadow-sm text-center">
                <FaQuoteLeft className="w-8 h-8 text-primary/50 mx-auto mb-4" />
                <p className="text-muted-foreground mb-4 italic">&quot;{testimonial.quote}&quot;</p>
                <p className="font-semibold">{testimonial.name}</p>
                <p className="text-sm text-muted-foreground">{testimonial.title}</p>
              </div>
            ))}
          </div>
        </div>
      </AnimatedSection>
    </main>
  );
}

function FeaturedProjectsSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      <ProjectCardSkeleton />
      <ProjectCardSkeleton />
    </div>
  );
}

function LatestBlogPostsSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      <Skeleton className="h-[250px] rounded-lg" />
      <Skeleton className="h-[250px] rounded-lg" />
      <Skeleton className="h-[250px] rounded-lg" />
    </div>
  );
}
