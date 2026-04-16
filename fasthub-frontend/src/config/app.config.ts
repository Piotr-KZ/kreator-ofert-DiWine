export const APP_CONFIG = {
  // Branding
  name: "WebCreator",
  shortName: "WC",
  tagline: "Kreator Stron WWW",

  // Logo
  logo: {
    icon: "WC",
    gradient: "from-indigo-500 to-purple-600",
  },

  // URLs
  api: {
    baseUrl: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  },

  // Auth
  auth: {
    accessTokenExpireMinutes: 30,
    rememberMeKey: "remember_me",
    tokenKey: "access_token",
    refreshTokenKey: "refresh_token",
  },

  // Design tokens
  theme: {
    primaryColor: "#4F46E5",
    primaryHoverColor: "#4338CA",
    fontFamily: "'Outfit', system-ui, sans-serif",
  },
} as const;
