"use client";

import React, { useState, useEffect, useMemo } from "react";
import type { NewsItemRead } from "@/types";
import { NewsCard } from "@/components/content/NewsCard";
import NewsForm from "@/components/news/NewsForm";
import { getNews as fetchNews } from "@/services/newsService";
import { useAuth } from "@/context/AuthContext";
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { LogIn } from 'lucide-react';
import { Button } from "@/components/ui/button";

// Función para derivar los sectores más populares de las noticias
const getTopSectors = (news: NewsItemRead[], limit = 7): string[] => {
  const sectorCounts = news.reduce((acc, item) => {
    if (item.sectors) {
      item.sectors.forEach(sector => {
        acc[sector] = (acc[sector] || 0) + 1;
      });
    }
    return acc;
  }, {} as Record<string, number>);

  return Object.entries(sectorCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, limit)
    .map(([sector]) => sector);
};

export default function NewsPage() {
  const [allNews, setAllNews] = useState<NewsItemRead[]>([]);
  const [topSectors, setTopSectors] = useState<string[]>([]);
  const [selectedSector, setSelectedSector] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();
  const isLoggedIn = !!token;

  useEffect(() => {
    const loadNews = async () => {
      try {
        setLoading(true);
        const newsData = await fetchNews({ limit: 100 }); // Pedimos más para tener buenos filtros
        setAllNews(newsData);
        setTopSectors(getTopSectors(newsData));
        setError(null);
      } catch (err) {
        setError("No se pudieron cargar las noticias.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadNews();
  }, []);

  const handleNewsSubmitted = (newNewsItem: NewsItemRead) => {
    const updatedNews = [newNewsItem, ...allNews];
    setAllNews(updatedNews);
    setTopSectors(getTopSectors(updatedNews));
  };

  const filteredNews = useMemo(() => {
    if (!selectedSector) {
      return allNews;
    }
    return allNews.filter(item => item.sectors?.includes(selectedSector));
  }, [allNews, selectedSector]);

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-2">
          Actualidad en IA & Tech
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
          Un feed de noticias y reportajes que analizan el presente y futuro de
          la IA
        </p>
      </header>

      {isLoggedIn && (
        <div className="mb-12 max-w-4xl mx-auto">
          <NewsForm onNewsItemAdded={handleNewsSubmitted} />
        </div>
      )}

      {!isLoggedIn && (
        <Link href="/login" className="block mb-12 transform hover:-translate-y-1 transition-transform duration-300 ease-in-out max-w-4xl mx-auto">
          <Card className="bg-secondary/40 border-primary/20 hover:border-primary/50 transition-all duration-300">
            <CardContent className="p-6 flex items-center justify-center space-x-4">
              <LogIn className="w-8 h-8 text-primary" />
              <div>
                <p className="font-bold text-lg text-primary">¡Únete a la comunidad!</p>
                <p className="text-muted-foreground">Inicia sesión para proponer noticias y participar.</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      )}

      {/* Filtros dinámicos */}
      {!loading && allNews.length > 0 && (
        <div className="mb-12 flex flex-wrap items-center justify-center gap-2">
          <Button
            variant={!selectedSector ? 'default' : 'outline'}
            onClick={() => setSelectedSector(null)}
            className="rounded-full"
          >
            Todos
          </Button>
          {topSectors.map(sector => (
            <Button
              key={sector}
              variant={selectedSector === sector ? 'default' : 'outline'}
              onClick={() => setSelectedSector(sector)}
              className="rounded-full"
            >
              {sector}
            </Button>
          ))}
        </div>
      )}

      {loading && <p className="text-center">Cargando noticias...</p>}
      {error && <p className="text-center text-red-500">{error}</p>}

      {!loading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 grid-flow-row-dense gap-6">
          {filteredNews.map((item) => (
            <NewsCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
} 