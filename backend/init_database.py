from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from domain.database.data_model.User import User
from domain.database.database import Base, engine

user_input = input("你確定真的要重新初始化資料庫嗎？確定的話請打：「I'm really super clear what I'm doing」\n")
if user_input != "I'm really super clear what I'm doing":
    print("拒絕初始化資料庫")
    exit(0)

# connection = pymysql.connect(
#     host=Config.db["host"],
#     user=Config.db["admin"],
#     password=Config.db["password"],
#     db=Config.db["database"],
#     charset="utf8mb4",
# )

# cursor = connection.cursor()

# cursor.execute("DROP TABLE IF EXISTS Users;")
# connection.commit()

# cursor.execute(
#     "CREATE TABLE IF NOT EXISTS Users( \
#         account char(50) NOT NULL, \
#         password char(50) NOT NULL, \
#         salt varchar(50) NOT NULL, \
#         PRIMARY KEY (user_ID) \
#     );"
# )
# connection.commit()

Base.metadata.create_all(bind=engine)
