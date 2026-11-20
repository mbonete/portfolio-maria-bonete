import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Dev only: lets a phone on the local network load the dev scripts, so the page hydrates there.
  allowedDevOrigins: ["10.1.5.124", "10.1.1.4"],
  images: {
    formats: ["image/avif", "image/webp"],
    qualities: [65, 70, 75, 90],
  },
};

export default nextConfig;
