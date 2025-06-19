"use client";

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { loginWithGoogle, loginWithGitHubCode } from '@/services/authService';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Github, Mail, Eye, EyeOff } from 'lucide-react';

// Un componente simple para el ícono de Google para no instalar más dependencias
const GoogleIcon = (props: React.ComponentProps<'svg'>) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="24px" height="24px" {...props}><path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12s5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24s8.955,20,20,20s20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z" /><path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z" /><path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.222,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z" /><path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.089,5.571l6.19,5.238C42.022,35.283,44,30.038,44,24C44,22.659,43.862,21.35,43.611,20.083z" /></svg>
);

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setAuthData, loginWithCredentials } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isGitHubLoading, setIsGitHubLoading] = useState(false);
  const [isGitHubCallbackLoading, setIsGitHubCallbackLoading] = useState(false);

  useEffect(() => {
    const githubCode = searchParams.get('code');
    if (githubCode) {
      setIsGitHubCallbackLoading(true);
      toast.loading('Finalizando autenticación con GitHub...');
      
      loginWithGitHubCode(githubCode)
        .then(data => {
          toast.dismiss();
          setAuthData(data);
          toast.success(`¡Bienvenido, ${data.user.full_name || data.user.email}!`);
          router.replace('/login');
          router.push('/noticias');
        })
        .catch(error => {
          toast.dismiss();
          toast.error(error.message || 'Error al iniciar sesión con GitHub.');
          router.replace('/login');
        });
    }
  }, [searchParams, setAuthData, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await loginWithCredentials({ username: email, password });
      toast.success('¡Bienvenido de nuevo!');
      router.push('/noticias');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Error desconocido.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsGoogleLoading(true);
    try {
      const data = await loginWithGoogle();
      setAuthData(data);
      toast.success(`¡Bienvenido, ${data.user.full_name || data.user.email}!`);
      router.push('/noticias');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Error desconocido.');
    } finally {
      setIsGoogleLoading(false);
    }
  };
  
  const handleGitHubRedirect = () => {
    setIsGitHubLoading(true);
    const githubClientId = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID;
    if (!githubClientId) {
      toast.error("La configuración para el login con GitHub no está disponible.");
      setIsGitHubLoading(false);
      return;
    }
    const authUrl = new URL('https://github.com/login/oauth/authorize');
    authUrl.searchParams.append('client_id', githubClientId);
    authUrl.searchParams.append('scope', 'read:user user:email');
    window.location.href = authUrl.toString();
  };

  if (isGitHubCallbackLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <p>Verificando con GitHub...</p>
      </div>
    );
  }
  
  const anyLoading = isLoading || isGoogleLoading || isGitHubLoading;

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
              <h2 className="text-2xl font-bold text-foreground text-center">Bienvenido de nuevo</h2>
              <p className="text-center text-muted-foreground mt-2">Inicia sesión para continuar</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email">Correo electrónico</Label>
              <Input id="email" type="email" placeholder="tu@email.com" value={email} onChange={(e) => setEmail(e.target.value)} required className="h-12" disabled={anyLoading} />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="password">Contraseña</Label>
                <Link href="#" className="text-xs text-primary hover:underline">¿Olvidaste tu contraseña?</Link>
              </div>
              <div className="relative">
                <Input id="password" type={showPassword ? "text" : "password"} placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required className="h-12 pr-12" disabled={anyLoading} />
                <Button type="button" variant="ghost" size="icon" className="absolute right-1 top-1/2 -translate-y-1/2 h-9 w-9" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}>
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <Button type="submit" className="w-full h-12 font-medium" disabled={anyLoading}>
              {isLoading ? 'Iniciando...' : 'Iniciar sesión'}
            </Button>
            
            <div className="flex items-center my-4">
              <div className="flex-1 h-px bg-border"></div>
              <span className="px-4 text-sm text-muted-foreground">o continuar con</span>
              <div className="flex-1 h-px bg-border"></div>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <Button onClick={handleGoogleLogin} disabled={anyLoading} variant="outline" className="h-12 gap-2">
                {isGoogleLoading ? 'Cargando...' : <><GoogleIcon className="h-5 w-5" /><span>Google</span></>}
              </Button>
              <Button onClick={handleGitHubRedirect} disabled={anyLoading} variant="outline" className="h-12 gap-2">
                {isGitHubLoading ? 'Redirigiendo...' : <><Github className="h-5 w-5" /><span>GitHub</span></>}
              </Button>
            </div>
          </form>

          <div className="mt-6">
            <p className="text-sm text-center text-muted-foreground">
              ¿No tienes una cuenta?{" "}
              <Link href="/register" className="text-primary hover:underline font-medium">Regístrate</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <LoginForm />
        </Suspense>
    )
}
