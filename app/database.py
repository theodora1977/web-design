import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def resolve_database_url(database_url=None):
    selected_url = database_url or os.getenv('DATABASE_URL')

    if selected_url:
        if selected_url == 'sqlite:///./tailor.db' and (
            os.getenv('RENDER') or os.getenv('HEROKU') or os.getenv('RAILWAY') or os.getenv('PORT') or not os.access(os.getcwd(), os.W_OK)
        ):
            fallback_path = os.path.join(tempfile.gettempdir(), 'tailor.db')
            return f'sqlite:///{fallback_path}'
        return selected_url

    if os.getenv('RENDER') or os.getenv('HEROKU') or os.getenv('RAILWAY') or os.getenv('PORT'):
        fallback_path = os.path.join(tempfile.gettempdir(), 'tailor.db')
        return f'sqlite:///{fallback_path}'

    return 'sqlite:///./tailor.db'


DATABASE_URL = resolve_database_url()

connect_args = {}
if DATABASE_URL.startswith('sqlite'):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()