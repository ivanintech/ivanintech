'use client'

import React, { useState, useEffect, useCallback, useRef } from 'react'
import useEmblaCarousel from 'embla-carousel-react'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui/button'
import { PlusCircle } from 'lucide-react'
import { toast } from 'sonner'
import { ImageEditModal } from '@/components/ui/ImageEditModal' // CORREGIDO: Usar alias de ruta

// --- NUEVO COMPONENTE INTERNO ---
// Este componente decide cómo mostrar la imagen basándose en su aspect ratio.
function CarouselImageWrapper({ src, alt }: { src: string; alt: string; }) {
  const [isTall, setIsTall] = useState(false);

  const handleImageLoad = (event: React.SyntheticEvent<HTMLImageElement, Event>) => {
    const { naturalWidth, naturalHeight } = event.currentTarget;
    // Solo actualizamos si el estado necesita cambiar para evitar bucles
    if (naturalHeight > naturalWidth && !isTall) {
      setIsTall(true);
    } else if (naturalHeight <= naturalWidth && isTall) {
      setIsTall(false);
    }
  };

  return (
    <img
      src={src}
      alt={alt}
      className={isTall ? 'object-contain' : 'object-cover'}
      style={{ width: '100%', height: '100%' }}
      onLoad={handleImageLoad}
    />
  );
}
// --- FIN DEL NUEVO COMPONENTE ---

// El tipo para una imagen individual
interface CarouselImage {
  src: string;
  alt: string;
}

// Props para el componente
interface PersonalCarouselProps {
  initialImagePaths: string[];
}

export function PersonalCarousel({ initialImagePaths }: PersonalCarouselProps) {
  const { user } = useAuth();
  
  // Convertimos las rutas iniciales en el formato de objeto que usa el carrusel
  const initialImages: CarouselImage[] = initialImagePaths.map(path => ({
    src: path,
    alt: `Imagen personal de Iván - ${path.split('/').pop()?.split('.')[0] || 'galería'}`
  }));

  const [images, setImages] = useState<CarouselImage[]>(initialImages);
  
  // Estado para el modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingImage, setEditingImage] = useState<{ image: { src: string; alt: string; }; index: number; } | null>(null);

  // Quitamos el plugin Autoplay de aquí
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true });

  // Nuevo estado para guardar los índices de las últimas 3 imágenes
  const [recentlyShownIndexes, setRecentlyShownIndexes] = useState<number[]>([]);
  const autoplayTimer = useRef<NodeJS.Timeout | null>(null);

  // Usamos una ref para la lógica aleatoria para que el callback no dependa del estado
  // y así evitar que el efecto principal se ejecute innecesariamente.
  const recentlyShownIndexesRef = useRef<number[]>([]);
  useEffect(() => {
    recentlyShownIndexesRef.current = recentlyShownIndexes;
  }, [recentlyShownIndexes]);

  const playNextRandom = useCallback(() => {
    if (!emblaApi) return;
    const slideCount = emblaApi.scrollSnapList().length;
    
    if (slideCount <= 3) {
      emblaApi.scrollNext();
      return;
    }

    const currentIndex = emblaApi.selectedScrollSnap();
    const recent = recentlyShownIndexesRef.current;
    let nextIndex;
    
    do {
      nextIndex = Math.floor(Math.random() * slideCount);
    } while (nextIndex === currentIndex || recent.includes(nextIndex));
    
    emblaApi.scrollTo(nextIndex);
  }, [emblaApi]);

  useEffect(() => {
    if (!emblaApi) return;

    const stopAutoplay = () => {
      if (autoplayTimer.current) clearInterval(autoplayTimer.current);
    };

    const startAutoplay = () => {
      stopAutoplay();
      autoplayTimer.current = setInterval(playNextRandom, 3000);
    };

    const onSelect = () => {
      const selectedIndex = emblaApi.selectedScrollSnap();
      setRecentlyShownIndexes(prev => [selectedIndex, ...prev.filter(i => i !== selectedIndex)].slice(0, 3));
    };
    
    emblaApi.on('select', onSelect);
    emblaApi.on('pointerDown', stopAutoplay);
    emblaApi.on('settle', startAutoplay); // Reinicia cuando el carrusel se asienta

    onSelect();
    startAutoplay();

    return () => {
      stopAutoplay();
      if (emblaApi) {
        emblaApi.off('select', onSelect);
        emblaApi.off('pointerDown', stopAutoplay);
        emblaApi.off('settle', startAutoplay);
      }
    };
  }, [emblaApi, playNextRandom]);

  // Recargar el carrusel cuando las imágenes (editadas/añadidas) cambian
  useEffect(() => {
    if (emblaApi) {
      emblaApi.reInit();
    }
  }, [images, emblaApi]);

  const handleAddImage = () => {
    setEditingImage(null); // Asegurarse de que no hay datos de edición
    setIsModalOpen(true);
  };

  const handleSaveImage = (imageData: { src: string; alt: string }) => {
    if (editingImage) {
      // Estamos editando una imagen existente
      const updatedImages = [...images];
      updatedImages[editingImage.index] = imageData;
      setImages(updatedImages);
      toast.success('Imagen actualizada correctamente.');
    } else {
      // Estamos añadiendo una nueva imagen
      setImages(prev => [...prev, imageData]);
      toast.success('Nueva imagen añadida a la galería.');
    }
    setEditingImage(null);
  };

  return (
    <div className="relative">
      {user?.is_superuser && (
        <div className="absolute top-2 right-2 z-20 flex gap-2">
           <Button size="sm" onClick={handleAddImage}>
            <PlusCircle className="w-4 h-4 mr-2" />
            Añadir Imagen
          </Button>
        </div>
      )}
      <div className="overflow-hidden rounded-lg border border-border shadow-lg" ref={emblaRef}>
        <div className="flex">
          {images.map((img, index) => (
            <div className="relative flex-grow-0 flex-shrink-0 w-full aspect-video bg-muted" key={`${img.src}-${index}`}>
              <CarouselImageWrapper
                src={img.src}
                alt={img.alt}
              />
            </div>
          ))}
        </div>
        {/* Podríamos añadir botones de navegación o puntos aquí si quisiéramos */}
      </div>

      {/* El Modal para añadir/editar */}
      <ImageEditModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveImage}
        imageToEdit={editingImage?.image || null}
      />
    </div>
  )
} 