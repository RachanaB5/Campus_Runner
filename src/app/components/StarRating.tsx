import { Star } from "lucide-react";

interface StarRatingProps {
  value: number;
  onChange?: (value: number) => void;
  readonly?: boolean;
  size?: number;
}

export function StarRating({ value, onChange, readonly = false, size = 20 }: StarRatingProps) {
  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: 5 }).map((_, index) => {
        const starValue = index + 1;
        const filled = starValue <= value;
        return (
          <button
            key={starValue}
            type="button"
            disabled={readonly}
            onClick={() => onChange?.(starValue)}
            className={`transition-transform ${readonly ? "cursor-default" : "hover:scale-110 active:scale-125"}`}
          >
            <Star
              className={filled ? "text-orange-500 fill-orange-500" : "text-gray-300"}
              style={{ width: size, height: size }}
            />
          </button>
        );
      })}
    </div>
  );
}
