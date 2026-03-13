# Trendcast — Sales Forecasting App

## Architecture

- **Frontend**: React + Vite (port 5000) — proxies `/api/*` to the backend
- **Backend**: FastAPI + Uvicorn (port 8000, internal only)
- **Auth & Database**: Firebase (Auth + Firestore)

## Workflows

- `Start application` — runs `npm run dev` (Vite dev server on port 5000)
- `Backend API` — runs `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

## Key Files

- `src/firebase.js` — Firebase app initialization (uses VITE_FIREBASE_* env vars)
- `src/page/AuthModal.jsx` — Firebase Auth context + login/signup modal
- `src/utils/api.js` — API helper with automatic Firebase token refresh
- `backend/api/firebase_admin_init.py` — Firebase Admin SDK init (uses FIREBASE_SERVICE_ACCOUNT secret)
- `backend/api/routes/auth.py` — Auth endpoints (signup, me, logout)
- `backend/api/routes/sales.py` — Sales data CRUD (Firestore `sales_data` collection)
- `backend/api/routes/forecasts.py` — Forecasting endpoints (SARIMA/Holt-Winters + Firestore `forecasts` collection)

## Environment Variables / Secrets

- `FIREBASE_SERVICE_ACCOUNT` — Full service account JSON for Firebase Admin SDK (backend)
- `VITE_FIREBASE_API_KEY` — Firebase web config (frontend)
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_FIREBASE_STORAGE_BUCKET`
- `VITE_FIREBASE_MESSAGING_SENDER_ID`
- `VITE_FIREBASE_APP_ID`

## Firebase Console Requirements

- **Authentication → Sign-in method**: Email/Password must be enabled
- **Firestore**: Collections used: `users`, `sales_data`, `forecasts`
- **Firestore rules**: Should allow authenticated users to read/write their own data

## Dependencies

### Python (backend)
- fastapi, uvicorn, firebase-admin, pandas, numpy, scikit-learn, statsmodels, scipy

### Node (frontend)
- react, vite, firebase, chart.js, react-chartjs-2, framer-motion, lucide-react, wouter
