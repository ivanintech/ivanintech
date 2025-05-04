import Link from 'next/link'; // Importar Link para el botón
import { AnimatedSection } from '@/components/animated-section';
import { ProjectCard } from '@/components/project-card';
import { BlogPostPreview } from '@/components/blog-post-preview';
import type { Project, BlogPost } from '@/lib/types'; // Importar tipos
import { API_V1_URL } from '@/lib/api-client'; // Importar URL base
import { FaBrain, FaCode, FaCube, FaQuoteLeft } from 'react-icons/fa'; // Iconos para áreas de enfoque y citas
import Image from 'next/image'; // Necesario para la imagen de fondo

// Helper para título de sección
const SectionTitle = ({ children }: { children: React.ReactNode }) => (
  <h2 className="text-3xl md:text-4xl font-semibold text-center mb-12">
    {children}
  </h2>
);

// Funciones para obtener datos de la API (¡Ahora lanza errores!)
async function getHomepageData(): Promise<{ projects: Project[], posts: BlogPost[] }> {
  try {
    const [projectsRes, postsRes] = await Promise.all([
      fetch(`${API_V1_URL}/portfolio/projects`, { next: { revalidate: 3600 } }),
      fetch(`${API_V1_URL}/content/blog`, { next: { revalidate: 3600 } }) // <- Endpoint correcto?
    ]);

    if (!projectsRes.ok) {
      throw new Error(`Error ${projectsRes.status}: Fallo al obtener proyectos (${projectsRes.statusText})`);
    }
    if (!postsRes.ok) {
       // Loguear respuesta de error antes de lanzar
      const errorText = await postsRes.text();
      console.error(`[getHomepageData] Error ${postsRes.status} al obtener posts: ${errorText}`);
      throw new Error(`Error ${postsRes.status}: Fallo al obtener posts (${postsRes.statusText})`);
    }

    const rawPostsResponse = await postsRes.text();
    console.log('[getHomepageData] Respuesta CRUDA de /content/blog:', rawPostsResponse);

    const postsData = JSON.parse(rawPostsResponse);

    // -------- LOG AÑADIDO 1 --------
    console.log('[getHomepageData] Posts recibidos de la API:', JSON.stringify(postsData, null, 2));
    // -------------------------------

    const projects = await projectsRes.json();

    return { projects, posts: postsData };

  } catch (error) {
    console.error("Error detallado en getHomepageData:", error);
    // Relanzar para que el Error Boundary lo capture
    throw new Error('No se pudieron cargar los datos principales de la página. Verifica la consola del servidor y del navegador.');
  }
}

// Datos Placeholder para Testimonios
const testimonials = [
  {
    id: 't1',
    quote: "Iván tiene una capacidad única para entender problemas complejos y traducirlos en soluciones de IA efectivas. Su visión tecnológica y gestión del producto fueron clave.",
    name: "Pablo Motos",
    title: "CEO & Fundador, El Hormiguero",
  },
  {
    id: 't2',
    quote: "Trabajar con Iván en el desarrollo 3D fue excepcional. Aporta creatividad, rigor técnico y una comunicación fluida.",
    name: "Pedro Sánchez",
    title: "Director Técnico, La que te cuento",
  },
  // Añadir más si es necesario
];

export default async function HomePage() {
  let projects: Project[] = [];
  let posts: BlogPost[] = [];
  let errorLoadingData = false; // Flag para manejar errores

  try {
      const data = await getHomepageData();
      projects = data.projects;
      posts = data.posts;
  } catch (error) {
      console.error("[HomePage] Error al obtener datos:", error);
      errorLoadingData = true;
      // No necesitas relanzar aquí si tienes un Error Boundary (error.tsx)
      // o si manejas el estado de error en el renderizado
  }

  // -------- LOG AÑADIDO 2 --------
  console.log('[HomePage] Posts recibidos (después de getHomepageData):', JSON.stringify(posts, null, 2));
  // -------------------------------

  // Procesar datos SOLO si no hubo error y posts existe
  let latestPosts: BlogPost[] = [];
  if (!errorLoadingData && Array.isArray(posts)) {
      try {
        latestPosts = [...posts]
          .sort((a, b) => {
            // Añadir validación por si published_date no es una fecha válida
            const dateA = new Date(a.published_date).getTime();
            const dateB = new Date(b.published_date).getTime();
            if (isNaN(dateA) || isNaN(dateB)) {
              console.warn('[HomePage] Fecha inválida encontrada al ordenar:', a, b);
              return 0; // No cambiar orden si hay fecha inválida
            }
            return dateB - dateA;
          })
          .slice(0, 3);
      } catch (sortError) {
           console.error("[HomePage] Error al procesar/ordenar posts:", sortError, posts);
           // latestPosts permanecerá vacío si hay error aquí
      }
  } else if (!errorLoadingData) {
      console.warn("[HomePage] 'posts' no es un array o está indefinido:", posts);
  }

  // -------- LOG AÑADIDO 3 --------
  console.log('[HomePage] latestPosts procesados:', JSON.stringify(latestPosts, null, 2));
  // -------------------------------

  const featuredProjects = Array.isArray(projects) ? projects.slice(0, 2) : [];

  return (
    <main className="flex flex-col items-center">
      {/* Hero Section */}
      <section className="w-full flex items-center justify-center min-h-[calc(100vh-80px)] py-20 md:py-32 lg:py-40 bg-gradient-to-br from-primary/5 via-background to-background dark:from-primary/10">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-foreground animate-fade-in-up">
            Iván In Tech
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-3xl mx-auto animate-fade-in-up animation-delay-200">
            Ingeniero IA explorando la intersección entre la inteligencia artificial, 
            el desarrollo web moderno y el futuro tecnológico.
          </p>
          <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4 animate-fade-in-up animation-delay-400">
            <Link 
              href="/sobre-mi"
              className="inline-block bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-3 rounded-md text-lg font-medium transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 hover:brightness-110 shadow-lg hover:shadow-primary/30 w-full sm:w-auto"
            >
              Conóceme
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

      {/* Proyectos Destacados */}
      <AnimatedSection className="w-full py-16 md:py-24 bg-muted/30 dark:bg-muted/5">
        <div className="container mx-auto px-4">
          <SectionTitle>Proyectos Destacados</SectionTitle>
          {/* Mostrar sección solo si hay proyectos, si hubo error, error.tsx se encarga */}
          {featuredProjects.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {featuredProjects.map((project, index) => (
                <AnimatedSection key={project.id} delay={index * 0.1}>
                  <ProjectCard project={project} />
                </AnimatedSection>
              ))}
            </div>
          ) : (
             /* Mostrar mensaje solo si la API devolvió OK pero array vacío */
            <p className="text-center text-muted-foreground">No hay proyectos destacados disponibles por el momento.</p>
          )}
          <div className="text-center mt-12">
            <Link href="/portfolio" className="text-primary hover:underline font-medium">
              Ver todos los proyectos →
            </Link>
          </div>
        </div>
      </AnimatedSection>

      {/* Áreas de Enfoque */}
      <AnimatedSection className="w-full py-16 md:py-24">
        <div className="container mx-auto px-4">
          <SectionTitle>Áreas de Enfoque</SectionTitle>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="border border-border rounded-lg p-6 bg-background shadow-sm">
              <FaBrain className="w-10 h-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Inteligencia Artificial</h3>
              <p className="text-muted-foreground text-sm">Desde modelos predictivos y NLP hasta <strong className="font-medium text-foreground/80 dark:text-gray-300">IA Generativa</strong> (Langchain, LLMs) para soluciones con impacto.</p>
            </div>
            <div className="border border-border rounded-lg p-6 bg-background shadow-sm">
              <FaCode className="w-10 h-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Desarrollo Web Moderno</h3>
              <p className="text-muted-foreground text-sm">Aplicaciones full-stack robustas y escalables con <strong className="font-medium text-foreground/80 dark:text-gray-300">FastAPI, Next.js, React</strong> y TypeScript.</p>
            </div>
            <div className="border border-border rounded-lg p-6 bg-background shadow-sm">
              <FaCube className="w-10 h-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Datos & Digital Twins</h3>
              <p className="text-muted-foreground text-sm">Experiencia en <strong className="font-medium text-foreground/80 dark:text-gray-300">analítica de datos, KPIs</strong> y el potencial de los <strong className="font-medium text-foreground/80 dark:text-gray-300">Gemelos Digitales</strong>.</p>
            </div>
          </div>
        </div>
      </AnimatedSection>

      {/* Últimas Entradas del Blog */}
      <AnimatedSection className="w-full py-16 md:py-24 bg-muted/30 dark:bg-muted/5">
        <div className="container mx-auto px-4">
          <SectionTitle>Desde el Blog</SectionTitle>
          {/* Mensaje de error si falló la carga */}
          {errorLoadingData && (
              <p className="text-center text-destructive">Error al cargar las entradas del blog.</p>
          )}
          {/* Mostrar posts si no hubo error y hay posts */}
          {!errorLoadingData && latestPosts.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {latestPosts.map((post, index) => (
                <AnimatedSection key={post.id || index} delay={index * 0.1}> {/* Añadir fallback key */}
                  <BlogPostPreview post={post} />
                </AnimatedSection>
              ))}
            </div>
          ) : null /* Ocultar si errorLoadingData es true */}
          {/* Mostrar mensaje si no hubo error pero no hay posts */}
          {!errorLoadingData && latestPosts.length === 0 && (
            <p className="text-center text-muted-foreground">No hay entradas de blog recientes disponibles.</p>
          )}
          <div className="text-center mt-12">
            <Link href="/blog" className="text-primary hover:underline font-medium">
              Leer más en el blog →
            </Link>
          </div>
        </div>
      </AnimatedSection>

      {/* Testimonios */}
      <AnimatedSection className="w-full py-16 md:py-24">
        <div className="container mx-auto px-4">
          <SectionTitle>Lo que dicen</SectionTitle>
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
            alt="Iván pensando cerca del mar"
            layout="fill"
            className="absolute inset-0 z-0 filter brightness-50 dark:brightness-40 object-cover object-top"
            priority
         />
         <div className="container mx-auto px-4 relative z-10 text-center text-white">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-semibold mb-6">
               "La tecnología es una herramienta, la verdadera odisea está en cómo la usamos para explorar lo desconocido."
            </h2>
            <p className="text-lg text-gray-300">
               - Iván In Tech (Inspirado en la naturaleza y lo distópico)
            </p>
         </div>
      </AnimatedSection>

      {/* CTA Final */}
      <AnimatedSection className="w-full py-20 md:py-32 text-center">
         <div className="container mx-auto px-4">
            <h2 className="text-3xl md:text-4xl font-semibold mb-6">¿Listo para colaborar o conectar?</h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-xl mx-auto">Hablemos sobre tu próximo proyecto o idea innovadora.</p>
            <Link href="/contacto" className="inline-block bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-3 rounded-md text-lg font-medium transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 hover:brightness-110 shadow-lg hover:shadow-primary/30">
               Contacta Conmigo
            </Link>
    </div>
      </AnimatedSection>

    </main>
  );
}
