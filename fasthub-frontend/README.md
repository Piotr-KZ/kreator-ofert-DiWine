# FastHub Frontend

Modern React 18 + TypeScript frontend for FastHub SaaS Boilerplate.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework (custom UI components)
- **React Router** - Client-side routing
- **Zustand** - Lightweight state management
- **Axios** - HTTP client with interceptors
- **Recharts** - Composable charting library

## Project Structure

```
src/
├── api/                    # API client and endpoints
│   ├── client.ts          # Axios client with interceptors
│   ├── auth.ts            # Authentication endpoints
│   ├── users.ts           # Users CRUD endpoints
│   ├── billing.ts         # Billing & subscriptions
│   ├── organizations.ts   # Organization management
│   └── superadmin.ts      # SuperAdmin features
├── components/            # Reusable components
│   ├── ui/               # Custom Tailwind UI components
│   │   ├── Btn.tsx       # Button (primary/secondary/ghost/danger)
│   │   ├── Fld.tsx       # Form field with label/error
│   │   ├── SectionCard.tsx # Card container
│   │   ├── StatusBadge.tsx # Badge (success/warning/error/info)
│   │   ├── Tile.tsx      # Stat tile
│   │   ├── Rad.tsx       # Radio
│   │   ├── Chk.tsx       # Checkbox
│   │   ├── Toggle.tsx    # Toggle switch
│   │   └── Lbl.tsx       # Label
│   ├── shared/           # Shared components
│   │   ├── Modal.tsx     # Modal dialog
│   │   ├── EmptyState.tsx # Empty state placeholder
│   │   └── ErrorBoundary.tsx # Error boundary
│   ├── layout/           # Layout components
│   │   ├── AppShell.tsx  # Main responsive layout
│   │   ├── SidebarLayout.tsx # Sidebar layout
│   │   └── WizardLayout.tsx  # Wizard/step layout
│   ├── auth/             # Auth-related components
│   └── common/           # Common UI components
├── config/
│   └── app.config.ts     # Centralized app configuration
├── pages/                # Page components
│   ├── auth/            # Auth pages (Login, Register, etc.)
│   ├── superadmin/      # SuperAdmin pages
│   ├── DashboardPage.tsx
│   ├── UsersPage.tsx
│   ├── TeamPage.tsx
│   ├── BillingPage.tsx
│   └── SettingsPage.tsx
├── store/               # Zustand stores
│   ├── authStore.ts    # Authentication state
│   └── orgStore.ts     # Organization state
├── types/              # TypeScript types
│   └── models.ts       # Data models
├── App.tsx             # Root component
├── router.tsx          # Routes configuration
└── main.tsx            # Entry point
```

## Setup & Installation

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on `http://localhost:8000`

### Install Dependencies

```bash
npm install
```

### Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

### Development

```bash
npm run dev
```

Frontend will start on `http://localhost:3000`.

### Build for Production

```bash
npm run build
```

## UI Components

All UI components are custom-built with Tailwind CSS (no external UI library):

### `components/ui/` — Atomic Components

| Component | Description |
|-----------|-------------|
| `Btn` | Button with variants: primary, secondary, ghost, danger. Loading state. |
| `Fld` | Form field with label, error message, type support (text, email, password, select, textarea) |
| `SectionCard` | Card container with title and description |
| `StatusBadge` | Badge with variants: success, warning, error, info, neutral |
| `Tile` | Stat card with icon, value, label |
| `Rad`, `Chk`, `Toggle` | Radio, checkbox, toggle inputs |
| `Lbl` | Form label |

### `components/shared/` — Composite Components

| Component | Description |
|-----------|-------------|
| `Modal` | Fullscreen modal with header, body, footer |
| `EmptyState` | Empty state with icon, title, description, action |
| `ErrorBoundary` | React error boundary |

### `components/layout/` — Layout Components

| Component | Description |
|-----------|-------------|
| `AppShell` | Main app layout with sidebar, topbar, user menu |
| `SidebarLayout` | Sidebar + content layout |
| `WizardLayout` | Step-by-step wizard layout |

## Centralized Configuration

`src/config/app.config.ts` — single source of truth for:
- Product name, tagline, logo
- API base URL
- Auth settings (token keys, expiry)
- Theme tokens (colors, radius, spacing)

## Features

### Authentication
- Login with email/password
- Registration with organization setup
- Password reset flow
- Token refresh with automatic retry
- Protected routes with role-based access

### Dashboard
- Key metrics cards
- Growth charts (Line & Bar charts)
- Recent users list
- Role-specific views

### Users Management (SuperAdmin)
- Custom Tailwind table with pagination
- Search functionality
- Edit/delete user with modals

### Team Management
- Team members list
- Invite new members
- Role assignment

### Billing & Subscriptions
- Current subscription status
- Available plans
- Upgrade/downgrade
- Invoices table

### Settings
- Profile management
- Password change
- Organization details
- Billing address

### SuperAdmin
- System metrics dashboard with recharts
- Organizations management
- Stat cards with Tailwind

## Routing

### Public Routes
- `/login` - Login page
- `/register` - Registration page
- `/forgot-password` - Password reset request
- `/reset-password` - Password reset confirmation

### Protected Routes
- `/dashboard` - Main dashboard
- `/users` - Users management
- `/team` - Team management
- `/billing` - Billing & subscriptions
- `/settings` - User & organization settings

### SuperAdmin Routes
- `/superadmin/organizations` - Organizations list
- `/superadmin/metrics` - System metrics

## Dependencies

### Core
- react, react-dom, react-router-dom
- typescript

### UI & Styling
- tailwindcss (utility-first CSS)
- recharts (charts)

### State & Data
- zustand (state management)
- axios (HTTP client)

---

**Built with React 18 + TypeScript + Tailwind CSS**
