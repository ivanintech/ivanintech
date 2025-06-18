import { Skeleton } from "@/components/ui/skeleton"

export function ProjectCardSkeleton() {
  return (
    <div className="border border-border rounded-lg p-4 flex flex-col h-full bg-card">
      <Skeleton className="w-full h-48 mb-4 rounded-md" />
      <Skeleton className="h-6 w-1/2 mb-2" />
      <Skeleton className="h-4 w-full mb-1" />
      <Skeleton className="h-4 w-5/6 mb-4" />
      <div className="flex flex-wrap gap-2 mt-auto">
        <Skeleton className="h-6 w-20 rounded-full" />
        <Skeleton className="h-6 w-24 rounded-full" />
        <Skeleton className="h-6 w-16 rounded-full" />
      </div>
    </div>
  )
} 