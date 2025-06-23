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
import type { BlogPost, BlogPostCreate, BlogPostUpdate } from '@/types';

interface AddBlogPostModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (postData: BlogPostCreate | BlogPostUpdate) => Promise<void>;
  postToEdit?: BlogPost | null;
  isEditing?: boolean;
}

export const AddBlogPostModal: React.FC<AddBlogPostModalProps> = ({ isOpen, onClose, onConfirm, postToEdit, isEditing = false }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [excerpt, setExcerpt] = useState('');
  const [tags, setTags] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [linkedinPostUrl, setLinkedinPostUrl] = useState('');
  const [status, setStatus] = useState('published');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen && isEditing && postToEdit) {
      setTitle(postToEdit.title || '');
      setContent(postToEdit.content || '');
      setExcerpt(postToEdit.excerpt || '');
      setTags(postToEdit.tags || '');
      setImageUrl(postToEdit.image_url || '');
      setLinkedinPostUrl(postToEdit.linkedin_post_url || '');
      setStatus(postToEdit.status || 'published');
    } else if (isOpen && !isEditing) {
      // Resetear campos para el modo de creación
      setTitle('');
      setContent('');
      setExcerpt('');
      setTags('');
      setImageUrl('');
      setLinkedinPostUrl('');
      setStatus('published');
    }
  }, [isOpen, isEditing, postToEdit]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    const postData: BlogPostUpdate | BlogPostCreate = {
      title,
      content,
      excerpt: excerpt || undefined,
      tags: tags || undefined,
      image_url: imageUrl || undefined,
      linkedin_post_url: linkedinPostUrl || undefined,
      status: status || 'published',
    };
    
    try {
      await onConfirm(postData);
    } catch (error) {
      console.error("Error submitting blog post from modal:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Editar Entrada de Blog' : 'Añadir Nueva Entrada de Blog'}</DialogTitle>
          <DialogDescription>
            {isEditing ? 'Modifica los detalles de la entrada existente.' : 'Completa los detalles de la nueva entrada del blog.'}
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
              {isSubmitting ? (isEditing ? 'Guardando...' : 'Creando...') : (isEditing ? 'Guardar Cambios' : 'Crear Entrada')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}; 