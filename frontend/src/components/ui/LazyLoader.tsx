"use client";

import React, { useState, useEffect } from 'react';

interface LazyLoaderProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  delay?: number;
  threshold?: number;
}

export function LazyLoader({ 
  children, 
  fallback, 
  delay = 200,
  threshold = 0.1 
}: LazyLoaderProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, delay);

    return () => clearTimeout(timer);
  }, [delay]);

  useEffect(() => {
    if (!isVisible) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setHasLoaded(true);
          observer.disconnect();
        }
      },
      { threshold }
    );

    const element = document.getElementById('lazy-loader-trigger');
    if (element) {
      observer.observe(element);
    }

    return () => observer.disconnect();
  }, [isVisible, threshold]);

  if (!isVisible) {
    return fallback || <div className="animate-pulse">Loading...</div>;
  }

  if (!hasLoaded) {
    return (
      <>
        {fallback || <div className="animate-pulse">Loading...</div>}
        <div id="lazy-loader-trigger" className="h-1" />
      </>
    );
  }

  return <>{children}</>;
}

interface ProgressiveLoaderProps {
  children: React.ReactNode;
  skeleton: React.ReactNode;
  loadingTime?: number;
}

export function ProgressiveLoader({ 
  children, 
  skeleton, 
  loadingTime = 1000 
}: ProgressiveLoaderProps) {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, loadingTime);

    return () => clearTimeout(timer);
  }, [loadingTime]);

  if (isLoading) {
    return <>{skeleton}</>;
  }

  return <>{children}</>;
}

interface SkeletonProps {
  className?: string;
  lines?: number;
}

export function Skeleton({ className = "", lines = 1 }: SkeletonProps) {
  return (
    <div className={`animate-pulse ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 bg-gray-200 rounded mb-2 last:mb-0"
          style={{ width: `${Math.random() * 40 + 60}%` }}
        />
      ))}
    </div>
  );
}

export function NewsCardSkeleton() {
  return (
    <div className="bg-card rounded-lg shadow-md overflow-hidden animate-pulse">
      <div className="h-48 bg-gray-200" />
      <div className="p-4">
        <Skeleton lines={2} className="mb-2" />
        <Skeleton lines={1} className="w-3/4" />
        <div className="flex justify-between items-center mt-4">
          <Skeleton lines={1} className="w-1/3" />
          <div className="flex space-x-1">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="w-4 h-4 bg-gray-200 rounded" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function ProjectCardSkeleton() {
  return (
    <div className="bg-card rounded-lg shadow-md overflow-hidden animate-pulse">
      <div className="h-32 bg-gray-200" />
      <div className="p-4">
        <Skeleton lines={1} className="mb-2" />
        <Skeleton lines={2} className="mb-3" />
        <div className="flex flex-wrap gap-1">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="w-16 h-6 bg-gray-200 rounded-full" />
          ))}
        </div>
      </div>
    </div>
  );
}
