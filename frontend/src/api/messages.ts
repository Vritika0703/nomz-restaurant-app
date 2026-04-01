import apiClient from './client'

// Types
export interface Message {
  id: number
  conversation_id: number
  sender_id: number
  sender_name: string
  sender_role: 'diner' | 'restaurant'
  content: string
  created_at: string
  is_read: boolean
}

export interface Conversation {
  id: number
  diner_id: number
  diner_name: string
  restaurant_id: number
  restaurant_name: string
  last_message: string
  last_message_time: string
  unread_count: number
  created_at: string
  updated_at: string
}

export interface SendMessageData {
  conversation_id: number
  content: string
}

export interface StartConversationData {
  restaurant_id: number
  initial_message?: string
}

// Messaging API endpoints
export const messageApi = {
  // Get user's conversations
  getConversations: async (params?: { limit?: number; offset?: number }) => {
    const { data } = await apiClient.get('/api/messages/conversations/', { params })
    return data
  },

  // Get single conversation
  getConversation: async (conversationId: number): Promise<Conversation> => {
    const { data } = await apiClient.get(`/api/messages/conversations/${conversationId}/`)
    return data
  },

  // Get messages in a conversation
  getMessages: async (conversationId: number, params?: { limit?: number; offset?: number }) => {
    const { data } = await apiClient.get(`/api/messages/conversations/${conversationId}/messages/`, {
      params,
    })
    return data
  },

  // Start conversation
  startConversation: async (conversationData: StartConversationData): Promise<Conversation> => {
    const { data } = await apiClient.post('/api/messages/conversations/', conversationData)
    return data
  },

  // Send message
  sendMessage: async (conversationId: number, content: string): Promise<Message> => {
    const { data } = await apiClient.post(`/api/messages/conversations/${conversationId}/send/`, {
      content,
    })
    return data
  },

  // Mark conversation as read
  markAsRead: async (conversationId: number): Promise<void> => {
    await apiClient.patch(`/api/messages/conversations/${conversationId}/mark-read/`)
  },

  // Get unread count
  getUnreadCount: async (): Promise<{ count: number }> => {
    const { data } = await apiClient.get('/api/messages/unread-count/')
    return data
  },
}

export default messageApi
