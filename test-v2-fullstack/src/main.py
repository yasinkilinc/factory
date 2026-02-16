"""
user-service
Simple user management service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from user.routes import router as user_router


app = FastAPI(
    title="user-service",
    description="Simple user management service",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers

app.include_router(user_router, prefix="/user", tags=["user"])


@app.get("/")
async def root():
    return {"message": "user-service API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)