import pymongo
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from domain.get_config import Config

CONFIG = Config.get_config()

engine = create_engine(
    f"mysql+pymysql://{CONFIG.sql_db['admin']}:{CONFIG.sql_db['password']}@{CONFIG.sql_db['host']}:{CONFIG.sql_db['port']}/{CONFIG.sql_db['database']}?charset=utf8mb4",
    pool_pre_ping=True,
)
Session = sessionmaker(bind=engine)
Base = declarative_base()

mongo_db_url = (
    f"mongodb://{CONFIG.mongo_db['admin']}:{CONFIG.mongo_db['password']}@"
    + f"{CONFIG.mongo_db['host']}:{CONFIG.mongo_db['port']}"
)

mongo_client = pymongo.MongoClient(mongo_db_url)
mongo_database = mongo_client["technical_order_editor_db"]
