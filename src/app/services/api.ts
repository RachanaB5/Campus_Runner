const API_BASE_URL = 'http://localhost:5000/api';

// Export API_BASE_URL for use in other services
export { API_BASE_URL };

// Helper function to get token from localStorage
export const getToken = () => {
  return localStorage.getItem('access_token');
};

// Helper function to set token
export const setToken = (token: string) => {
  localStorage.setItem('access_token', token);
};

// Helper function to remove token
export const removeToken = () => {
  localStorage.removeItem('access_token');
};

// Make API request with token
const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const token = getToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Unauthorized - clear token
      removeToken();
      window.location.href = '/login';
    }
    const error = await response.json();
    throw new Error(error.error || 'API request failed');
  }

  return response.json();
};

// Auth API
export const authAPI = {
  register: async (data: { name: string; email: string; password: string; phone?: string }) => {
    return apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  login: async (email: string, password: string) => {
    return apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  getCurrentUser: async () => {
    return apiRequest('/auth/me', {
      method: 'GET',
    });
  },

  updateProfile: async (data: { name?: string; phone?: string; profile_image?: string }) => {
    return apiRequest('/auth/update-profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  logout: async () => {
    return apiRequest('/auth/logout', {
      method: 'POST',
    });
  },
};

// Menu API
export const menuAPI = {
  getAllFoods: async () => {
    return apiRequest('/menu/all');
  },

  searchFoods: async (query: string) => {
    return apiRequest(`/menu/search?q=${encodeURIComponent(query)}`);
  },

  getFoodsByCategory: async (category: string) => {
    return apiRequest(`/menu/category/${category}`);
  },

  getFoodDetail: async (foodId: string) => {
    return apiRequest(`/menu/${foodId}`);
  },

  // Admin operations
  addFood: async (data: any) => {
    return apiRequest('/menu/add', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  updateFood: async (foodId: string, data: any) => {
    return apiRequest(`/menu/items/${foodId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  deleteFood: async (foodId: string) => {
    return apiRequest(`/menu/items/${foodId}`, {
      method: 'DELETE',
    });
  },
};

// Rewards API
export const rewardsAPI = {
  getMyPoints: async () => {
    return apiRequest('/rewards/my-points');
  },

  getRewardTransactions: async () => {
    return apiRequest('/rewards/transactions');
  },

  redeemPoints: async (points: number) => {
    return apiRequest('/rewards/redeem', {
      method: 'POST',
      body: JSON.stringify({ points }),
    });
  },

  getAvailableRewards: async () => {
    return apiRequest('/rewards/available');
  },

  claimDailyBonus: async () => {
    return apiRequest('/rewards/claim-daily-bonus', {
      method: 'POST',
    });
  },
};

// Order API
export const orderAPI = {
  createOrder: async (data: {
    items: Array<{ food_id: string; quantity: number }>;
    delivery_address: string;
    special_instructions?: string;
    delivery_fee?: number;
    payment_method?: string;
  }) => {
    return apiRequest('/order/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  getMyOrders: async () => {
    return apiRequest('/order/my-orders');
  },

  getOrderDetail: async (orderId: string) => {
    return apiRequest(`/order/${orderId}`);
  },

  cancelOrder: async (orderId: string) => {
    return apiRequest(`/order/${orderId}/cancel`, {
      method: 'POST',
    });
  },

  confirmOrder: async (orderId: string) => {
    return apiRequest(`/order/${orderId}/confirm`, {
      method: 'POST',
    });
  },

  updateOrderStatus: async (orderId: string, status: string) => {
    return apiRequest(`/order/${orderId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  },
};

// Runner API
export const runnerAPI = {
  registerAsRunner: async (data: { vehicle_type: string; license_number: string }) => {
    return apiRequest('/runner/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  getRunnerProfile: async () => {
    return apiRequest('/runner/profile');
  },

  updateLocation: async (latitude: number, longitude: number) => {
    return apiRequest('/runner/update-location', {
      method: 'POST',
      body: JSON.stringify({ latitude, longitude }),
    });
  },

  toggleAvailability: async () => {
    return apiRequest('/runner/toggle-availability', {
      method: 'POST',
    });
  },

  // New order tracking endpoints
  getAvailableOrders: async () => {
    return apiRequest('/runner/available-orders');
  },

  pickupOrder: async (orderId: string) => {
    return apiRequest(`/runner/pickup-order/${orderId}`, {
      method: 'POST',
    });
  },

  markInTransit: async (orderId: string) => {
    return apiRequest(`/runner/mark-in-transit/${orderId}`, {
      method: 'POST',
    });
  },

  deliverOrder: async (orderId: string) => {
    return apiRequest(`/runner/deliver-order/${orderId}`, {
      method: 'POST',
    });
  },

  confirmDelivery: async (orderId: string, otp: string) => {
    return apiRequest(`/runner/confirm-delivery/${orderId}`, {
      method: 'POST',
      body: JSON.stringify({ otp }),
    });
  },

  // Legacy endpoints for backward compatibility
  getAvailableDeliveries: async () => {
    return apiRequest('/runner/available-deliveries');
  },

  acceptDelivery: async (deliveryId: string) => {
    return apiRequest(`/runner/accept-delivery/${deliveryId}`, {
      method: 'POST',
    });
  },

  getMyDeliveries: async () => {
    return apiRequest('/runner/my-deliveries');
  },

  updateDeliveryStatus: async (deliveryId: string, status: string) => {
    return apiRequest(`/runner/delivery/${deliveryId}/update-status`, {
      method: 'POST',
      body: JSON.stringify({ status }),
    });
  },

  rateDelivery: async (deliveryId: string, rating: number, review?: string) => {
    return apiRequest(`/runner/delivery/${deliveryId}/rate`, {
      method: 'POST',
      body: JSON.stringify({ rating, review }),
    });
  },
};

// Admin API
export const adminAPI = {
  getDashboardStats: async () => {
    return apiRequest('/admin/dashboard-stats');
  },

  getAllOrders: async (status?: string) => {
    let endpoint = '/admin/orders';
    if (status) {
      endpoint += `?status=${status}`;
    }
    return apiRequest(endpoint);
  },

  assignRunnerToOrder: async (orderId: string, runnerId: string) => {
    return apiRequest(`/admin/order/${orderId}/assign-runner`, {
      method: 'POST',
      body: JSON.stringify({ runner_id: runnerId }),
    });
  },

  markOrderReady: async (orderId: string) => {
    return apiRequest(`/admin/order/${orderId}/mark-ready`, {
      method: 'POST',
    });
  },

  getAllUsers: async (role?: string) => {
    let endpoint = '/admin/users';
    if (role) {
      endpoint += `?role=${role}`;
    }
    return apiRequest(endpoint);
  },

  updateUserRole: async (userId: string, role: string) => {
    return apiRequest(`/admin/user/${userId}/update-role`, {
      method: 'PUT',
      body: JSON.stringify({ role }),
    });
  },

  getFoodsInventory: async () => {
    return apiRequest('/admin/foods/inventory');
  },

  toggleFoodAvailability: async (foodId: string) => {
    return apiRequest(`/admin/food/${foodId}/toggle-availability`, {
      method: 'POST',
    });
  },

  getSalesReport: async () => {
    return apiRequest('/admin/reports/sales');
  },
};

// Cart API
export const cartAPI = {
  getCart: async () => {
    return apiRequest('/cart/get', {
      method: 'GET',
    });
  },

  addToCart: async (foodId: string, quantity: number) => {
    return apiRequest('/cart/add', {
      method: 'POST',
      body: JSON.stringify({ food_id: foodId, quantity }),
    });
  },

  updateCartItem: async (itemId: string, quantity: number) => {
    return apiRequest(`/cart/item/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify({ quantity }),
    });
  },

  removeFromCart: async (itemId: string) => {
    return apiRequest(`/cart/item/${itemId}`, {
      method: 'DELETE',
    });
  },

  clearCart: async () => {
    return apiRequest('/cart/clear', {
      method: 'DELETE',
    });
  },
};

// Combined API export for convenience
export const api = {
  // Export constants
  API_BASE_URL,
  getToken,
  setToken,
  removeToken,
  
  // Auth methods
  ...authAPI,
  
  // Menu methods
  getAllFoods: menuAPI.getAllFoods,
  searchFoods: menuAPI.searchFoods,
  getFoodsByCategory: menuAPI.getFoodsByCategory,
  getFoodDetail: menuAPI.getFoodDetail,
  addFood: menuAPI.addFood,
  updateFood: menuAPI.updateFood,
  deleteFood: menuAPI.deleteFood,
  
  // Order methods
  createOrder: orderAPI.createOrder,
  getMyOrders: orderAPI.getMyOrders,
  getOrderDetail: orderAPI.getOrderDetail,
  cancelOrder: orderAPI.cancelOrder,
  confirmOrder: orderAPI.confirmOrder,
  updateOrderStatus: orderAPI.updateOrderStatus,
  
  // Rewards methods
  getMyPoints: rewardsAPI.getMyPoints,
  getRewardTransactions: rewardsAPI.getRewardTransactions,
  redeemPoints: rewardsAPI.redeemPoints,
  getAvailableRewards: rewardsAPI.getAvailableRewards,
  claimDailyBonus: rewardsAPI.claimDailyBonus,
  
  // Runner methods
  registerAsRunner: runnerAPI.registerAsRunner,
  getRunnerProfile: runnerAPI.getRunnerProfile,
  updateLocation: runnerAPI.updateLocation,
  toggleRunnerAvailability: runnerAPI.toggleAvailability,
  getAvailableOrders: runnerAPI.getAvailableOrders,
  pickupOrder: runnerAPI.pickupOrder,
  markInTransit: runnerAPI.markInTransit,
  deliverOrder: runnerAPI.deliverOrder,
  confirmDelivery: runnerAPI.confirmDelivery,
  getAvailableDeliveries: runnerAPI.getAvailableDeliveries,
  acceptDelivery: runnerAPI.acceptDelivery,
  getMyDeliveries: runnerAPI.getMyDeliveries,
  updateDeliveryStatus: runnerAPI.updateDeliveryStatus,
  rateDelivery: runnerAPI.rateDelivery,
  
  // Admin methods
  getDashboardStats: adminAPI.getDashboardStats,
  getAllOrders: adminAPI.getAllOrders,
  assignRunnerToOrder: adminAPI.assignRunnerToOrder,
  markOrderReady: adminAPI.markOrderReady,
  getAllUsers: adminAPI.getAllUsers,
  updateUserRole: adminAPI.updateUserRole,
  getFoodsInventory: adminAPI.getFoodsInventory,
  toggleFoodAvailability: adminAPI.toggleFoodAvailability,
  getSalesReport: adminAPI.getSalesReport,
  
  // Cart methods
  getCart: cartAPI.getCart,
  addToCart: cartAPI.addToCart,
  updateCartItem: cartAPI.updateCartItem,
  removeFromCart: cartAPI.removeFromCart,
  clearCart: cartAPI.clearCart,
};
