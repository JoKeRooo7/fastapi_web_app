import uvicorn
from fastapi import FastAPI
from settings import settings
from routers.product_router import router, database, redis_service
from services.redis_services import RedisService


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
    redis_service.start()
    await redis_service.get_client()
    await database.create_db()


@app.on_event("shutdown")
async def startup_event():
    await redis_service.clear_all_rating_counts()
    await redis_service.stop()


if __name__ == "__main__":
    uvicorn.run(app, host=settings.UVICORN_HOST, port=settings.UVICORN_PORT)