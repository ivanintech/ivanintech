import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from '@/components/layout/navbar';
import Footer from '@/components/layout/footer';
import { ThemeProvider } from "@/components/theme/theme-provider";
import { AuthProvider } from "@/context/AuthContext";
import { Toaster } from "sonner";
// Elimina los hooks de aquí
// import { useEffect, useState } from "react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Iván In Tech",
  description: "Iván In Tech's personal site. Exploring the future of AI and technology.",
  icons: {
    icon: '/img/ivan-profile.webp',
  },
};

// Nuevo componente cliente para manejar el loading y hooks
import ClientLayout from "@/components/layout/ClientLayout";

export default function RootLayout({ children }: { children: React.ReactNode }) {
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
            <ClientLayout>
              <Navbar />
              <main className="flex-grow">{children}</main>
              <Footer />
              <Toaster richColors />
            </ClientLayout>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
