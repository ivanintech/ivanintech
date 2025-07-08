'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Edit } from 'lucide-react';
import { HeroMediaManager } from '@/components/home/HeroMediaManager';

export function HeroSection({ children }: { children: React.ReactNode }) {
    const { user } = useAuth();
    const [isManagerOpen, setIsManagerOpen] = useState(false);

    return (
        <section className="relative w-full flex items-center justify-center min-h-[calc(100vh-80px)] py-20 md:py-32 lg:py-40 text-white overflow-hidden">
            {children}
            <div className="absolute inset-0 bg-black/50 z-10"></div>

            {user?.is_superuser && (
                <div className="absolute top-4 right-4 z-30">
                    <Button onClick={() => setIsManagerOpen(true)} variant="outline" className="bg-black/50 hover:bg-black/70 border-white/30">
                        <Edit className="w-4 h-4 mr-2" />
                        Edit Background
                    </Button>
                </div>
            )}

            <HeroMediaManager isOpen={isManagerOpen} onClose={() => setIsManagerOpen(false)} />

            <div className="container mx-auto px-4 text-center relative z-20">
                <h1 className="text-5xl md:text-7xl font-bold mb-6 text-white animate-fade-in-up">
                    Iván In Tech
                </h1>
                <p className="text-xl md:text-2xl text-gray-200 mb-10 max-w-3xl mx-auto animate-fade-in-up animation-delay-200">
                    AI Engineer exploring the intersection of artificial intelligence,
                    modern web development, and the tech future.
                </p>
                <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4 animate-fade-in-up animation-delay-400">
                    <Link
                        href="/about-me"
                        className="inline-block bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-3 rounded-md text-lg font-medium transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 hover:brightness-110 shadow-lg hover:shadow-primary/30 w-full sm:w-auto"
                    >
                        About Me
                    </Link>
                    <Link
                        href="/portfolio"
                        className="inline-block bg-white/10 backdrop-blur-sm border border-white/20 text-white hover:bg-white/20 px-8 py-3 rounded-md text-lg font-medium transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 w-full sm:w-auto"
                    >
                        View Portfolio
                    </Link>
                </div>
            </div>
        </section>
    );
} 