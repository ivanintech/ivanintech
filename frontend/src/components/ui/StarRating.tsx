'use client';

import React, { useState } from 'react';
import { FaStar } from 'react-icons/fa';
import { cn } from '@/lib/utils';

interface StarRatingProps {
  rating: number;
  onRatingChange?: (rating: number) => void;
  className?: string;
  totalStars?: number;
  size?: number;
}

export function StarRating({ rating, onRatingChange, className, totalStars = 5, size = 16 }: StarRatingProps) {
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
    <div className={cn("flex items-center", className)}>
      {[...Array(totalStars)].map((_, index) => {
        const starValue = index + 1;
        const currentRating = hoverRating || rating;
        
        // Calculate fill percentage for each star
        const fillPercentage = Math.min(Math.max(currentRating - index, 0), 1) * 100;
        
        return (
          <div
            key={starValue}
            className="relative"
            onMouseEnter={() => handleMouseEnter(starValue)}
            onMouseLeave={handleMouseLeave}
            onClick={() => handleRatingClick(starValue)}
          >
            <FaStar
              size={size}
              className={cn("text-gray-300 dark:text-gray-600", onRatingChange ? "cursor-pointer" : "")}
            />
            <div
              className="absolute top-0 left-0 h-full overflow-hidden"
              style={{ width: `${fillPercentage}%` }}
            >
              <FaStar
                size={size}
                className={cn("text-yellow-400", onRatingChange ? "cursor-pointer" : "")}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
} 