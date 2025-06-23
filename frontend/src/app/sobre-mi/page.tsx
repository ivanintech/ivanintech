import fs from 'fs';
import path from 'path';
import { SobreMiClientPage } from './client-page'; // Componente de cliente para partes interactivas

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