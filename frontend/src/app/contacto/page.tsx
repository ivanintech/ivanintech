'use client'; // Necesario para usar hooks (useState, etc.)

import { useState } from 'react';
import type { FormEvent } from 'react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Loader2 } from 'lucide-react'; // Icono de carga
import { API_V1_URL } from '@/lib/api-client'; // Importar URL base

export default function ContactoPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [isError, setIsError] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setStatusMessage('');
    setIsError(false);

    try {
      const response = await fetch(`${API_V1_URL}/contact/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, message }),
      });

      const result = await response.json();

      if (response.ok) {
        setStatusMessage(result.message || 'Mensaje enviado con éxito.');
        setName('');
        setEmail('');
        setMessage('');
      } else {
        throw new Error(result.detail || 'Error al enviar el mensaje.');
      }
    } catch (error) {
      console.error('Submission error:', error);
      setIsError(true);
      setStatusMessage(error instanceof Error ? error.message : 'Ocurrió un error inesperado.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-center mb-8 text-primary">Contacto</h1>
      <p className="text-center text-lg text-foreground/80 mb-12 max-w-2xl mx-auto">
        ¿Tienes alguna pregunta, propuesta o simplemente quieres conectar? 
        ¡No dudes en enviarme un mensaje!
      </p>

      <div className="max-w-xl mx-auto bg-card p-8 border rounded-lg shadow-md">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <Label htmlFor="name">Nombre</Label>
            <Input 
              type="text" 
              id="name" 
              name="name" 
              required 
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Tu nombre"
              disabled={isLoading}
            />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input 
              type="email" 
              id="email" 
              name="email" 
              required 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@email.com"
              disabled={isLoading}
            />
          </div>
          <div>
            <Label htmlFor="message">Mensaje</Label>
            <Textarea 
              id="message" 
              name="message" 
              rows={5} 
              required 
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Escribe tu mensaje aquí..."
              disabled={isLoading}
            />
          </div>
          
          {/* Mensajes de estado */} 
          {statusMessage && (
            <p className={`text-sm ${isError ? 'text-destructive' : 'text-emerald-600 dark:text-emerald-500'}`}>
              {statusMessage}
            </p>
          )}

          <div>
            <Button 
              type="submit" 
              className="w-full transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 hover:brightness-110 shadow-lg hover:shadow-primary/30"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Enviando...
                </>
              ) : (
                'Enviar Mensaje'
              )}
            </Button>
          </div>
        </form>
      </div>
      
      {/* Opcional: Otras formas de contacto */}
      <div className="text-center mt-12">
          <p className="text-foreground/70">También puedes encontrarme en:</p>
          {/* Añadir enlaces a LinkedIn, GitHub, etc. con iconos si es posible */}
          <a href="https://www.linkedin.com/in/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a/" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline mx-2">LinkedIn</a>
          <a href="https://github.com/ivanintech" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline mx-2">GitHub</a>
      </div>
    </div>
  );
} 