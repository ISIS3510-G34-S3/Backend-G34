from fastapi import FastAPI
from fastapi_app.routes.auth import router as auth_router

app = FastAPI(title="Sustainable Travel API")

app.include_router(auth_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "FastAPI running"}
