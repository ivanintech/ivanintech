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
        <h1 className="text-center mb-16">About Iván In Tech</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-16 items-center">
          <div className="md:col-span-1 flex justify-center">
            {/* Imagen Profesional */}
            <Image
              src="/img/ivan-profile.webp" // Volver a la imagen de perfil original
              alt="Profile picture of Iván In Tech"
              width={320} 
              height={320}
              className="rounded-full object-cover shadow-lg aspect-square border-4 border" // Volver a rounded-full
              priority
            />
          </div>
          <div className="md:col-span-2">
            <h2 className="mb-6">AI Engineer and Technological Explorer</h2>
            <div className="space-y-5 text-base md:text-lg text-muted-foreground dark:text-muted-foreground leading-relaxed">
              <p>
                Hi! I&apos;m Iván, an AI Engineer (Master&apos;s in AI, UNIR) and Computer Engineer (University of León), 
                passionate about exploring technology from San Sebastián. My world revolves around AI, product management, 
                and 3D development, always looking to build the future.
              </p>
              <p>
                Currently, I focus on developing applications with <strong className="text-foreground dark:text-gray-200">Generative AI</strong> that solve real problems 
                for users and SMEs. Projects like my book recommender (FAISS) or stroke predictor 
                (Neural Networks, Langchain) are born from this vocation to <strong className="text-foreground dark:text-gray-200">generate tangible impact</strong>. 
                I am an <strong className="text-foreground dark:text-gray-200">automation</strong> enthusiast and enjoy sharing knowledge, 
                giving talks on AI for all audiences and teaching how to <strong className="text-foreground dark:text-gray-200">improve prompts</strong> for optimal results.
              </p>
              <p>
                For me, every project is an odyssey. I love diving into complexity, finding patterns 
                and creating innovative solutions, whether in AI, <strong className="text-foreground dark:text-gray-200">data analytics and KPIs</strong>, 
                or exploring the world of <strong className="text-foreground dark:text-gray-200">Digital Twins</strong>.
              </p>
            </div>
            {/* Botones CTA */}
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <Link 
                href="/portfolio"
                className="inline-block text-center bg-primary text-primary-foreground hover:bg-primary/90 px-6 py-2.5 rounded-md text-base font-medium transition-all duration-300 transform hover:scale-105 shadow hover:shadow-primary/30 w-full sm:w-auto"
              >
                View My Portfolio
              </Link>
              <Link 
                href="/contacto"
                className="inline-block text-center bg-muted text-muted-foreground hover:bg-border px-6 py-2.5 rounded-md text-base font-medium transition-all duration-300 transform hover:scale-105 w-full sm:w-auto"
              >
                Contact Me
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
            <h2 className="mb-6">My Approach: From Idea to Reality</h2>
            <div className="space-y-4 text-muted-foreground dark:text-muted-foreground">
              <p>
                I transform abstract concepts into tangible solutions. My process combines rigorous analysis, 
                agile experimentation, and a vision centered on the final product. 
              </p>
              <p>
                I believe in rapid iteration, constant feedback, and in the pursuit of technical excellence 
                without losing sight of real impact. Every challenge is an opportunity to innovate and push 
                beyond established limits.
              </p>
               {/* Podríamos añadir puntos clave o lista */}
            </div>
          </div>
          {/* Columna Imagen Pitching */} 
          <div className="order-1 md:order-2 flex justify-center md:justify-end">
            <Image
              src="/img/ivan-pitching.webp"
              alt="Iván In Tech pitching an idea"
              width={500} 
              height={350} // Ajustar ratio si es necesario
              className="rounded-lg object-cover shadow-xl border border-border"
            />
          </div>
        </div>
      </AnimatedSection>
      
      {/* Nueva Sección: Habilidades y Tecnologías */}
      <AnimatedSection>
         <h2 className="text-center mb-12">Skills and Technologies</h2>
         <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 md:gap-8 max-w-4xl mx-auto">
           <SkillCard icon={FaBrain} title="AI & Machine Learning" description="GenAI, Langchain, Scikit-learn, Pandas, Tensorflow, NLP, Predictive Models" />
           <SkillCard icon={FaCode} title="Web Development" description="FastAPI, Next.js, React, Python, TypeScript, Backend/Frontend" />
           <SkillCard icon={FaChartLine} title="Data and Analytics" description="Data Analysis, KPIs, Visualization, Digital Twins" />
           <SkillCard icon={FaCube} title="3D Development" description="Interactive Visualization, Immersive Experiences" />
           <SkillCard icon={FaRobot} title="Generative AI" description="Practical Applications, Problem Solving" />
           <SkillCard icon={FaBolt} title="Automation" description="Process Optimization, Efficiency" />
           {/* Añadir más si es relevante: Prompt Engineering, Pitching... */}
         </div>
      </AnimatedSection>
      
      {/* Nueva Sección: Momentos / Galería Personal */}
      <AnimatedSection>
         <h2 className="text-center mb-12">A Personal Glimpse</h2>
         <div className="max-w-3xl mx-auto">
           <PersonalCarousel />
         </div>
         <p className="text-center mt-6 text-sm text-muted-foreground">
           Some moments beyond code and algorithms.
         </p>
      </AnimatedSection>
    </div>
  );
} 