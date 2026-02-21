/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true, // Required for static export
  },
  // Optional: if deploying to subdirectory
  // basePath: '/grapegeek',
  // assetPrefix: '/grapegeek',
}

module.exports = nextConfig
