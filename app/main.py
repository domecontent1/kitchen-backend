# app/main.py
from fastapi import FastAPI

from app.routes import test
from app.routes import dishes

from app.routes import auth
from contextlib import asynccontextmanager
from app.core.database import database
from app.core.indexes import create_indexes
from app.routes import users
from app.routes import addresses
from app.routes import orders
from app.routes import dashboard
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):

    await database.command("ping")

    await create_indexes()

    yield


app = FastAPI(
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8100",
        "http://127.0.0.1:8100",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(test.router)
app.include_router(dishes.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(addresses.router)
app.include_router(orders.router)
app.include_router(dashboard.router)


@app.get("/")
def home():
    return {"message": "Kitchen API is running"}