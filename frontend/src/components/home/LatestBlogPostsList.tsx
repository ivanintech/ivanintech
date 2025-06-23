import type { BlogPost } from '@/types';
import apiClient from '@/lib/api-client';
import { adaptLinkedInPostForHomePage } from '@/lib/linkedin-posts-data';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { format } from "date-fns";
import { enUS } from "date-fns/locale";
import { AnimatedSection } from '@/components/ui/animated-section';
import Link from 'next/link';

// Definimos el tipo aquí para resolver el linter error y para mayor claridad.
interface HomePageBlogPost {
    id: string;
    slug: string;
    title: string;
    excerpt?: string;
    published_date: string;
    linkedInUrl?: string;
    embedUrl?: string; // Cambiado de embedCode
}

async function getBlogAndLinkedInPosts(): Promise<HomePageBlogPost[]> {
    try {
      const response = await apiClient<{ items: BlogPost[] }>('/blog/?show_automated=true&limit=20');
      const allPosts = response.items;

      // 1. Filtrar solo los posts que están publicados
      const publishedPosts = allPosts.filter(p => p.status === 'published');
  
      // 2. De los publicados, intentar encontrar y adaptar los de LinkedIn
      const linkedInPosts = publishedPosts
        .map(post => adaptLinkedInPostForHomePage(post))
        .filter((p): p is HomePageBlogPost => p !== null)
        .slice(0, 3);
      
      // Si encontramos posts de LinkedIn, los devolvemos
      if (linkedInPosts.length > 0) {
        return linkedInPosts;
      }

      // 3. Fallback: Si no hay de LinkedIn, devolver los 3 posts normales más recientes que estén publicados
      return publishedPosts.slice(0, 3).map(post => ({
        id: post.id,
        slug: post.slug,
        title: post.title,
        excerpt: post.excerpt ?? 'Click to read more about this post.',
        published_date: post.published_date,
      }));
  
    } catch (error) {
      console.error("Failed to fetch blog posts:", error);
      return [];
    }
}

function HomePageBlogPostPreview({ post }: { post: HomePageBlogPost }) {
    if (post.embedUrl) {
      return (
        <Card className="h-full flex flex-col">
          <CardHeader>
            <CardTitle className="text-lg leading-tight truncate">{post.title}</CardTitle>
            <p className="text-sm text-muted-foreground">{format(new Date(post.published_date), "MMMM d, yyyy", { locale: enUS })}</p>
          </CardHeader>
          <CardContent className="flex-grow">
            <div className="aspect-w-16 aspect-h-9 h-full">
              <iframe
                src={post.embedUrl}
                className="w-full h-full border-0"
                allowFullScreen
                title={`LinkedIn Post: ${post.title}`}
              ></iframe>
            </div>
          </CardContent>
        </Card>
      );
    }
  
    return (
      <Card className="h-full flex flex-col">
         <CardHeader>
            <CardTitle className="text-lg leading-tight">{post.title}</CardTitle>
         </CardHeader>
         <CardContent className="flex-grow">
            <p className="text-sm text-muted-foreground line-clamp-3">{post.excerpt}</p>
         </CardContent>
         <CardFooter>
            <p className="text-xs text-muted-foreground">{format(new Date(post.published_date), "MMMM d, yyyy", { locale: enUS })}</p>
         </CardFooter>
      </Card>
    )
}
  
export async function LatestBlogPostsList() {
    const posts = await getBlogAndLinkedInPosts();
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {posts.map((post, index) => {
          const postUrl = post.linkedInUrl || `/blog/${post.slug}`;
          const isExternal = !!post.linkedInUrl;

          return (
            <Link 
              href={postUrl} 
              key={post.id || index} 
              target={isExternal ? '_blank' : undefined} 
              rel={isExternal ? 'noopener noreferrer' : undefined}
              className="block h-full"
            >
              <AnimatedSection delay={index * 0.1} className="h-full">
                <HomePageBlogPostPreview post={post} />
              </AnimatedSection>
            </Link>
          )
        })}
      </div>
    );
} 