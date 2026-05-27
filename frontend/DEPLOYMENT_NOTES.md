# Deployment Notes

## Frontend

- Configure `VITE_API_URL` to the deployed FastAPI base URL.
- Optional: configure `VITE_API_TIMEOUT_MS` for request timeout tuning. The default is `12000`.
- Build with `npm run build`; deploy the generated `dist/` directory to a static host.
- The app uses browser routing, so the static host should fall back unknown paths to `index.html`.

## Backend

- Set `DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM`, and `JWT_EXPIRE_MINUTES` in the production environment.
- Run Alembic migrations before serving traffic: `alembic upgrade head`.
- Serve with a production ASGI process manager rather than `--reload`.
- Keep frontend CORS origins aligned with the production frontend URL.
