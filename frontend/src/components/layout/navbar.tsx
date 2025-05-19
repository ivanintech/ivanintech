'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { ThemeSwitcher } from '@/components/theme-switcher';
import { FiUser } from 'react-icons/fi';

// TODO: Mejorar icono hamburguesa y animación

export default function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Restaurar funciones
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };
  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <nav className="bg-background/95 backdrop-blur-sm border-b border-border shadow-sm sticky top-0 z-50 dark:border-gray-700">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        {/* Logo/Marca */}
        <Link href="/" className="text-2xl font-semibold text-primary hover:text-primary/80 transition-colors" onClick={closeMobileMenu}>
          Iván In Tech
        </Link>

        {/* Navegación Principal (Desktop) */}
        <div className="hidden md:flex space-x-6 items-center">
          {/* Restaurar NavLinks completos */}
          <NavLink href="/" onClick={closeMobileMenu}>Home</NavLink>
          <NavLink href="/sobre-mi" onClick={closeMobileMenu}>Sobre mí</NavLink>
          <NavLink href="/portfolio" onClick={closeMobileMenu}>Portfolio</NavLink>
          <NavLink href="/blog" onClick={closeMobileMenu}>Blog</NavLink>
          <NavLink href="/noticias" onClick={closeMobileMenu}>Noticias IA</NavLink>
          <NavLink href="/contacto" onClick={closeMobileMenu}>Contacto</NavLink>
          <ThemeSwitcher />
          <Link href="/login" onClick={closeMobileMenu} className="text-foreground/80 hover:text-primary transition-colors" title="Login/Register">
            <FiUser size={22} />
          </Link>
        </div>

        {/* Botón Menú Hamburguesa (Móvil) */}
        <div className="md:hidden">
          <button 
            onClick={toggleMobileMenu} 
            className="text-foreground p-2 focus:outline-none focus:ring-2 focus:ring-primary rounded"
            aria-label="Toggle menu"
            aria-expanded={isMobileMenuOpen}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isMobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
            </svg>
          </button>
        </div>
      </div>

      {/* Menú Desplegable (Móvil) */}
      {isMobileMenuOpen && (
        <div className="md:hidden absolute top-full left-0 w-full bg-background border-b border-gray-200 dark:border-gray-700 shadow-md py-4">
          <div className="container mx-auto px-4 flex flex-col space-y-4">
            {/* Restaurar NavLinks completos */}
            <NavLink href="/" onClick={closeMobileMenu}>Home</NavLink>
            <NavLink href="/sobre-mi" onClick={closeMobileMenu}>Sobre mí</NavLink>
            <NavLink href="/portfolio" onClick={closeMobileMenu}>Portfolio</NavLink>
            <NavLink href="/blog" onClick={closeMobileMenu}>Blog</NavLink>
            <NavLink href="/noticias" onClick={closeMobileMenu}>Noticias IA</NavLink>
            <NavLink href="/contacto" onClick={closeMobileMenu}>Contacto</NavLink>
            <div className="pt-2 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <ThemeSwitcher />
              <Link href="/login" onClick={closeMobileMenu} className="text-foreground/80 hover:text-primary transition-colors p-2" title="Login/Register">
                <FiUser size={24} />
              </Link>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}

// Restaurar componente NavLink
function NavLink({ href, children, onClick }: { href: string; children: React.ReactNode; onClick?: () => void }) {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <Link
      href={href}
      onClick={onClick}
      className={`transition-colors font-medium ${ 
        isActive 
          ? 'text-primary'
          : 'text-foreground/80 hover:text-primary'
      } block py-1 md:inline md:py-0`}
    >
      {children}
    </Link>
  );
}
 