import { Skeleton } from "@/components/ui/skeleton"

export function BlogPostPreviewSkeleton() {
  return (
    <div className="border border-border rounded-lg overflow-hidden bg-muted/50 dark:bg-muted/10 flex flex-col">
      {/* Media Placeholder */}
      <Skeleton className="aspect-video w-full" />
      
      {/* Content Placeholder */}
      <div className="p-5 flex flex-col flex-grow">
        {/* Date Placeholder */}
        <Skeleton className="h-3 w-24 mb-3" />
        
        {/* Title Placeholder */}
        <Skeleton className="h-5 w-4/5 mb-3" /> 
        
        {/* Excerpt Placeholder */}
        <Skeleton className="h-4 w-full mb-1" />
        <Skeleton className="h-4 w-full mb-1" />
        <Skeleton className="h-4 w-1/2 mb-4" />
        
        {/* Read More Placeholder */}
        <Skeleton className="h-4 w-20 mt-auto" />
      </div>
    </div>
  )
} 