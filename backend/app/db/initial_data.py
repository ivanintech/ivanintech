# app/db/initial_data.py
# Datos iniciales para poblar la base de datos
from datetime import date
import uuid

# --- Proyectos ---
initial_projects = [
    {
        "id": 'semantic-recommender',
        "title": 'Semantic Book Recommender',
        "description": 'Sistema de recomendación semántica de libros usando FAISS para búsquedas vectoriales eficientes y análisis de texto.',
        "technologies": ['Python', 'NLP', 'Machine Learning', 'FAISS', 'FastAPI'],
        "githubUrl": 'https://github.com/ivanintech/semantic-book-recommender',
        "videoUrl": '/img/projects/recommender.mkv', 
        "imageUrl": None, # Añadir si corresponde
        "liveUrl": None,
    },
    {
        "id": 'stroke-predictor',
        "title": 'Stroke Predictor',
        "description": 'Modelo predictivo para riesgo de ACV utilizando Redes Neuronales y análisis de datos para generar impacto en la prevención.',
        "technologies": ['Jupyter', 'Python', 'Machine Learning', 'Neural Networks', 'Pandas', 'Scikit-learn'],
        "githubUrl": 'https://github.com/ivanintech/stroke-predictor',
        "videoUrl": '/img/projects/stroke.mkv',
        "imageUrl": None,
        "liveUrl": None,
    },
    # Añadir más proyectos si es necesario
]

# --- Posts del Blog ---
initial_blog_posts = [
    {
        "id": 'post-1',
        "slug": 'primeros-pasos-con-ia-generativa',
        "title": 'Primeros Pasos con IA Generativa',
        "excerpt": 'Una introducción a los conceptos básicos y herramientas clave para empezar a experimentar con modelos de IA generativa como GPT y Stable Diffusion.',
        "content": "<p>Este es el contenido completo del post sobre <strong>IA Generativa</strong>.</p><p>Aquí exploraremos los fundamentos y cómo empezar.</p>",
        "published_date": date(2024, 7, 28),
        "image_url": None,
    },
    {
        "id": 'post-2',
        "slug": 'optimizando-nextjs-para-web-vitals',
        "title": 'Optimizando Next.js para Core Web Vitals',
        "excerpt": 'Consejos prácticos y técnicas para mejorar el rendimiento LCP, CLS y FID en tus aplicaciones Next.js y alcanzar puntuaciones altas en Lighthouse.',
        "content": "<p>Profundizamos en la optimización de <strong>Core Web Vitals</strong> con Next.js.</p><ul><li>Optimizar Imágenes</li><li>Lazy Loading</li><li>Code Splitting</li></ul>",
        "published_date": date(2024, 7, 20),
        "image_url": None,
    },
    {
        "id": 'post-3',
        "slug": 'fastapi-vs-nodejs-backend-moderno',
        "title": 'FastAPI vs. Node.js: ¿Cuál elegir para tu próximo backend?',
        "excerpt": 'Comparativa de rendimiento, facilidad de uso y ecosistema entre FastAPI (Python) y Node.js (JavaScript) para el desarrollo de APIs modernas.',
        "content": "<p>Una comparativa detallada entre <strong>FastAPI</strong> y <strong>Node.js</strong> para tomar la mejor decisión.</p>",
        "published_date": date(2024, 7, 15),
        "image_url": None,
    },
    {
        "id": 'post-4',
        "slug": 'prompt-engineering-practico',
        "title": 'Ingeniería de Prompts: Más Allá de lo Básico',
        "excerpt": 'Técnicas y consejos prácticos para diseñar prompts efectivos que expriman al máximo el potencial de modelos como GPT-4.',
        "content": "<p>Exploramos técnicas avanzadas de <strong>Prompt Engineering</strong>.</p>",
        "published_date": date(2024, 6, 10),
        "image_url": None,
    },
    {
        "id": 'post-5',
        "slug": 'automatizando-tareas-con-ia',
        "title": 'Automatizando el Día a Día con IA: Casos de Uso Reales',
        "excerpt": 'Explorando herramientas y enfoques para automatizar tareas repetitivas usando IA, desde scripts de Python hasta plataformas low-code.',
        "content": "<p>Casos prácticos de <strong>automatización con IA</strong>.</p>",
        "published_date": date(2024, 5, 25),
        "image_url": None,
    },
    {
        "id": 'post-6',
        "slug": 'gemelos-digitales-industria',
        "title": 'Gemelos Digitales: Revolucionando la Industria con Datos',
        "excerpt": 'Una introducción al concepto de Gemelos Digitales, sus aplicaciones industriales y cómo la IA potencia su desarrollo y utilidad.',
        "content": "<p>Introducción a los <strong>Gemelos Digitales</strong> y su impacto.</p>",
        "published_date": date(2024, 5, 5),
        "image_url": None,
    },
]

# --- Noticias ---
initial_news_items = [
    {
        "id": str(uuid.uuid4()),
        "title": 'OpenAI presenta Sora, un modelo de IA que crea vídeo a partir de texto',
        "source": 'OpenAI Blog',
        "url": 'https://openai.com/sora',
        "publishedAt": date(2024, 2, 15),
        "summary": 'Sora puede generar vídeos de hasta un minuto de duración manteniendo la calidad visual y la adherencia a la indicación del usuario.',
        "image_url": None,
        "relevance_score": 0,
        "time_category": 'general'
    },
    {
        "id": str(uuid.uuid4()),
        "title": 'Google lanza Gemini 1.5 Pro con ventana de contexto de 1 millón de tokens',
        "source": 'Google AI Blog',
        "url": 'https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/',
        "publishedAt": date(2024, 2, 15),
        "summary": 'Una nueva versión del modelo Gemini con mejoras significativas en el razonamiento largo y una ventana de contexto sin precedentes.',
        "image_url": None,
        "relevance_score": 0,
        "time_category": 'general'
    },
    {
        "id": str(uuid.uuid4()),
        "title": 'NVIDIA anuncia la plataforma Blackwell para la próxima generación de IA',
        "source": 'NVIDIA Newsroom',
        "url": 'https://nvidianews.nvidia.com/news/nvidia-blackwell-platform-arrives-to-power-a-new-era-of-computing',
        "publishedAt": date(2024, 3, 18),
        "summary": 'La nueva arquitectura GPU Blackwell promete acelerar drásticamente el entrenamiento y la inferencia de modelos de IA a gran escala.',
        "image_url": None,
        "relevance_score": 0,
        "time_category": 'general'
    },
    {
        "id": str(uuid.uuid4()),
        "title": 'Cómo la IA está transformando el desarrollo de software',
        "source": 'GitHub Blog',
        "url": 'https://github.blog/2024-01-10-how-ai-is-transforming-software-development/',
        "publishedAt": date(2024, 1, 10),
        "summary": 'Un análisis sobre el impacto de herramientas como GitHub Copilot en la productividad y el flujo de trabajo de los desarrolladores.',
        "image_url": None,
        "relevance_score": 0,
        "time_category": 'general'
    },
] 