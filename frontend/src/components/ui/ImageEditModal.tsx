'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface ImageEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (imageData: { src: string; alt: string }) => void;
  imageToEdit: { src: string; alt: string } | null;
}

export function ImageEditModal({ isOpen, onClose, onSave, imageToEdit }: ImageEditModalProps) {
  const [src, setSrc] = useState('');
  const [alt, setAlt] = useState('');

  useEffect(() => {
    if (imageToEdit) {
      setSrc(imageToEdit.src);
      setAlt(imageToEdit.alt);
    } else {
      // Si es para añadir, reseteamos los campos
      setSrc('');
      setAlt('');
    }
  }, [imageToEdit, isOpen]); // Se actualiza cuando cambia la imagen a editar o se abre/cierra

  const handleSave = () => {
    if (src && alt) {
      onSave({ src, alt });
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{imageToEdit ? 'Editar Imagen' : 'Añadir Nueva Imagen'}</DialogTitle>
          <DialogDescription>
            Introduce la URL de la imagen y un texto descriptivo (alt).
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="src" className="text-right">URL</Label>
            <Input id="src" value={src} onChange={(e) => setSrc(e.target.value)} className="col-span-3" />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="alt" className="text-right">Alt Text</Label>
            <Input id="alt" value={alt} onChange={(e) => setAlt(e.target.value)} className="col-span-3" />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancelar</Button>
          <Button onClick={handleSave}>Guardar Cambios</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 