'use client';

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import apiClient from '@/lib/api-client';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import { Trash2, Film, Image as ImageIcon } from 'lucide-react';

interface HeroMediaItem {
  id: number;
  name: string;
  media_type: 'image' | 'video';
  media_url: string;
  order?: number;
}

interface HeroMediaManagerProps {
  isOpen: boolean;
  onClose: () => void;
}

export function HeroMediaManager({ isOpen, onClose }: HeroMediaManagerProps) {
  const { token } = useAuth();
  const [mediaItems, setMediaItems] = useState<HeroMediaItem[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchMediaItems = async () => {
    setLoading(true);
    try {
      const data = await apiClient<HeroMediaItem[]>('/hero/');
      setMediaItems(data);
    } catch (error) {
      toast.error('Failed to load media items.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchMediaItems();
    }
  }, [isOpen]);

  const handleDelete = async (id: number) => {
    if (!token) {
      toast.error('Authentication token not found.');
      return;
    }
    try {
      await apiClient<void>(`/hero/${id}`, {
        method: 'DELETE',
        token: token,
      });
      toast.success('Media item deleted successfully.');
      setMediaItems((prevItems) => prevItems.filter((item) => item.id !== id));
    } catch (error) {
      toast.error('Failed to delete media item.');
      console.error(error);
    }
  };

  const handleAddMedia = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token) {
      toast.error('Authentication token not found.');
      return;
    }

    const form = event.currentTarget;
    const mediaNameInput = form.elements.namedItem('media-name') as HTMLInputElement;
    const mediaFileInput = form.elements.namedItem('media-file') as HTMLInputElement;

    const file = mediaFileInput.files?.[0];
    const name = mediaNameInput.value;

    if (!file || !name) {
      toast.error('Please provide a name and a file.');
      return;
    }

    // 1. Upload the file
    const formData = new FormData();
    formData.append('file', file);

    try {
      const uploadResponse = await apiClient<{ media_url: string }>('/utils/upload-hero-media/', {
        method: 'POST',
        token,
        body: formData,
      });

      const mediaUrl = uploadResponse.media_url;
      const mediaType = file.type.startsWith('video') ? 'video' : 'image';

      // 2. Create the media item record
      const newMediaItem = await apiClient<HeroMediaItem>('/hero/', {
        method: 'POST',
        token,
        body: {
          name,
          media_type: mediaType,
          media_url: mediaUrl,
        },
      });

      toast.success('Media item added successfully!');
      setMediaItems((prev) => [...prev, newMediaItem].sort((a,b) => (a.order || 0) - (b.order || 0)));
      form.reset();
    } catch (error) {
      toast.error('Failed to add media item.');
      console.error(error);
    }
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Manage Hero Background</DialogTitle>
          <DialogDescription>
            Add, remove, and reorder the media items for the homepage carousel.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid grid-cols-2 gap-8">
          {/* Columna para añadir nuevos */}
          <div className="border-r pr-8">
            <h3 className="text-lg font-semibold mb-4">Add New Media</h3>
            <form onSubmit={handleAddMedia} className="space-y-4">
               <div>
                  <Label htmlFor="media-name">Media Name</Label>
                  <Input id="media-name" required placeholder="e.g., Beach Sunset Video" />
               </div>
               <div>
                  <Label htmlFor="media-file">Media File (Image or Video)</Label>
                  <Input id="media-file" type="file" required />
               </div>
               <Button type="submit">Add Media</Button>
            </form>
          </div>
          
          {/* Columna para ver los existentes */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Current Media</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {loading && <p>Loading...</p>}
              {!loading && mediaItems.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-2 rounded-md bg-muted">
                  <div className="flex items-center gap-3">
                    {item.media_type === 'image' ? <ImageIcon className="h-5 w-5" /> : <Film className="h-5 w-5" />}
                    <span className="font-medium">{item.name}</span>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => handleDelete(item.id)}>
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              ))}
              {!loading && mediaItems.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">No media items found.</p>
              )}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 