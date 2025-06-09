import Link from 'next/link'; // Importar Link para el botón
import { AnimatedSection } from '@/components/animated-section';
import { ProjectCard } from '@/components/project-card';
import { BlogPostPreview } from '@/components/blog-post-preview';
import type { Project } from '@/types'; // Tipo Project para los proyectos de la API
import { FaBrain, FaCode, FaCube, FaQuoteLeft } from 'react-icons/fa'; // Iconos para áreas de enfoque y citas
import Image from 'next/image'; // Necesario para la imagen de fondo
import { API_V1_URL } from '@/lib/api-client'; // <--- AÑADIR IMPORTACIÓN
// IMPORTAR datos y funciones de LinkedIn
import { 
  getProcessedLinkedInPosts, 
  adaptLinkedInPostForHomePage,
  type HomePageBlogPost // Usaremos este tipo para los posts en la home
} from '@/lib/linkedin-posts-data';

// Helper para título de sección
const SectionTitle = ({ children }: { children: React.ReactNode }) => (
  <h2 className="text-3xl md:text-4xl font-semibold text-center mb-12">
    {children}
  </h2>
);

// Función para obtener datos de PROYECTOS de la API 
async function getHomepageProjects(): Promise<Project[]> {
  console.log('[getHomepageProjects] Usando API_V1_URL:', API_V1_URL);
  try {
    const projectsRes = await fetch(`${API_V1_URL}/portfolio/projects`, { cache: 'no-store' });
    if (!projectsRes.ok) {
      console.error(`Error fetching projects: ${projectsRes.status} ${projectsRes.statusText}`);
      throw new Error('Failed to fetch homepage projects');
    }
    const projects = await projectsRes.json();
    console.log('[getHomepageProjects] Proyectos recibidos de la API:', projects);
    return projects;
  } catch (error) {
    console.error("Error en getHomepageProjects:", error);
    throw error; 
  }
}

// Datos Placeholder para Testimonios
const testimonials = [
  {
    id: 't1',
    quote: "Iván has a unique ability to understand complex problems and translate them into effective AI solutions. His technological vision and product management were key.",
    name: "Pablo Motos",
    title: "CEO & Founder, El Hormiguero",
  },
  {
    id: 't2',
    quote: "Working with Iván on 3D development was exceptional. He brings creativity, technical rigor, and fluid communication.",
    name: "Pedro Sánchez",
    title: "Technical Director, La que te cuento",
  },
  // Añadir más si es necesario
];

export default async function HomePage() {
  let allProjects: Project[] = []; // Renamed from 'projects' for clarity
  let errorLoadingProjects = false;

  try {
      allProjects = await getHomepageProjects();
  } catch (error) {
      console.error("[HomePage] Error fetching projects:", error);
      errorLoadingProjects = true;
  }

  // Obtener y procesar los posts de LinkedIn para la Home
  let latestLinkedInPostsForHome: HomePageBlogPost[] = [];
  try {
    const allLinkedInPosts = getProcessedLinkedInPosts(); // Obtiene todos, ya ordenados
    latestLinkedInPostsForHome = allLinkedInPosts
      .slice(0, 3) // Tomar los 3 más recientes
      .map(adaptLinkedInPostForHomePage); // Adaptarlos al formato de BlogPostPreview
    
    console.log('[HomePage] latestLinkedInPostsForHome para mostrar:', JSON.stringify(latestLinkedInPostsForHome, null, 2));
  } catch (error) {
    console.error("[HomePage] Error al procesar posts de LinkedIn para la home:", error);
    // latestLinkedInPostsForHome permanecerá vacío
  }

  // Correctly filter for featured projects then slice
  const trulyFeaturedProjects = !errorLoadingProjects && Array.isArray(allProjects)
    ? allProjects.filter(p => p.videoUrl || p.is_featured)
    : [];
  const featuredProjectsForHomepage = trulyFeaturedProjects.slice(0, 2); // Take the first 2 of the truly featured

  return (
    <main className="flex flex-col items-center">
      {/* Hero Section */}
      <section className="w-full flex items-center justify-center min-h-[calc(100vh-80px)] py-20 md:py-32 lg:py-40 bg-gradient-to-br from-primary/5 via-background to-background dark:from-primary/10">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-foreground animate-fade-in-up">
            Iván In Tech
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-3xl mx-auto animate-fade-in-up animation-delay-200">
            AI Engineer exploring the intersection of artificial intelligence, 
            modern web development, and the technological future.
          </p>
          <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4 animate-fade-in-up animation-delay-400">
            <Link 
              href="/sobre-mi"
              className="inline-block bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-3 rounded-md text-lg font-medium transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 hover:brightness-110 shadow-lg hover:shadow-primary/30 w-full sm:w-auto"
            >
              About Me
            </Link>
            <Link 
              href="/portfolio"
              className="inline-block bg-muted text-muted-foreground hover:bg-border hover:text-foreground dark:hover:bg-muted/80 px-8 py-3 rounded-md text-lg font-medium transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 w-full sm:w-auto"
            >
              View Projects
            </Link>
          </div>
        </div>
      </section>

      {/* Featured Projects */}
      <AnimatedSection className="w-full py-16 md:py-24 bg-muted/30 dark:bg-muted/5">
        <div className="container mx-auto px-4">
          <SectionTitle>Featured Projects</SectionTitle>
          {errorLoadingProjects && (
            <p className="text-center text-destructive">Error loading projects.</p>
          )}
          {!errorLoadingProjects && featuredProjectsForHomepage.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {featuredProjectsForHomepage.map((project, index) => (
                <AnimatedSection key={project.id} delay={index * 0.1}>
                  <ProjectCard project={project} />
                </AnimatedSection>
              ))}
            </div>
          ) : null}
          {!errorLoadingProjects && featuredProjectsForHomepage.length === 0 && (
            <p className="text-center text-muted-foreground">No featured projects available at the moment.</p>
          )}
          <div className="text-center mt-12">
            <Link href="/portfolio" className="text-primary hover:underline font-medium">
              View all projects →
            </Link>
          </div>
        </div>
      </AnimatedSection>

      {/* Áreas de Enfoque */}
      <AnimatedSection className="w-full py-16 md:py-24">
        <div className="container mx-auto px-4">
          <SectionTitle>Focus Areas</SectionTitle>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="border border-border rounded-lg p-6 bg-background shadow-sm">
              <FaBrain className="w-10 h-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Artificial Intelligence</h3>
              <p className="text-muted-foreground text-sm">From predictive models and NLP to <strong className="font-medium text-foreground/80 dark:text-gray-300">Generative AI</strong> (Langchain, LLMs) for impactful solutions.</p>
            </div>
            <div className="border border-border rounded-lg p-6 bg-background shadow-sm">
              <FaCode className="w-10 h-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Modern Web Development</h3>
              <p className="text-muted-foreground text-sm">Robust and scalable full-stack applications with <strong className="font-medium text-foreground/80 dark:text-gray-300">FastAPI, Next.js, React</strong> and TypeScript.</p>
            </div>
            <div className="border border-border rounded-lg p-6 bg-background shadow-sm">
              <FaCube className="w-10 h-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Data & Digital Twins</h3>
              <p className="text-muted-foreground text-sm">Experience in <strong className="font-medium text-foreground/80 dark:text-gray-300">data analytics, KPIs</strong> and the potential of <strong className="font-medium text-foreground/80 dark:text-gray-300">Digital Twins</strong>.</p>
            </div>
          </div>
        </div>
      </AnimatedSection>

      {/* Últimas Entradas del Blog */}
      <AnimatedSection className="w-full py-16 md:py-24 bg-muted/30 dark:bg-muted/5">
        <div className="container mx-auto px-4">
          <SectionTitle>From the Blog (LinkedIn)</SectionTitle>
          {latestLinkedInPostsForHome.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {latestLinkedInPostsForHome.map((post, index) => (
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
          ) : (
            <p className="text-center text-muted-foreground">No recent LinkedIn activity to display.</p>
          )}
          <div className="text-center mt-12">
            <Link href="/blog" className="text-primary hover:underline font-medium">
              View all LinkedIn activity →
            </Link>
          </div>
        </div>
      </AnimatedSection>

      {/* Testimonios */}
      <AnimatedSection className="w-full py-16 md:py-24">
        <div className="container mx-auto px-4">
          <SectionTitle>What They Say</SectionTitle>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {testimonials.map((testimonial, index) => (
              <AnimatedSection 
                key={testimonial.id} 
                delay={index * 0.1}
                className="border border-border rounded-lg p-6 bg-muted/50 dark:bg-muted/10 shadow-sm flex flex-col items-center text-center"
              >
                <FaQuoteLeft className="w-8 h-8 text-primary/50 dark:text-primary/40 mb-4" />
                <blockquote className="italic text-foreground/90 dark:text-foreground/80 mb-4">
                  “{testimonial.quote}”
                </blockquote>
                <p className="font-semibold text-foreground">{testimonial.name}</p>
                <p className="text-sm text-muted-foreground">{testimonial.title}</p>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </AnimatedSection>
      
      {/* Nueva Sección: Filosofía / Inspiración */}
      <AnimatedSection className="w-full relative py-32 md:py-48 overflow-hidden">
          <Image
            src="/img/ivan-thinking-near-the-sea.jpg"
            fill
            style={{ objectFit: "cover" }}
            alt="Iván thinking"
            className="absolute inset-0 z-0 filter brightness-50 dark:brightness-40 object-cover object-top"
            priority
         />
         <div className="container mx-auto px-4 relative z-10 text-center text-white">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-semibold mb-6">
               Technology is a tool, the true odyssey lies in how we use it to explore the unknown.
            </h2>
            <p className="text-lg text-gray-300">
               - Iván In Tech (Inspired by nature and the dystopian)
            </p>
         </div>
      </AnimatedSection>

      {/* CTA Final */}
      <AnimatedSection className="w-full py-20 md:py-32 text-center">
         <div className="container mx-auto px-4">
            <h2 className="text-3xl md:text-4xl font-semibold mb-6">Ready to collaborate or connect?</h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-xl mx-auto">Let&apos;s talk about your next project or innovative idea.</p>
            <Link href="/contacto" className="inline-block bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-3 rounded-md text-lg font-medium transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 hover:brightness-110 shadow-lg hover:shadow-primary/30">
               Contact Me
            </Link>
    </div>
      </AnimatedSection>

    </main>
  );
}
