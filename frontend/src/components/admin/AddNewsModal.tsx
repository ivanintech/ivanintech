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
import type { NewsItemCreate } from '@/types';
import { toast } from 'sonner'; // Para notificaciones (opcional, pero bueno)

interface AddNewsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddNews: (newsData: NewsItemCreate) => Promise<void>; // Función para manejar el envío
  defaultSectors?: string[]; // Sectores comunes para preseleccionar o sugerir
}

const initialFormData: NewsItemCreate = {
  title: '',
  url: '',
  description: '',
  publishedAt: new Date().toISOString(),
  sectors: [],
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
      toast.success('News item added successfully!');
      onClose(); // Close modal after adding
    } catch (error) {
      const err = error as Error;
      console.error("Error adding news item:", err);
      toast.error(err.message || 'Could not add the news item.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open: boolean) => !open && onClose()}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Add New News Item</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          <div>
            <Label htmlFor="title">Title</Label>
            <Input id="title" name="title" value={formData.title} onChange={handleChange} required />
          </div>
          <div>
            <Label htmlFor="url">Source URL</Label>
            <Input id="url" name="url" type="url" value={formData.url} onChange={handleChange} required />
          </div>
          <div>
            <Label htmlFor="description">Summary</Label>
            <Textarea id="description" name="description" value={formData.description ?? ''} onChange={handleChange} required />
          </div>
          {/* <div>
            <Label htmlFor="imageUrl">Image URL (Optional)</Label>
            <Input id="imageUrl" name="imageUrl" type="url" value={formData.imageUrl || ''} onChange={handleChange} />
          </div> */}
          <div>
            <Label htmlFor="publishedAt">Publication Date</Label>
            <Input 
              id="publishedAt" 
              name="publishedAt" 
              type="datetime-local" // Allows selecting date and time
              value={formData.publishedAt ? new Date(formData.publishedAt).toISOString().substring(0, 16) : ''} // Format for datetime-local
              onChange={(e) => setFormData((prev: NewsItemCreate) => ({ ...prev, publishedAt: new Date(e.target.value).toISOString() }))} 
              required 
            />
          </div>
          
          <div>
            <Label>Sectors</Label>
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
                placeholder="Add new sector" 
                value={newSector}
                onChange={(e) => setNewSector(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddNewSector())}
              />
              <Button type="button" onClick={handleAddNewSector} variant="outline" size="sm">Add</Button>
            </div>
            {selectedSectors.length > 0 && (
                <div className="mt-2 text-sm text-muted-foreground">
                    Selected: {selectedSectors.join(', ')}
                </div>
            )}
          </div>

          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
                Cancel
              </Button>
            </DialogClose>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Adding...' : 'Add News Item'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}; 