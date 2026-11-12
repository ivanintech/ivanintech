export const dynamic = 'force-dynamic';

import { Suspense } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { FaBrain, FaCode, FaCube } from 'react-icons/fa';
import { AnimatedSection } from '@/components/animated-section';
import { ProjectCard } from '@/components/project-card';
import { BlogPostPreview } from '@/components/blog-post-preview';
import { ProjectCardSkeleton } from '@/components/project-card-skeleton';
import { BlogPostPreviewSkeleton } from '@/components/blog-post-preview-skeleton';
import type { Project, HomePageBlogPost } from '@/types';
import { API_V1_URL } from '@/lib/api-client';
import { getProcessedLinkedInPosts, adaptLinkedInPostForHomePage } from '@/lib/linkedin-posts-data';

// --- DATA FETCHING ---

async function getHomepageProjects(): Promise<Project[]> {
  try {
    // Esta llamada ahora se beneficia del cacheo por defecto de fetch en Next.js.
    // Timeout explícito: si el backend (free tier de Render) está arrancando o
    // tarda en despertar, el render del servidor no debe quedarse colgado ni
    // tumbar la home con un error boundary.
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 12000);
    let projectsRes: Response;
    try {
      projectsRes = await fetch(`${API_V1_URL}/projects`, {
        next: { revalidate: 3600 },
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeoutId);
    }
    if (!projectsRes.ok) {
      throw new Error(`backend respondió ${projectsRes.status}`);
    }
    const projects = await projectsRes.json();
    return projects.filter((p: Project) => p.videoUrl || p.is_featured).slice(0, 2);
  } catch (error) {
    // NO se relanza: la home debe renderizar siempre. Se degrada a sin
    // proyectos destacados en el peor caso, en vez de mostrar una pantalla
    // de error al visitante (y de inundar los logs en bucle).
    console.error("getHomepageProjects degradado:", (error as Error)?.message);
    return [];
  }
}

async function getHomepageBlogPosts(): Promise<HomePageBlogPost[]> {
  // Esta función ahora es asíncrona para simular una posible llamada a API en el futuro
  // y para mantener la consistencia con getHomepageProjects.
  const allLinkedInPosts = getProcessedLinkedInPosts();
  return allLinkedInPosts.slice(0, 3).map(adaptLinkedInPostForHomePage);
}

// --- ASYNC COMPONENTS FOR STREAMING ---

async function FeaturedProjectsList() {
  const projects = await getHomepageProjects();
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {projects.map((project, index) => (
        <AnimatedSection key={project.id} delay={index * 0.1}>
          <ProjectCard project={project} />
        </AnimatedSection>
      ))}
    </div>
  );
}

async function LatestBlogPostsList() {
  const posts = await getHomepageBlogPosts();
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {posts.map((post, index) => (
        <AnimatedSection key={post.id || index} delay={index * 0.1}>
          <BlogPostPreview
            post={post}
            isLinkedInEmbed={true}
            linkedInUrl={post.linkedInUrl}
            embedCode={post.embedCode}
          />
        </AnimatedSection>
      ))}
    </div>
  );
}

// --- UI COMPONENTS ---

const SectionTitle = ({ children }: { children: React.ReactNode }) => (
  <h2 className="text-3xl md:text-4xl font-semibold text-center mb-12">
    {children}
  </h2>
);

// Sin testimonios inventados: en un portfolio para recruiters, un testimonio falso
// (o atribuido a alguien que no lo dijo) destruye más credibilidad de la que aporta.
// Este bloque muestra hechos verificables en su lugar.

const facts = [
  {
    id: 'f1',
    label: 'Experiencia',
    value: '5 años',
    detail: 'IA/ML en IMMERSIA: de prototipo a producción.',
  },
  {
    id: 'f2',
    label: 'Este sitio',
    value: 'Full-stack',
    detail: 'Next.js 15 + FastAPI + Postgres. Backend propio, ~9.000 líneas.',
  },
  {
    id: 'f3',
    label: 'Pipeline de IA',
    value: '$0,0001',
    detail: 'Coste por noticia del radar: scraping + redacción con LLM.',
  },
  {
    id: 'f4',
    label: 'Formación',
    value: 'Máster IA',
    detail: 'Especialización en IA aplicada y análisis de datos.',
  },
];

// --- MAIN PAGE COMPONENT ---

export default function HomePage() {
  return (
    <main className="flex flex-col items-center">
      {/* Hero Section */}
      <section className="w-full flex items-center justify-center min-h-[calc(100vh-80px)] py-20 md:py-32 lg:py-40 bg-gradient-to-br from-primary/5 via-background to-background dark:from-primary/10">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-foreground animate-fade-in-up">
            Iván In Tech
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-3xl mx-auto animate-fade-in-up animation-delay-200">
            Ingeniero IA explorando la intersección de la inteligencia artificial, 
            el desarrollo web moderno y el futuro tecnológico.
          </p>
          <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4 animate-fade-in-up animation-delay-400">
            <Link
              href="/sobre-mi"
              className="inline-block bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-3 rounded-md text-lg font-medium transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 hover:brightness-110 shadow-lg hover:shadow-primary/30 w-full sm:w-auto"
            >
              Sobre Mí
            </Link>
            <Link
              href="/portfolio"
              className="inline-block bg-muted text-muted-foreground hover:bg-border hover:text-foreground dark:hover:bg-muted/80 px-8 py-3 rounded-md text-lg font-medium transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 w-full sm:w-auto"
            >
              Ver Proyectos
            </Link>
          </div>
        </div>
      </section>

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

      {/* Hechos verificables (antes: testimonios inventados) */}
      <AnimatedSection className="w-full py-16 md:py-24">
        <div className="container mx-auto px-4">
          <SectionTitle>Datos, no promesas</SectionTitle>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {facts.map((fact, index) => (
              <AnimatedSection
                key={fact.id}
                delay={index * 0.1}
                className="border border-border rounded-lg p-6 bg-muted/50 dark:bg-muted/10 shadow-sm flex flex-col items-center text-center"
              >
                <span className="text-xs uppercase tracking-widest text-muted-foreground mb-2">
                  {fact.label}
                </span>
                <p className="text-2xl md:text-3xl font-semibold text-primary mb-3">
                  {fact.value}
                </p>
                <p className="text-sm text-muted-foreground">{fact.detail}</p>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </AnimatedSection>
      
      {/* Philosophy Section */}
      <AnimatedSection className="w-full relative py-32 md:py-48 overflow-hidden">
        <Image
          src="/img/ivan-thinking-near-the-sea.jpg"
          fill
          style={{ objectFit: "cover" }}
          alt="Iván pensando cerca del mar"
          className="absolute inset-0 z-0 filter brightness-50 dark:brightness-40 object-cover object-top"
          priority
        />
        <div className="container mx-auto px-4 relative z-10 text-center text-white">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-semibold mb-6">
            La tecnología es una herramienta, la verdadera odisea reside en cómo la usamos para explorar lo desconocido.
          </h2>
          <p className="text-lg text-gray-300">
            - Iván In Tech (Inspirado por la naturaleza y lo distópico)
          </p>
        </div>
      </AnimatedSection>

      {/* Final CTA */}
      <AnimatedSection className="w-full py-20 md:py-32 text-center">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-semibold mb-6">¿Listo para colaborar o conectar?</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-xl mx-auto">Hablemos sobre tu próximo proyecto o idea innovadora.</p>
          <Link href="/contacto" className="inline-block bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-3 rounded-md text-lg font-medium transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 hover:brightness-110 shadow-lg hover:shadow-primary/30">
            Contáctame
          </Link>
        </div>
      </AnimatedSection>
    </main>
  );
}

// --- SKELETON COMPONENTS FOR SUSPENSE FALLBACK ---

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
      <BlogPostPreviewSkeleton />
      <BlogPostPreviewSkeleton />
      <BlogPostPreviewSkeleton />
    </div>
  );
}
