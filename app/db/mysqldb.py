import aiomysql
import logging
from app.core.config import settings

class MySQLDB:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Establish connection pool to MySQL."""
        try:
            self.pool = await aiomysql.create_pool(
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password,
                db=settings.mysql_db,
                autocommit=True,
                minsize=1,
                maxsize=100,
                connect_timeout=10,  # Timeout for establishing a connection
            )
            logging.info(f"Connected to MySQL: {settings.mysql_db}")

            # Ensure tables and columns exist before proceeding
            await self.ensure_tables_exist()
        except Exception as e:
            logging.error(f"Failed to connect to MySQL: {e}")
            raise e

    async def close(self):
        """Close the MySQL connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logging.info("MySQL connection pool closed.")

    async def ensure_tables_exist(self):
        """Ensure necessary tables and columns exist in the database."""
        if not self.pool:
            raise RuntimeError("Connection pool is not initialized.")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Suppress warnings for table creation
                await cursor.execute("SET sql_notes = 0;")

                # Create categories table
                await cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id CHAR(36) PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    create_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    no_of_articles INT DEFAULT 0,
                    order_no INT DEFAULT 0,
                    icon_name VARCHAR(255) DEFAULT NULL
                );
                """)

                # Create subcategories table
                await cursor.execute("""
                CREATE TABLE IF NOT EXISTS subcategories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    category_id CHAR(36) NOT NULL,
                    create_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    no_of_articles INT DEFAULT 0,
                    order_no INT DEFAULT 0,
                    icon_name VARCHAR(255) DEFAULT NULL,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                );
                """)

                # Create articles table
                await self.ensure_article_table(cursor)

                # Ensure all required columns exist in the categories table
                await self.ensure_columns_exist(
                    cursor,
                    "categories",
                    {
                        "no_of_articles": "INT DEFAULT 0",
                        "order_no": "INT DEFAULT 0",
                        "create_date": "DATETIME DEFAULT CURRENT_TIMESTAMP",
                        "update_date": "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
                        "icon_name": "VARCHAR(255) DEFAULT NULL"
                    }
                )

                # Re-enable warnings
                await cursor.execute("SET sql_notes = 1;")

                logging.info("Ensured all necessary tables and columns exist.")

    async def ensure_article_table(self, cursor):
        """Ensure the articles table exists."""
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_articles (
            id CHAR(36) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            author VARCHAR(255) DEFAULT NULL,
            create_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            category_id CHAR(36) DEFAULT NULL,
            image_url VARCHAR(255) DEFAULT NULL,
            is_published BOOLEAN DEFAULT FALSE,
            views INT DEFAULT 0,
            tags JSON DEFAULT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        );
        """)
        logging.info("Ensured the 'news_articles' table exists.")

    async def ensure_columns_exist(self, cursor, table_name, required_columns):
        """Ensure required columns exist in a table."""
        # Fetch existing columns from the table
        await cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        existing_columns = [row[0] for row in await cursor.fetchall()]  # Column names in the table

        # Iterate through required columns and add missing ones
        for column_name, column_definition in required_columns.items():
            if column_name.strip("`") not in existing_columns:  # Remove backticks for consistent comparison
                logging.info(f"Adding missing column '{column_name}' to table '{table_name}'.")
                await cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition};")
            else:
                logging.info(f"Column '{column_name}' already exists in table '{table_name}'.")
