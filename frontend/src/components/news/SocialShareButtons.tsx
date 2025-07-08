"use client";

import React, { useState } from 'react';
import {
  FacebookShare,
  TwitterShare,
  LinkedinShare,
  WhatsappShare,
  TelegramShare,
  EmailShare
} from 'react-share-kit';
import { Share2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Toast, useToast } from '@/components/ui/toast';

interface SocialShareButtonsProps {
  url: string;
  title: string;
  description?: string;
  hashtags?: string[];
  className?: string;
}

export default function SocialShareButtons({
  url,
  title,
  description = "",
  hashtags = ["IA", "Tecnologia", "IvanInTech"],
  className = ""
}: SocialShareButtonsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { toast, showToast, hideToast } = useToast();

  // Optimizar título y descripción para redes sociales
  const shareTitle = title.length > 100 ? title.substring(0, 97) + "..." : title;
  const shareDescription = description.length > 200 ? description.substring(0, 197) + "..." : description;

  // URL completa para compartir
  const shareUrl = url.startsWith('http') ? url : `${window.location.origin}${url}`;

  const shareButtonProps = {
    size: 40,
    round: true,
    borderRadius: 8,
  };

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      showToast("¡Enlace copiado al portapapeles!");
    } catch (err) {
      console.error("Error al copiar enlace:", err);
      showToast("Error al copiar el enlace");
    }
  };

  return (
    <>
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className={`flex items-center gap-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 transition-colors ${className}`}
          >
            <Share2 size={16} />
            <span className="hidden sm:inline">Compartir</span>
          </Button>
        </DialogTrigger>
        
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Share2 size={20} />
              Compartir noticia
            </DialogTitle>
            <DialogDescription>
              Comparte esta noticia en tus redes sociales favoritas
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Título de la noticia */}
            <div className="p-3 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-sm text-gray-900 line-clamp-2">
                {shareTitle}
              </h4>
              {shareDescription && (
                <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                  {shareDescription}
                </p>
              )}
            </div>

            {/* Botones de redes sociales */}
            <div className="grid grid-cols-3 gap-4">
              <div className="flex flex-col items-center gap-2">
                <FacebookShare
                  url={shareUrl}
                  quote={shareTitle}
                  hashtag={`#${hashtags[0]}`}
                  {...shareButtonProps}
                />
                <span className="text-xs text-gray-600">Facebook</span>
              </div>

              <div className="flex flex-col items-center gap-2">
                <TwitterShare
                  url={shareUrl}
                  title={shareTitle}
                  hashtags={hashtags}
                  {...shareButtonProps}
                />
                <span className="text-xs text-gray-600">Twitter</span>
              </div>

              <div className="flex flex-col items-center gap-2">
                <LinkedinShare
                  url={shareUrl}
                  title={shareTitle}
                  summary={shareDescription}
                  {...shareButtonProps}
                />
                <span className="text-xs text-gray-600">LinkedIn</span>
              </div>

              <div className="flex flex-col items-center gap-2">
                <WhatsappShare
                  url={shareUrl}
                  title={shareTitle}
                  separator=" - "
                  {...shareButtonProps}
                />
                <span className="text-xs text-gray-600">WhatsApp</span>
              </div>

              <div className="flex flex-col items-center gap-2">
                <TelegramShare
                  url={shareUrl}
                  title={shareTitle}
                  {...shareButtonProps}
                />
                <span className="text-xs text-gray-600">Telegram</span>
              </div>

              <div className="flex flex-col items-center gap-2">
                <EmailShare
                  url={shareUrl}
                  subject={shareTitle}
                  body={`${shareDescription}\n\nLeer más: ${shareUrl}`}
                  {...shareButtonProps}
                />
                <span className="text-xs text-gray-600">Email</span>
              </div>
            </div>

            {/* Botón para copiar enlace */}
            <div className="pt-4 border-t">
              <Button
                variant="outline"
                className="w-full"
                onClick={handleCopyLink}
              >
                📋 Copiar enlace
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Toast
        message={toast.message}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />
    </>
  );
} 