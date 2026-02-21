import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        brand: {
          DEFAULT: '#6B46C1',
          dark: '#3D3553',
          light: '#8B5CF6',
          soft: '#A5A5C8',
          hover: '#5B3BA8',
          active: '#4C328F',
        },
      },
      boxShadow: {
        'brand': '0 8px 20px rgba(34,40,49,0.06)',
        'brand-hover': '0 10px 24px rgba(34,40,49,0.08)',
        'brand-glow': '0 0 0 4px rgba(107,70,193,0.15)',
      },
    },
  },
  plugins: [],
};
export default config;
