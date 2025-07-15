'use client';

import { AnimatedSection } from "@/components/ui/animated-section";

export function PhilosophySection() {
    return (
        <AnimatedSection className="w-full relative py-32 md:py-48 overflow-hidden">
            <img
                src="/img/ivan-thinking-near-the-sea.jpg"
                alt="Iván thinking near the sea"
                className="absolute inset-0 w-full h-full filter brightness-50 dark:brightness-40 object-cover object-top"
                style={{ objectFit: 'cover', width: '100%', height: '100%' }}
            />
            <div className="container mx-auto px-4 relative z-10 text-center text-white">
                <h2 className="text-3xl md:text-4xl lg:text-5xl font-semibold mb-6">
                    Technology is a tool; the real odyssey lies in how we use it to explore the unknown.
                </h2>
                <p className="text-lg text-gray-300">
                    - Iván In Tech (Inspired by nature and the dystopian)
                </p>
            </div>
      </AnimatedSection>
    );
} 