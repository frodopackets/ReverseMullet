'use client'

import { useAuth } from '@/contexts/auth-context';
import { useEffect, useState } from 'react';

interface AuthWrapperProps {
  children: React.ReactNode;
}

export function AuthWrapper({ children }: AuthWrapperProps) {
  const { isLoading, authMode } = useAuth();
  const [AmplifyAuthenticator, setAmplifyAuthenticator] = useState<any>(null);
  const [shouldUseAmplify, setShouldUseAmplify] = useState(false);
  
  useEffect(() => {
    // Determine if we should use Amplify auth
    const useAmplify = authMode === 'amplify' && 
                       typeof window !== 'undefined' &&
                       process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID &&
                       process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID !== 'us-east-1_DUMMY123';
    
    setShouldUseAmplify(!!useAmplify);
    
    // Only load Amplify Authenticator if we should use it
    if (useAmplify) {
      import('@aws-amplify/ui-react').then((module) => {
        setAmplifyAuthenticator(() => module.Authenticator);
      }).catch(err => {
        console.warn('Failed to load Amplify UI components:', err);
        setShouldUseAmplify(false);
      });
      // Styles import commented out for build
      // import('@aws-amplify/ui-react/styles.css').catch(() => {});
    }
  }, [authMode]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // For ALB auth, always bypass Amplify Authenticator
  if (authMode === 'alb' || !shouldUseAmplify) {
    return <>{children}</>;
  }

  // Use Amplify Authenticator for amplify auth mode with proper Cognito setup
  if (shouldUseAmplify && AmplifyAuthenticator) {
    return (
      <AmplifyAuthenticator
        hideSignUp={false}
        components={{
          Header() {
            return (
              <div className="text-center mb-6">
                <h1 className="text-2xl font-bold text-foreground mb-2">
                  AWS Bedrock Nova Lite Chat
                </h1>
                <p className="text-muted-foreground">
                  Sign in to access your AI chat assistant
                </p>
              </div>
            );
          },
        }}
        formFields={{
          signIn: {
            username: {
              placeholder: 'Enter your email',
              label: 'Email',
            },
          },
          signUp: {
            username: {
              placeholder: 'Enter your email',
              label: 'Email',
              order: 1,
            },
            password: {
              placeholder: 'Enter your password',
              label: 'Password',
              order: 2,
            },
            confirm_password: {
              placeholder: 'Confirm your password',
              label: 'Confirm Password',
              order: 3,
            },
          },
        }}
      >
        {children}
      </AmplifyAuthenticator>
    );
  }

  // Loading Amplify components
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-muted-foreground">Loading authentication...</p>
      </div>
    </div>
  );
}