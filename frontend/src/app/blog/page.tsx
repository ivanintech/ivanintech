// ivanintech/frontend/src/app/blog/page.tsx
// --- COMPONENTE BlogPage ---
'use client';

import { SocialPostEmbed } from '@/components/content/SocialPostEmbed';
import { useState, useMemo } from 'react';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge"; // Asegúrate de haber ejecutado 'npx shadcn-ui@latest add badge'

// --- LISTA DE POSTS A INCRUSTAR ---
// AÑADIDO: author ('me' | 'recommended') - ¡VERIFICA ESTO!
const postsToEmbed = [
  {
    id: 'li-flora-photoshop',
    url: 'https://www.linkedin.com/posts/eric-vyacheslav-156273169_chatgpt-4o-flora-just-killed-photoshop-ugcPost-7322702227528105984-H94n',
    description: "ChatGPT-4o Flora vs Photoshop",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7322702227528105984?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`,
    publishedDate: '2025-04-13',
    category: 'IA Generativa',
    author: 'recommended' // Asumo recomendado
  },
  {
    id: 'li-ai-agents',
    url: 'https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_ai-agents-activity-7322529580295110656-dCBf',
    description: "AI Agents",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7322529340309549059?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`,
    publishedDate: '2025-04-28',
    category: 'Agentes IA',
    author: 'me' // Asumo tuyo (Ivan C.)
  },
   {
    id: 'li-audio-driven-video', // Este es el ID que tenías para 'Tokii VR', pero la URL es de 'EMO: Audio-Driven...' así que lo ajusto.
    url: 'https://www.linkedin.com/posts/alessandroperrilli_emo-audio-driven-video-avatar-ugcPost-7169728132965384192-xZgT',
    description: "EMO: Audio-Driven Video Avatar",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7169728132965384192?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`, // Código que tenías en 'Tokii VR'
    publishedDate: '2025-02-04', // Fecha estimada basada en Alessandro F.
    category: 'IA Generativa',
    author: 'recommended' // Asumo recomendado
  },
  {
    id: 'li-suenos',
    url: 'https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_este-siempre-ha-sido-uno-de-mis-sue%C3%B1os-activity-7254226595668774912-5-LM',
    description: "Uno de mis sueños",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7254024202280706050?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`,
    publishedDate: '2024-11-04',
    category: 'VR/AR',
    author: 'me' // Asumo tuyo (Ivan C.)
  },
  {
    id: 'li-immersia-team',
    url: 'https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_immersia-immersianos-weareimmersians-activity-7250138812738093058-iBKy',
    description: "Equipo Immersia",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:share:7250120840480968705?collapsed=1" height="265" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`,
    publishedDate: '2024-11-04',
    category: 'Equipo/Cultura',
    author: 'me' // Asumo tuyo (Ivan C. / Immersia)
  },
  {
    id: 'li-reinforcement-learning',
    url: 'https://www.linkedin.com/posts/imarpit_ai-reinforcementlearning-machinelearning-ugcPost-7219951802492874752-fTcz',
    description: "Reinforcement Learning",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7219951802492874752?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`,
    publishedDate: '2024-08-04',
    category: 'Aprendizaje Automático',
    author: 'recommended' // Asumo recomendado
  },
  {
    id: 'li-future-of-work',
    url: 'https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_ive-been-thinking-a-lot-about-the-future-activity-7217659492472107009--ifb',
    description: "Futuro del Trabajo",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7216163666256179202?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`,
    publishedDate: '2024-05-04',
    category: 'Futuro del Trabajo',
    author: 'me' // Asumo tuyo (Ivan C.)
  },
  {
    id: 'li-tokii-vr-immersia', // El id que tenías antes como 'li-tokii-vr'
    url: 'https://www.linkedin.com/posts/immersia-datavisualization_tokii-vr-tokii-ugcPost-7303414239958831104-x1Un',
    description: "Tokii VR (Immersia)",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7303414239958831104?collapsed=1" height="878" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`,
    publishedDate: '2024-05-04',
    category: 'Educación IA/VR',
    author: 'me' // Asumo tuyo (Immersia)
  },
  {
    id: 'li-neural-net-graphical',
    url: 'https://www.linkedin.com/posts/eric-vyacheslav-156273169_amazing-graphical-representation-of-a-neural-ugcPost-7274785920447320065-EPL4',
    description: "Neural Net Graphical Representation",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7274785920447320065?collapsed=1" height="878" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`,
    publishedDate: '2025-01-04',
    category: 'Visualización IA',
    author: 'recommended' // Asumo recomendado
  },
  {
    id: 'li-immersia-visit', // Este es el que antes era 'li-tolosaldealhii' por la URL
    url: 'https://www.linkedin.com/posts/immersia-datavisualization_tokii-tolosaldealhii-hezkuntza-ugcPost-7272648387458408450-TXcJ',
    description: "Visita Delegación Japonesa",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7272648387458408450-TXcJ?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`,
    publishedDate: '2025-04-27', // Fecha estimada
    category: 'Equipo/Cultura',
    author: 'me' // Asumo tuyo (Immersia)
  },
  {
    id: 'li-ai-glasses-privacy',
    url: 'https://www.linkedin.com/posts/endritrestelica_rip-privacy-this-guy-used-ai-powered-glasses-ugcPost-7320915912096657412-jeBW',
    description: "AI Powered Glasses Privacy",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7320915912096657412?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`,
    publishedDate: '2025-04-27',
    category: 'Privacidad IA',
    author: 'recommended' // Asumo recomendado
  },
  // ---- Posts que faltan o sin fecha clara ----
   {
    id: 'li-transformers-explained',
    url: 'https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_transformers-how-llms-work-explained-visually-activity-7299518428141281283--v7L',
    description: "Transformers Explained Visually",
    embedCode: `<!-- PEGA AQUÍ EL CÓDIGO EMBED -->`,
    publishedDate: '2024-02-20',
    category: 'Aprendizaje Automático',
    author: 'recommended' // Asumo recomendado
  },
  {
    id: 'li-visionarynet-ai',
    url: 'https://www.linkedin.com/posts/visionarynet_artificialintelligence-machinelearning-ml-ugcPost-7288501315444363264-lEa2',
    description: "VisionaryNet AI",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7288501315444363264?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`,
    publishedDate: '2024-04-10',
    category: 'IA Generativa',
    author: 'recommended' // Asumo recomendado
  },
   {
    id: 'li-tolosaldealhii', // Este ID lo reutilizo para el que no tenía embed antes
    url: 'https://www.linkedin.com/posts/immersia-datavisualization_tokii-tolosaldealhii-hezkuntza-ugcPost-7272648387458408450-TXcJ', // URL repetida, puede ser error
    description: "Tokii Tolosaldealhii",
    embedCode: `<!-- PEGA AQUÍ EL CÓDIGO EMBED -->`,
    publishedDate: '2024-03-01',
    category: 'Educación IA/VR',
    author: 'me' // Asumo tuyo (Immersia)
   },
   {
    id: 'li-smartglass-ai',
    url: 'https://www.linkedin.com/posts/smartglassnews_ai-tech-innovation-ugcPost-7170174855294730241-Bv4z',
    description: "SmartGlass AI",
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7169728132965384192?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`, // Código correcto?
    publishedDate: '2024-02-25',
    category: 'Hardware/Dispositivos',
    author: 'recommended' // Asumo recomendado
   },
   {
     id: 'li-tokii-provider',
     url:'https://www.linkedin.com/posts/immersia-datavisualization_tokii-provider-tokii-ugcPost-7285995908935131138-i3io',
     description: 'Tokii Provider',
     embedCode: '<!-- PEGA AQUÍ EL CÓDIGO EMBED -->',
     publishedDate: '2024-04-05',
     category: 'VR/AR',
     author: 'me' // Asumo tuyo (Immersia)
    }
];

// --- FUNCIONES HELPER FECHAS ---
// ... (getStartOfDay, getStartOfWeek, getStartOfMonth sin cambios)
function getStartOfDay(date: Date): Date {
  const start = new Date(date);
  start.setHours(0, 0, 0, 0);
  return start;
}
function getStartOfWeek(date: Date): Date { // Lunes como inicio de semana
  const start = getStartOfDay(date);
  const day = start.getDay(); // Domingo = 0, Lunes = 1, ...
  const diff = start.getDate() - day + (day === 0 ? -6 : 1); // Ajustar para Lunes
  return new Date(start.setDate(diff));
}
function getStartOfMonth(date: Date): Date {
  const start = new Date(date);
  start.setDate(1);
  start.setHours(0, 0, 0, 0);
  return start;
}

// Corrección: Usar Type Alias con intersección en lugar de interface con extends
type ProcessedPost = (typeof postsToEmbed)[number] & {
  publishedDateObject: Date | null;
};

export default function BlogPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const parsedAndFilteredPosts: ProcessedPost[] = useMemo(() => {
    let filtered = postsToEmbed.map(post => {
        let dateObject: Date | null = null;
        try {
            dateObject = new Date(post.publishedDate);
        } catch (e) { console.error('Error parsing date:', post.id, e); }
        return {
            ...post,
            publishedDateObject: dateObject instanceof Date && !isNaN(dateObject.getTime()) ? dateObject : null,
        };
        }).filter(post => post.publishedDateObject !== null && !post.embedCode.startsWith('<!-- PEGA AQUÍ'));

        if (selectedCategory) {
            filtered = filtered.filter(post => post.category === selectedCategory);
        }

        return filtered.sort((a, b) => (b.publishedDateObject as Date).getTime() - (a.publishedDateObject as Date).getTime());
  }, [selectedCategory]);

  const groupedPosts = useMemo(() => {
     const now = new Date();
     const yesterdayStart = getStartOfDay(new Date(now.getTime() - 24 * 60 * 60 * 1000));
     const weekStart = getStartOfWeek(now);

     const ultimos = parsedAndFilteredPosts.filter(p => p.publishedDateObject && p.publishedDateObject >= yesterdayStart);
     const semana = parsedAndFilteredPosts.filter(p => p.publishedDateObject && p.publishedDateObject >= weekStart && p.publishedDateObject < yesterdayStart);
     const anteriores = parsedAndFilteredPosts.filter(p => p.publishedDateObject && p.publishedDateObject < weekStart);

     return { ultimos, semana, anteriores };
  }, [parsedAndFilteredPosts]);

  const availableCategories = useMemo(() => {
    const categories = new Set(postsToEmbed.map(p => p.category).filter(Boolean) as string[]); // Añadir 'as string[]'
    return Array.from(categories).sort();
  }, []);

  // Helper para renderizar una sección de posts
  function renderPostSection(title: string, posts: ProcessedPost[], isLatestSection: boolean = false) {
    if (posts.length === 0) return null;

    return (
      <section className="mb-16">
        <h2 className={`text-3xl font-semibold mb-6 ${isLatestSection ? 'text-center md:text-left' : ''}`}>
          {title}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start">
          {posts.map((post, index) => {
            const shouldSpan = (isLatestSection && index === 0 && posts.length > 1) || post.author === 'me';
            // Corrección: Usar string literal normal y añadir la clase condicionalmente
            const columnSpanClass = shouldSpan ? 'md:col-span-2 lg:col-span-2' : '';

            return (
              // Corrección: Aplicar clases correctamente
              <div
                key={post.id}
                className={`bg-card border border-border rounded-lg overflow-hidden shadow-sm flex flex-col ${columnSpanClass}`}
              >
                <div className="p-1 flex-grow">
                  <SocialPostEmbed embedHtml={post.embedCode} />
                </div>
                <div className="p-2 text-right border-t border-border space-x-2">
                   {post.author === 'me' && (
                     <Badge variant="default">Mi Post</Badge>
                   )}
                   {post.author === 'recommended' && (
                      <Badge variant="secondary">Recomendado</Badge>
                   )}
                  <Badge variant="outline">{post.category}</Badge>
                </div>
              </div> // Cierre correcto del div
            );
          })}
        </div> {/* Cierre correcto del div grid */}
      </section> // Cierre correcto de section
    );
  } // Cierre correcto de la función


  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-center mb-8 text-primary">
        Actividad Reciente en LinkedIn
      </h1>

      {/* Filtros por Categoría */}
      <div className="flex flex-wrap justify-center gap-2 mb-12">
         <Button
            variant={!selectedCategory ? "default" : "outline"}
            onClick={() => setSelectedCategory(null)}
            size="sm"
            >
            Todos
            </Button>
            {/* Corrección: Añadir tipo explícito a category */}
            {availableCategories.map((category: string) => (
            <Button
                key={category}
                variant={selectedCategory === category ? "default" : "outline"}
                onClick={() => setSelectedCategory(category)}
                size="sm"
            >
                {category}
            </Button>
            ))}
      </div>

      {parsedAndFilteredPosts.length === 0 ? (
         <p className="text-center text-muted-foreground mt-12">
           No hay actividad para mostrar {selectedCategory ? `en la categoría "${selectedCategory}"` : ''}.
        </p>
      ) : (
        <>
          {renderPostSection("Últimos Posts", groupedPosts.ultimos, true)}
          {renderPostSection("Esta Semana", groupedPosts.semana)}
          {renderPostSection("Anteriores", groupedPosts.anteriores)}
        </>
      )}
    </div>
  );
} // Cierre correcto del componente
