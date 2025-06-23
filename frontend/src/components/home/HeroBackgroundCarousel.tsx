import fs from 'fs';
import path from 'path';
import { HeroCarouselClient } from './HeroCarouselClient';

export function HeroBackgroundCarousel() {
  const mediaDir = path.join(process.cwd(), 'public', 'Heromedia');
  let mediaFiles: string[] = [];

  try {
    mediaFiles = fs.readdirSync(mediaDir)
      .filter(file => /\.(mp4|webm|jpg|jpeg|png|webp)$/i.test(file))
      .map(file => `/Heromedia/${file}`);
  } catch (error) {
    console.error("Could not read hero media directory:", error);
  }

  if (mediaFiles.length === 0) {
    return (
      <div className="absolute inset-0 bg-gray-900">
        <img src="/img/ivan-on-thailand.jpeg" alt="Default hero background" className="w-full h-full object-cover opacity-30" />
      </div>
    );
  }

  return <HeroCarouselClient mediaFiles={mediaFiles} />;
} 