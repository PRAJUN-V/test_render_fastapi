# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import async_session, engine, Base
from models import User
from sqlalchemy import select

app = FastAPI()

# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def read_root():
    return {"message": "Hello from async FastAPI + PostgreSQL!"}

@app.get("/users/")
async def get_users(db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(User))
        return result.scalars().all()
