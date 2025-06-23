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
import type { NewsItemRead, NewsItemUpdate } from '@/types';

interface EditNewsItemModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (itemData: NewsItemUpdate) => Promise<void>;
  itemToEdit: NewsItemRead | null;
}

export const EditNewsItemModal: React.FC<EditNewsItemModalProps> = ({ isOpen, onClose, onConfirm, itemToEdit }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState(''); // String separado por comas
  const [imageUrl, setImageUrl] = useState('');
  const [relevanceRating, setRelevanceRating] = useState<number | undefined>(undefined);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen && itemToEdit) {
      setTitle(itemToEdit.title || '');
      setDescription(itemToEdit.description || '');
      setTags(itemToEdit.sectors?.join(', ') || '');
      setImageUrl(itemToEdit.imageUrl || '');
      setRelevanceRating(itemToEdit.relevance_rating);
    }
  }, [isOpen, itemToEdit]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    const itemData: NewsItemUpdate = {
      title,
      description: description || undefined,
      sectors: tags.split(',').map(t => t.trim()).filter(t => t),
      imageUrl: imageUrl || undefined,
      relevance_rating: relevanceRating
    };
    
    try {
      await onConfirm(itemData);
    } catch (error) {
      console.error("Error submitting news item from modal:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Editar Noticia</DialogTitle>
          <DialogDescription>
            Modifica los detalles de la noticia.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="title" className="text-right">Título</Label>
            <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} className="col-span-3" required />
          </div>
          <div className="grid grid-cols-4 items-start gap-4">
            <Label htmlFor="description" className="text-right pt-2">Descripción</Label>
            <Textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} className="col-span-3 min-h-[100px]" />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="tags" className="text-right">Sectores (CSV)</Label>
            <Input id="tags" value={tags} onChange={(e) => setTags(e.target.value)} className="col-span-3" placeholder="ej: ia, fintech, salud"/>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="imageUrl" className="text-right">URL Imagen</Label>
            <Input id="imageUrl" type="url" value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} className="col-span-3" />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="relevance" className="text-right">Relevancia (0-5)</Label>
            <Input id="relevance" type="number" step="0.1" min="0" max="5" value={relevanceRating ?? ''} onChange={(e) => setRelevanceRating(parseFloat(e.target.value))} className="col-span-3" />
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>Cancelar</Button>
            </DialogClose>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Guardando...' : 'Guardar Cambios'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}; 