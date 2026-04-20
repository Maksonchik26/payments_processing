from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings


DATABASE_URL = settings.database_url

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)
Base = declarative_base()

async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False,
)

async def get_async_session() -> AsyncSession:
    """
    Return a new database session to use in FastAPI dependency.

    Returns:
        Session: A new database session.

    """
    async with async_session() as session:
        yield session


class UpdateMixin:
    """
    Mixin class providing functionality to update entity attributes dynamically.

    Methods:
        - update_entity: Update entity attributes dynamically.
    """

    def update_entity(self, **kwargs):
        """
        Update entity attributes dynamically.

        Args:
            **kwargs: Arbitrary keyword arguments representing entity attribute names and values.
        """
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
