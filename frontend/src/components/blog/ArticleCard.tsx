import Link from "next/link";
import Image from "next/image";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ExternalLink } from "lucide-react";
import type { BlogPost } from "@/types";

interface ArticleCardProps {
  post: BlogPost;
}

export function ArticleCard({ post }: ArticleCardProps) {
  let formattedDate = "";
  try {
    const date = new Date(post.published_date);
    formattedDate = format(date, "d 'de' MMMM 'de' yyyy", { locale: es });
  } catch (error) {
    console.error("Error parsing date:", post.published_date, error);
    formattedDate = "Fecha inválida";
  }

  return (
    <Card className="flex flex-col h-full overflow-hidden transition-shadow duration-300 ease-in-out hover:shadow-lg">
      <CardHeader>
        {post.image_url && (
          <div className="relative w-full h-48 mb-4">
            <Image
              src={post.image_url}
              alt={`Imagen para ${post.title}`}
              fill
              style={{ objectFit: "cover" }}
              className="rounded-t-lg"
              onError={(e) => {
                console.error(`Error loading image: ${post.image_url}`);
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
        {post.linkedin_post_url && (
          <div className="w-full mt-2">
            <iframe 
              src={post.linkedin_post_url} 
              height="400" 
              width="100%" 
              frameBorder="0" 
              allowFullScreen={true}
              title="Embedded post"
              className="w-full border-none"
            ></iframe>
          </div>
        )}
      </CardFooter>
    </Card>
  );
} 