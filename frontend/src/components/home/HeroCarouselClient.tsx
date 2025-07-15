'use client';

import { useRef, useEffect, useState } from 'react';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  type CarouselApi,
} from "@/components/ui/carousel";
import Autoplay from "embla-carousel-autoplay";
import Image from 'next/image';

interface HeroCarouselClientProps {
  mediaFiles: string[];
}

export function HeroCarouselClient({ mediaFiles }: HeroCarouselClientProps) {
  const plugin = useRef(
    Autoplay({ delay: 7000, stopOnInteraction: false, stopOnMouseEnter: false })
  );
  
  const [api, setApi] = useState<CarouselApi>()
  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    if (!api) {
      return
    }

    const onSelect = () => {
      setIsTransitioning(true);
      setTimeout(() => setIsTransitioning(false), 300);
    }

    api.on('select', onSelect)

    return () => {
      api.off('select', onSelect)
    }
  }, [api])


  return (
    <Carousel
      setApi={setApi}
      className="absolute inset-0 w-full h-full"
      plugins={[plugin.current]}
      opts={{
        loop: true,
      }}
    >
      <CarouselContent className="w-full h-full">
        {mediaFiles.map((mediaUrl, index) => (
          <CarouselItem key={index} className="w-full h-full">
            {mediaUrl.endsWith('.mp4') || mediaUrl.endsWith('.webm') ? (
              <video
                className="w-full h-full object-cover"
                autoPlay
                loop
                muted
                playsInline
                src={mediaUrl}
              />
            ) : (
              <Image
                src={mediaUrl}
                alt={`Hero media ${index + 1}`}
                className="w-full h-full object-cover"
                unoptimized
              />
            )}
          </CarouselItem>
        ))}
      </CarouselContent>
      
      {/* Gradient Wipe Effect Overlay */}
      {isTransitioning && (
        <div 
          className="absolute inset-0 z-20 pointer-events-none"
          style={{
            background: `linear-gradient(110deg, 
              rgba(255,255,255,0) 0%, 
              rgba(255,255,255,0.25) 45%, 
              rgba(255,255,255,0.25) 55%, 
              rgba(255,255,255,0) 100%
            )`,
            backgroundSize: '300% 100%',
            animation: `gradient-wipe 0.3s ease-in-out forwards`,
          }}
        />
      )}
    </Carousel>
  );
} 