import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from '@/components/layout/navbar';
import Footer from '@/components/layout/footer';
import { ThemeProvider } from "@/components/theme/theme-provider";
import { AuthProvider } from "@/context/AuthContext";
import { Toaster } from "sonner";
import { useEffect, useState } from "react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Iván In Tech",
  description: "Iván In Tech's personal site. Exploring the future of AI and technology.",
  icons: {
    icon: '/img/ivan-profile.webp',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simula espera de backend, reemplaza con lógica real si tienes SSR o fetch inicial
    const timer = setTimeout(() => setLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <html lang="es">
        <body>
          <div className="flex flex-col items-center justify-center h-screen bg-black text-white">
            <span className="loader mb-4" style={{ width: 48, height: 48, border: '6px solid #fff', borderTop: '6px solid #00bcd4', borderRadius: '50%', animation: 'spin 1s linear infinite', display: 'inline-block' }} />
            <p className="text-lg font-semibold mt-2">¡Estamos preparando todo para ti! Esto puede tardar unos segundos si es tu primera visita del día.</p>
            <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
          </div>
        </body>
      </html>
    );
  }

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} antialiased flex flex-col min-h-screen`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
          <Navbar />
          <main className="flex-grow">{children}</main>
          <Footer />
          <Toaster richColors />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
