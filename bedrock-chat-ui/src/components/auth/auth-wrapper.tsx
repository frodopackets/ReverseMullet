'use client'

import { useAuth } from '@/contexts/auth-context';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

interface AuthWrapperProps {
  children: React.ReactNode;
}

export function AuthWrapper({ children }: AuthWrapperProps) {
  const { isLoading } = useAuth();

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

  return (
    <Authenticator
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
    </Authenticator>
  );
}