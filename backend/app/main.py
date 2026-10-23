from __future__ import annotations

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.security_middleware import SecurityHeadersMiddleware, api_rate_limiter
from app.routers import search, analyze, compare, reports, auth
from app.routers.auth import get_current_user

app = FastAPI(
    title="Ecommerce Research API - Flamante Lab",
    version="1.0.0",
    description="Motor algorítmico de investigación de productos y detección de vacíos de mercado",
)

# 1. OWASP Top 10 Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 2. Strict CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 3. Rate Limiting Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    # Rate limit search, analyze, and compare endpoints to protect quotas and ML APIs
    if any(request.url.path.startswith(p) for p in ["/search", "/analyze", "/compare"]):
        allowed, retry_after = api_rate_limiter.check(client_ip)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": f"Límite de peticiones excedido. Reintenta en {retry_after} segundos."},
                headers={"Retry-After": str(retry_after)},
            )
    return await call_next(request)


# 4. Public and Protected Routers
app.include_router(auth.router)
app.include_router(search.router, dependencies=[Depends(get_current_user)])
app.include_router(analyze.router, dependencies=[Depends(get_current_user)])
app.include_router(compare.router, dependencies=[Depends(get_current_user)])
app.include_router(reports.router, dependencies=[Depends(get_current_user)])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ecommerce-research-api", "version": "1.0.0"}
