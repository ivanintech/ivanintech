import apiClient from '@/lib/api-client';
import type { NewsItemRead, NewsItemSubmit } from '@/types';

/**
 * Submits a new news item URL to the backend.
 * @param token The authentication token for the user.
 * @param url The URL of the news item to submit.
 * @returns The newly created news item.
 */
export const submitNewsItem = async (token: string, url: string): Promise<NewsItemRead> => {
  const payload: NewsItemSubmit = { url };
  
  const response = await apiClient<NewsItemRead>('/news/submit', {
    method: 'POST',
    token: token,
    body: payload,
  });

  return response;
};

/**
 * Fetches news items from the API.
 * @param options Optional parameters like limit and skip.
 * @returns A list of news items.
 */
export const getNews = async (options?: { limit?: number; skip?: number }): Promise<NewsItemRead[]> => {
  const query = new URLSearchParams();
  if (options?.limit) {
    query.append("limit", options.limit.toString());
  }
  if (options?.skip) {
    query.append("skip", options.skip.toString());
  }

  const response = await apiClient<NewsItemRead[]>(`/news?${query.toString()}`);
  return response;
} 