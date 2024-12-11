import os

class Settings:
    mongo_database_url = os.getenv("MONGO_DB_URL", "mongodb+srv://useradmin:ZOq5aUL56Z02sfUk@keepbookserverlessinsta.2zvtn.mongodb.net")
    mongo_database_name = os.getenv("MONGO_DB_NAME", "cco_WellnessWisdomBeta")

    mysql_host = os.getenv("MYSQL_HOST", "159.65.135.205")
    mysql_port = int(os.getenv("MYSQL_PORT", 3306))
    mysql_user = os.getenv("MYSQL_USER", "root")
    mysql_password = os.getenv("MYSQL_PASSWORD", "MacS3cur3P@Pssw0rd")
    mysql_db = os.getenv("MYSQL_DB", "health_blog_db")

    redis_url = os.getenv("REDIS_URL","redis://:77c7e379fec5ftg_3434@159.65.135.205:6379/0")

settings = Settings()
