import fs from 'fs';
import path from 'path';
import { SobreMiClientPage } from './client-page'; // Componente de cliente para partes interactivas
import { Metadata } from 'next';

// --- Lógica de servidor para leer imágenes ---
const getImages = () => {
  const imgDirectory = path.join(process.cwd(), 'public/img');
  const allFiles = fs.readdirSync(imgDirectory, { withFileTypes: true });
  
  return allFiles
    .filter(dirent => dirent.isFile() && /\.(jpg|jpeg|png|webp)$/i.test(dirent.name))
    .map(dirent => `/img/${dirent.name}`);
}

export async function generateMetadata(): Promise<Metadata> {
  const imageFilenames = getImages();

  const preloadLinks = imageFilenames.map(src => ({
    rel: 'preload',
    href: src,
    as: 'image',
  }));

  return {
    other: {
      // @ts-ignore - 'preload' is a valid rel value but not in the default type
      preload: preloadLinks,
    },
  };
}

export default function SobreMiPage() {
  const imageFilenames = getImages();
  
  return (
    <SobreMiClientPage imagePaths={imageFilenames} />
  );
}

// He movido todo el contenido visual a un componente de cliente (`client-page.tsx`)
// para separar la lógica de servidor (lectura de archivos) de la lógica de cliente (hooks, estado).
// El siguiente paso será crear ese archivo. 