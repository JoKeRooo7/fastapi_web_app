import uvicorn
from fastapi import FastAPI
from settings import settings
from routers.product_router import router, database, redis_service
from contextlib import asynccontextmanager
# from services.redis_services import RedisService 



# @app.on_event("startup")
async def startup_event():
    redis_service.start()
    await redis_service.get_client()
    await redis_service.clear_all_rating_counts()
    await database.create_db()
    

# @app.on_event("shutdown")
async def shutdown_event():
    # await redis_service.clear_all_rating_counts()
    await redis_service.stop()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    yield
    await shutdown_event()

app = FastAPI(
    tittle = "Web-app",
    version="0.1.0",
    lifespan=lifespan
)


app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome! =)"}



if __name__ == "__main__":
    uvicorn.run(app, host=settings.UVICORN_HOST, port=settings.UVICORN_PORT)