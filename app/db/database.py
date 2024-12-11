from app.db.mysqldb import MySQLDB

# Initialize MongoDB and MySQL instances
mysql = MySQLDB()

async def connect_all():
    # Establish both MongoDB and MySQL connections
    await mysql.connect()

async def close_all():
    # Close both MongoDB and MySQL connections
    await mysql.close()
