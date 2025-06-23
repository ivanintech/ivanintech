'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import apiClient from '@/lib/api-client';
import type { BlogSuggestion } from '@/types';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { format } from 'date-fns';

export default function SuggestionsPage() {
  const { user, token } = useAuth();
  const [suggestions, setSuggestions] = useState<BlogSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSuggestions = async () => {
    if (!token) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient<BlogSuggestion[]>('/suggestions/', { token });
      setSuggestions(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMessage);
      toast.error(`Failed to load suggestions: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (user?.is_superuser) {
      fetchSuggestions();
    } else {
      setIsLoading(false);
      setError("You do not have permission to view this page.");
    }
  }, [user, token]);

  const handlePublish = async (suggestionId: string) => {
    if (!token) return;
    toast.info("Publishing suggestion...");
    try {
      await apiClient(`/suggestions/${suggestionId}/publish`, { method: 'POST', token });
      toast.success("Suggestion published successfully!");
      fetchSuggestions(); // Refresh the list
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      toast.error(`Failed to publish: ${errorMessage}`);
    }
  };

  const handleReject = async (suggestionId: string) => {
    if (!token) return;
    toast.info("Rejecting suggestion...");
    try {
      await apiClient(`/suggestions/${suggestionId}`, { method: 'DELETE', token });
      toast.success("Suggestion rejected successfully!");
      fetchSuggestions(); // Refresh the list
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      toast.error(`Failed to reject: ${errorMessage}`);
    }
  };

  if (isLoading) {
    return <div className="container mx-auto px-4 py-16 text-center">Loading suggestions...</div>;
  }

  if (error) {
    return <div className="container mx-auto px-4 py-16 text-center text-destructive">{error}</div>;
  }

  if (!user?.is_superuser) {
    return <div className="container mx-auto px-4 py-16 text-center">Access Denied.</div>;
  }

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold text-primary">Blog Post Suggestions</h1>
        <p className="text-muted-foreground">{suggestions.length} pending</p>
      </div>

      {suggestions.length === 0 ? (
        <p className="text-center text-muted-foreground py-10">No pending suggestions. Great job!</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {suggestions.map((suggestion) => (
            <Card key={suggestion.id} className="flex flex-col">
              <CardHeader>
                <CardTitle>{suggestion.title}</CardTitle>
                <CardDescription>
                  From: {suggestion.source || 'Unknown'} | Created: {format(new Date(suggestion.created_at), 'dd MMM yyyy')}
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-grow">
                <p className="text-sm text-muted-foreground mb-4">{suggestion.excerpt}</p>
                {suggestion.tags && (
                  <div className="flex flex-wrap gap-2">
                    {suggestion.tags.split(',').map(tag => (
                      <Badge key={tag} variant="secondary">{tag.trim()}</Badge>
                    ))}
                  </div>
                )}
              </CardContent>
              <Separator />
              <CardFooter className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={() => handleReject(suggestion.id)}>Reject</Button>
                <Button onClick={() => handlePublish(suggestion.id)}>Publish</Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
} 