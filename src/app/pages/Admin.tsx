import { useState, useEffect } from "react";
import { Trash2, Edit2, Plus, Package } from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router";

interface FoodItem {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  image_url: string;
  prep_time: number;
  available: boolean;
  is_veg: boolean;
  rating: number;
}

const DEFAULT_FOOD_IMAGES: Record<string, string> = {
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
  beverages: "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop",
  soda: "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop",
  lassi: "https://images.unsplash.com/photo-1582735689369-e68a7d48b69e?w=400&h=300&fit=crop",
  "milk shakes": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400&h=300&fit=crop",
  "ice cream": "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=400&h=300&fit=crop",
  desserts: "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop",
};

const FALLBACK_FOOD_IMAGE =
  "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop";

const getFoodImageUrl = (food: FoodItem) =>
  food.image_url?.trim() ||
  DEFAULT_FOOD_IMAGES[food.category?.trim().toLowerCase()] ||
  FALLBACK_FOOD_IMAGE;

export function Admin() {
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();
  const [isAdmin, setIsAdmin] = useState(false);
  const [foods, setFoods] = useState<FoodItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingFood, setEditingFood] = useState<FoodItem | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    price: 0,
    category: "Main Course",
    image_url: "",
    prep_time: 15,
    is_veg: true,
    available: true,
    rating: 4.5,
  });

  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/login");
      return;
    }
    fetchFoods();
  }, [isLoggedIn, navigate]);

  const fetchFoods = async () => {
    try {
      setIsLoading(true);
      const response = await api.getAllFoods();
      if (response && response.foods) {
        setFoods(response.foods);
        setIsAdmin(true);
      }
    } catch (error) {
      console.error("Error fetching foods or not authorized:", error);
      navigate("/");
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : type === "number" ? parseFloat(value) : value,
    });
  };

  const handleAddFood = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      const response = await api.addFood(formData);
      if (response && response.food) {
        setFoods([...foods, response.food]);
        resetForm();
        alert("Food item added successfully!");
      }
    } catch (error) {
      console.error("Error adding food:", error);
      alert("Failed to add food item. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateFood = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingFood) return;

    try {
      setIsSubmitting(true);
      const response = await api.updateFood(editingFood.id, formData);
      if (response && response.food) {
        setFoods(foods.map((f) => (f.id === editingFood.id ? response.food : f)));
        resetForm();
        alert("Food item updated successfully!");
      }
    } catch (error) {
      console.error("Error updating food:", error);
      alert("Failed to update food item. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteFood = async (foodId: string) => {
    if (!window.confirm("Are you sure you want to delete this item?")) return;

    try {
      setIsLoading(true);
      await api.deleteFood(foodId);
      setFoods(foods.filter((f) => f.id !== foodId));
      alert("Food item deleted successfully!");
    } catch (error) {
      console.error("Error deleting food:", error);
      alert(error instanceof Error ? error.message : "Failed to delete food item. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditFood = (food: FoodItem) => {
    setEditingFood(food);
    setFormData({
      name: food.name,
      description: food.description,
      price: food.price,
      category: food.category,
      image_url: food.image_url,
      prep_time: food.prep_time,
      is_veg: food.is_veg,
      available: food.available,
      rating: food.rating,
    });
    setShowForm(true);
  };

  const resetForm = () => {
    setFormData({
      name: "",
      description: "",
      price: 0,
      category: "Main Course",
      image_url: "",
      prep_time: 15,
      is_veg: true,
      available: true,
      rating: 4.5,
    });
    setEditingFood(null);
    setShowForm(false);
  };

  if (!isAdmin && !isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center">
        <h1 className="text-2xl text-gray-900 mb-4">Access Denied</h1>
        <p className="text-gray-600">You do not have permission to access this page.</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl text-gray-900 mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">Manage food items and menu</p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setShowForm(true);
          }}
          className="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          Add Food Item
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl text-gray-900 mb-6">
            {editingFood ? "Edit Food Item" : "Add New Food Item"}
          </h2>

          <form onSubmit={editingFood ? handleUpdateFood : handleAddFood} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-700 mb-2">Food Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  placeholder="e.g., Butter Chicken"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-700 mb-2">Price (₹) *</label>
                <input
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleInputChange}
                  required
                  step="0.01"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  placeholder="e.g., 250"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-700 mb-2">Category *</label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                >
                  <option>Main Course</option>
                  <option>Biryani</option>
                  <option>Starters</option>
                  <option>Beverages</option>
                  <option>Desserts</option>
                  <option>Breads</option>
                  <option>Rice & More</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-700 mb-2">Prep Time (minutes)</label>
                <input
                  type="number"
                  name="prep_time"
                  value={formData.prep_time}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  placeholder="e.g., 15"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm text-gray-700 mb-2">Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  placeholder="Item description..."
                  rows={3}
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm text-gray-700 mb-2">Image URL</label>
                <input
                  type="url"
                  name="image_url"
                  value={formData.image_url}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  placeholder="https://..."
                />
              </div>

              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    name="is_veg"
                    checked={formData.is_veg}
                    onChange={handleInputChange}
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-gray-700">Vegetarian</span>
                </label>
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 bg-orange-500 hover:bg-orange-600 text-white py-3 rounded-lg transition-colors disabled:opacity-50"
              >
                {isSubmitting
                  ? "Saving..."
                  : editingFood
                  ? "Update Food Item"
                  : "Add Food Item"}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-3 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-12">
          <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-600">Loading food items...</p>
        </div>
      ) : (
        <div>
          <h2 className="text-2xl text-gray-900 mb-6">Food Items ({foods.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {foods.map((food) => (
              <div key={food.id} className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden">
                <div className="h-40 bg-gray-200 relative">
                  <img
                    src={getFoodImageUrl(food)}
                    alt={food.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = FALLBACK_FOOD_IMAGE;
                    }}
                  />
                  <div className="absolute top-3 right-3 bg-white rounded-full px-3 py-1 shadow-lg">
                    <span className="text-sm font-semibold text-orange-600">₹{food.price}</span>
                  </div>
                </div>

                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">{food.name}</h3>
                      <p className="text-xs text-gray-500">{food.category}</p>
                    </div>
                    {food.is_veg && (
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                        Veg
                      </span>
                    )}
                  </div>

                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{food.description}</p>

                  <div className="flex items-center gap-2 mb-4 text-xs text-gray-600">
                    <span>{food.prep_time} min</span>
                    <span>•</span>
                    <span>⭐ {food.rating}</span>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEditFood(food)}
                      className="flex-1 flex items-center justify-center gap-2 bg-blue-50 hover:bg-blue-100 text-blue-600 py-2 rounded-lg transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteFood(food.id)}
                      className="flex-1 flex items-center justify-center gap-2 bg-red-50 hover:bg-red-100 text-red-600 py-2 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {foods.length === 0 && (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No food items yet</p>
              <p className="text-gray-400 text-sm mt-2">Start by adding your first food item</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
