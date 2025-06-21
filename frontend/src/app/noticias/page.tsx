"use client";

import React, { useState, useEffect } from "react";
import type { NewsItemRead } from "@/types";
import { NewsCard } from "@/components/content/NewsCard";
import NewsForm from "@/components/news/NewsForm";
import { getNews as fetchNews } from "@/services/newsService";
import { useAuth } from "@/context/AuthContext";

export default function NewsPage() {
  const [news, setNews] = useState<NewsItemRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user, token } = useAuth();

  useEffect(() => {
    const loadNews = async () => {
      try {
        setLoading(true);
        const newsData = await fetchNews({ limit: 50 });
        setNews(newsData);
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
    setNews((prevNews) => [newNewsItem, ...prevNews]);
  };

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

      {user && token && (
        <div className="mb-12">
          <NewsForm onNewsItemAdded={handleNewsSubmitted} />
        </div>
      )}

      {loading && <p className="text-center">Cargando noticias...</p>}
      {error && <p className="text-center text-red-500">{error}</p>}

      {!loading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 grid-flow-row-dense gap-6">
          {news.map((item) => (
            <NewsCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
} 