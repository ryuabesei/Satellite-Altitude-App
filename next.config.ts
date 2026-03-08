import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // In local development, you can optionally set BACKEND_URL (server-side only,
  // NOT NEXT_PUBLIC_) to proxy API calls to the Python FastAPI backend.
  // On Vercel, this env var should NOT be set — the built-in Next.js API route is used.
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL;
    if (backendUrl) {
      return [
        {
          source: "/api/altitude",
          destination: `${backendUrl}/altitude`,
        },
        {
          source: "/api/track",
          destination: `${backendUrl}/track`,
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
