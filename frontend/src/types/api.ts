export type UserRole = 'customer' | 'support_agent' | 'admin'

export interface User {
  id: number
  name: string
  email: string
  role: UserRole
  created_at: string
}

export interface AuthResponse {
  access_token: string
  refresh_token?: string
  token_type: string
  user: User
}

export interface PasswordResetResponse {
  message: string
  email_sent: boolean
  dev_reset_url?: string | null
}

export type TicketStatus = 'open' | 'in_progress' | 'resolved' | 'closed'
export type TicketPriority = 'low' | 'medium' | 'high'

export interface Ticket {
  id: number
  title: string
  description: string
  status: TicketStatus
  priority: TicketPriority
  customer_id: number
  assigned_agent_id: number | null
  sentiment?: string | null
  ai_reply?: string | null
  is_escalated?: boolean
  category?: string | null
  urgency_score?: number
  sla_tag?: string | null
  smart_labels?: string | null
  created_at: string
  updated_at: string | null
}

export interface TicketPageData {
  items: Ticket[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface TicketListResponse {
  success: boolean
  data: TicketPageData
}

export type TicketSortOption = 'newest' | 'oldest' | 'priority' | 'status'

export interface TicketQueryParams {
  page?: number
  limit?: number
  search?: string
  status?: TicketStatus | ''
  priority?: TicketPriority | ''
  sentiment?: string
  assigned_agent_id?: number | ''
  sort?: TicketSortOption
}

export type ChatSender = 'user' | 'assistant'

export interface ChatMessage {
  id: number
  conversation_id: number
  sender: ChatSender
  content: string
  created_at: string
}

export interface ConversationSummary {
  id: number
  title: string
  user_id: number
  created_at: string
  updated_at: string | null
}

export interface ConversationDetail extends ConversationSummary {
  messages: ChatMessage[]
}

export interface ChatSendResponse {
  conversation: ConversationSummary
  user_message: ChatMessage
  ai_message: ChatMessage
}

export interface KnowledgeDocument {
  id: number
  filename: string
  content_type: string
  file_size: number
  text_length: number
  chunk_count: number
  uploaded_by_id: number
  created_at: string
}

export interface Lead {
  id: number
  name: string
  email: string
  phone: string
  source: string
  matched_keyword: string | null
  source_message: string | null
  followup_sent: boolean
  captured_by_user_id: number | null
  created_at: string
}

export interface LeadAnalytics {
  total: number
  today: number
  followups_sent: number
  conversion_rate: number
}

export interface LeadPageData {
  items: Lead[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface LeadCreatePayload {
  name: string
  email: string
  phone: string
  source?: string
  matched_keyword?: string | null
  source_message?: string | null
}
