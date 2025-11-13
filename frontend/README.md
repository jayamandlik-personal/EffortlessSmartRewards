# Effortless Frontend

React frontend for the Effortless Smart Rewards platform.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3000`

## Features

- **Dashboard**: Account summary, savings KPIs, rewards pie chart, AI insights
- **Transactions**: Full transaction history with reward status
- **Rewards**: Browse available rewards and Priceless experiences
- **Settings**: Configure preferences, notifications, and geo-location

## Components

- `Sidebar`: Navigation sidebar with Effortless branding
- `TopBar`: Header with user avatar and notifications
- `Dashboard`: Main dashboard with KPIs, charts, and insights
- `Transactions`: Transaction list/table view
- `Rewards`: Rewards catalog
- `Settings`: User preferences and settings

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`. The Vite proxy is configured to forward `/api/*` requests to the backend.

## Mock Authentication

Currently uses a hardcoded `MOCK_USER_ID = 1`. Replace with proper authentication in production.

