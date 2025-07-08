'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import apiClient from '@/lib/api-client';
import type { Project } from '@/types'; // Importar el tipo global

interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
  project?: Project;
}

const getInitialFormData = (): Omit<Project, 'id' | 'created_at' | 'updated_at'> => ({
  title: '',
  description: '',
  technologies: [],
  imageUrl: '',
  videoUrl: '',
  githubUrl: '',
  liveUrl: '',
  is_featured: false,
  category: 'all',
});

export default function ProjectModal({ isOpen, onClose, onSave, project }: ProjectModalProps) {
  const [formData, setFormData] = useState(getInitialFormData());
  const [technologiesInput, setTechnologiesInput] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && project) {
      setFormData({
        title: project.title || '',
        description: project.description || '',
        technologies: project.technologies || [],
        imageUrl: project.imageUrl || '',
        videoUrl: project.videoUrl || '',
        githubUrl: project.githubUrl || '',
        liveUrl: project.liveUrl || '',
        is_featured: project.is_featured || false,
        category: project.category || 'all',
      });
      const techNames = Array.isArray(project.technologies) 
        ? project.technologies.map(tech => 
            typeof tech === 'string' ? tech : (tech && typeof tech === 'object' && 'name' in tech ? tech.name : '')
          ).filter(Boolean)
        : [];
      setTechnologiesInput(techNames.join(', '));
    } else if (isOpen) {
      setFormData(getInitialFormData());
      setTechnologiesInput('');
    }
  }, [project, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const projectData = {
        ...formData,
        technologies: technologiesInput.split(',').map(tech => tech.trim()).filter(tech => tech),
      };

      if (project?.id) {
        // Actualizar proyecto existente
        await apiClient(`/projects/${project.id}`, {
          method: 'PUT',
          body: projectData,
        });
      } else {
        // Crear nuevo proyecto
        await apiClient('/projects/', {
          method: 'POST',
          body: projectData,
        });
      }

      onSave();
      onClose();
    } catch (error) {
      console.error('Error saving project:', error);
      alert('Error al guardar el proyecto');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {project ? 'Editar Proyecto' : 'Nuevo Proyecto'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="title">Título *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
            />
          </div>

          <div>
            <Label htmlFor="description">Descripción</Label>
            <Textarea
              id="description"
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
            />
          </div>

          <div>
            <Label htmlFor="technologies">Tecnologías (separadas por comas)</Label>
            <Input
              id="technologies"
              value={technologiesInput}
              onChange={(e) => setTechnologiesInput(e.target.value)}
              placeholder="React, TypeScript, Next.js"
            />
          </div>

          <div>
            <Label htmlFor="imageUrl">URL de Imagen</Label>
            <Input
              id="imageUrl"
              value={formData.imageUrl || ''}
              onChange={(e) => setFormData({ ...formData, imageUrl: e.target.value })}
              placeholder="https://example.com/image.jpg"
            />
          </div>

          <div>
            <Label htmlFor="videoUrl">URL de Video</Label>
            <Input
              id="videoUrl"
              value={formData.videoUrl || ''}
              onChange={(e) => setFormData({ ...formData, videoUrl: e.target.value })}
              placeholder="https://example.com/video.mp4"
            />
          </div>

          <div>
            <Label htmlFor="githubUrl">URL de GitHub</Label>
            <Input
              id="githubUrl"
              value={formData.githubUrl || ''}
              onChange={(e) => setFormData({ ...formData, githubUrl: e.target.value })}
              placeholder="https://github.com/user/repo"
            />
          </div>

          <div>
            <Label htmlFor="liveUrl">URL Live Demo</Label>
            <Input
              id="liveUrl"
              value={formData.liveUrl || ''}
              onChange={(e) => setFormData({ ...formData, liveUrl: e.target.value })}
              placeholder="https://example.com"
            />
          </div>

          <div className="flex items-center space-x-2">
            <Switch
              id="is_featured"
              checked={formData.is_featured || false}
              onCheckedChange={(checked) => setFormData({ ...formData, is_featured: checked })}
            />
            <Label htmlFor="is_featured">Proyecto Destacado</Label>
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Guardando...' : (project ? 'Actualizar' : 'Crear')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
} 