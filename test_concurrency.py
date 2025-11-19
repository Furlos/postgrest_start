import asyncio
import pytest
import os
from db import UserDB, Base

# Используем локальный PostgreSQL
DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"

@pytest.mark.asyncio
async def test_100_concurrent_creations():
    db = UserDB(DATABASE_URL)
    await db.init()

    # Очищаем таблицу перед тестом
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async def create_one(i):
        success = await db.create_user(f"user_{i}", f"user{i}@test.com")
        return success

    # Уменьшаем количество для теста (100 для начала)
    tasks = [create_one(i) for i in range(100)]
    results = await asyncio.gather(*tasks)

    successful_creations = sum(results)
    print(f"Успешных созданий: {successful_creations} из {len(results)}")

    # Проверяем количество пользователей в БД
    count = await db.count_users()
    print(f"Пользователей в БД: {count}")

    # Ожидаем, что все создания прошли успешно
    assert successful_creations == len(results), f"Не все создания успешны: {successful_creations}/{len(results)}"
    assert count == len(results), f"Количество в БД не совпадает: {count}/{len(results)}"

    print("100 одновременных созданий — УСПЕШНО!")
    await db.close()