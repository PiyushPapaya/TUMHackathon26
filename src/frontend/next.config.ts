import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Kein "N"-Badge des Dev-Servers unten links: Es landet sonst in Demo-Video und Screenshots.
  devIndicators: false,
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
