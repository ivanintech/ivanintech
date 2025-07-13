"use client";

import React, { useState } from 'react';
import {
  Facebook,
  Twitter,
  Linkedin,
  MessageCircle, // Para WhatsApp
  Send, // Para Telegram
  Mail,
  Copy,
  Share2
} from 'lucide-react';
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
  className?: string;
}

const SocialButton = ({
  href,
  children,
  label,
}: {
  href: string;
  children: React.ReactNode;
  label: string;
}) => (
  <a
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    className="flex flex-col items-center gap-2 group"
  >
    <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center transition-all duration-300 group-hover:bg-gray-200 group-hover:scale-110">
      {children}
    </div>
    <span className="text-xs text-gray-600">{label}</span>
  </a>
);

export default function SocialShareButtons({
  url,
  title,
  description = "",
  className = ""
}: SocialShareButtonsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { toast, showToast, hideToast } = useToast();

  const shareUrl = url.startsWith('http') ? url : (typeof window !== 'undefined' ? `${window.location.origin}${url}` : url);
  const encodedUrl = encodeURIComponent(shareUrl);
  const encodedTitle = encodeURIComponent(title);
  const encodedDescription = encodeURIComponent(description);

  const socialLinks = {
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
    twitter: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
    linkedin: `https://www.linkedin.com/shareArticle?mini=true&url=${encodedUrl}&title=${encodedTitle}&summary=${encodedDescription}`,
    whatsapp: `https://api.whatsapp.com/send?text=${encodedTitle}%20${encodedUrl}`,
    telegram: `https://t.me/share/url?url=${encodedUrl}&text=${encodedTitle}`,
    email: `mailto:?subject=${encodedTitle}&body=${encodedDescription}%0A%0A${encodedUrl}`,
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
            <div className="p-3 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-sm text-gray-900 line-clamp-2">
                {title}
              </h4>
            </div>

            <div className="grid grid-cols-3 gap-y-6 gap-x-4 pt-4">
              <SocialButton href={socialLinks.facebook} label="Facebook">
                <Facebook size={24} className="text-[#1877F2]" />
              </SocialButton>
              <SocialButton href={socialLinks.twitter} label="Twitter">
                <Twitter size={24} className="text-[#1DA1F2]" />
              </SocialButton>
              <SocialButton href={socialLinks.linkedin} label="LinkedIn">
                <Linkedin size={24} className="text-[#0A66C2]" />
              </SocialButton>
              <SocialButton href={socialLinks.whatsapp} label="WhatsApp">
                <MessageCircle size={24} className="text-[#25D366]" />
              </SocialButton>
              <SocialButton href={socialLinks.telegram} label="Telegram">
                <Send size={24} className="text-[#0088cc]" />
              </SocialButton>
              <SocialButton href={socialLinks.email} label="Email">
                <Mail size={24} className="text-gray-600" />
              </SocialButton>
            </div>

            <div className="pt-4 border-t">
              <Button variant="outline" className="w-full" onClick={handleCopyLink}>
                <Copy size={16} className="mr-2" /> Copiar enlace
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