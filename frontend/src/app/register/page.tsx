'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Eye, EyeOff, UserPlus, Link as LinkIcon } from "lucide-react";
import { AvatarUploader } from '@/components/ui/AvatarUploader';

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [websiteUrl, setWebsiteUrl] = useState("");

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }

    try {
      let avatarUrl: string | undefined = undefined;

      // 1. Subir el avatar si existe
      if (avatarFile) {
        setIsUploading(true);
        const formData = new FormData();
        formData.append("file", avatarFile);

        const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
        const avatarResponse = await fetch(`${apiBaseUrl}/api/v1/users/upload-avatar`, {
          method: 'POST',
          body: formData,
        });

        const avatarData = await avatarResponse.json();
        setIsUploading(false);

        if (!avatarResponse.ok) {
          throw new Error(avatarData.detail || "Error uploading the image.");
        }
        avatarUrl = avatarData.avatar_url;
      }
      
      // 2. Registrar al usuario (con o sin extras)
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiBaseUrl}/api/v1/users/open`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password,
          full_name: fullName || undefined,
          avatar_url: avatarUrl,
          website_url: websiteUrl || undefined,
        }),
      });

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.detail || 'Error registering the user.');
      }
      
      // User registered successfully
      setSuccessMessage("User registered successfully! You will be redirected to the login page.");
      console.log("Registration successful:", responseData);
      
      // Redirigir al login después de un breve retraso
      setTimeout(() => {
        router.push('/login');
      }, 2000);

    } catch (err: unknown) {
      console.error("Registration failed:", err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred during registration.');
      }
      setIsUploading(false);
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
                <UserPlus className="h-6 w-6 text-primary" />
              </div>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-foreground text-center">
                Create an Account
              </h2>
              <p className="text-center text-muted-foreground mt-2">
                Join to access all features.
              </p>
            </div>
          </div>

          <form onSubmit={handleRegisterSubmit} className="space-y-5">
            <div className="flex justify-center">
              <AvatarUploader onFileSelect={setAvatarFile} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="fullName">Full Name (Optional)</Label>
              <Input 
                id="fullName"
                type="text"
                placeholder="Your full name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="h-12"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email_register">Email</Label>
              <Input 
                id="email_register"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-12"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="websiteUrl">Website (Optional)</Label>
              <div className="relative">
                <LinkIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input 
                  id="websiteUrl"
                  type="url"
                  placeholder="https://your-website.com"
                  value={websiteUrl}
                  onChange={(e) => setWebsiteUrl(e.target.value)}
                  className="h-12 pl-10"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="password_register">Password</Label>
              <div className="relative">
                <Input
                  id="password_register"
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
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm password</Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="h-12 pr-12"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-1 top-1/2 -translate-y-1/2 h-9 w-9"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            {error && <p className="text-sm text-red-500 text-center py-2">{error}</p>}
            {successMessage && <p className="text-sm text-green-500 text-center py-2">{successMessage}</p>}

            <Button 
              type="submit" 
              className="w-full h-12 font-medium"
              disabled={isUploading}
            >
              {isUploading ? "Processing..." : "Create account"}
            </Button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link href="/login" className="text-primary hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
} 