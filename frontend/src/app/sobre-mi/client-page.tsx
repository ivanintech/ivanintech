'use client';

import Link from 'next/link';
import { AnimatedSection } from '@/components/ui/animated-section';
import { FaBrain, FaCode, FaCube, FaChartLine, FaRobot, FaBolt } from 'react-icons/fa';
import { PersonalCarousel } from '@/components/about/personal-carousel';
import { EditableImage } from '@/components/ui/EditableImage';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { BrainCircuit, PenTool, Rocket } from 'lucide-react';

// Componente para Skill Card, se mantiene igual
const SkillCard = ({ icon: Icon, title, description }: { icon: React.ElementType, title: string, description: string }) => (
  <div className="border border-border rounded-lg p-6 bg-background shadow-sm text-center">
    <Icon className="w-8 h-8 text-primary mx-auto mb-4" />
    <h3 className="font-semibold mb-2">{title}</h3>
    <p className="text-xs text-muted-foreground">{description}</p>
  </div>
);

interface SobreMiClientPageProps {
    imagePaths: string[];
}

export function SobreMiClientPage({ imagePaths }: SobreMiClientPageProps) {
  return (
    <div className="bg-background text-foreground">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16">
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">
            Sobre Mí
          </h1>
          <p className="mt-4 text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto">
            Un apasionado por la intersección entre la tecnología, el producto y las personas.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-12 items-start">
          
          <div className="lg:col-span-3 space-y-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <h2 className="text-3xl font-bold text-primary mb-4">Mi Filosofía</h2>
              <p className="text-muted-foreground text-lg leading-relaxed">
                Creo firmemente en la tecnología como un catalizador para el progreso humano. No se trata solo de crear herramientas, sino de diseñar experiencias que sean intuitivas, eficientes y, sobre todo, que aporten un valor real. Mi enfoque se centra en entender profundamente el problema antes de escribir una sola línea de código, combinando una mentalidad de producto con una ejecución técnica rigurosa.
              </p>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="space-y-6"
            >
                <h3 className="text-2xl font-semibold text-secondary">Mis Áreas de Expertise</h3>
                <ul className="space-y-4">
                  <li className="flex items-start">
                    <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center mr-4">
                      <Rocket className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h4 className="font-bold">Desarrollo de Producto y Estrategia</h4>
                      <p className="text-muted-foreground">Desde la concepción de la idea y la validación con usuarios hasta la definición del roadmap y el lanzamiento. Conectando las necesidades del negocio con soluciones técnicas viables.</p>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center mr-4">
                      <BrainCircuit className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h4 className="font-bold">Inteligencia Artificial y Machine Learning</h4>
                      <p className="text-muted-foreground">Aplicación de modelos de IA para resolver problemas complejos, desde sistemas de recomendación y procesamiento de lenguaje natural hasta la automatización de procesos con agentes inteligentes.</p>
                    </div>
                  </li>
                   <li className="flex items-start">
                    <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center mr-4">
                      <PenTool className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h4 className="font-bold">Diseño y Arquitectura de Software</h4>
                      <p className="text-muted-foreground">Creación de sistemas escalables, mantenibles y robustos. Experiencia en arquitecturas de microservicios, CI/CD y despliegue en la nube (AWS, GCP, Render).</p>
                    </div>
                  </li>
                </ul>
            </motion.div>
          </div>

          <motion.div 
            className="lg:col-span-2"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <PersonalCarousel initialImagePaths={imagePaths} />
            <p className="text-center text-sm text-muted-foreground mt-4 italic">
              Un vistazo a mi vida más allá del código.
            </p>
          </motion.div>

        </div>
      </div>
    </div>
  );
} 