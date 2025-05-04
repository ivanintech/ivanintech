import { Skeleton } from "@/components/ui/skeleton"

export function ProjectCardSkeleton() {
  return (
    <div className="border border-border rounded-lg overflow-hidden bg-muted/50 dark:bg-muted/10 flex flex-col">
      {/* Media Placeholder */}
      <Skeleton className="aspect-video w-full" />
      
      {/* Content Placeholder */}
      <div className="p-5 flex flex-col flex-grow">
        {/* Title Placeholder */}
        <Skeleton className="h-5 w-3/4 mb-3" /> 
        
        {/* Description Placeholder */}
        <Skeleton className="h-4 w-full mb-1" />
        <Skeleton className="h-4 w-5/6 mb-4" />
        
        {/* Technologies Placeholder */}
        <div className="mb-4 flex flex-wrap gap-1.5">
          <Skeleton className="h-5 w-16 rounded-full" />
          <Skeleton className="h-5 w-20 rounded-full" />
          <Skeleton className="h-5 w-14 rounded-full" />
        </div>
        
        {/* Links Placeholder (Optional, could omit for skeleton) */}
        <div className="flex justify-end space-x-3 mt-auto">
          <Skeleton className="h-4 w-12" />
          {/* <Skeleton className="h-4 w-10" /> */}
        </div>
      </div>
    </div>
  )
} 