"use client";

import React, { useState, useEffect, useCallback } from "react";
import type { NewsItemRead, NewsItemUpdate } from "@/types";
import { NewsCard } from "@/components/news/NewsCard";
import { getNews as fetchNews, updateNewsItem, deleteNewsItem } from "@/services/newsService";
import { useAuth } from "@/context/AuthContext";
import { JoinCommunityBanner } from '@/components/ui/JoinCommunityBanner';
import { LazyLoader, NewsCardSkeleton, ProgressiveLoader } from "@/components/ui/LazyLoader";
import { EditNewsItemModal } from "@/components/admin/EditNewsItemModal";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

// Define a unified state structure for each news section
interface NewsSectionState {
  items: NewsItemRead[];
  page: number;
  loading: boolean;
  hasMore: boolean;
}

const createInitialSectionState = (): NewsSectionState => ({
  items: [],
  page: 1,
  loading: false,
  hasMore: true,
});

const LATEST_COUNT = 12; // Aumentar a 12
const WEEK_COUNT = 24;   // Nueva sección para la semana
const MORE_PER_PAGE = 30; // Más noticias por página

export default function NewsPage() {
  const [latestNews, setLatestNews] = useState<NewsSectionState>(createInitialSectionState());
  const [weekNews, setWeekNews] = useState<NewsSectionState>(createInitialSectionState());
  const [moreNews, setMoreNews] = useState<NewsSectionState>(createInitialSectionState());
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();
  const isLoggedIn = !!token;
  
  const [editingItem, setEditingItem] = useState<NewsItemRead | null>(null);
  const [deletingItem, setDeletingItem] = useState<NewsItemRead | null>(null);

  const loadInitialNews = useCallback(async () => {
    setLatestNews(s => ({ ...s, loading: true }));
    setWeekNews(s => ({ ...s, loading: true }));
    setMoreNews(s => ({ ...s, loading: true }));

    try {
      // Pedir un lote grande de noticias
      const initialData = await fetchNews({ page: 1, per_page: LATEST_COUNT + WEEK_COUNT + MORE_PER_PAGE });
      const allItems = initialData.items;

      // Dividir en secciones
      const latestItems = allItems.slice(0, LATEST_COUNT);
      const weekItems = allItems.slice(LATEST_COUNT, LATEST_COUNT + WEEK_COUNT);
      const moreItems = allItems.slice(LATEST_COUNT + WEEK_COUNT);

      setLatestNews({
        items: latestItems,
        page: 1,
        loading: false,
        hasMore: true,
      });
      setWeekNews({
        items: weekItems,
        page: 1,
        loading: false,
        hasMore: true,
      });
      setMoreNews({
        items: moreItems,
        page: 1,
        loading: false,
        hasMore: true,
      });
      } catch (err) {
      setError("Could not load initial news.");
      setLatestNews(s => ({ ...s, loading: false }));
      setWeekNews(s => ({ ...s, loading: false }));
      setMoreNews(s => ({ ...s, loading: false }));
        console.error(err);
      }
  }, []);

  useEffect(() => {
    loadInitialNews();
  }, [loadInitialNews]);

  // Nuevo handler para cargar más en cada sección
  const handleLoadMoreSection = useCallback(async (section: 'latest' | 'week' | 'more') => {
    let sectionState, setSection, offset;
    if (section === 'latest') {
      sectionState = latestNews;
      setSection = setLatestNews;
      offset = sectionState.items.length;
    } else if (section === 'week') {
      sectionState = weekNews;
      setSection = setWeekNews;
      offset = sectionState.items.length + LATEST_COUNT;
    } else {
      sectionState = moreNews;
      setSection = setMoreNews;
      offset = sectionState.items.length + LATEST_COUNT + WEEK_COUNT;
    }
    if (sectionState.loading || !sectionState.hasMore) return;
    setSection(s => ({ ...s, loading: true }));
    try {
      const data = await fetchNews({ page: 1, per_page: offset + MORE_PER_PAGE });
      const newItems = data.items.slice(offset, offset + MORE_PER_PAGE);
      setSection(prev => {
        const allItems = [...prev.items, ...newItems];
        return {
          ...prev,
          items: allItems,
          loading: false,
          hasMore: allItems.length < data.total,
        };
    });
    } catch (err) {
      setError("Could not load more news.");
      setSection(s => ({ ...s, loading: false }));
      console.error(err);
    }
  }, [latestNews, weekNews, moreNews]);
  
  // --- Admin/User Handlers ---
  const applyUpdateToSection = (setter: React.Dispatch<React.SetStateAction<NewsSectionState>>, updatedItem: NewsItemRead) => {
    setter(prev => ({
      ...prev,
      items: prev.items.map(item => item.id === updatedItem.id ? updatedItem : item),
    }));
  };

  const applyDeleteToSection = (setter: React.Dispatch<React.SetStateAction<NewsSectionState>>, itemId: string) => {
    setter(prev => ({
      ...prev,
      items: prev.items.filter(item => item.id !== itemId),
    }));
  };

  const handleUpdateItem = async (itemData: NewsItemUpdate) => {
    if (!editingItem || !token) return;
    try {
      const updatedItem = await updateNewsItem(editingItem.id, itemData, token);
      applyUpdateToSection(setLatestNews, updatedItem);
      applyUpdateToSection(setWeekNews, updatedItem);
      applyUpdateToSection(setMoreNews, updatedItem);
      setEditingItem(null);
    } catch (error) {
      console.error("Failed to update news item:", error);
    }
  };

  const handleDeleteItem = async () => {
    if (!deletingItem || !token) return;
    try {
      await deleteNewsItem(deletingItem.id, token);
      applyDeleteToSection(setLatestNews, deletingItem.id);
      applyDeleteToSection(setWeekNews, deletingItem.id);
      applyDeleteToSection(setMoreNews, deletingItem.id);
      setDeletingItem(null);
    } catch (error) {
      console.error("Failed to delete news item:", error);
    }
  };

  const NewsSection = ({ title, sectionState, onLoadMore }: { title: string; sectionState: NewsSectionState; onLoadMore?: () => void; }) => {
    if (sectionState.loading && sectionState.items.length === 0) {
      return (
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8">{title}</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 grid-flow-row-dense gap-6">
            {Array.from({ length: 8 }).map((_, i) => (
              <NewsCardSkeleton key={i} />
            ))}
          </div>
        </section>
      );
    }
    if (sectionState.items.length === 0) return null;

    return (
      <section className="mb-16">
        <h2 className="text-3xl font-bold mb-8">{title}</h2>
        <LazyLoader
          fallback={
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 grid-flow-row-dense gap-6">
              {Array.from({ length: 8 }).map((_, i) => (
                <NewsCardSkeleton key={i} />
              ))}
            </div>
          }
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 grid-flow-row-dense gap-6">
            {sectionState.items.map((item, index) => (
              <ProgressiveLoader
                key={item.id}
                skeleton={<NewsCardSkeleton />}
                loadingTime={index * 50} // Stagger loading for better UX
              >
                <NewsCard 
                  item={item} 
                  onEdit={() => setEditingItem(item)}
                  onDelete={() => setDeletingItem(item)}
                />
              </ProgressiveLoader>
            ))}
          </div>
        </LazyLoader>
        {onLoadMore && sectionState.hasMore && !sectionState.loading && (
          <div className="text-center mt-12">
            <Button onClick={onLoadMore} size="lg">Load More</Button>
          </div>
        )}
        {sectionState.loading && sectionState.items.length > 0 && <p className="text-center py-8">Loading more...</p>}
      </section>
    );
  };

  // Renderizar las tres secciones
  return (
    <main className="container mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">News In AI & Tech</h1>
        <p className="mt-3 text-lg text-muted-foreground">
          A feed of news and reports analyzing the present and future of AI
        </p>
        </div>
      {!isLoggedIn && (
        <JoinCommunityBanner className="mb-24" />
      )}
      <NewsSection title="Latest News" sectionState={latestNews} onLoadMore={() => handleLoadMoreSection('latest')} />
      <NewsSection title="Week News" sectionState={weekNews} onLoadMore={() => handleLoadMoreSection('week')} />
      <NewsSection title="More News" sectionState={moreNews} onLoadMore={() => handleLoadMoreSection('more')} />
      {error && <p className="text-red-500 text-center mt-8">{error}</p>}
      <EditNewsItemModal
        isOpen={!!editingItem}
        itemToEdit={editingItem}
        onClose={() => setEditingItem(null)}
        onConfirm={handleUpdateItem}
      />
      <AlertDialog open={!!deletingItem} onOpenChange={open => !open && setDeletingItem(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete News Item</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this news item?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteItem}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </main>
  );
} 
