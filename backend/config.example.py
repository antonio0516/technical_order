class ProdConfig:
    sql_db = {
        "host": "db",
        "port": "3306",
        "database": "technical_order_editor_db",
        "admin": "root",
        "password": "",
    }
    jwt = {"exp": 999999, "secret_key": "secret"}  # hours
    mongo_db = {
        "host": "mongodb",
        "port": "27017",
        "admin": "root",
        "password": "",
    }


class DevConfig:
    sql_db = {
        "host": "localhost",
        "port": "3306",
        "database": "technical_order_editor_db",
        "admin": "root",
        "password": "",
    }
    jwt = {"exp": 999999, "secret_key": "secret"}  # hours
    mongo_db = {
        "host": "localhost",
        "port": "27017",
        "admin": "root",
        "password": "",
    }
