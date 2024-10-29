from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database_model.tables import Base
# DATABASE_URL = "sqlite:///app/database_model/my_database.db"

DATABASE_URL = "sqlite:///database_model/my_database.db"

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
