'use client';

import React, { useState } from 'react';
import { FaStar } from 'react-icons/fa';
import { cn } from '@/lib/utils';

interface StarRatingProps {
  rating: number;
  onRatingChange?: (rating: number) => void;
  className?: string;
  totalStars?: number;
}

export function StarRating({ rating, onRatingChange, className, totalStars = 5 }: StarRatingProps) {
  const [hoverRating, setHoverRating] = useState(0);

  const handleRatingClick = (rate: number) => {
    if (onRatingChange) {
      onRatingChange(rate);
    }
  };

  const handleMouseEnter = (rate: number) => {
    if (onRatingChange) {
      setHoverRating(rate);
    }
  };

  const handleMouseLeave = () => {
    if (onRatingChange) {
      setHoverRating(0);
    }
  };

  return (
    <div className={cn("flex items-center gap-1", className)}>
      {[...Array(totalStars)].map((_, index) => {
        const starValue = index + 1;
        const isActive = starValue <= (hoverRating || rating);
        
        return (
          <FaStar
            key={starValue}
            className={cn(
              "text-gray-300 transition-colors",
              isActive ? "text-yellow-400" : "text-gray-300",
              onRatingChange ? "cursor-pointer hover:text-yellow-300" : ""
            )}
            onMouseEnter={() => handleMouseEnter(starValue)}
            onMouseLeave={handleMouseLeave}
            onClick={() => handleRatingClick(starValue)}
          />
        );
      })}
    </div>
  );
} 