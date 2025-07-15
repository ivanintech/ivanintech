import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { LogIn } from 'lucide-react';

export function JoinCommunityBanner({ className = "" }) {
  return (
    <Link
      href="/login"
      className={`block mb-12 transform hover:-translate-y-1 transition-transform duration-300 ease-in-out max-w-4xl mx-auto ${className}`}
      legacyBehavior
    >
      <Card className="bg-secondary/40 border-primary/20 hover:border-primary/50 transition-all duration-300">
        <CardContent className="p-6 flex items-center justify-center space-x-4">
          <LogIn className="w-8 h-8 text-primary" />
          <div>
            <p className="font-bold text-lg text-primary">Join the community!</p>
            <p className="text-muted-foreground">Log in to suggest resources and participate.</p>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
} 