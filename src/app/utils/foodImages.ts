export const FALLBACK_FOOD_IMAGE =
  "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop";

// Multiple unique images per category for variety
const CATEGORY_IMAGE_POOLS: Record<string, string[]> = {
  meals: [
    "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop",
  ],
  combos: [
    "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=400&h=300&fit=crop",
  ],
  "north indian": [
    "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1645177628172-a5f5aff0e4af?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=400&h=300&fit=crop",
  ],
  parathas: [
    "https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1631515243349-e0cb75fb8d3a?w=400&h=300&fit=crop",
  ],
  rolls: [
    "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?w=400&h=300&fit=crop",
  ],
  biryanis: [
    "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1574653853027-5382a3d23a15?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1596797038530-2c107229654b?w=400&h=300&fit=crop",
  ],
  biryani: [
    "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1574653853027-5382a3d23a15?w=400&h=300&fit=crop",
  ],
  burgers: [
    "https://images.unsplash.com/photo-1550547660-d9450f859349?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1586816001966-79b736744398?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1529006557810-274b9b2fc783?w=400&h=300&fit=crop",
  ],
  maggi: [
    "https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1569407228235-6f4220b8b4e5?w=400&h=300&fit=crop",
  ],
  pizzas: [
    "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&h=300&fit=crop",
  ],
  "pizza & bread": [
    "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&h=300&fit=crop",
  ],
  beverages: [
    "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&h=300&fit=crop",
  ],
  juices: [
    "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400&h=300&fit=crop",
  ],
  desserts: [
    "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1567327613485-fae086351c6e?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&h=300&fit=crop",
  ],
  pasta: [
    "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1551183053-bf91798d792b?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=400&h=300&fit=crop",
  ],
  "ice cream": [
    "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1488900128323-21503983a07e?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1576506295286-5cda18df43e7?w=400&h=300&fit=crop",
  ],
  snacks: [
    "https://images.unsplash.com/photo-1555685812-4b943f1cb0eb?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1621996659490-3275b4d0d951?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&h=300&fit=crop",
  ],
  sandwiches: [
    "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1481070414801-51fd732d7184?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1553909489-cd47e0907980?w=400&h=300&fit=crop",
  ],
  wraps: [
    "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1590947132387-155cc02f3212?w=400&h=300&fit=crop",
  ],
  salads: [
    "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=300&fit=crop",
  ],
  soups: [
    "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=400&h=300&fit=crop",
  ],
  breakfast: [
    "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=400&h=300&fit=crop",
  ],
  "south indian": [
    "https://images.unsplash.com/photo-1600803907087-f56d462fd26b?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=400&h=300&fit=crop",
  ],
  dosas: [
    "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1600803907087-f56d462fd26b?w=400&h=300&fit=crop",
  ],
  noodles: [
    "https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1626804475297-41608ea09aeb?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1562802378-063ec186a863?w=400&h=300&fit=crop",
  ],
  "chinese & noodles": [
    "https://images.unsplash.com/photo-1562802378-063ec186a863?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=400&h=300&fit=crop",
  ],
  mocktails: [
    "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1543362906-acfc16c67564?w=400&h=300&fit=crop",
  ],
  shakes: [
    "https://images.unsplash.com/photo-1572490122747-3a3a4a25dd5a?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1553361371-9b22f78e8b1d?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1563805042-8f7ce527f9e5?w=400&h=300&fit=crop",
  ],
  cakes: [
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1607478900766-efe13248b125?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop",
  ],
};

// Deterministic but appears random: pick image based on item name hash
function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

export function getFoodImageUrl(imageUrl?: string | null, category?: string | null, name?: string | null): string {
  if (imageUrl && imageUrl.trim() && !imageUrl.includes("placeholder")) return imageUrl;
  const normalized = (category || "").trim().toLowerCase();
  const pool =
    CATEGORY_IMAGE_POOLS[normalized] ||
    Object.values(CATEGORY_IMAGE_POOLS).flat();
  const seed = hashString((name || "") + (category || ""));
  return pool[seed % pool.length];
}
