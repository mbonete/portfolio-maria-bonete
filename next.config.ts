import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    formats: ["image/avif", "image/webp"],
    qualities: [65, 70, 75],
  },
  experimental: {
    optimizeCss: true,
  },
};

export default nextConfig;
