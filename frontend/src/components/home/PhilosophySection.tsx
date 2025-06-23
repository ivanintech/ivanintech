'use client';

import { AnimatedSection } from "@/components/ui/animated-section";
import { EditableImage } from "@/components/ui/EditableImage";
import { toast } from 'sonner';

export function PhilosophySection() {
    return (
        <AnimatedSection className="w-full relative py-32 md:py-48 overflow-hidden">
            <EditableImage
                wrapperClassName="absolute inset-0 group"
                src="/img/ivan-thinking-near-the-sea.jpg"
                fill
                style={{ objectFit: "cover" }}
                alt="Iván thinking near the sea"
                className="filter brightness-50 dark:brightness-40 object-cover object-top"
                priority
                onEdit={() => toast.info('Editing static images on the main page will be available soon.')}
                onDelete={() => toast.warning('Deleting static images on the main page will be available soon.')}
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