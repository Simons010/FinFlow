/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./templates/**/*.html",
    "./static/**/*.html",
    "./static/**/*.js",
    "./**/*.html",
  ],
  safelist: [
    // Colors from custom variables
    'bg-custom-card',
    'bg-custom-accent',
    'bg-custom-destructive',
    'bg-custom-muted',
    'text-custom-accent',
    'text-custom-foreground',
    'text-custom-muted-foreground',
    'text-custom-destructive',
    'border-custom-border',
    // Responsive breakpoint variants
    'lg:hidden',
    'lg:block',
    'lg:w-64',
    'lg:flex-row',
    'lg:overflow-hidden',
    'lg:border-b-0',
    'lg:border-r',
    'md:',
    'sm:',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // Custom variables (non-conflicting namespace)
        'custom-border': "hsl(var(--tw-custom-border))",
        'custom-input': "hsl(var(--tw-custom-input))",
        'custom-ring': "hsl(var(--tw-custom-ring))",
        'custom-background': "hsl(var(--tw-custom-background))",
        'custom-foreground': "hsl(var(--tw-custom-foreground))",
        'custom-primary': {
          DEFAULT: "hsl(var(--tw-custom-primary))",
          foreground: "hsl(var(--tw-custom-primary-foreground))",
        },
        'custom-secondary': {
          DEFAULT: "hsl(var(--tw-custom-secondary))",
          foreground: "hsl(var(--tw-custom-secondary-foreground))",
        },
        'custom-destructive': {
          DEFAULT: "hsl(var(--tw-custom-destructive))",
          foreground: "hsl(var(--tw-custom-destructive-foreground))",
        },
        'custom-muted': {
          DEFAULT: "hsl(var(--tw-custom-muted))",
          foreground: "hsl(var(--tw-custom-muted-foreground))",
        },
        'custom-accent': {
          DEFAULT: "hsl(var(--tw-custom-accent))",
          foreground: "hsl(var(--tw-custom-accent-foreground))",
        },
        'custom-success': {
          DEFAULT: "hsl(var(--tw-custom-success))",
          foreground: "hsl(var(--tw-custom-success-foreground))",
        },
        'custom-warning': {
          DEFAULT: "hsl(var(--tw-custom-warning))",
          foreground: "hsl(var(--tw-custom-warning-foreground))",
        },
        'custom-popover': {
          DEFAULT: "hsl(var(--tw-custom-popover))",
          foreground: "hsl(var(--tw-custom-popover-foreground))",
        },
        'custom-card': {
          DEFAULT: "hsl(var(--tw-custom-card))",
          foreground: "hsl(var(--tw-custom-card-foreground))",
        },
        'custom-sidebar': {
          DEFAULT: "hsl(var(--tw-custom-sidebar-background))",
          foreground: "hsl(var(--tw-custom-sidebar-foreground))",
          primary: "hsl(var(--tw-custom-sidebar-primary))",
          "primary-foreground": "hsl(var(--tw-custom-sidebar-primary-foreground))",
          accent: "hsl(var(--tw-custom-sidebar-accent))",
          "accent-foreground": "hsl(var(--tw-custom-sidebar-accent-foreground))",
          border: "hsl(var(--tw-custom-sidebar-border))",
          ring: "hsl(var(--tw-custom-sidebar-ring))",
        },
        'custom-chart': {
          "1": "hsl(var(--tw-custom-chart-1))",
          "2": "hsl(var(--tw-custom-chart-2))",
          "3": "hsl(var(--tw-custom-chart-3))",
          "4": "hsl(var(--tw-custom-chart-4))",
          "5": "hsl(var(--tw-custom-chart-5))",
        },
      },
      borderRadius: {
        lg: "var(--tw-custom-radius)",
        md: "calc(var(--tw-custom-radius) - 2px)",
        sm: "calc(var(--tw-custom-radius) - 4px)",
      },
    },
  },
  plugins: [],
};