/** @type {import('next').NextConfig} */
const nextConfig = {
  devIndicators: false,
  // Proxy requests to the backend server
  async rewrites() {
    return [
      {
        source: "/chat",
        destination: "http://127.0.0.1:8000/chat",
      },
      {
        source: "/user/:path*",
        destination: "http://127.0.0.1:8000/user/:path*",
      },
      {
        source: "/customer/:path*",
        destination: "http://127.0.0.1:8000/customer/:path*",
      },
      {
        source: "/booking/:path*",
        destination: "http://127.0.0.1:8000/booking/:path*",
      },
    ];
  },
};

export default nextConfig;