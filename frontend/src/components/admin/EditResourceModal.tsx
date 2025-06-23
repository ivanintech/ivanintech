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
import type { ResourceLink, ResourceLinkUpdate } from '@/types';
import { StarRating } from '@/components/ui/StarRating';
import { Switch } from '@/components/ui/switch';

interface EditResourceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (itemData: ResourceLinkUpdate) => Promise<void>;
  itemToEdit: ResourceLink | null;
}

export const EditResourceModal: React.FC<EditResourceModalProps> = ({ isOpen, onClose, onConfirm, itemToEdit }) => {
  const [title, setTitle] = useState('');
  const [personalNote, setPersonalNote] = useState('');
  const [tags, setTags] = useState('');
  const [starRating, setStarRating] = useState(0);
  const [isFavorite, setIsFavorite] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen && itemToEdit) {
      setTitle(itemToEdit.title || '');
      setPersonalNote(itemToEdit.personal_note || '');
      setTags(itemToEdit.tags || '');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setStarRating((itemToEdit as any).star_rating || 0);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setIsFavorite((itemToEdit as any).is_favorite || false);
    }
  }, [isOpen, itemToEdit]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    const itemData: ResourceLinkUpdate = {
      title,
      personal_note: personalNote,
      tags,
      star_rating: starRating,
      is_favorite: isFavorite,
    } as ResourceLinkUpdate;
    
    try {
      await onConfirm(itemData);
    } catch (error) {
      console.error("Error submitting resource from modal:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Editar Recurso</DialogTitle>
          <DialogDescription>
            Modifica los detalles del recurso. La URL y la descripción de la IA no se pueden cambiar.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="grid gap-6 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="title" className="text-right">Título</Label>
            <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} className="col-span-3" required />
          </div>
          <div className="grid grid-cols-4 items-start gap-4">
            <Label htmlFor="personalNote" className="text-right pt-2">Nota Personal</Label>
            <Textarea id="personalNote" value={personalNote} onChange={(e) => setPersonalNote(e.target.value)} className="col-span-3 min-h-[100px]" />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="tags" className="text-right">Tags (CSV)</Label>
            <Input id="tags" value={tags} onChange={(e) => setTags(e.target.value)} className="col-span-3" placeholder="ej: python, nextjs, ai"/>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="starRating" className="text-right">Calificación</Label>
            <div className="col-span-3">
               <StarRating rating={starRating} onRatingChange={setStarRating} />
            </div>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="isFavorite" className="text-right">Favorito</Label>
            <div className="col-span-3">
              <Switch
                id="isFavorite"
                checked={isFavorite}
                onCheckedChange={setIsFavorite}
              />
            </div>
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