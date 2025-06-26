# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import async_session, engine, Base
from models import User
from schemas import UserCreate, UserResponse
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

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        # Create new user instance
        new_user = User(name=user.name)
        db.add(new_user)
        await db.flush()  # Flush to get the ID
        await db.refresh(new_user)  # Refresh to get the auto-generated ID
        return new_user
