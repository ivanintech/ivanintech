'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Image as ImageIcon, X, Edit } from 'lucide-react';

interface AvatarUploaderProps {
  onFileSelect: (file: File | null) => void;
  currentAvatarUrl?: string;
}

export function AvatarUploader({ onFileSelect, currentAvatarUrl }: AvatarUploaderProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Si la URL del avatar actual cambia desde el padre (p.ej. después de guardar),
    // y no estamos previsualizando un archivo nuevo, limpiamos la preview.
    // Esto asegura que si el usuario sube, cancela, y luego los datos se refrescan,
    // el componente muestre la imagen correcta.
    if (currentAvatarUrl) {
      setPreview(null);
    }
  }, [currentAvatarUrl]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0] || null;
    onFileSelect(selectedFile); // Notificar al padre sobre el archivo seleccionado

    if (selectedFile) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    } else {
      setPreview(null); // Limpiar preview si no se selecciona archivo
    }
  };
  
  const triggerFileSelect = () => fileInputRef.current?.click();

  const clearPreview = (e: React.MouseEvent) => {
    e.stopPropagation();
    setPreview(null);
    onFileSelect(null);
    if(fileInputRef.current) {
        fileInputRef.current.value = "";
    }
  };

  const displayUrl = preview || currentAvatarUrl;

  return (
    <div className="flex flex-col items-center space-y-4">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept="image/*"
      />
      <div
        className="relative w-32 h-32 bg-muted rounded-full flex items-center justify-center cursor-pointer group border-2 border-dashed border-border hover:border-primary transition-colors"
        onClick={triggerFileSelect}
      >
        {displayUrl ? (
          <>
            <img src={displayUrl} alt="Avatar" className="rounded-full w-full h-full object-cover" />
            <div className="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <Edit className="h-8 w-8 text-white" />
            </div>
            {preview && (
                 <button
                    onClick={clearPreview}
                    className="absolute top-0 right-0 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-transform transform hover:scale-110"
                    aria-label="Cancelar cambio"
                >
                    <X className="h-4 w-4" />
                </button>
            )}
          </>
        ) : (
          <div className="text-center text-muted-foreground">
            <ImageIcon className="h-8 w-8 mx-auto" />
            <p className="text-xs mt-1">Subir imagen</p>
          </div>
        )}
      </div>
    </div>
  );
} 