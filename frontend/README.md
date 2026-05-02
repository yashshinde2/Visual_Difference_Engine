# Frontend

Development notes and how to connect to backend

- In development the Next.js config proxies requests under `/api/backend/*` to `http://localhost:8000/*` (see `next.config.mjs`). This allows the UI to call `/api/backend/api/image/analyze` without CORS issues.

- In production set `NEXT_PUBLIC_API_BASE` to your backend URL (e.g. `https://api.example.com`) and the frontend will call `${NEXT_PUBLIC_API_BASE}/api/image/analyze` or `/api/video/analyze` directly.

- Example .env file: copy `.env.example` and set `NEXT_PUBLIC_API_BASE`.

Run locally:

```powershell
cd frontend
pnpm install   # or npm install
pnpm dev       # or npm run dev
```

The UI upload component expects fields:
- `rgb_before` (file)
- `rgb_after` (file)
- optional `thermal_before` and `thermal_after`

The backend endpoints are:
- `GET /health`
- `POST /api/image/analyze` (multipart form)
- `POST /api/video/analyze` (multipart form)

If you want, I can also add example UI mappings for backend `outputs` static URLs once a result contains output file paths.
