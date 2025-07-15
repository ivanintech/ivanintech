'use client';

import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Pencil, Trash2 } from 'lucide-react';

interface EditableImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  alt: string;
  onEdit: () => void;
  onDelete: () => void;
  wrapperClassName?: string;
}

export function EditableImage({ onEdit, onDelete, wrapperClassName, ...props }: EditableImageProps) {
  const { user } = useAuth();

  if (!user?.is_superuser) {
    // Si no es superusuario, renderiza la imagen normal sin controles
    return <img {...props} alt={props.alt} />;
  }

  // Si es superusuario, envuelve la imagen con controles de edición
  return (
    <div className={wrapperClassName || "relative group w-full h-full"}>
      <img {...props} alt={props.alt} />
      
      {/* Overlay con botones que aparece al hacer hover */}
      <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <div className="flex gap-4">
          <Button variant="outline" size="icon" onClick={onEdit}>
            <Pencil className="w-5 h-5" />
            <span className="sr-only">Editar imagen</span>
          </Button>
          <Button variant="destructive" size="icon" onClick={onDelete}>
            <Trash2 className="w-5 h-5" />
            <span className="sr-only">Eliminar imagen</span>
          </Button>
        </div>
      </div>
    </div>
  );
} 