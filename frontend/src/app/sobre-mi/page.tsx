import fs from 'fs';
import path from 'path';
import Link from 'next/link'; // Importar Link para botones
import { AnimatedSection } from '@/components/ui/animated-section'; // Importar para animación
import { FaBrain, FaCode, FaCube, FaChartLine, FaRobot, FaBolt } from 'react-icons/fa'; // Añadir más iconos
import { PersonalCarousel } from '@/components/about/personal-carousel'; // Importar carrusel
import { EditableImage } from '@/components/ui/EditableImage'; // Importar componente de imagen editable
import { toast } from 'sonner'; // Para notificaciones
import { SobreMiClientPage } from './client-page'; // Componente de cliente para partes interactivas

// Componente para Skill Card
const SkillCard = ({ icon: Icon, title, description }: { icon: React.ElementType, title: string, description: string }) => (
  <div className="border border-border rounded-lg p-6 bg-background shadow-sm text-center">
    <Icon className="w-8 h-8 text-primary mx-auto mb-4" />
    <h3 className="font-semibold mb-2">{title}</h3>
    <p className="text-xs text-muted-foreground">{description}</p>
  </div>
);

export default function SobreMiPage() {
  // --- Lógica de servidor para leer imágenes ---
  const imgDirectory = path.join(process.cwd(), 'public/img');
  const allFiles = fs.readdirSync(imgDirectory, { withFileTypes: true });
  
  const imageFilenames = allFiles
    .filter(dirent => dirent.isFile() && /\.(jpg|jpeg|png|webp)$/i.test(dirent.name))
    .map(dirent => `/img/${dirent.name}`);
  // --- Fin de la lógica de servidor ---

  return (
    <SobreMiClientPage imagePaths={imageFilenames} />
  );
}

// He movido todo el contenido visual a un componente de cliente (`client-page.tsx`)
// para separar la lógica de servidor (lectura de archivos) de la lógica de cliente (hooks, estado).
// El siguiente paso será crear ese archivo. 