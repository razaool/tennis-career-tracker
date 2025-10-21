# Tennis Career Tracker - Frontend

Modern React + TypeScript frontend for the Tennis Career Tracker application.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Lucide React** - Icons

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

## Project Structure

```
src/
├── pages/          # Page components
│   ├── HomePage.tsx
│   ├── RankingsPage.tsx
│   ├── PlayersPage.tsx
│   ├── PlayerDetailPage.tsx
│   └── PredictPage.tsx
├── lib/            # Utilities
│   └── api.ts      # API client and types
├── App.tsx         # Main app component with routing
└── main.tsx        # Entry point
```

## Features

- ✅ **Home Page** - Stat of the day, top 10 rankings, quick stats
- ✅ **Rankings Page** - Browse rankings by ELO, TSR, Glicko-2
- 🚧 **Players Page** - Search and browse players (coming soon)
- 🚧 **Player Detail** - Detailed player profiles (coming soon)
- 🚧 **Match Predictor** - Predict match outcomes (coming soon)

## API Integration

The frontend connects to the Tennis Career Tracker API at `http://localhost:8000`.

All API calls are made through the centralized `api.ts` client with TypeScript types.

## Development

```bash
# Start dev server
npm run dev

# Type check
npm run type-check

# Lint
npm run lint

# Build
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

## Dark Mode

The app is built with a dark theme by default, optimized for comfortable viewing during long coding sessions.

## Color Palette

- **Primary**: Blue (#0284c7)
- **Tennis Green**: #7FB800
- **Clay**: #D4876A (orange/brown)
- **Grass**: #7FB800 (green)
- **Hard Court**: #4A90E2 (blue)
