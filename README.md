# Seva Setu

AI-powered smart resource allocation platform connecting NGOs, volunteers, and urgent community needs.

Seva Setu is wired as one app:

- `frontend`: React/Vite UI
- `backend`: Express API gateway, Supabase CRUD, and AI proxy
- `ai-service`: FastAPI services for priority, volunteer recommendations, request autofill, and fraud scoring

## Local run

1. Copy `backend/.env.example` to `backend/.env` and fill the Supabase values.
2. Start the AI services in separate terminals:

```bash
cd ai-service/priority-ai && uvicorn app:app --reload --port 8000
cd ai-service/task-recommend && uvicorn app:app --reload --port 8001
cd ai-service/request-autofill && uvicorn app:app --reload --port 8002
cd ai-service/fraud-detection && uvicorn app:app --reload --port 8003
```

3. Start the backend:

```bash
npm run backend:dev
```

4. Start the frontend:

```bash
npm run frontend:dev
```

The frontend calls `/api`, Vite proxies that to `http://localhost:5000`, and the backend talks to the AI services through the URLs in `backend/.env`.
