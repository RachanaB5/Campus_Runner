export interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
  image: string;
  category: string;
  isVeg: boolean;
  rating: number;
  prepTime: string;
}

export interface Order {
  id: string;
  items: { item: MenuItem; quantity: number }[];
  total: number;
  status: 'pending' | 'preparing' | 'ready' | 'delivered';
  timestamp: Date;
  deliveryLocation: string;
  customerName: string;
  points?: number;
}

export interface Reward {
  id: number;
  name: string;
  description: string;
  pointsRequired: number;
  image: string;
  category: string;
}

export interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
  image: string;
  category: string;
  isVeg: boolean;
  rating: number;
  prepTime: string;
}

export interface Order {
  id: string;
  items: { item: MenuItem; quantity: number }[];
  total: number;
  status: 'pending' | 'preparing' | 'ready' | 'delivered';
  timestamp: Date;
  deliveryLocation: string;
  customerName: string;
  points?: number;
}

export interface Reward {
  id: number;
  name: string;
  description: string;
  pointsRequired: number;
  image: string;
  category: string;
}

export const menuItems: MenuItem[] = [
  // ── MEALS ──────────────────────────────────────────────────────────
  {
    id: 1,
    name: "North Mini Meals",
    description: "A wholesome North Indian mini thali with dal, sabzi, roti and rice",
    price: 70,
    image: "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=300&fit=crop",
    category: "Meals",
    isVeg: true,
    rating: 4.4,
    prepTime: "15-20 min"
  },
  {
    id: 2,
    name: "North Full Meals",
    description: "Full North Indian thali with dal, 2 sabzis, roti, rice, salad and pickle",
    price: 120,
    image: "https://images.unsplash.com/photo-1546839213-23296281120?w=400&h=300&fit=crop",
    category: "Meals",
    isVeg: true,
    rating: 4.5,
    prepTime: "20-25 min"
  },
  {
    id: 3,
    name: "South Mini Meals",
    description: "South Indian mini meal with sambar, rasam, rice and curry",
    price: 50,
    image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop",
    category: "Meals",
    isVeg: true,
    rating: 4.3,
    prepTime: "15 min"
  },
  {
    id: 4,
    name: "South Full Meals",
    description: "Complete South Indian meal with sambar, rasam, curry, rice and pickles",
    price: 100,
    image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop",
    category: "Meals",
    isVeg: true,
    rating: 4.4,
    prepTime: "20 min"
  },

  // ── COMBOS ──────────────────────────────────────────────────────────
  {
    id: 5,
    name: "Jeera Rice with Dal Tadka",
    description: "Fragrant jeera rice paired with creamy dal tadka",
    price: 70,
    image: "https://images.unsplash.com/photo-1609501676725-7186f017a4b0?w=400&h=300&fit=crop",
    category: "Combos",
    isVeg: true,
    rating: 4.5,
    prepTime: "18 min"
  },
  {
    id: 6,
    name: "Rajma/Chole Rice",
    description: "Aromatic rice with kidney beans or chickpeas curry",
    price: 70,
    image: "https://images.unsplash.com/photo-1609501676725-7186f017a4b0?w=400&h=300&fit=crop",
    category: "Combos",
    isVeg: true,
    rating: 4.4,
    prepTime: "20 min"
  },
  {
    id: 7,
    name: "Aloo Paratha with Chole",
    description: "Soft potato-filled paratha with chickpea curry",
    price: 80,
    image: "https://images.unsplash.com/photo-1585238341710-4913968ba8f7?w=400&h=300&fit=crop",
    category: "Combos",
    isVeg: true,
    rating: 4.5,
    prepTime: "18 min"
  },
  {
    id: 8,
    name: "Paneer Curry Combo",
    description: "Creamy paneer curry with rice and bread",
    price: 120,
    image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop",
    category: "Combos",
    isVeg: true,
    rating: 4.6,
    prepTime: "22 min"
  },
  {
    id: 9,
    name: "Veg Chinese Combo",
    description: "Fried rice or noodles with veg curry",
    price: 120,
    image: "https://images.unsplash.com/photo-1609501676725-7186f017a4b0?w=400&h=300&fit=crop",
    category: "Combos",
    isVeg: true,
    rating: 4.4,
    prepTime: "20 min"
  },
  {
    id: 10,
    name: "Non Veg Chinese Combo",
    description: "Fried rice or noodles with non-vegetarian curry",
    price: 150,
    image: "https://images.unsplash.com/photo-1609501676725-7186f017a4b0?w=400&h=300&fit=crop",
    category: "Combos",
    isVeg: false,
    rating: 4.6,
    prepTime: "22 min"
  },
  {
    id: 11,
    name: "Chicken Curry Combo",
    description: "Tender chicken curry with rice and bread",
    price: 120,
    image: "https://images.unsplash.com/photo-1565937539826-b6e9db1b2da1?w=400&h=300&fit=crop",
    category: "Combos",
    isVeg: false,
    rating: 4.7,
    prepTime: "25 min"
  },
  {
    id: 12,
    name: "Egg Curry Combo",
    description: "Spiced egg curry with rice and bread",
    price: 100,
    image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop",
    category: "Combos",
    isVeg: false,
    rating: 4.3,
    prepTime: "18 min"
  },

  // ── BIRYANI ──────────────────────────────────────────────────────────
  {
    id: 13,
    name: "Veg Hyderabadi Biryani",
    description: "Fragrant basmati rice with mixed vegetables and spices",
    price: 100,
    image: "https://images.unsplash.com/photo-1714611626323-5ba6204453be?w=400&h=300&fit=crop",
    category: "Biryani",
    isVeg: true,
    rating: 4.5,
    prepTime: "30 min"
  },
  {
    id: 14,
    name: "Mushroom Donne Biryani",
    description: "Aromatic rice with mushrooms in traditional cooking vessel",
    price: 120,
    image: "https://images.unsplash.com/photo-1714611626323-5ba6204453be?w=400&h=300&fit=crop",
    category: "Biryani",
    isVeg: true,
    rating: 4.5,
    prepTime: "32 min"
  },
  {
    id: 15,
    name: "Egg Hyderabadi Biryani",
    description: "Basmati rice layered with boiled eggs and aromatic spices",
    price: 110,
    image: "https://images.unsplash.com/photo-1714611626323-5ba6204453be?w=400&h=300&fit=crop",
    category: "Biryani",
    isVeg: false,
    rating: 4.4,
    prepTime: "32 min"
  },
  {
    id: 16,
    name: "Chicken Hyderabadi Biryani",
    description: "Tender chicken biryani with fragrant Hyderabadi spices",
    price: 140,
    image: "https://images.unsplash.com/photo-1714611626323-5ba6204453be?w=400&h=300&fit=crop",
    category: "Biryani",
    isVeg: false,
    rating: 4.7,
    prepTime: "35 min"
  },
  {
    id: 17,
    name: "Chicken Donne Biryani",
    description: "Chicken biryani cooked in traditional earthen vessel",
    price: 140,
    image: "https://images.unsplash.com/photo-1714611626323-5ba6204453be?w=400&h=300&fit=crop",
    category: "Biryani",
    isVeg: false,
    rating: 4.6,
    prepTime: "35 min"
  },
  {
    id: 18,
    name: "Chicken Kabab Biryani",
    description: "Aromatic biryani with tender chicken kababs",
    price: 150,
    image: "https://images.unsplash.com/photo-1714611626323-5ba6204453be?w=400&h=300&fit=crop",
    category: "Biryani",
    isVeg: false,
    rating: 4.7,
    prepTime: "35 min"
  },

  // ── NORTH INDIAN ──────────────────────────────────────────────────────────
  {
    id: 19,
    name: "Poori Chole",
    description: "Fluffy deep-fried bread with spiced chickpea curry",
    price: 50,
    image: "https://images.unsplash.com/photo-1585238341710-4913968ba8f7?w=400&h=300&fit=crop",
    category: "North Indian",
    isVeg: true,
    rating: 4.6,
    prepTime: "15 min"
  },
  {
    id: 20,
    name: "Chole Batura",
    description: "Large, fluffy fried bread served with chickpea curry",
    price: 60,
    image: "https://images.unsplash.com/photo-1585238341710-4913968ba8f7?w=400&h=300&fit=crop",
    category: "North Indian",
    isVeg: true,
    rating: 4.5,
    prepTime: "18 min"
  },
  {
    id: 21,
    name: "Dal Khichadi",
    description: "Comfort food made with rice and lentils with ghee",
    price: 70,
    image: "https://images.unsplash.com/photo-1609501676725-7186f017a4b0?w=400&h=300&fit=crop",
    category: "North Indian",
    isVeg: true,
    rating: 4.3,
    prepTime: "20 min"
  },

  // ── PARATHAS ──────────────────────────────────────────────────────────
  {
    id: 22,
    name: "Aloo Paratha with Curd",
    description: "Potato-filled paratha served with yogurt",
    price: 50,
    image: "https://images.unsplash.com/photo-1585238341710-4913968ba8f7?w=400&h=300&fit=crop",
    category: "Parathas",
    isVeg: true,
    rating: 4.5,
    prepTime: "15 min"
  },
  {
    id: 23,
    name: "Aloo Cheese Paratha with Curd",
    description: "Potato and cheese-filled paratha with yogurt",
    price: 60,
    image: "https://images.unsplash.com/photo-1585238341710-4913968ba8f7?w=400&h=300&fit=crop",
    category: "Parathas",
    isVeg: true,
    rating: 4.6,
    prepTime: "16 min"
  },
  {
    id: 24,
    name: "Aloo Paneer Mix Paratha",
    description: "Paratha with potato and cottage cheese filling",
    price: 60,
    image: "https://images.unsplash.com/photo-1585238341710-4913968ba8f7?w=400&h=300&fit=crop",
    category: "Parathas",
    isVeg: true,
    rating: 4.6,
    prepTime: "16 min"
  },
  {
    id: 25,
    name: "Paneer Paratha with Curd",
    description: "Cottage cheese-filled paratha served with yogurt",
    price: 70,
    image: "https://images.unsplash.com/photo-1585238341710-4913968ba8f7?w=400&h=300&fit=crop",
    category: "Parathas",
    isVeg: true,
    rating: 4.7,
    prepTime: "16 min"
  },
  {
    id: 26,
    name: "Paneer Cheese Paratha with Curd",
    description: "Paneer and cheese-filled paratha with yogurt",
    price: 80,
    image: "https://images.unsplash.com/photo-1585238341710-4913968ba8f7?w=400&h=300&fit=crop",
    category: "Parathas",
    isVeg: true,
    rating: 4.7,
    prepTime: "17 min"
  },

  // ── PASTA ──────────────────────────────────────────────────────────
  {
    id: 27,
    name: "Pasta Creamy Alfredo",
    description: "Rich white sauce pasta with garlic and butter",
    price: 70,
    image: "https://images.unsplash.com/photo-1621996346565-9ddf30910b8e?w=400&h=300&fit=crop",
    category: "Pasta",
    isVeg: true,
    rating: 4.4,
    prepTime: "15 min"
  },
  {
    id: 28,
    name: "Pasta Alfredo with Cheese",
    description: "Creamy alfredo pasta with melted cheese",
    price: 80,
    image: "https://images.unsplash.com/photo-1621996346565-9ddf30910b8e?w=400&h=300&fit=crop",
    category: "Pasta",
    isVeg: true,
    rating: 4.5,
    prepTime: "16 min"
  },
  {
    id: 29,
    name: "Peri Peri Mac N Cheese",
    description: "Spicy macaroni and cheese with peri peri seasoning",
    price: 90,
    image: "https://images.unsplash.com/photo-1621996346565-9ddf30910b8e?w=400&h=300&fit=crop",
    category: "Pasta",
    isVeg: true,
    rating: 4.5,
    prepTime: "16 min"
  },

  // ── ROLLS ──────────────────────────────────────────────────────────
  {
    id: 30,
    name: "Veg Roll",
    description: "Vegetable-filled roll",
    price: 70,
    image: "https://images.unsplash.com/photo-1599599810694-b5ac4dd97a2f?w=400&h=300&fit=crop",
    category: "Rolls",
    isVeg: true,
    rating: 4.3,
    prepTime: "12 min"
  },
  {
    id: 31,
    name: "Paneer Roll",
    description: "Paneer and vegetable-filled roll",
    price: 90,
    image: "https://images.unsplash.com/photo-1599599810694-b5ac4dd97a2f?w=400&h=300&fit=crop",
    category: "Rolls",
    isVeg: true,
    rating: 4.4,
    prepTime: "12 min"
  },
  {
    id: 32,
    name: "Egg Roll",
    description: "Scrambled egg and vegetable roll",
    price: 70,
    image: "https://images.unsplash.com/photo-1599599810694-b5ac4dd97a2f?w=400&h=300&fit=crop",
    category: "Rolls",
    isVeg: false,
    rating: 4.3,
    prepTime: "12 min"
  },
  {
    id: 33,
    name: "Chicken Roll",
    description: "Tender chicken and vegetable roll",
    price: 100,
    image: "https://images.unsplash.com/photo-1599599810694-b5ac4dd97a2f?w=400&h=300&fit=crop",
    category: "Rolls",
    isVeg: false,
    rating: 4.5,
    prepTime: "14 min"
  },
  {
    id: 34,
    name: "Peri Peri Chicken Roll",
    description: "Spicy peri peri flavored chicken roll",
    price: 100,
    image: "https://images.unsplash.com/photo-1599599810694-b5ac4dd97a2f?w=400&h=300&fit=crop",
    category: "Rolls",
    isVeg: false,
    rating: 4.6,
    prepTime: "14 min"
  },
  {
    id: 35,
    name: "BBQ Chicken Roll",
    description: "BBQ flavored chicken roll",
    price: 100,
    image: "https://images.unsplash.com/photo-1599599810694-b5ac4dd97a2f?w=400&h=300&fit=crop",
    category: "Rolls",
    isVeg: false,
    rating: 4.5,
    prepTime: "14 min"
  },

  // ── BURGER ──────────────────────────────────────────────────────────
  {
    id: 36,
    name: "Veg Burger",
    description: "Vegetables and paneer patty burger",
    price: 60,
    image: "https://images.unsplash.com/photo-1565066169537-bb4e98b434c0?w=400&h=300&fit=crop",
    category: "Burger",
    isVeg: true,
    rating: 4.3,
    prepTime: "12 min"
  },
  {
    id: 37,
    name: "Chicken Burger",
    description: "Tender chicken patty burger",
    price: 70,
    image: "https://images.unsplash.com/photo-1565066169537-bb4e98b434c0?w=400&h=300&fit=crop",
    category: "Burger",
    isVeg: false,
    rating: 4.5,
    prepTime: "13 min"
  },
  {
    id: 38,
    name: "Peri Peri Chicken Burger",
    description: "Spicy peri peri chicken burger",
    price: 90,
    image: "https://images.unsplash.com/photo-1565066169537-bb4e98b434c0?w=400&h=300&fit=crop",
    category: "Burger",
    isVeg: false,
    rating: 4.6,
    prepTime: "13 min"
  },
  {
    id: 39,
    name: "BBQ Chicken Burger",
    description: "BBQ flavored chicken burger",
    price: 90,
    image: "https://images.unsplash.com/photo-1565066169537-bb4e98b434c0?w=400&h=300&fit=crop",
    category: "Burger",
    isVeg: false,
    rating: 4.5,
    prepTime: "13 min"
  },
  {
    id: 40,
    name: "Vada Pav",
    description: "Spicy potato dumpling in bread",
    price: 30,
    image: "https://images.unsplash.com/photo-1599599810694-b5ac4dd97a2f?w=400&h=300&fit=crop",
    category: "Burger",
    isVeg: true,
    rating: 4.2,
    prepTime: "8 min"
  },
  {
    id: 41,
    name: "Bun Samosa",
    description: "Crispy samosa served in bread",
    price: 40,
    image: "https://images.unsplash.com/photo-1599599810694-b5ac4dd97a2f?w=400&h=300&fit=crop",
    category: "Burger",
    isVeg: true,
    rating: 4.3,
    prepTime: "8 min"
  },

  // ── MAGGI ──────────────────────────────────────────────────────────
  {
    id: 42,
    name: "Maggi Masala",
    description: "Plain Maggi noodles with masala",
    price: 35,
    image: "https://images.unsplash.com/photo-1633086965954-e37e5c1d4d0c?w=400&h=300&fit=crop",
    category: "Maggi",
    isVeg: true,
    rating: 4.1,
    prepTime: "5 min"
  },
  {
    id: 43,
    name: "Maggi Peri Peri",
    description: "Maggi with peri peri spice",
    price: 45,
    image: "https://images.unsplash.com/photo-1633086965954-e37e5c1d4d0c?w=400&h=300&fit=crop",
    category: "Maggi",
    isVeg: true,
    rating: 4.2,
    prepTime: "6 min"
  },
  {
    id: 44,
    name: "Maggi with Corn/Cheese",
    description: "Maggi with corn and cheese",
    price: 45,
    image: "https://images.unsplash.com/photo-1633086965954-e37e5c1d4d0c?w=400&h=300&fit=crop",
    category: "Maggi",
    isVeg: true,
    rating: 4.3,
    prepTime: "6 min"
  },
  {
    id: 45,
    name: "Maggi Extra Masala",
    description: "Maggi with extra masala and peri peri with cheese",
    price: 50,
    image: "https://images.unsplash.com/photo-1633086965954-e37e5c1d4d0c?w=400&h=300&fit=crop",
    category: "Maggi",
    isVeg: true,
    rating: 4.4,
    prepTime: "7 min"
  },

  // ── PIZZA ──────────────────────────────────────────────────────────
  {
    id: 46,
    name: "Cheesy Garlic Bread",
    description: "Garlic bread with melted cheese",
    price: 50,
    image: "https://images.unsplash.com/photo-1585238341710-4913968ba8f7?w=400&h=300&fit=crop",
    category: "Pizza & Bread",
    isVeg: true,
    rating: 4.4,
    prepTime: "8 min"
  },
  {
    id: 47,
    name: "Margherita Pizza",
    description: "Classic pizza with tomato, mozzarella and basil",
    price: 100,
    image: "https://images.unsplash.com/photo-1628840042765-356cda07f4ee?w=400&h=300&fit=crop",
    category: "Pizza & Bread",
    isVeg: true,
    rating: 4.5,
    prepTime: "18 min"
  },
  {
    id: 48,
    name: "Tandoori Paneer Pizza",
    description: "Pizza with tandoori paneer and peppers",
    price: 120,
    image: "https://images.unsplash.com/photo-1628840042765-356cda07f4ee?w=400&h=300&fit=crop",
    category: "Pizza & Bread",
    isVeg: true,
    rating: 4.6,
    prepTime: "20 min"
  },
  {
    id: 49,
    name: "Tandoori Mushroom Pizza",
    description: "Pizza with tandoori mushrooms and onions",
    price: 120,
    image: "https://images.unsplash.com/photo-1628840042765-356cda07f4ee?w=400&h=300&fit=crop",
    category: "Pizza & Bread",
    isVeg: true,
    rating: 4.5,
    prepTime: "20 min"
  },
  {
    id: 50,
    name: "Bread Paneer Pizza",
    description: "Pan-cooked bread pizza with paneer",
    price: 50,
    image: "https://images.unsplash.com/photo-1628840042765-356cda07f4ee?w=400&h=300&fit=crop",
    category: "Pizza & Bread",
    isVeg: true,
    rating: 4.3,
    prepTime: "10 min"
  },
  {
    id: 51,
    name: "Bread Mushroom Pizza",
    description: "Pan-cooked bread pizza with mushrooms",
    price: 50,
    image: "https://images.unsplash.com/photo-1628840042765-356cda07f4ee?w=400&h=300&fit=crop",
    category: "Pizza & Bread",
    isVeg: true,
    rating: 4.3,
    prepTime: "10 min"
  },

  // ── BEVERAGES ──────────────────────────────────────────────────────────
  {
    id: 52,
    name: "Coke",
    description: "Cold carbonated cola drink",
    price: 20,
    image: "https://images.unsplash.com/photo-1554866585-b92e5a1c0f5f?w=400&h=300&fit=crop",
    category: "Beverages",
    isVeg: true,
    rating: 4.2,
    prepTime: "2 min"
  },
  {
    id: 53,
    name: "Sprite",
    description: "Refreshing lemon-lime soda",
    price: 20,
    image: "https://images.unsplash.com/photo-1554866585-b92e5a1c0f5f?w=400&h=300&fit=crop",
    category: "Beverages",
    isVeg: true,
    rating: 4.1,
    prepTime: "2 min"
  },
  {
    id: 54,
    name: "Fanta",
    description: "Colorful fruity soda",
    price: 20,
    image: "https://images.unsplash.com/photo-1554866585-b92e5a1c0f5f?w=400&h=300&fit=crop",
    category: "Beverages",
    isVeg: true,
    rating: 4.1,
    prepTime: "2 min"
  },
  {
    id: 55,
    name: "Pepsi",
    description: "Cola drink",
    price: 20,
    image: "https://images.unsplash.com/photo-1554866585-b92e5a1c0f5f?w=400&h=300&fit=crop",
    category: "Beverages",
    isVeg: true,
    rating: 4.2,
    prepTime: "2 min"
  },
  {
    id: 56,
    name: "Mango Lassi",
    description: "Traditional yogurt-based mango drink",
    price: 80,
    image: "https://images.unsplash.com/photo-1590080876-c72e5f37b0c6?w=400&h=300&fit=crop",
    category: "Beverages",
    isVeg: true,
    rating: 4.6,
    prepTime: "5 min"
  },
  {
    id: 57,
    name: "Sweet Lassi",
    description: "Sweet yogurt drink",
    price: 50,
    image: "https://images.unsplash.com/photo-1590080876-c72e5f37b0c6?w=400&h=300&fit=crop",
    category: "Beverages",
    isVeg: true,
    rating: 4.5,
    prepTime: "5 min"
  },
  {
    id: 58,
    name: "Fresh Lime Juice",
    description: "Freshly squeezed lime juice",
    price: 25,
    image: "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=300&fit=crop",
    category: "Beverages",
    isVeg: true,
    rating: 4.4,
    prepTime: "3 min"
  },

  // ── DESSERTS ──────────────────────────────────────────────────────────
  {
    id: 59,
    name: "Gulab Jamun",
    // amazonq-ignore-next-line
    description: "Soft spongy balls in sugar syrup",
    price: 70,
    image: "https://images.unsplash.com/photo-1551632840-3b83ce93e72b?w=400&h=300&fit=crop",
    category: "Desserts",
    isVeg: true,
    rating: 4.7,
    prepTime: "5 min"
  },
  {
    id: 60,
    name: "Ice Cream - Vanilla",
    description: "Creamy vanilla ice cream",
    price: 50,
    image: "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop",
    category: "Desserts",
    isVeg: true,
    rating: 4.5,
    prepTime: "2 min"
  },
  {
    id: 61,
    name: "Ice Cream - Chocolate",
    description: "Rich chocolate ice cream",
    price: 50,
    image: "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop",
    category: "Desserts",
    isVeg: true,
    rating: 4.6,
    prepTime: "2 min"
  },
  {
    id: 62,
    name: "Strawberry Dolly",
    description: "Cold strawberry ice cream bar",
    price: 20,
    image: "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop",
    category: "Desserts",
    isVeg: true,
    rating: 4.3,
    prepTime: "2 min"
  },
  {
    id: 63,
    name: "Mango Dolly",
    description: "Cold mango ice cream bar",
    price: 20,
    image: "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop",
    category: "Desserts",
    isVeg: true,
    rating: 4.4,
    prepTime: "2 min"
  },
  {
    id: 64,
    name: "Chocolate Ice Cream Cone",
    description: "Chocolate ice cream in a crispy cone",
    price: 40,
    image: "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop",
    category: "Desserts",
    isVeg: true,
    rating: 4.5,
    prepTime: "2 min"
  },
  {
    id: 65,
    name: "Butterscotch Cone",
    description: "Butterscotch ice cream cone",
    price: 40,
    image: "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop",
    category: "Desserts",
    isVeg: true,
    rating: 4.5,
    prepTime: "2 min"
  },

];

export const rewards: Reward[] = [
  {
    id: 1,
    name: "Free Vada Pav",
    description: "Get a free Vada Pav — Mumbai's street food classic",
    pointsRequired: 50,
    image: "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400&h=300&fit=crop",
    category: "Food"
  },
  {
    id: 2,
    name: "Free Filter Coffee",
    description: "Redeem for a complimentary filter coffee or tea",
    pointsRequired: 30,
    image: "https://images.unsplash.com/photo-1593111774240-d529f12cf4bb?w=400&h=300&fit=crop",
    category: "Beverages"
  },
  {
    id: 3,
    name: "50% Off on Biryani",
    description: "Get 50% discount on any biryani of your choice",
    pointsRequired: 150,
    image: "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=400&h=300&fit=crop",
    category: "Discount"
  },
  {
    id: 4,
    name: "Free Maggi",
    description: "Enjoy a free Maggi Masala",
    pointsRequired: 60,
    image: "https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=400&h=300&fit=crop",
    category: "Food"
  },
  {
    id: 5,
    name: "₹50 Off on Orders",
    description: "Get ₹50 discount on orders above ₹200",
    pointsRequired: 100,
    image: "https://images.unsplash.com/photo-1597098494674-28a56a6a6d5c?w=400&h=300&fit=crop",
    category: "Discount"
  },
  {
    id: 6,
    name: "Free Kulfi",
    description: "Free Matka Kulfi — most popular ice cream on campus",
    pointsRequired: 80,
    image: "https://images.unsplash.com/photo-1576618148400-f54bed99fcfd?w=400&h=300&fit=crop",
    category: "Food"
  }
];

export const availableOrders: Order[] = [
  {
    id: "ORD001",
    items: [
      { item: menuItems[18], quantity: 1 },
      { item: menuItems[53], quantity: 1 }
    ],
    total: 190,
    status: "ready",
    timestamp: new Date(Date.now() - 10 * 60000),
    deliveryLocation: "Block A, Room 204",
    customerName: "Rahul Sharma",
    points: 19
  },
  {
    id: "ORD002",
    items: [
      { item: menuItems[2], quantity: 1 },
      { item: menuItems[46], quantity: 2 }
    ],
    total: 120,
    status: "ready",
    timestamp: new Date(Date.now() - 5 * 60000),
    deliveryLocation: "Block B, Room 101",
    customerName: "Priya Singh",
    points: 12
  },
  {
    id: "ORD003",
    items: [
      { item: menuItems[29], quantity: 1 }
    ],
    total: 100,
    status: "preparing",
    timestamp: new Date(Date.now() - 15 * 60000),
    deliveryLocation: "Library — 2nd Floor",
    customerName: "Aditya Kumar",
    points: 10
  }
];