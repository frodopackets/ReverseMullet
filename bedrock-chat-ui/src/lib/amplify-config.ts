// Amplify configuration - only used when NEXT_PUBLIC_AUTH_MODE is 'amplify'
const amplifyConfig = {
  Auth: {
    Cognito: {
      userPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID || '',
      userPoolClientId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_CLIENT_ID || '',
      loginWith: {
        email: true,
      },
      signUpVerificationMethod: 'code' as const,
      userAttributes: {
        email: {
          required: true,
        },
      },
      allowGuestAccess: false,
      passwordFormat: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireNumbers: true,
        requireSpecialCharacters: true,
      },
    },
  },
};

// Initialize Amplify only if using Amplify auth mode with proper configuration
export function initializeAmplify() {
  // Check if we have proper Cognito configuration
  const hasCognitoConfig = process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID && 
                           process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID !== 'us-east-1_DUMMY123' &&
                           process.env.NEXT_PUBLIC_COGNITO_USER_POOL_CLIENT_ID &&
                           process.env.NEXT_PUBLIC_COGNITO_USER_POOL_CLIENT_ID !== 'dummy-client-id-123456';
  
  if (process.env.NEXT_PUBLIC_AUTH_MODE === 'amplify' && hasCognitoConfig) {
    // Dynamic import to avoid loading Amplify when using ALB auth
    import('aws-amplify').then(({ Amplify }) => {
      // Add identityPoolId for the configuration to be valid
      const completeConfig = {
        ...amplifyConfig,
        Auth: {
          ...amplifyConfig.Auth,
          Cognito: {
            ...amplifyConfig.Auth.Cognito,
            identityPoolId: 'us-east-1:dummy-identity-pool-id' // Not used in user pool only mode
          }
        }
      };
      Amplify.configure(completeConfig);
    }).catch((error) => {
      console.warn('Failed to initialize Amplify:', error);
    });
  }
}

export default amplifyConfig;