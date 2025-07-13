"use client";

import React from 'react';
import Link from 'next/link';
import { FaBrain, FaCode, FaCube } from 'react-icons/fa';
import { AnimatedSection } from '@/components/ui/animated-section';
import { Button } from '@/components/ui/button';

import { PhilosophySection } from '@/components/home/PhilosophySection';
import { LatestBlogPostsList } from '@/components/home/LatestBlogPostsList';
import { HeroSection } from '@/components/home/HeroSection';
import { FeaturedProjectsList } from '@/components/home/FeaturedProjectsList';
import { HeroBackgroundCarousel } from '@/components/home/HeroBackgroundCarousel';
import { getNews } from '@/services/newsService';
import { NewsCard } from '@/components/news/NewsCard';
import { useState, useEffect } from 'react';
import type { NewsItemRead } from '@/types';

const SectionTitle = ({ children }: { children: React.ReactNode }) => (
  <h2 className="text-3xl md:text-4xl font-semibold text-center mb-12">
    {children}
  </h2>
);

export default function HomePage() {
  // Estado para las noticias recientes
  const [news, setNews] = useState<NewsItemRead[]>([]);
  const [loadingNews, setLoadingNews] = useState(true);

  useEffect(() => {
    async function fetchNews() {
      try {
        const response = await getNews({ per_page: 3, page: 1 });
        setNews(response.items || []);
      } catch {
        setNews([]);
      } finally {
        setLoadingNews(false);
      }
    }
    fetchNews();
  }, []);

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

      {/* Últimas noticias de IA (reemplaza testimonios) */}
      <AnimatedSection className="w-full py-16 md:py-24 bg-muted/30 dark:bg-muted/5">
        <div className="container mx-auto px-4">
          <SectionTitle>Latest AI News</SectionTitle>
          {loadingNews ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="h-64 bg-muted rounded-lg animate-pulse" />
              <div className="h-64 bg-muted rounded-lg animate-pulse" />
              <div className="h-64 bg-muted rounded-lg animate-pulse" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {news.map((item) => (
                <NewsCard key={item.id} item={item} onEdit={() => {}} onDelete={() => {}} className="md:col-span-1" />
              ))}
            </div>
          )}
          <div className="text-center mt-12">
            <Link href="/news" className="text-primary hover:underline font-medium">
              View all news →
            </Link>
          </div>
        </div>
      </AnimatedSection>

      {/* Contact Section */}
      <section className="w-full py-16 md:py-24 bg-muted/30">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-8">For more information, contact me.</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Do you have questions, want to know more about my services, or need a custom solution in AI or digital development? I am available to answer any inquiries and explore possible collaborations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/contact">
              <Button size="lg" className="w-full sm:w-auto">
                Contact
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




