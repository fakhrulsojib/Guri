export interface User {
  id: string
  email: string
  email_verified: boolean
  name: string
  given_name: string
  family_name: string
  picture: string
  locale: string
  hd: string
  is_active: boolean
  created_at: string
  last_login: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
} 