import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.generate import router as generate_router
from app.api.regenerate import router as regenerate_router

app = FastAPI(
    title="AI Content Platform API",
    version="1.0.0",
    description="Backend API for AI Content Platform"
)

# Configure CORS origins from environment variable
cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]
if not cors_origins:
    cors_origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(generate_router, prefix="/api", tags=["Content Generation"])
app.include_router(regenerate_router, prefix="/api", tags=["Single Post Regeneration"])

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Content Platform API. Check /api/health for system status."}
