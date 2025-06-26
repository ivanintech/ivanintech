'use client'; // Necesario para usar hooks (useState, etc.)

import { useState } from 'react';
import type { FormEvent } from 'react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Loader2 } from 'lucide-react'; // Loading icon
import apiClient from '@/lib/api-client'; // Cambiado

export default function ContactPage() {
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
      const result = await apiClient<{ message: string }>('/contact/submit', {
        method: 'POST',
        body: { name, email, message },
      });

        setStatusMessage(result.message || 'Message sent successfully.');
        setName('');
        setEmail('');
        setMessage('');
      
    } catch (error) {
      console.error('Submission error:', error);
      setIsError(true);
      setStatusMessage(error instanceof Error ? error.message : 'An unexpected error occurred.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-center mb-8 text-primary">Contact</h1>
      <p className="text-center text-lg text-foreground/80 mb-12 max-w-2xl mx-auto">
        Have a question, a proposal, or just want to connect? 
        Feel free to send me a message!
      </p>

      <div className="max-w-xl mx-auto bg-card p-8 border rounded-lg shadow-md">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <Label htmlFor="name">Name</Label>
            <Input 
              type="text" 
              id="name" 
              name="name" 
              required 
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
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
              placeholder="you@email.com"
              disabled={isLoading}
            />
          </div>
          <div>
            <Label htmlFor="message">Message</Label>
            <Textarea 
              id="message" 
              name="message" 
              rows={5} 
              required 
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Write your message here..."
              disabled={isLoading}
            />
          </div>
          
          {/* Status Messages */} 
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
                  Sending...
                </>
              ) : (
                'Send Message'
              )}
            </Button>
          </div>
        </form>
      </div>
      
      {/* Optional: Other contact methods */}
      <div className="text-center mt-12">
          <p className="text-foreground/70">You can also find me on:</p>
          {/* Add links to LinkedIn, GitHub, etc. with icons if possible */}
          <a href="https://www.linkedin.com/in/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a/" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline mx-2">LinkedIn</a>
          <a href="https://github.com/ivanintech" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline mx-2">GitHub</a>
      </div>
    </div>
  );
} 