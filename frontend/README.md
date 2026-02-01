# Transaction Ledger – Frontend

React + Vite + Tailwind CSS frontend for the Transaction Ledger app. Displays account summary (name, masked number, available/current balance) and the transaction ledger in list views.

## Run locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the dev server:
   ```bash
   npm run dev
   ```
   The app will be available at **http://localhost:5173** (or the port Vite prints).

## Environment

Optional `.env` in the frontend directory:

- **`VITE_API_URL`** – Backend API base URL (default: `http://localhost:8000`).
- **`VITE_ACCOUNT_ID`** – Account ID to load (default: `1`).

Copy `.env.example` to `.env` and adjust if needed. The app expects the backend to be running at the configured API URL (e.g. port 8000).

## Build

```bash
npm run build
```

Output is in `dist/`. Preview with `npm run preview`.
