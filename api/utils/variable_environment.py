import os
class VarEnv:
    DBUSER = os.environ.get("DBUSER")
    DBPASSWORD = os.environ.get("DBPASSWORD")
    DBHOST = os.environ.get("DBHOST")
    DBNAME = os.environ.get("DBNAME")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    RABBITMQ_URL = os.environ.get("RABBITMQ_URL")
    MINIO_PUB = os.environ.get("MINIO_PUB")
    MINIO_PRI = os.environ.get("MINIO_PRI")
    MINIO_URL = os.environ.get("MINIO_URL")