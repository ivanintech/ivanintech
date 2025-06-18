import { Skeleton } from "@/components/ui/skeleton"

export function BlogPostPreviewSkeleton() {
  return (
    <div className="border border-border rounded-lg p-4 flex flex-col h-full bg-card">
      <Skeleton className="w-full h-40 mb-4 rounded-md" />
      <Skeleton className="h-6 w-3/4 mb-2" />
      <Skeleton className="h-4 w-full mb-1" />
      <Skeleton className="h-4 w-5/6 mb-4" />
      <Skeleton className="h-4 w-1/2 mt-auto" />
    </div>
  )
} 