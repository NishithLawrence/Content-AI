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

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
