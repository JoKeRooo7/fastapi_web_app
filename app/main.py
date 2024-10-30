import uvicorn
from fastapi import FastAPI
from settings import settings
from database.create_database import create_db
from routers.user_registration import router

app = FastAPI(
    tittle = "Web-app",
    version="0.1.0"
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome! =)"}

@app.on_event("startup")
async def startup_event():
    await create_db()


if __name__ == "__main__":
    uvicorn.run(app, host=settings.uvicorn_host, port=settings.uvicorn_port)