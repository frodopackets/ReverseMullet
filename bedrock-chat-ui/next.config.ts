import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable static export for Amplify deployment
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  experimental: {
    esmExternals: true
  },
  // Allow build to continue with ESLint warnings
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  }
};

export default nextConfig;
