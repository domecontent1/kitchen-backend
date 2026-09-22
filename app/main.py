# backend/app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import database
from app.core.indexes import create_indexes
from app.routes import addresses, auth, dashboard, dishes, notifications, orders, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.command("ping")
    await create_indexes()
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8100",
        "http://127.0.0.1:8100"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(dishes.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(addresses.router)
app.include_router(orders.router)
app.include_router(dashboard.router)
app.include_router(notifications.router)


@app.get("/")
def home():
    return {"message": "Kitchen API is running"}