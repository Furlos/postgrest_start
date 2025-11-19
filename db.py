# db.py
from sqlalchemy import Column, Integer, String, DateTime, func, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserDB:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=False)
        self.session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def init(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_user(self, username: str, email: str) -> bool:
        async with self.session() as s:
            async with s.begin():
                try:
                    s.add(User(username=username, email=email))
                    await s.commit()
                    return True
                except IntegrityError:
                    await s.rollback()
                    return False

    async def count_users(self) -> int:
        async with self.session() as s:
            result = await s.execute(select(func.count()).select_from(User))
            return result.scalar()

    async def close(self):
        await self.engine.dispose()