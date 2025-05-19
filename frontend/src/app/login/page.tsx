"use client";

import React, { useState } from "react";
import { useRouter } from 'next/navigation';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Eye, EyeOff, Github, Mail } from "lucide-react";
import { RiGoogleFill } from "@remixicon/react";
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';

const LoginForm = () => {
  const router = useRouter();
  const auth = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await auth.login(email, password);
    } catch (err: any) {
      // No es necesario hacer nada aquí si el contexto actualiza su propio estado de error
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-background/90 p-4">
      <div className="w-full max-w-md bg-card rounded-2xl shadow-xl overflow-hidden border border-border relative">
        {/* Decorative gradient */}
        <div className="absolute top-0 left-0 right-0 h-48 bg-gradient-to-b from-primary/10 via-primary/5 to-transparent opacity-40 blur-3xl -mt-20"></div>
        
        <div className="p-8 relative z-10">
          {/* Header */}
          <div className="flex flex-col items-center mb-8">
            <div className="bg-background p-4 rounded-2xl shadow-lg mb-6 border border-border/50">
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
                <Mail className="h-6 w-6 text-primary" />
              </div>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-foreground text-center">
                Bienvenido de nuevo
              </h2>
              <p className="text-center text-muted-foreground mt-2">
                Inicia sesión para continuar a tu cuenta
              </p>
            </div>
          </div>

          {/* Form */}
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
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="password">Contraseña</Label>
                <a href="#" className="text-xs text-primary hover:underline">
                  ¿Olvidaste tu contraseña?
                </a>
              </div>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="h-12 pr-12"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-1 top-1/2 -translate-y-1/2 h-9 w-9"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            {auth.error && <p className="text-sm text-red-500 text-center">{auth.error}</p>}

            <Button 
              type="submit" 
              className="w-full h-12 font-medium"
            >
              Iniciar sesión
            </Button>

            {/* Divider */}
            <div className="flex items-center my-4">
              <div className="flex-1 h-px bg-border"></div>
              <span className="px-4 text-sm text-muted-foreground">
                o continuar con
              </span>
              <div className="flex-1 h-px bg-border"></div>
            </div>

            {/* Social login */}
            <div className="grid grid-cols-2 gap-3">
              <Button 
                type="button" 
                variant="outline" 
                className="h-12 gap-2"
              >
                <RiGoogleFill className="h-5 w-5" />
                <span>Google</span>
              </Button>
              <Button 
                type="button" 
                variant="outline" 
                className="h-12 gap-2"
              >
                <Github className="h-5 w-5" />
                <span>GitHub</span>
              </Button>
            </div>
          </form>

          {/* Footer */}
          <div className="mt-6">
            <p className="text-sm text-center text-muted-foreground">
              ¿No tienes una cuenta?{" "}
              <Link href="/register" className="text-primary hover:underline font-medium">
                Regístrate
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Example usage
export default function LoginPage() {
  return <LoginForm />;
} 