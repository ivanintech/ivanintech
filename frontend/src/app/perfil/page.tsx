'use client';

import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { AvatarUploader } from '@/components/ui/AvatarUploader';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import apiClient from '@/lib/api-client';
import { User } from '@/types/api';

export default function ProfilePage() {
  const { user, isLoading, setUser, bustAvatarCache, avatarVersion, apiBaseUrl } = useAuth();
  const router = useRouter();

  const [fullName, setFullName] = useState(user?.full_name || '');
  const [websiteUrl, setWebsiteUrl] = useState(user?.website_url || '');
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
    if (user) {
      setFullName(user.full_name || '');
      setWebsiteUrl(user.website_url || '');
    }
  }, [user, isLoading, router]);
  
  // Usamos useEffect para disparar el "cache buster" DESPUÉS de que el usuario se actualice.
  useEffect(() => {
    // Si la URL del avatar existe y ha cambiado (comparando con algo, o simplemente siempre que el user cambie),
    // disparamos la actualización de la versión.
    // Para simplificar, lo disparamos si hay un usuario.
    if (user?.avatar_url) {
      bustAvatarCache();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.avatar_url]); // Se ejecuta solo cuando la URL del avatar cambia.

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      // 1. Actualizar el avatar si se ha seleccionado uno nuevo
      if (avatarFile) {
        const formData = new FormData();
        formData.append("file", avatarFile);
        const avatarResponse = await apiClient<{ avatar_url: string }>(`/users/upload-avatar`, {
            method: 'POST',
            body: formData,
            isFormData: true,
        });
        // Actualizamos la info del usuario con el nuevo avatar
        const updatedUserWithAvatar = await apiClient<User>(`/users/me/avatar`, {
            method: 'PATCH',
            body: { avatar_url: avatarResponse.avatar_url }
        });
        setUser(updatedUserWithAvatar); // Actualizar el contexto global
      }

      // 2. Actualizar nombre y sitio web
      const updateData: { full_name?: string; website_url?: string | null } = {};
      if (fullName !== (user?.full_name || '')) {
        updateData.full_name = fullName;
      }
      // Solo actualizar si el valor ha cambiado. Enviar `null` si el campo está vacío.
      if (websiteUrl !== (user?.website_url || '')) {
          updateData.website_url = websiteUrl || null;
      }

      if (Object.keys(updateData).length > 0) {
        const updatedUser = await apiClient<User>(`/users/me`, {
          method: 'PATCH',
          body: updateData,
        });
        setUser(updatedUser); // Actualizar el contexto global
      }
      
      setSuccess("¡Perfil actualizado con éxito!");

    } catch (err) {
       const apiError = err as { message?: string };
       setError(apiError.message || "Ocurrió un error al actualizar el perfil.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Construye la URL completa del avatar, combinando la URL base del backend
  // con la ruta relativa del avatar.
  const avatarUrl = user?.avatar_url 
    ? `${apiBaseUrl}${user.avatar_url}?v=${avatarVersion}` 
    : '/img/placeholder-user.png';

  if (isLoading || !user) {
    return <div className="min-h-screen flex items-center justify-center"><p>Cargando perfil...</p></div>;
  }

  return (
    <div className="container mx-auto py-10 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Mi Perfil</CardTitle>
          <CardDescription>Gestiona la información de tu cuenta.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleProfileUpdate} className="space-y-6">
            <div className="space-y-2">
                <Label>Foto de Perfil</Label>
                <AvatarUploader 
                    onFileSelect={setAvatarFile} 
                    currentAvatarUrl={avatarUrl}
                />
            </div>

            <div className="space-y-2">
              <Label htmlFor="fullName">Nombre completo</Label>
              <Input 
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="websiteUrl">Sitio Web</Label>
              <Input 
                id="websiteUrl"
                type="url"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                placeholder="https://tu-sitio-web.com"
              />
            </div>

            {error && <p className="text-sm text-red-500">{error}</p>}
            {success && <p className="text-sm text-green-500">{success}</p>}

            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Guardando...' : 'Guardar Cambios'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
} 