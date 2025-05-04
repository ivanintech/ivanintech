import Image from 'next/image';
import Link from 'next/link'; // Importar Link para botones
import { AnimatedSection } from '@/components/animated-section'; // Importar para animación
import { FaBrain, FaCode, FaCube, FaChartLine, FaRobot, FaBolt } from 'react-icons/fa'; // Añadir más iconos
import { PersonalCarousel } from '@/components/personal-carousel'; // Importar carrusel

// Componente para Skill Card
const SkillCard = ({ icon: Icon, title, description }: { icon: React.ElementType, title: string, description: string }) => (
  <div className="border border-border rounded-lg p-6 bg-background shadow-sm text-center">
    <Icon className="w-8 h-8 text-primary mx-auto mb-4" />
    <h3 className="font-semibold mb-2">{title}</h3>
    <p className="text-xs text-muted-foreground">{description}</p>
  </div>
);

export default function SobreMiPage() {
  return (
    <div className="container mx-auto px-4 py-16 md:py-24 space-y-24 md:space-y-32">
      {/* Sección Principal Bio + Imagen Perfil */}
      <AnimatedSection>
        <h1 className="text-center mb-16">Sobre Iván In Tech</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-16 items-center">
          <div className="md:col-span-1 flex justify-center">
            {/* Imagen Profesional */}
            <Image
              src="/img/ivan-profile.webp" // Volver a la imagen de perfil original
              alt="Foto de perfil de Iván In Tech"
              width={320} 
              height={320}
              className="rounded-full object-cover shadow-lg aspect-square border-4 border" // Volver a rounded-full
              priority
            />
          </div>
          <div className="md:col-span-2">
            <h2 className="mb-6">Ingeniero de IA y Explorador Tecnológico</h2>
            <div className="space-y-5 text-base md:text-lg text-muted-foreground dark:text-muted-foreground leading-relaxed">
              <p>
                ¡Hola! Soy Iván, Ingeniero de IA (Máster en IA, UNIR) e Ingeniero Informático (Universidad de León), 
                apasionado por explorar la tecnología desde San Sebastián. Mi mundo gira en torno a la IA, la gestión 
                de productos y el desarrollo 3D, buscando siempre construir el futuro.
              </p>
              <p>
                Actualmente, me enfoco en desarrollar aplicaciones con <strong className="text-foreground dark:text-gray-200">IA Generativa</strong> que solucionen problemas 
                reales para usuarios y PYMES. Proyectos como mi recomendador de libros (FAISS) o el predictor de ACV 
                (Redes Neuronales, Langchain) nacen de esta vocación por <strong className="text-foreground dark:text-gray-200">generar impacto tangible</strong>. 
                Soy un entusiasta de la <strong className="text-foreground dark:text-gray-200">automatización</strong> y disfruto compartiendo conocimiento, 
                dando charlas sobre IA para todos los públicos y enseñando a <strong className="text-foreground dark:text-gray-200">mejorar prompts</strong> para obtener resultados óptimos.
              </p>
              <p>
                Para mí, cada proyecto es una odisea. Me encanta sumergirme en la complejidad, encontrar patrones 
                y crear soluciones innovadoras, ya sea en IA, <strong className="text-foreground dark:text-gray-200">analítica de datos y KPIs</strong>, 
                o explorando el mundo de los <strong className="text-foreground dark:text-gray-200">Gemelos Digitales</strong>.
              </p>
            </div>
            {/* Botones CTA */}
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <Link 
                href="/portfolio"
                className="inline-block text-center bg-primary text-primary-foreground hover:bg-primary/90 px-6 py-2.5 rounded-md text-base font-medium transition-all duration-300 transform hover:scale-105 shadow hover:shadow-primary/30 w-full sm:w-auto"
              >
                Ver mi Portfolio
              </Link>
              <Link 
                href="/contacto"
                className="inline-block text-center bg-muted text-muted-foreground hover:bg-border px-6 py-2.5 rounded-md text-base font-medium transition-all duration-300 transform hover:scale-105 w-full sm:w-auto"
              >
                Contacta Conmigo
              </Link>
            </div>
          </div>
        </div>
      </AnimatedSection>
      
      {/* Nueva Sección: Mi Enfoque */}
      <AnimatedSection>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-16 items-center">
          {/* Columna Texto */} 
          <div className="order-2 md:order-1">
            <h2 className="mb-6">Mi Enfoque: De la Idea a la Realidad</h2>
            <div className="space-y-4 text-muted-foreground dark:text-muted-foreground">
              <p>
                Transformo conceptos abstractos en soluciones tangibles. Mi proceso combina análisis riguroso, 
                experimentación ágil y una visión centrada en el producto final. 
              </p>
              <p>
                Creo en la iteración rápida, el feedback constante y en la búsqueda de la excelencia técnica 
                sin perder de vista el impacto real. Cada desafío es una oportunidad para innovar y superar 
                los límites establecidos.
              </p>
               {/* Podríamos añadir puntos clave o lista */}
            </div>
          </div>
          {/* Columna Imagen Pitching */} 
          <div className="order-1 md:order-2 flex justify-center md:justify-end">
            <Image
              src="/img/ivan-pitching.webp"
              alt="Iván In Tech presentando una idea"
              width={500} 
              height={350} // Ajustar ratio si es necesario
              className="rounded-lg object-cover shadow-xl border border-border"
            />
          </div>
        </div>
      </AnimatedSection>
      
      {/* Nueva Sección: Habilidades y Tecnologías */}
      <AnimatedSection>
         <h2 className="text-center mb-12">Habilidades y Tecnologías</h2>
         <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 md:gap-8 max-w-4xl mx-auto">
           <SkillCard icon={FaBrain} title="IA & Machine Learning" description="GenAI, Langchain, Scikit-learn, Pandas, Tensorflow, NLP, Modelos Predictivos" />
           <SkillCard icon={FaCode} title="Desarrollo Web" description="FastAPI, Next.js, React, Python, TypeScript, Backend/Frontend" />
           <SkillCard icon={FaChartLine} title="Datos y Analítica" description="Análisis de Datos, KPIs, Visualización, Gemelos Digitales" />
           <SkillCard icon={FaCube} title="Desarrollo 3D" description="Visualización Interactiva, Experiencias Inmersivas" />
           <SkillCard icon={FaRobot} title="IA Generativa" description="Aplicaciones Prácticas, Solución de Problemas" />
           <SkillCard icon={FaBolt} title="Automatización" description="Optimización de Procesos, Eficiencia" />
           {/* Añadir más si es relevante: Prompt Engineering, Pitching... */}
         </div>
      </AnimatedSection>
      
      {/* Nueva Sección: Momentos / Galería Personal */}
      <AnimatedSection>
         <h2 className="text-center mb-12">Un Vistazo Personal</h2>
         <div className="max-w-3xl mx-auto">
           <PersonalCarousel />
         </div>
         <p className="text-center mt-6 text-sm text-muted-foreground">
           Algunos momentos más allá del código y los algoritmos.
         </p>
      </AnimatedSection>
    </div>
  );
} 