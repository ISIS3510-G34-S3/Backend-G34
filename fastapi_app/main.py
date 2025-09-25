from fastapi import FastAPI

from fastapi_app import auth

app = FastAPI(title="Sustainable Travel API")

app.include_router(auth.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "FastAPI running"}
