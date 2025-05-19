'use client';

import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { NewsItemCreate } from '@/lib/types'; // Supondremos que existe este tipo o lo crearemos
import { toast } from 'sonner'; // Para notificaciones (opcional, pero bueno)

interface AddNewsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddNews: (newsData: NewsItemCreate) => Promise<void>; // Función para manejar el envío
  defaultSectors?: string[]; // Sectores comunes para preseleccionar o sugerir
}

const initialFormData: NewsItemCreate = {
  title: '',
  sourceUrl: '',
  summary: '',
  imageUrl: '',
  publishedAt: new Date().toISOString(), // Por defecto hoy, el admin puede cambiarlo
  sectors: [],
  // Añade otros campos que definas en NewsItemCreate
};

export const AddNewsModal: React.FC<AddNewsModalProps> = ({
  isOpen,
  onClose,
  onAddNews,
  defaultSectors = [],
}) => {
  const [formData, setFormData] = useState<NewsItemCreate>(initialFormData);
  const [selectedSectors, setSelectedSectors] = useState<string[]>([]);
  const [newSector, setNewSector] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Resetear formulario cuando se abre o se cierra
    if (isOpen) {
      setFormData(initialFormData);
      setSelectedSectors([]);
      setNewSector('');
    } else {
        // Pequeño retraso para que la animación de cierre no muestre el reset
        setTimeout(() => {
            setFormData(initialFormData);
            setSelectedSectors([]);
            setNewSector('');
        }, 300)
    }
  }, [isOpen]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev: NewsItemCreate) => ({ ...prev, [name]: value }));
  };

  const handleSectorToggle = (sector: string) => {
    setSelectedSectors((prev: string[]) => 
      prev.includes(sector) ? prev.filter(s => s !== sector) : [...prev, sector]
    );
  };

  const handleAddNewSector = () => {
    if (newSector && !selectedSectors.includes(newSector.trim())) {
      setSelectedSectors((prev: string[]) => [...prev, newSector.trim()]);
      setNewSector('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const newsDataToSubmit: NewsItemCreate = {
        ...formData,
        sectors: selectedSectors,
        // Asegurarse que publishedAt es un string ISO si el backend lo espera así
        publishedAt: new Date(formData.publishedAt).toISOString(), 
      };
      await onAddNews(newsDataToSubmit);
      toast.success('Noticia añadida con éxito!');
      onClose(); // Cerrar el modal después de añadir
    } catch (error: any) {
      console.error("Error al añadir noticia:", error);
      toast.error(error.message || 'No se pudo añadir la noticia.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open: boolean) => !open && onClose()}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Añadir Nueva Noticia</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          <div>
            <Label htmlFor="title">Título</Label>
            <Input id="title" name="title" value={formData.title} onChange={handleChange} required />
          </div>
          <div>
            <Label htmlFor="sourceUrl">URL de la Fuente</Label>
            <Input id="sourceUrl" name="sourceUrl" type="url" value={formData.sourceUrl} onChange={handleChange} required />
          </div>
          <div>
            <Label htmlFor="summary">Resumen</Label>
            <Textarea id="summary" name="summary" value={formData.summary} onChange={handleChange} required />
          </div>
          <div>
            <Label htmlFor="imageUrl">URL de la Imagen (Opcional)</Label>
            <Input id="imageUrl" name="imageUrl" type="url" value={formData.imageUrl || ''} onChange={handleChange} />
          </div>
          <div>
            <Label htmlFor="publishedAt">Fecha de Publicación</Label>
            <Input 
              id="publishedAt" 
              name="publishedAt" 
              type="datetime-local" // Permite seleccionar fecha y hora
              value={formData.publishedAt ? new Date(formData.publishedAt).toISOString().substring(0, 16) : ''} // Formato para datetime-local
              onChange={(e) => setFormData((prev: NewsItemCreate) => ({ ...prev, publishedAt: new Date(e.target.value).toISOString() }))} 
              required 
            />
          </div>
          
          <div>
            <Label>Sectores</Label>
            <div className="flex flex-wrap gap-2 mb-2">
              {defaultSectors.map(sector => (
                <Button 
                  key={sector} 
                  type="button"
                  variant={selectedSectors.includes(sector) ? "default" : "secondary"}
                  onClick={() => handleSectorToggle(sector)}
                >
                  {sector}
                </Button>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <Input 
                type="text" 
                placeholder="Añadir nuevo sector" 
                value={newSector}
                onChange={(e) => setNewSector(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddNewSector())}
              />
              <Button type="button" onClick={handleAddNewSector} variant="outline" size="sm">Añadir</Button>
            </div>
            {selectedSectors.length > 0 && (
                <div className="mt-2 text-sm text-muted-foreground">
                    Seleccionados: {selectedSectors.join(', ')}
                </div>
            )}
          </div>

          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
                Cancelar
              </Button>
            </DialogClose>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Añadiendo...' : 'Añadir Noticia'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}; 