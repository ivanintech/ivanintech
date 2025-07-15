"use client";
import { useEffect, useState } from "react";
import React from "react";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simula espera de backend, reemplaza con lógica real si tienes SSR o fetch inicial
    const timer = setTimeout(() => setLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-black text-white">
        <span
          className="loader mb-4"
          style={{
            width: 48,
            height: 48,
            border: "6px solid #fff",
            borderTop: "6px solid #00bcd4",
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
            display: "inline-block",
          }}
        />
        <p className="text-lg font-semibold mt-2">
          ¡Estamos preparando todo para ti! Esto puede tardar unos segundos si es tu primera visita del día.
        </p>
        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return <>{children}</>;
} 