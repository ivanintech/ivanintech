export interface LinkedInPost {
  id: string;
  url: string;
  description: string;
  embedCode: string;
  publishedDate: string; // Mantener como string inicialmente, se procesará
  category: string;
  author: 'me' | 'recommended';
}

// Definición de los posts (movido de blog/page.tsx)
export const rawLinkedInPosts: LinkedInPost[] = [
  {
    id: 'li-flora-photoshop',
    url: 'https://www.linkedin.com/posts/eric-vyacheslav-156273169_chatgpt-4o-flora-just-killed-photoshop-ugcPost-7322702227528105984-H94n',
    description: "ChatGPT-4o Flora vs Photoshop",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7322702227528105984?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2025-04-13',
    category: 'IA Generativa',
    author: 'recommended' 
  },
  {
    id: 'li-ai-agents',
    url: 'https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_ai-agents-activity-7322529580295110656-dCBf',
    description: "AI Agents",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7322529340309549059?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2025-04-28',
    category: 'Agentes IA',
    author: 'me' 
  },
   {
    id: 'li-audio-driven-video',
    url: 'https://www.linkedin.com/posts/alessandroperrilli_emo-audio-driven-video-avatar-ugcPost-7169728132965384192-xZgT',
    description: "EMO: Audio-Driven Video Avatar",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7169728132965384192?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2025-02-04',
    category: 'IA Generativa',
    author: 'recommended'
  },
  {
    id: 'li-suenos',
    url: 'https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_este-siempre-ha-sido-uno-de-mis-sue%C3%B1os-activity-7254226595668774912-5-LM',
    description: "Uno de mis sueños",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7254024202280706050?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2024-11-04',
    category: 'VR/AR',
    author: 'me'
  },
  {
    id: 'li-immersia-team',
    url: 'https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_immersia-immersianos-weareimmersians-activity-7250138812738093058-iBKy',
    description: "Equipo Immersia",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:share:7250120840480968705?collapsed=1" height="265" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2024-11-04',
    category: 'Equipo/Cultura',
    author: 'me'
  },
  {
    id: 'li-reinforcement-learning',
    url: 'https://www.linkedin.com/posts/imarpit_ai-reinforcementlearning-machinelearning-ugcPost-7219951802492874752-fTcz',
    description: "Reinforcement Learning",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7219951802492874752?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2024-08-04',
    category: 'Aprendizaje Automático',
    author: 'recommended'
  },
  {
    id: 'li-future-of-work',
    url: 'https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_ive-been-thinking-a-lot-about-the-future-activity-7217659492472107009--ifb',
    description: "Futuro del Trabajo",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7216163666256179202?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2024-05-04',
    category: 'Futuro del Trabajo',
    author: 'me'
  },
  {
    id: 'li-tokii-vr-immersia',
    url: 'https://www.linkedin.com/posts/immersia-datavisualization_tokii-vr-tokii-ugcPost-7303414239958831104-x1Un',
    description: "Tokii VR (Immersia)",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7303414239958831104?collapsed=1" height="878" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2024-05-04',
    category: 'Educación IA/VR',
    author: 'me'
  },
  {
    id: 'li-neural-net-graphical',
    url: 'https://www.linkedin.com/posts/eric-vyacheslav-156273169_amazing-graphical-representation-of-a-neural-ugcPost-7274785920447320065-EPL4',
    description: "Neural Net Graphical Representation",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7274785920447320065?collapsed=1" height="878" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2025-01-04',
    category: 'Visualización IA',
    author: 'recommended'
  },
  {
    id: 'li-immersia-visit',
    url: 'https://www.linkedin.com/posts/immersia-datavisualization_tokii-vr-tokii-ugcPost-7303414239958831104-x1Un',
    description: "Visita Delegación Japonesa",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7303414239958831104?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2025-04-27',
    category: 'Equipo/Cultura',
    author: 'me' 
  },
  {
    id: 'li-ai-glasses-privacy',
    url: 'https://www.linkedin.com/posts/endritrestelica_rip-privacy-this-guy-used-ai-powered-glasses-ugcPost-7320915912096657412-jeBW',
    description: "AI Powered Glasses Privacy",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7320915912096657412?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2025-04-27',
    category: 'Privacidad IA',
    author: 'recommended'
  },
  {
    id: 'li-transformers-explained',
    url: 'https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_transformers-how-llms-work-explained-visually-activity-7299518428141281283--v7L',
    description: "Transformers Explained Visually",
    embedCode: '<!-- PEGA AQUÍ EL CÓDIGO EMBED -->',
    publishedDate: '2024-02-20',
    category: 'Aprendizaje Automático',
    author: 'recommended'
  },
  {
    id: 'li-visionarynet-ai',
    url: 'https://www.linkedin.com/posts/visionarynet_artificialintelligence-machinelearning-ml-ugcPost-7288501315444363264-lEa2',
    description: "VisionaryNet AI",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7288501315444363264?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2024-04-10',
    category: 'IA Generativa',
    author: 'recommended'
  },
   {
    id: 'li-tolosaldealhii',
    url: 'https://www.linkedin.com/posts/immersia-datavisualization_tokii-tolosaldealhii-hezkuntza-ugcPost-7272648387458408450-TXcJ', 
    description: "Tokii Tolosaldealhii",
    embedCode: '<!-- PEGA AQUÍ EL CÓDIGO EMBED -->',
    publishedDate: '2024-03-01',
    category: 'Educación IA/VR',
    author: 'me'
   },
   {
    id: 'li-smartglass-ai',
    url: 'https://www.linkedin.com/posts/smartglassnews_ai-tech-innovation-ugcPost-7170174855294730241-Bv4z',
    description: "SmartGlass AI",
    embedCode: '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7169728132965384192?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    publishedDate: '2024-02-25',
    category: 'Hardware/Dispositivos',
    author: 'recommended'
   },
   {
     id: 'li-tokii-provider',
     url:'https://www.linkedin.com/posts/immersia-datavisualization_tokii-provider-tokii-ugcPost-7285995908935131138-i3io',
     description: 'Tokii Provider',
     embedCode: '<!-- PEGA AQUÍ EL CÓDIGO EMBED -->',
     publishedDate: '2024-04-05',
     category: 'VR/AR',
     author: 'me'
    }
];

export interface ProcessedLinkedInPost extends LinkedInPost {
  publishedDateObject: Date; // Asegurar que siempre sea Date después del procesamiento
}

// Función para procesar y ordenar los posts
export function getProcessedLinkedInPosts(): ProcessedLinkedInPost[] {
  return rawLinkedInPosts
    .map(post => {
      const dateObject = new Date(post.publishedDate);
      return {
        ...post,
        // Asegurarnos de que publishedDateObject sea un objeto Date válido
        publishedDateObject: dateObject instanceof Date && !isNaN(dateObject.getTime()) ? dateObject : new Date(0) // Fallback a una fecha muy antigua si es inválida
      };
    })
    .filter(post => {
      // Filtrar posts con fechas inválidas (si usamos el fallback anterior, este filtro podría no ser estrictamente necesario aquí)
      // y también aquellos que aún no tienen el embedCode real.
      const isValidDate = post.publishedDateObject.getTime() !== new Date(0).getTime();
      const hasValidEmbed = !post.embedCode.startsWith('<!-- PEGA AQUÍ');
      return isValidDate && hasValidEmbed;
    })
    .sort((a, b) => b.publishedDateObject.getTime() - a.publishedDateObject.getTime());
}

// Función para adaptar un LinkedInPost a lo que espera BlogPostPreview para la Home
export interface HomePageBlogPost {
  id: string;
  slug: string;
  title: string;
  excerpt?: string; // excerpt es opcional en BlogPostPreview
  published_date: string; // El tipo BlogPost espera string, aunque BlogPostPreview podría manejar Date
  image_url?: string | null; // image_url es opcional
  linkedInUrl?: string; // <--- AÑADIDO
  embedCode?: string; // <--- AÑADIDO para el iframe
  // No necesitamos linkedin_post_url aquí si no lo usa BlogPostPreview directamente
}

export function adaptLinkedInPostForHomePage(post: ProcessedLinkedInPost): HomePageBlogPost {
  // Intentar modificar el embedCode para quitar el collapsed=1
  let modifiedEmbedCode = post.embedCode;
  if (modifiedEmbedCode) {
    modifiedEmbedCode = modifiedEmbedCode.replace("?collapsed=1", ""); // Quita ?collapsed=1
    // Si después de quitarlo, la URL del src termina en '?' (porque no había más parámetros), la quitamos también.
    // O si ?collapsed=1 era &collapsed=1, lo reemplazamos por nada.
    modifiedEmbedCode = modifiedEmbedCode.replace("&collapsed=1", "");
  }

  return {
    id: post.id,
    slug: post.id, // Usamos el ID como slug para la URL en la home
    title: post.description, // Usamos la descripción como título
    excerpt: post.description, // Usamos la descripción también como excerpt
    published_date: post.publishedDateObject.toISOString(), // Formatear a ISO string
    image_url: null, // Los posts de LinkedIn aquí no tienen imagen destacada separada del embed
    linkedInUrl: post.url, 
    embedCode: modifiedEmbedCode, // Usar el embedCode modificado
  };
} 