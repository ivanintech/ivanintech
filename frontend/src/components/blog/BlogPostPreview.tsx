import Link from "next/link";
import { format } from "date-fns"; // Assuming date-fns is used for formatting
import { es } from "date-fns/locale"; // Import Spanish locale
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge"; // If you want to show status or tags as badges
import { Pencil, Trash2 } from "lucide-react"; // Example icons for LinkedIn link and edit/delete
import type { BlogPost } from "@/types"; // Corrected path
import { useAuth } from "@/context/AuthContext"; // Import AuthContext
import { Button } from "@/components/ui/button"; // Import Button
import { EditableImage } from "@/components/ui/EditableImage";

// Remove internal interface definition
// interface BlogPost { ... }

interface BlogPostPreviewProps {
  post: BlogPost;
  onEdit: (post: BlogPost) => void;
  onDelete: (post: BlogPost) => void;
  className?: string;
}

export function BlogPostPreview({ post, onEdit, onDelete, className }: BlogPostPreviewProps) {
  const { user } = useAuth(); // Get user from context

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
    <Link href={`/blog/${post.slug}`} className={className}>
      <Card className={`flex flex-col h-full overflow-hidden transition-shadow duration-300 ease-in-out hover:shadow-lg min-h-[550px]`}>
        <CardHeader>
          {post.image_url && (
            <div className="relative w-full h-48 mb-4">
              <EditableImage
                src={post.image_url}
                alt={`Imagen para ${post.title}`}
                fill
                style={{ objectFit: "cover" }}
                className="rounded-t-lg"
                onEdit={() => onEdit(post)}
                onDelete={() => onDelete(post)}
                onError={() => { // Simplified onError
                  console.error(`Error loading image: ${post.image_url}`);
                }}
              />
            </div>
          )}
          <CardTitle className="text-lg font-semibold leading-tight text-foreground group-hover:text-primary transition-colors duration-200">
            {post.title}
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-grow">
          {/* <p className="text-sm text-muted-foreground mb-2">{previewContent}</p> */} 
          {/* Display tags as badges if available */}
          {post.tags && (
            <div className="flex flex-wrap gap-1 mb-3">
              {post.tags.split(',').map((tag: string) => (
                <Badge key={tag.trim()} variant="secondary">{tag.trim()}</Badge>
              ))}
            </div>
          )}
        </CardContent>
        <CardFooter className="flex flex-col items-start mt-auto pt-4 border-t">
          <div className="flex justify-between w-full items-center">
            <p className="text-xs text-muted-foreground">{formattedDate}</p>
            
          </div>
          
          {user?.is_superuser && (
            <div className="flex gap-2 mt-4 self-end">
              <Button variant="outline" size="sm" onClick={() => onEdit(post)}>
                <Pencil className="w-4 h-4 mr-1" />
                Editar
              </Button>
              <Button variant="destructive" size="sm" onClick={() => onDelete(post)}>
                <Trash2 className="w-4 h-4 mr-1" />
                Eliminar
              </Button>
            </div>
          )}
        </CardFooter>
      </Card>
    </Link>
  );
} 