import React from 'react';
import Link from 'next/link';
import { FaBrain, FaCode, FaCube, FaQuoteLeft } from 'react-icons/fa';
import { AnimatedSection } from '@/components/ui/animated-section';
import { Button } from '@/components/ui/button';

import { PhilosophySection } from '@/components/home/PhilosophySection';
import { LatestBlogPostsList } from '@/components/home/LatestBlogPostsList';
import { HeroSection } from '@/components/home/HeroSection';
import { FeaturedProjectsList } from '@/components/home/FeaturedProjectsList';
import { HeroBackgroundCarousel } from '@/components/home/HeroBackgroundCarousel';

const SectionTitle = ({ children }: { children: React.ReactNode }) => (
  <h2 className="text-3xl md:text-4xl font-semibold text-center mb-12">
    {children}
  </h2>
);

const testimonials = [
  {
    id: 't1',
    quote: "Ivan has a unique ability to understand complex problems and translate them into effective AI solutions. His technological vision and product management were key.",
    name: "Pablo Motos",
    title: "CEO & Founder, El Hormiguero",
  },
  {
    id: 't2',
    quote: "Working with Ivan on 3D development was exceptional. He brings creativity, technical rigor, and fluid communication.",
    name: "Pedro Sanchez",
    title: "Technical Director, La que te cuento",
  },
];

export default function HomePage() {
  return (
    <main className="flex flex-col items-center">
      <HeroSection>
        <HeroBackgroundCarousel />
      </HeroSection>

      {/* Featured Projects */}
      <AnimatedSection className="w-full py-16 md:py-24 bg-muted/30 dark:bg-muted/5">
        <div className="container mx-auto px-4">
          <SectionTitle>Featured Projects</SectionTitle>
            <FeaturedProjectsList />
          <div className="text-center mt-12">
            <Link href="/portfolio" className="text-primary hover:underline font-medium">
              View all projects →
            </Link>
          </div>
        </div>
      </AnimatedSection>

      {/* Focus Areas */}
      <AnimatedSection className="w-full py-16 md:py-24">
        <div className="container mx-auto px-4">
          <SectionTitle>Focus Areas</SectionTitle>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="border border-border rounded-lg p-6 bg-background shadow-sm">
              <FaBrain className="w-10 h-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Artificial Intelligence</h3>
              <p className="text-muted-foreground text-sm">From predictive models and NLP to <strong className="font-medium text-foreground/80 dark:text-gray-300">Generative AI</strong> (Langchain, LLMs) for impactful solutions.</p>
            </div>
            <div className="border border-border rounded-lg p-6 bg-background shadow-sm">
              <FaCode className="w-10 h-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Modern Web Development</h3>
              <p className="text-muted-foreground text-sm">Robust and scalable full-stack applications with <strong className="font-medium text-foreground/80 dark:text-gray-300">FastAPI, Next.js, React</strong> and TypeScript.</p>
            </div>
            <div className="border border-border rounded-lg p-6 bg-background shadow-sm">
              <FaCube className="w-10 h-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Data and Digital Twins</h3>
              <p className="text-muted-foreground text-sm">Experience in <strong className="font-medium text-foreground/80 dark:text-gray-300">data analytics, KPIs</strong> and the potential of <strong className="font-medium text-foreground/80 dark:text-gray-300">Digital Twins</strong>.</p>
            </div>
          </div>
        </div>
      </AnimatedSection>

      {/* Latest Blog Posts */}
      <AnimatedSection className="w-full py-16 md:py-24 bg-muted/30 dark:bg-muted/5">
        <div className="container mx-auto px-4">
          <SectionTitle>From the Blog (LinkedIn Activity)</SectionTitle>
            <LatestBlogPostsList />
          <div className="text-center mt-12">
            <Link href="/blog" className="text-primary hover:underline font-medium">
              View all LinkedIn activity →
            </Link>
          </div>
        </div>
      </AnimatedSection>

      {/* Philosophy */}
      <PhilosophySection />

      {/* Testimonials */}
      <AnimatedSection className="w-full py-16 md:py-24">
        <div className="container mx-auto px-4">
          <SectionTitle>What they say about my work</SectionTitle>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {testimonials.map((testimonial) => (
              <div key={testimonial.id} className="border border-border rounded-lg p-6 bg-background shadow-sm text-center">
                <FaQuoteLeft className="w-8 h-8 text-primary/50 mx-auto mb-4" />
                <p className="text-muted-foreground mb-4 italic">&quot;{testimonial.quote}&quot;</p>
                <p className="font-semibold">{testimonial.name}</p>
                <p className="text-sm text-muted-foreground">{testimonial.title}</p>
              </div>
            ))}
          </div>
        </div>
      </AnimatedSection>

      {/* Contact Section */}
      <section className="w-full py-16 md:py-24 bg-muted/30">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-8">¿Hablamos?</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Si tienes un proyecto en mente o quieres colaborar, estaré encantado de conectar contigo.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/contact">
              <Button size="lg" className="w-full sm:w-auto">
                Enviar Mensaje
              </Button>
            </Link>
            <a 
              href="https://www.linkedin.com/in/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a/" 
              target="_blank" 
              rel="noopener noreferrer"
            >
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                LinkedIn
              </Button>
            </a>
          </div>
        </div>
      </section>
    </main>
  );
}

// Force reload - Contact section should appear now




