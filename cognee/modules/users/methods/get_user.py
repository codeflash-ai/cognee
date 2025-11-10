from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import sqlalchemy.exc
from cognee.infrastructure.databases.relational import get_relational_engine
from cognee.infrastructure.databases.exceptions import EntityNotFoundError
from ..models import User
from functools import lru_cache


async def get_user(user_id: UUID):
    db_engine = _get_relational_engine_cached()

    async with db_engine.get_async_session() as session:
        user = (
            await session.execute(
                select(User)
                .options(selectinload(User.roles), selectinload(User.tenant))
                .where(User.id == user_id)
            )
        ).scalar()

        if not user:
            raise EntityNotFoundError(message=f"Could not find user: {user_id}")

        return user


@lru_cache(maxsize=1)
def _get_relational_engine_cached():
    return get_relational_engine()
