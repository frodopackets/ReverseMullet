import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  // Disable server-side features for static export
  experimental: {
    esmExternals: true
  },
  // Allow build to continue with ESLint warnings
  eslint: {
    ignoreDuringBuilds: true, // Skip ESLint during builds
  },
  typescript: {
    ignoreBuildErrors: false, // Keep type checking
  }
};

export default nextConfig;
