# AutoFlow Frontend

Modern React 19 + TypeScript frontend for AutoFlow SaaS Boilerplate.

## 🚀 Tech Stack

- **React 19** - Latest React with modern features
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Ant Design** - Enterprise-grade UI components
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Zustand** - Lightweight state management
- **Axios** - HTTP client with interceptors
- **Recharts** - Composable charting library

## 📁 Project Structure

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
│   ├── auth/             # Auth-related components
│   ├── layout/           # Layout components (AppLayout)
│   ├── common/           # Common UI components
│   └── tables/           # Table components
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

## 🔧 Setup & Installation

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

Frontend will start on `http://localhost:3000` (or 3001 if 3000 is occupied).

### Build for Production

```bash
npm run build
```

## 🎨 Features

### Authentication
- ✅ Login with email/password
- ✅ Registration with organization setup
- ✅ Password reset flow
- ✅ Token refresh with automatic retry
- ✅ Protected routes with role-based access

### Dashboard
- ✅ Key metrics cards (users, organizations, subscriptions, revenue)
- ✅ Growth charts (Line & Bar charts)
- ✅ Recent users list
- ✅ Role-specific views (SuperAdmin vs regular user)

### Users Management
- ✅ Users table with pagination
- ✅ Search functionality
- ✅ Edit user (name, email, role, position)
- ✅ Delete user with confirmation
- ✅ Role badges (SuperAdmin, Admin, User, Viewer)
- ✅ Status indicators (Active/Inactive, Verified)

### Team Management
- ✅ Team members list
- ✅ Invite new members (modal form)
- ✅ Role assignment
- ✅ Last login tracking

### Billing & Subscriptions
- ✅ Current subscription status
- ✅ Available plans (Free, Pro, Enterprise)
- ✅ Upgrade/downgrade functionality
- ✅ Cancel subscription
- ✅ Invoices table
- ✅ Download invoice PDF

### Settings
- ✅ Profile management (name, email, position)
- ✅ Password change
- ✅ Organization details
- ✅ Billing address
- ✅ Tabbed interface (Profile, Organization)

### SuperAdmin
- ✅ System metrics dashboard
- ✅ Organizations list
- ✅ Advanced charts (growth trends, plan distribution, revenue)
- ✅ Recent users monitoring

## 🔐 Authentication Flow

1. User logs in → receives `access_token` + `refresh_token`
2. Tokens stored in `localStorage`
3. `access_token` added to all API requests via Axios interceptor
4. On 401 error → automatic token refresh using `refresh_token`
5. If refresh fails → redirect to login

## 🎯 API Integration

### Axios Client (`src/api/client.ts`)

- Automatic token injection
- Token refresh on 401
- Error handling
- Base URL configuration

### API Modules

- `auth.ts` - Login, register, logout, password reset
- `users.ts` - Users CRUD operations
- `billing.ts` - Subscriptions and invoices
- `organizations.ts` - Organization management
- `superadmin.ts` - Admin metrics and stats

## 🧩 State Management

### Zustand Stores

**authStore** (`src/store/authStore.ts`)
- Current user
- Authentication status
- Login/logout actions
- Token management

**orgStore** (`src/store/orgStore.ts`)
- Current organization
- Update organization
- Organization state

## 🎨 Styling

### Ant Design Theme

Custom theme configuration in `App.tsx`:

```typescript
theme={{
  token: {
    colorPrimary: '#667eea',
    borderRadius: 6,
  },
}}
```

### Tailwind CSS

Configured with Ant Design compatibility:

```javascript
corePlugins: {
  preflight: false, // Don't conflict with Ant Design
}
```

## 🚦 Routing

### Public Routes
- `/login` - Login page
- `/register` - Registration page
- `/forgot-password` - Password reset request
- `/reset-password` - Password reset confirmation

### Protected Routes (require authentication)
- `/` - Redirects to `/dashboard`
- `/dashboard` - Main dashboard
- `/users` - Users management
- `/team` - Team management
- `/billing` - Billing & subscriptions
- `/settings` - User & organization settings

### SuperAdmin Routes (require `superadmin` role)
- `/superadmin/organizations` - Organizations list
- `/superadmin/metrics` - System metrics

## 📊 Charts & Visualizations

Using **Recharts** library:

- Line charts (growth trends)
- Bar charts (revenue)
- Pie charts (plan distribution)
- Responsive containers
- Custom tooltips and legends

## 🐛 Known Limitations

1. **Team Invite** - Backend `/team/invite` endpoint not implemented yet (shows placeholder message)
2. **Profile Update** - Backend `/users/me` PATCH endpoint not fully implemented (shows placeholder message)
3. **Google OAuth** - Not implemented in backend yet
4. **Organization Suspend** - Not implemented in backend yet

## 📝 Backend API Compatibility

Frontend is designed to work with FastAPI backend at `http://localhost:8000/api/v1`.

### Adjusted Endpoint Names

Some endpoints use adjusted names to match backend:

- `/auth/password-reset/request` (instead of `/auth/forgot-password`)
- `/auth/password-reset/confirm` (instead of `/auth/reset-password`)
- `/subscriptions/current` (instead of `/billing/subscription`)
- `/subscriptions/change-plan` (instead of `/billing/subscription/upgrade`)
- `/admin/stats` (instead of `/admin/metrics`)

## 🚀 Deployment

### Build

```bash
npm run build
```

Output in `dist/` directory.

### Serve

Use any static file server:

```bash
npm install -g serve
serve -s dist
```

Or deploy to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Nginx

### Environment Variables

Set `VITE_API_URL` to production API URL.

## 📦 Dependencies

### Core
- react@19.0.0
- react-dom@19.0.0
- react-router-dom@7.1.3
- typescript@5.6.2

### UI
- antd@5.23.6
- @ant-design/icons@5.5.2
- tailwindcss@4.0.0

### State & Data
- zustand@5.0.3
- axios@1.7.9
- recharts@2.15.0

---

**Built with ❤️ using React 19 + TypeScript + Ant Design**
