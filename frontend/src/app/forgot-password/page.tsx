"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { ArrowLeft, Mail } from 'lucide-react';
import apiClient from '@/lib/api-client';

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    toast.loading('Enviando enlace de recuperación...');

    try {
      await apiClient(`/password-recovery/${email}`, { method: 'POST' });
      
      toast.dismiss();
      toast.success('Correo enviado', {
        description: 'Si existe una cuenta con ese correo, recibirás un enlace para restablecer tu contraseña.',
        duration: 8000
      });
      router.push('/login');
    } catch {
      toast.dismiss();
      // Mostramos un mensaje genérico para no revelar si un email existe o no
      toast.success('Correo enviado', {
        description: 'Si existe una cuenta con ese correo, recibirás un enlace para restablecer tu contraseña.',
        duration: 8000
      });
       router.push('/login');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-background/90 p-4">
      <div className="w-full max-w-md bg-card rounded-2xl shadow-xl overflow-hidden border border-border relative">
        <div className="absolute top-0 left-0 right-0 h-48 bg-gradient-to-b from-primary/10 via-primary/5 to-transparent opacity-40 blur-3xl -mt-20"></div>
        <div className="p-8 relative z-10">
          
          <div className="flex flex-col items-center mb-8">
             <div className="bg-background p-4 rounded-2xl shadow-lg mb-6 border border-border/50">
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
                <Mail className="h-6 w-6 text-primary" />
              </div>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-foreground text-center">¿Olvidaste tu contraseña?</h2>
              <p className="text-center text-muted-foreground mt-2">No te preocupes. Introduce tu email y te enviaremos un enlace para recuperarla.</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email">Correo electrónico</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="tu@email.com" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                required 
                className="h-12"
                disabled={isLoading}
              />
            </div>

            <Button type="submit" className="w-full h-12 font-medium" disabled={isLoading}>
              {isLoading ? 'Enviando...' : 'Enviar enlace de recuperación'}
            </Button>
          </form>

          <div className="mt-6">
            <Link href="/login" className="text-sm text-center text-muted-foreground flex items-center justify-center gap-2 hover:text-primary transition-colors">
              <ArrowLeft className="h-4 w-4" />
              Volver a inicio de sesión
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
} 