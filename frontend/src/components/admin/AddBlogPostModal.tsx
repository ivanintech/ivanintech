'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import type { BlogPostCreate } from '@/lib/types';

interface AddBlogPostModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddPost: (postData: BlogPostCreate) => Promise<void>;
  // Podríamos añadir defaultTags o categorías si las tenemos
}

export const AddBlogPostModal: React.FC<AddBlogPostModalProps> = ({ isOpen, onClose, onAddPost }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [excerpt, setExcerpt] = useState('');
  const [tags, setTags] = useState(''); // String separado por comas
  const [imageUrl, setImageUrl] = useState('');
  const [linkedinPostUrl, setLinkedinPostUrl] = useState('');
  const [status, setStatus] = useState('published'); // Default status
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Resetear campos cuando el modal se abre/cierra o cambia el prop isOpen
    if (isOpen) {
      setTitle('');
      setContent('');
      setExcerpt('');
      setTags('');
      setImageUrl('');
      setLinkedinPostUrl('');
      setStatus('published');
    } else {
        // Pequeño delay para que la UI no parezca que salta al limpiar mientras se cierra
        setTimeout(() => {
            setTitle('');
            setContent('');
            setExcerpt('');
            setTags('');
            setImageUrl('');
            setLinkedinPostUrl('');
            setStatus('published');
        }, 300)
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    const postData: BlogPostCreate = {
      title,
      content,
      excerpt: excerpt || undefined, // Enviar undefined si está vacío para que Pydantic use el default si lo tiene
      tags: tags || undefined,
      image_url: imageUrl || undefined,
      linkedin_post_url: linkedinPostUrl || undefined,
      status: status || 'published',
    };
    try {
      await onAddPost(postData);
      // onClose(); // El que llama (page.tsx) cerrará el modal si tiene éxito
    } catch (error) {
      // El error ya se maneja en la página que llama con toast
      console.error("Error submitting blog post from modal:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Añadir Nueva Entrada de Blog</DialogTitle>
          <DialogDescription>
            Completa los detalles de la nueva entrada del blog.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="title" className="text-right">
              Título
            </Label>
            <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} className="col-span-3" required />
          </div>
          
          <div className="grid grid-cols-4 items-start gap-4">
            <Label htmlFor="content" className="text-right pt-2">
              Contenido
            </Label>
            <Textarea id="content" value={content} onChange={(e) => setContent(e.target.value)} className="col-span-3 min-h-[150px]" required />
          </div>

          <div className="grid grid-cols-4 items-start gap-4">
            <Label htmlFor="excerpt" className="text-right pt-2">
              Extracto (Opcional)
            </Label>
            <Textarea id="excerpt" value={excerpt} onChange={(e) => setExcerpt(e.target.value)} className="col-span-3" />
          </div>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="tags" className="text-right">
              Tags (Opcional, CSV)
            </Label>
            <Input id="tags" value={tags} onChange={(e) => setTags(e.target.value)} className="col-span-3" placeholder="ej: ia, desarrollo, tutorial"/>
          </div>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="imageUrl" className="text-right">
              URL Imagen (Opcional)
            </Label>
            <Input id="imageUrl" type="url" value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} className="col-span-3" placeholder="https://ejemplo.com/imagen.jpg" />
          </div>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="linkedinPostUrl" className="text-right">
              URL LinkedIn (Opcional)
            </Label>
            <Input id="linkedinPostUrl" type="url" value={linkedinPostUrl} onChange={(e) => setLinkedinPostUrl(e.target.value)} className="col-span-3" placeholder="https://linkedin.com/feed/update/..."/>
          </div>

           <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="status" className="text-right">
              Estado
            </Label>
            {/* Podríamos usar un Select de shadcn/ui aquí para 'published', 'draft' */}
            <Input id="status" value={status} onChange={(e) => setStatus(e.target.value)} className="col-span-3" /> 
          </div>

          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
                Cancelar
              </Button>
            </DialogClose>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Creando...' : 'Crear Entrada'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}; 