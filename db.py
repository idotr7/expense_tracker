from sqlmodel import SQLModel, create_engine, Session
import os

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
DATABASE = os.getenv("DATABASE")

engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}/{DATABASE}")
    
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session