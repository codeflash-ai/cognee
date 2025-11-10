from uuid import UUID
from typing import Union

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from cognee.modules.data.methods import create_dataset

from cognee.infrastructure.databases.relational import get_relational_engine
from cognee.modules.data.methods import get_unique_dataset_id
from cognee.modules.users.models import DatasetDatabase
from cognee.modules.users.models import User
from functools import lru_cache


async def get_or_create_dataset_database(
    dataset: Union[str, UUID],
    user: User,
) -> DatasetDatabase:
    """
    Return the `DatasetDatabase` row for the given owner + dataset.

    • If the row already exists, it is fetched and returned.
    • Otherwise a new one is created atomically and returned.

    Parameters
    ----------
    user : User
        Principal that owns this dataset.
    dataset : Union[str, UUID]
        Dataset being linked.
    """
    db_engine = _get_relational_engine_cached()

    dataset_id = await get_unique_dataset_id(dataset, user)

    vector_db_name = f"{dataset_id}.lance.db"
    graph_db_name = f"{dataset_id}.pkl"

    async with db_engine.get_async_session() as session:
        # Try to fetch an existing row first
        stmt = select(DatasetDatabase).where(
            DatasetDatabase.owner_id == user.id,
            DatasetDatabase.dataset_id == dataset_id,
        )
        existing: DatasetDatabase = await session.scalar(stmt)
        if existing:
            return existing

        # If there are no existing rows build a new row

        # If it doesn't exist, create the Dataset if necessary (for string-named datasets)
        if isinstance(dataset, str):
            dataset = await create_dataset(dataset, user, session)

        # Build and commit the new DatasetDatabase record
        record = DatasetDatabase(
            owner_id=user.id,
            dataset_id=dataset_id,
            vector_database_name=vector_db_name,
            graph_database_name=graph_db_name,
        )

        try:
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record

        except IntegrityError:
            await session.rollback()
            raise


@lru_cache(maxsize=1)
def _get_relational_engine_cached():
    return get_relational_engine()
