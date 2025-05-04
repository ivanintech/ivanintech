import Link from "next/link";
import Image from "next/image";
import { format } from "date-fns"; // Assuming date-fns is used for formatting
import { es } from "date-fns/locale"; // Import Spanish locale
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge"; // If you want to show status or tags as badges
import { ExternalLink } from "lucide-react"; // Example icon for LinkedIn link
import type { BlogPost } from "@/lib/types"; // Import from shared types

// Remove internal interface definition
// interface BlogPost { ... }

interface BlogPostPreviewProps {
  post: BlogPost;
}

export function BlogPostPreview({ post }: BlogPostPreviewProps) {
  // Attempt to parse the date
  let formattedDate = "";
  try {
    const date = new Date(post.published_date);
    // Format date in Spanish, e.g., "4 de mayo de 2025"
    formattedDate = format(date, "d 'de' MMMM 'de' yyyy", { locale: es });
  } catch (error) {
    console.error("Error parsing date:", post.published_date, error);
    formattedDate = "Fecha inválida";
  }

  // Optional: Generate a short preview from content if needed
  // const previewContent = post.content.substring(0, 150) + (post.content.length > 150 ? "..." : "");

  return (
    <Card className="flex flex-col h-full overflow-hidden transition-shadow duration-300 ease-in-out hover:shadow-lg">
      <CardHeader>
        {post.image_url && (
          <div className="relative w-full h-48 mb-4">
            <Image
              src={post.image_url}
              alt={`Imagen para ${post.title}`}
              layout="fill"
              objectFit="cover"
              className="rounded-t-lg"
              // Add error handling if desired
              onError={(e) => {
                console.error(`Error loading image: ${post.image_url}`);
                // Optionally set a fallback image
                // e.currentTarget.src = '/path/to/fallback-image.png'; 
              }}
            />
          </div>
        )}
        <CardTitle className="text-lg font-semibold leading-tight">
          <Link href={`/blog/${post.slug}`} className="hover:text-primary transition-colors duration-200">
            {post.title}
          </Link>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-grow">
        {/* <p className="text-sm text-muted-foreground mb-2">{previewContent}</p> */} 
        {/* Display tags as badges if available */}
        {post.tags && (
          <div className="flex flex-wrap gap-1 mb-3">
            {post.tags.split(',').map((tag) => (
              <Badge key={tag.trim()} variant="secondary">{tag.trim()}</Badge>
            ))}
          </div>
        )}
      </CardContent>
      <CardFooter className="flex flex-col items-start mt-auto pt-4 border-t">
        <p className="text-xs text-muted-foreground mb-2">{formattedDate}</p>
        {/* Add LinkedIn link/button if URL exists */}
        {post.linkedin_post_url && (
          <a
            href={post.linkedin_post_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-3 py-1 text-xs font-medium text-white bg-blue-700 rounded-md hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800 transition-colors duration-200"
          >
            Ver en LinkedIn
            <ExternalLink className="w-3 h-3 ml-1.5" />
          </a>
        )}
      </CardFooter>
    </Card>
  );
} 