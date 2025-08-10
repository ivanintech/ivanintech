"use client";
import { useEffect, useState } from "react";
import React from "react";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar que el backend esté disponible antes de mostrar la aplicación
    const checkBackendHealth = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
        const response = await fetch(`${apiUrl}/health`, { 
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          signal: AbortSignal.timeout(5000) // 5 segundos timeout
        });
        
        if (response.ok) {
          setLoading(false);
        } else {
          // Si el backend no responde, esperar un poco más
          setTimeout(() => setLoading(false), 2000);
        }
      } catch (error) {
        console.warn('Backend health check failed, continuing anyway:', error);
        // Si hay error, continuar después de un delay más largo
        setTimeout(() => setLoading(false), 3000);
      }
    };

    checkBackendHealth();
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