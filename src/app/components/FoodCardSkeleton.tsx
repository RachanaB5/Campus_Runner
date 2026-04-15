import { motion } from "motion/react";

export function FoodCardSkeleton() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white rounded-2xl shadow-sm overflow-hidden flex flex-col h-full border border-gray-100"
    >
      {/* Image Skeleton */}
      <div className="relative h-48 sm:h-56 w-full bg-gray-200 animate-pulse" />

      {/* Content Skeleton */}
      <div className="p-4 flex flex-col flex-grow">
        {/* Title */}
        <div className="h-6 bg-gray-200 rounded-md w-3/4 mb-2 animate-pulse" />
        
        {/* Labels/Badges */}
        <div className="flex gap-2 mb-3">
          <div className="h-4 bg-gray-200 rounded-md w-12 animate-pulse" />
          <div className="h-4 bg-gray-200 rounded-md w-16 animate-pulse" />
        </div>

        {/* Text */}
        <div className="h-4 bg-gray-200 rounded-md w-full mb-1 animate-pulse" />
        <div className="h-4 bg-gray-200 rounded-md w-5/6 mb-4 animate-pulse" />

        <div className="mt-auto flex items-center justify-between">
          {/* Price */}
          <div className="h-6 bg-gray-200 rounded-md w-16 animate-pulse" />
          {/* Button */}
          <div className="h-10 bg-gray-200 w-24 rounded-full animate-pulse" />
        </div>
      </div>
    </motion.div>
  );
}
