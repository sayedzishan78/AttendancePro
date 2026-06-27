## Frontend (Vite + React)

This is the frontend for the Multiface Recognition app, built with Vite and React.

## Prerequisites

- Node.js 18+ and npm
- Backend running at `http://localhost:8000`

## Setup

```bash
npm install
```

## Run in Development

```bash
npm run dev -- --host
```

Vite will print the local URL in the terminal (default `http://localhost:5173`).

## Build for Production

```bash
npm run build
```

## Preview Production Build

```bash
npm run preview
```

## API Base URL

The frontend calls the backend via Axios. The base URL is determined in this order:

1. `localStorage["attendance_api_base"]` (if set)
2. `VITE_API_BASE_URL` (from your `.env` file)
3. Default: `http://localhost:8000/api`

If your backend is running elsewhere, you can set:

```bash
# in frontend/.env
VITE_API_BASE_URL=http://localhost:8000/api
```

Or override at runtime in the browser console:

```js
localStorage.setItem("attendance_api_base", "http://localhost:8000/api");
```

