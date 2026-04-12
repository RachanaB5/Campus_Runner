export const FALLBACK_FOOD_IMAGE =
  "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop";

const CATEGORY_IMAGES: Record<string, string> = {
  meals: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop",
  combos: "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=400&h=300&fit=crop",
  "north indian": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&h=300&fit=crop",
  parathas: "https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=400&h=300&fit=crop",
  rolls: "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400&h=300&fit=crop",
  biryanis: "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&h=300&fit=crop",
  biryani: "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&h=300&fit=crop",
  burgers: "https://images.unsplash.com/photo-1550547660-d9450f859349?w=400&h=300&fit=crop",
  maggi: "https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=400&h=300&fit=crop",
  pizzas: "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&h=300&fit=crop",
  "pizza & bread": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&h=300&fit=crop",
  beverages: "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop",
  desserts: "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop",
  pasta: "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400&h=300&fit=crop",
  "ice cream": "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=400&h=300&fit=crop",
};

export function getFoodImageUrl(imageUrl?: string | null, category?: string | null) {
  if (imageUrl && imageUrl.trim()) return imageUrl;
  const normalized = (category || "").trim().toLowerCase();
  return CATEGORY_IMAGES[normalized] || FALLBACK_FOOD_IMAGE;
}
