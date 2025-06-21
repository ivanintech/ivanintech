import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import { submitNewsItem } from '@/services/newsService';
import type { NewsItemRead } from '@/types';

interface NewsFormProps {
  onNewsItemAdded: (newNewsItem: NewsItemRead) => void;
}

const NewsForm: React.FC<NewsFormProps> = ({ onNewsItemAdded }) => {
  const [url, setUrl] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const { token } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      toast.error('Debes iniciar sesión para compartir noticias.');
      return;
    }
    if (!url.trim()) {
      setFormError('La URL de la noticia es obligatoria.');
      toast.error('La URL de la noticia es obligatoria.');
      return;
    }
    try {
      new URL(url);
    } catch {
      setFormError('El formato de la URL no es válido.');
      toast.error('El formato de la URL no es válido.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      const newNewsItem = await submitNewsItem(token, url);
      toast.success('¡Noticia enviada! Se está procesando y se añadirá a la lista si es relevante.');
      setUrl('');
      onNewsItemAdded(newNewsItem);
    } catch (err) {
      const error = err as Error & { response?: { data?: { detail?: string } } };
      const errorMessage = error.response?.data?.detail || error.message || 'No se pudo enviar la noticia.';
      setFormError(errorMessage);
      toast.error(errorMessage);
    }
    setIsSubmitting(false);
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 md:p-8 rounded-xl shadow-xl mb-10 border border-gray-200 dark:border-gray-700">
      <form onSubmit={handleSubmit}>
        <h2 className="text-xl font-semibold mb-5 text-gray-800 dark:text-gray-100 border-b border-gray-300 dark:border-gray-600 pb-3">
          Comparte una Noticia de IA con la Comunidad
        </h2>
        <div className="grid grid-cols-1 gap-y-5">
          <div>
            <label htmlFor="community-news-url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              URL de la Noticia *
            </label>
            <input 
              type="url" 
              name="community-news-url" 
              id="community-news-url" 
              value={url} 
              onChange={(e) => {
                setUrl(e.target.value);
                if (e.target.value.trim() !== '') setFormError(null);
              }} 
              required 
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 text-sm"
              placeholder="https://ejemplo.com/noticia-sobre-ia"
            />
            <p className="mt-1.5 text-xs text-gray-500 dark:text-gray-400">
              Solo necesitas la URL. Un agente de IA analizará la noticia, la puntuará y la publicará si es relevante.
            </p>
          </div>
        </div>
        {formError && (
          <p className="mt-3 text-red-600 dark:text-red-400 text-sm bg-red-50 dark:bg-red-900/30 p-2.5 rounded-md">
            {formError}
          </p>
        )}
        <button 
          type="submit" 
          disabled={isSubmitting || !token}
          className="mt-5 w-full flex justify-center items-center px-5 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:ring-offset-gray-800 disabled:opacity-50 transition-colors duration-200 font-medium text-sm"
        >
          {isSubmitting ? (
            <>
              <svg className="animate-spin -ml-1 mr-2.5 h-4.5 w-4.5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analizando...
            </>
          ) : 'Compartir Noticia'}
        </button>
      </form>
    </div>
  );
};

export default NewsForm; 