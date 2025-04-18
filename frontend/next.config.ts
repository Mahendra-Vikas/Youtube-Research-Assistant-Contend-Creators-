import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  basePath: '',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: '/api/:path*',
      },
    ];
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3000',
  },
  images: {
    domains: ['i.ytimg.com', 'yt3.ggpht.com'],
  },
};

export default nextConfig;
