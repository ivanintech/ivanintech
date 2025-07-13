import { HeroCarouselClient } from './HeroCarouselClient';

export function HeroBackgroundCarousel() {
  // Lista manual de archivos multimedia para el carrusel
  const mediaFiles = [
    '/Heromedia/ivan-aexplaining-show.mp4',
    '/Heromedia/ivan-dancing.mp4',
    '/Heromedia/ivan-graduated-ai-master.mp4',
    '/Heromedia/ivan-on-boat.mp4',
    '/Heromedia/ivan-on-top-fansipan-with-a-flag.mp4',
    '/Heromedia/ivan-playing-martillazo.mp4',
    '/Heromedia/ivan-upstairs-fansipan.mp4',
    '/Heromedia/ivan-with-quest3.mp4',
    '/Heromedia/ivan-with-vr.mp4',
    // Puedes añadir más rutas aquí si tienes más archivos
  ];

  if (mediaFiles.length === 0) {
    return (
      <div className="absolute inset-0 bg-gray-900">
        <img src="/img/ivan-on-thailand.jpeg" alt="Default hero background" className="w-full h-full object-cover opacity-30" />
      </div>
    );
  }

  return <HeroCarouselClient mediaFiles={mediaFiles} />;
} 