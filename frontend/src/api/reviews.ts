import apiClient from './client'

// Types
export interface Review {
  id: number
  restaurant_id: number
  author_id: number
  author_name: string
  food_rating: number
  service_rating: number
  ambience_rating: number
  location_rating: number
  value_rating: number
  dietary_rating: number
  cleanliness_rating: number
  overall_rating: number
  comment: string
  created_at: string
  updated_at: string
  is_flagged?: boolean
  moderation_status?: 'pending' | 'approved' | 'rejected'
}

export interface CreateReviewData {
  restaurant_id: number
  food_rating: number
  service_rating: number
  ambience_rating: number
  location_rating: number
  value_rating: number
  dietary_rating: number
  cleanliness_rating: number
  overall_rating: number
  comment: string
}

export interface UpdateReviewData extends Partial<CreateReviewData> {}

export interface ModerationReport {
  id: number
  review_id?: number
  user_id?: number
  reason: string
  details?: string
  created_at: string
  status: 'pending' | 'resolved'
}

export interface ReportReviewData {
  review_id: number
  reason: string
  details?: string
}

// Review API endpoints
export const reviewApi = {
  // Get reviews for a restaurant
  getReviews: async (restaurantId: number, params?: { limit?: number; offset?: number }) => {
    const { data } = await apiClient.get(`/api/restaurants/${restaurantId}/reviews/`, { params })
    return data
  },

  // Get single review
  getReview: async (reviewId: number): Promise<Review> => {
    const { data } = await apiClient.get(`/api/reviews/${reviewId}/`)
    return data
  },

  // Create review
  createReview: async (reviewData: CreateReviewData): Promise<Review> => {
    const { data } = await apiClient.post('/api/reviews/', reviewData)
    return data
  },

  // Update review
  updateReview: async (reviewId: number, updateData: UpdateReviewData): Promise<Review> => {
    const { data } = await apiClient.patch(`/api/reviews/${reviewId}/`, updateData)
    return data
  },

  // Delete review
  deleteReview: async (reviewId: number): Promise<void> => {
    await apiClient.delete(`/api/reviews/${reviewId}/`)
  },

  // Report review
  reportReview: async (reportData: ReportReviewData): Promise<ModerationReport> => {
    const { data } = await apiClient.post('/api/reviews/report/', reportData)
    return data
  },

  // Get user's reviews
  getUserReviews: async (params?: { limit?: number; offset?: number }) => {
    const { data } = await apiClient.get('/api/reviews/my-reviews/', { params })
    return data
  },
}

export default reviewApi
