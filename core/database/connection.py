from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import db_settings

DEFAULT_URL = f"postgresql+asyncpg://{db_settings.DB_USER}:{db_settings.DB_PASSWORD}@{db_settings.DB_HOST}:5432/{db_settings.DB_NAME}"
use_cloud_sql_socket = bool(db_settings.CLOUD_SQL_CONNECTION_NAME)

if use_cloud_sql_socket:
    database_url = f"postgresql+asyncpg://{db_settings.DB_USER}:{db_settings.DB_PASSWORD}@127.0.0.1:5432/{db_settings.DB_NAME}"
else:
    database_url = db_settings.DATABASE_URL or DEFAULT_URL

async_database_url = database_url

engine = create_async_engine(
    async_database_url,
    pool_size=3,
    max_overflow=12,
    pool_pre_ping=True,
    pool_recycle=180,
    pool_timeout=2,
    echo_pool=False,
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()
