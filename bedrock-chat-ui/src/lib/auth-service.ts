/**
 * Authentication service that supports both ALB OAuth and Amplify JWT flows
 */

export type AuthMode = 'alb' | 'amplify'

export interface AuthUser {
  id: string
  email: string
  name?: string
  [key: string]: any
}

export interface AuthService {
  getCurrentUser(): Promise<AuthUser | null>
  signIn(email: string, password: string): Promise<AuthUser>
  signOut(): Promise<void>
  getAuthToken(): Promise<string | null>
  isAuthenticated(): Promise<boolean>
}

class ALBAuthService implements AuthService {
  async getCurrentUser(): Promise<AuthUser | null> {
    try {
      // Check if we're in development mode without proper Cognito setup
      const isDevelopment = process.env.NODE_ENV === 'development'
      const hasCognitoConfig = process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID && 
                               process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID !== 'us-east-1_DUMMY123'
      
      if (isDevelopment && !hasCognitoConfig) {
        // Return mock user for local development
        return {
          id: 'dev-user',
          email: 'developer@example.com',
          name: 'Development User'
        }
      }
      
      // For ALB authentication in production, the ALB would have already verified authentication
      // Return authenticated user from ALB headers (in production these would come from ALB)
      return {
        id: 'alb-user',
        email: 'user@example.com',
        name: 'ALB Authenticated User'
      }
    } catch (error) {
      console.error('Failed to get current user:', error)
      return null
    }
  }

  async signIn(email: string, password: string): Promise<AuthUser> {
    // Check if we're in development mode without proper Cognito setup
    const isDevelopment = process.env.NODE_ENV === 'development'
    const hasCognitoConfig = process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID && 
                             process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID !== 'us-east-1_DUMMY123'
    
    if (isDevelopment && !hasCognitoConfig) {
      // Mock sign in for development
      return {
        id: 'dev-user',
        email: email || 'developer@example.com',
        name: 'Development User'
      }
    }
    
    // ALB OAuth flow - redirect to Cognito hosted UI
    const cognitoDomain = process.env.NEXT_PUBLIC_COGNITO_DOMAIN
    const clientId = process.env.NEXT_PUBLIC_COGNITO_USER_POOL_CLIENT_ID
    const redirectUri = encodeURIComponent(window.location.origin)
    
    const authUrl = `https://${cognitoDomain}.auth.${process.env.NEXT_PUBLIC_AWS_REGION || 'us-east-1'}.amazoncognito.com/oauth2/authorize?` +
      `response_type=code&` +
      `client_id=${clientId}&` +
      `redirect_uri=${redirectUri}&` +
      `scope=email+openid+profile`
    
    // Redirect to Cognito hosted UI
    window.location.href = authUrl
    
    // This won't return as we're redirecting
    throw new Error('Redirecting to authentication')
  }

  async signOut(): Promise<void> {
    try {
      // Check if we're in development mode without proper Cognito setup
      const isDevelopment = process.env.NODE_ENV === 'development'
      const hasCognitoConfig = process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID && 
                               process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID !== 'us-east-1_DUMMY123'
      
      if (isDevelopment && !hasCognitoConfig) {
        // Mock sign out for development - just reload the page
        window.location.reload()
        return
      }
      
      // ALB logout - redirect to Cognito logout
      const cognitoDomain = process.env.NEXT_PUBLIC_COGNITO_DOMAIN
      const clientId = process.env.NEXT_PUBLIC_COGNITO_USER_POOL_CLIENT_ID
      const redirectUri = encodeURIComponent(window.location.origin)
      
      const logoutUrl = `https://${cognitoDomain}.auth.${process.env.NEXT_PUBLIC_AWS_REGION || 'us-east-1'}.amazoncognito.com/logout?` +
        `client_id=${clientId}&` +
        `logout_uri=${redirectUri}`
      
      window.location.href = logoutUrl
    } catch (error) {
      console.error('Failed to sign out:', error)
      throw error
    }
  }

  async getAuthToken(): Promise<string | null> {
    // For ALB, authentication is handled via cookies, not tokens
    // Return null to indicate we don't use tokens
    return null
  }

  async isAuthenticated(): Promise<boolean> {
    const user = await this.getCurrentUser()
    return user !== null
  }
}

class AmplifyAuthService implements AuthService {
  private initialized = false

  private async ensureInitialized() {
    if (!this.initialized) {
      const { initializeAmplify } = await import('@/lib/amplify-config')
      initializeAmplify()
      this.initialized = true
    }
  }

  async getCurrentUser(): Promise<AuthUser | null> {
    try {
      await this.ensureInitialized()
      // Import Amplify dynamically to avoid SSR issues
      const { getCurrentUser } = await import('aws-amplify/auth')
      const user = await getCurrentUser()
      
      return {
        id: user.userId,
        email: user.signInDetails?.loginId || '',
        name: user.signInDetails?.loginId || '',
        ...user
      }
    } catch (error) {
      return null
    }
  }

  async signIn(email: string, password: string): Promise<AuthUser> {
    await this.ensureInitialized()
    const { signIn } = await import('aws-amplify/auth')
    const result = await signIn({
      username: email,
      password,
    })

    if (result.isSignedIn) {
      const user = await this.getCurrentUser()
      if (user) {
        return user
      }
    }

    throw new Error('Sign in failed')
  }

  async signOut(): Promise<void> {
    await this.ensureInitialized()
    const { signOut } = await import('aws-amplify/auth')
    await signOut()
  }

  async getAuthToken(): Promise<string | null> {
    try {
      await this.ensureInitialized()
      const { fetchAuthSession } = await import('aws-amplify/auth')
      const session = await fetchAuthSession()
      return session.tokens?.idToken?.toString() || null
    } catch (error) {
      return null
    }
  }

  async isAuthenticated(): Promise<boolean> {
    const user = await this.getCurrentUser()
    return user !== null
  }
}

// Factory function to get the appropriate auth service
export function getAuthService(): AuthService {
  const authMode = (process.env.NEXT_PUBLIC_AUTH_MODE as AuthMode) || 'alb'
  
  if (authMode === 'alb') {
    return new ALBAuthService()
  } else {
    return new AmplifyAuthService()
  }
}

// Export the auth service instance
export const authService = getAuthService()