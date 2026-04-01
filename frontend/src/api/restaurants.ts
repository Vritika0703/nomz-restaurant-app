import apiClient from './client'

// Types
export interface Restaurant {
  id: number
  name: string
  address: string
  cuisine: string[]
  price_range: 1 | 2 | 3 | 4
  rating: number
  review_count: number
  phone?: string
  website?: string
  hours?: string
  latitude?: number
  longitude?: number
  owner_id?: number
  is_claimed?: boolean
  photos?: RestaurantPhoto[]
  inspection_grade?: string
  health_score?: number
}

export interface RestaurantPhoto {
  id: number
  restaurant_id: number
  image: string
  is_primary: boolean
  created_at: string
}

export interface RestaurantSearchParams {
  query?: string
  cuisine?: string[]
  price_range?: number
  neighborhood?: string
  dietary_restrictions?: string[]
  sort_by?: 'rating' | 'name' | 'review_count' | 'distance'
  limit?: number
  offset?: number
}

export interface MapData {
  id: number
  name: string
  latitude: number
  longitude: number
  rating: number
  cuisine: string[]
  price_range: number
}

export interface CreateRestaurantData {
  name: string
  address: string
  phone?: string
  website?: string
  cuisine: string[]
  price_range: 1 | 2 | 3 | 4
}

export interface UpdateRestaurantData extends Partial<CreateRestaurantData> {
  description?: string
  hours?: string
}

// Restaurant API endpoints
export const restaurantApi = {
  // Get restaurant list with filters
  listRestaurants: async (params?: RestaurantSearchParams) => {
    const { data } = await apiClient.get('/api/restaurants/', { params })
    return data
  },

  // Get single restaurant
  getRestaurant: async (id: number): Promise<Restaurant> => {
    const { data } = await apiClient.get(`/api/restaurants/${id}/`)
    return data
  },

  // Search restaurants
  searchRestaurants: async (params: RestaurantSearchParams) => {
    const { data } = await apiClient.get('/api/restaurants/search/', { params })
    return data
  },

  // Get map data (advanced filtering)
  getMapData: async (filters?: Record<string, unknown>) => {
    const { data } = await apiClient.get('/api/restaurants/map-data/', { params: filters })
    return data as MapData[]
  },

  // Create new restaurant (owner only)
  createRestaurant: async (restaurantData: CreateRestaurantData): Promise<Restaurant> => {
    const { data } = await apiClient.post('/api/restaurants/', restaurantData)
    return data
  },

  // Update restaurant (owner/admin only)
  updateRestaurant: async (id: number, updateData: UpdateRestaurantData): Promise<Restaurant> => {
    const { data } = await apiClient.put(`/api/restaurants/${id}/`, updateData)
    return data
  },

  // Delete restaurant (admin only)
  deleteRestaurant: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/restaurants/${id}/`)
  },

  // Get restaurant photos
  getPhotos: async (restaurantId: number): Promise<RestaurantPhoto[]> => {
    const { data } = await apiClient.get(`/api/restaurants/${restaurantId}/photos/`)
    return data
  },

  // Upload photo
  uploadPhoto: async (restaurantId: number, image: File): Promise<RestaurantPhoto> => {
    const formData = new FormData()
    formData.append('image', image)
    const { data } = await apiClient.post(`/api/restaurants/${restaurantId}/photos/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  // Set primary photo
  setPrimaryPhoto: async (restaurantId: number, photoId: number): Promise<RestaurantPhoto> => {
    const { data } = await apiClient.patch(`/api/restaurants/${restaurantId}/photos/${photoId}/set-primary/`)
    return data
  },

  // Delete photo
  deletePhoto: async (restaurantId: number, photoId: number): Promise<void> => {
    await apiClient.delete(`/api/restaurants/${restaurantId}/photos/${photoId}/`)
  },

  // Claim restaurant
  claimRestaurant: async (restaurantId: number): Promise<{ detail: string }> => {
    const { data } = await apiClient.post('/api/restaurants/claims/', {
      restaurant_id: restaurantId,
    })
    return data
  },

  // Get restaurant availability
  getAvailability: async (restaurantId: number) => {
    const { data } = await apiClient.get(`/api/restaurants/${restaurantId}/availability/`)
    return data
  },

  // Update restaurant availability
  updateAvailability: async (restaurantId: number, availability: Record<string, unknown>) => {
    const { data } = await apiClient.put(`/api/restaurants/${restaurantId}/availability/`, availability)
    return data
  },
}

export default restaurantApi
