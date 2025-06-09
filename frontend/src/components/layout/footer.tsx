import Link from 'next/link';
import { FaLinkedin, FaGithub } from 'react-icons/fa';

// TODO: Reemplazar placeholders con iconos reales (SVG o librería)
const SocialLink = ({ href, label, children }: { href: string; label: string; children: React.ReactNode }) => (
  <a 
    href={href} 
    target="_blank" 
    rel="noopener noreferrer" 
    aria-label={label}
    className="text-muted-foreground hover:text-primary transition-colors"
  >
    {children}
  </a>
);

export default function Footer() {
  const currentYear = new Date().getFullYear();
  // TODO: Añadir iconos reales y enlaces a redes sociales
  // TODO: Añadir enlaces a Política de Privacidad, Términos, etc.
  return (
    <footer className="bg-muted text-muted-foreground py-8 mt-16">
      <div className="container mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-4">
        <p className="text-sm text-center sm:text-left">
          &copy; {currentYear} Iván In Tech. All rights reserved.
        </p>
        
        <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6">
          <div className="flex gap-4 text-sm">
            <Link href="/politica-privacidad" className="hover:text-primary transition-colors">Privacy Policy</Link>
            <Link href="/terminos-uso" className="hover:text-primary transition-colors">Terms of Use</Link>
          </div>
          <div className="flex gap-5">
            <SocialLink href="https://www.linkedin.com/in/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a/" label="LinkedIn">
              <FaLinkedin className="w-5 h-5" />
            </SocialLink>
            <SocialLink href="https://github.com/ivancastroprojects" label="GitHub">
              <FaGithub className="w-5 h-5" />
            </SocialLink>
          </div>
        </div>
      </div>
    </footer>
  );
} 