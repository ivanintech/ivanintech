"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { KeyRound, Eye, EyeOff, ArrowLeft } from 'lucide-react';
import apiClient from '@/lib/api-client';

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [token, setToken] = useState<string | null>(null);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const urlToken = searchParams.get('token');
    if (urlToken) {
      setToken(urlToken);
    } else {
      toast.error("Recovery token not found.", {
          description: "Please request a new link to reset your password."
      });
      router.push('/forgot-password');
    }
  }, [searchParams, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }
    setError('');
    setIsLoading(true);
    toast.loading('Resetting password...');

    try {
      await apiClient('/reset-password/', {
        method: 'POST',
        body: {
          token: token,
          new_password: newPassword,
        },
      });
      
      toast.dismiss();
      toast.success('Password reset successfully', {
        description: 'You can now log in with your new password.',
        duration: 5000
      });
      router.push('/login');
    } catch (err) {
      toast.dismiss();
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred.';
      toast.error('Error resetting password', {
          description: errorMessage
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!token) {
    return (
        <div className="flex items-center justify-center min-h-screen bg-background">
            <p>Verifying token...</p>
        </div>
    );
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-background/90 p-4">
      <div className="w-full max-w-md bg-card rounded-2xl shadow-xl overflow-hidden border border-border relative">
        <div className="p-8 relative z-10">
          
          <div className="flex flex-col items-center mb-8">
             <div className="bg-background p-4 rounded-2xl shadow-lg mb-6 border border-border/50">
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
                <KeyRound className="h-6 w-6 text-primary" />
              </div>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-foreground text-center">Create a new password</h2>
              <p className="text-center text-muted-foreground mt-2">Your new password must be secure and easy to remember.</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="new-password">New Password</Label>
              <div className="relative">
                <Input 
                  id="new-password" 
                  type={showPassword ? "text" : "password"} 
                  placeholder="••••••••" 
                  value={newPassword} 
                  onChange={(e) => setNewPassword(e.target.value)} 
                  required 
                  className="h-12 pr-12"
                  disabled={isLoading}
                />
                 <Button type="button" variant="ghost" size="icon" className="absolute right-1 top-1/2 -translate-y-1/2 h-9 w-9" onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm-password">Confirm Password</Label>
               <div className="relative">
                <Input 
                  id="confirm-password" 
                  type={showConfirmPassword ? "text" : "password"} 
                  placeholder="••••••••" 
                  value={confirmPassword} 
                  onChange={(e) => setConfirmPassword(e.target.value)} 
                  required 
                  className="h-12 pr-12"
                  disabled={isLoading}
                />
                <Button type="button" variant="ghost" size="icon" className="absolute right-1 top-1/2 -translate-y-1/2 h-9 w-9" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>
            
            {error && <p className="text-sm text-destructive text-center">{error}</p>}

            <Button type="submit" className="w-full h-12 font-medium" disabled={isLoading}>
              {isLoading ? 'Saving...' : 'Save new password'}
            </Button>
          </form>

           <div className="mt-6">
            <Link
              href="/login"
              className="text-sm text-center text-muted-foreground flex items-center justify-center gap-2 hover:text-primary transition-colors"
              legacyBehavior>
              <ArrowLeft className="h-4 w-4" />
              Back to login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}


export default function ResetPasswordPage() {
    return (
        <ResetPasswordForm />
    )
} 