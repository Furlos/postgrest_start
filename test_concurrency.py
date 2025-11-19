# test_concurrency.py
import asyncio
import pytest
from db import UserDB, Base

# Укажи свой пароль или используй переменную окружения
DATABASE_URL = "YOUR_DATABASE_URL"

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

    # Запускаем 2000 одновременных созданий и ждем завершения
    tasks = [create_one(i) for i in range(10000)]
    results = await asyncio.gather(*tasks)  # ДОБАВЛЕНО: ожидание завершения всех задач

    # Проверяем, что все операции завершились успешно
    assert all(results), "Не все создания пользователей завершились успешно"

    # Проверяем, что в БД действительно 2000 пользователей
    count = await db.count_users()
    assert count == 10000

    print("10000 одновременных созданий — УСПЕШНО!")

    await db.close()