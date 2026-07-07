/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Standalone output is enabled only for the Docker image (see Dockerfile),
  // so that plain `npm run build && npm start` keeps working locally.
  output: process.env.NEXT_OUTPUT === 'standalone' ? 'standalone' : undefined,
  async redirects() {
    return [
      {
        source: '/',
        destination: '/overview',
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
