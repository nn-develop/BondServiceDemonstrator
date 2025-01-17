import psycopg2
import os
import time
import subprocess
from psycopg2.extensions import connection
from dotenv import load_dotenv
from bond_service_demonstrator.logger import logger, setup_logging

load_dotenv()


class PostgresDatabaseManager:
    def __init__(self):
        """Initialize the database manager, ensuring all required environment variables are set."""
        self.user: str = self._get_env_variable("POSTGRES_USER")
        self.password: str = self._get_env_variable("POSTGRES_PASSWORD")
        self.host: str = self._get_env_variable("POSTGRES_HOST")
        self.port: str = self._get_env_variable("POSTGRES_PORT")
        self.dbname: str = self._get_env_variable("POSTGRES_DB")

    def _get_env_variable(self, var_name: str) -> str:
        """Retrieve an environment variable, raising an error if it is not set."""
        value: str | None = os.getenv(var_name)
        if not value:
            raise ValueError(
                f"Environment variable {var_name} is required but not set."
            )
        return value

    def connect_to_postgres(self, dbname: str) -> connection:
        """Connect to PostgreSQL database."""
        logger.debug(f"Attempting to connect to PostgreSQL database: {dbname}")
        return psycopg2.connect(
            dbname=dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

    def check_database_exists(self, cursor: psycopg2.extensions.cursor) -> bool:
        """Check if the database already exists."""
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.dbname}'")
        return cursor.fetchone() is not None

    def drop_database(self, cursor: psycopg2.extensions.cursor) -> None:
        """Drop the database if it exists."""
        logger.info(f"Dropping database '{self.dbname}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {self.dbname}")

    def create_database(self, cursor: psycopg2.extensions.cursor) -> None:
        """Create the database if it doesn't exist."""
        logger.info(f"Creating database '{self.dbname}'...")
        cursor.execute(f"CREATE DATABASE {self.dbname}")
        cursor.execute(
            f"GRANT ALL PRIVILEGES ON DATABASE {self.dbname} TO {self.user};"
        )

    def wait_for_postgres(self, timeout: int, delay: int = 5) -> bool:
        start_time: float = time.time()
        logger.info(f"Waiting for PostgreSQL server at {self.host}:{self.port}...")
        while time.time() - start_time < timeout:
            if (
                subprocess.run(
                    ["nc", "-zv", self.host, self.port],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                ).returncode
                == 0
            ):
                logger.info("PostgreSQL server is up!")
                return True
            time.sleep(delay)
        logger.error(
            f"PostgreSQL server did not become available after {timeout} seconds."
        )
        return False

    def run_django_migrations(self) -> None:
        """Run Django migrations (makemigrations and migrate)."""
        try:
            logger.info("Running Django migrations...")
            subprocess.run(["python", "manage.py", "makemigrations"], check=True)
            subprocess.run(["python", "manage.py", "migrate"], check=True)
            logger.info("Migrations completed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running migrations: {e}", exc_info=True)

    def manage_database(self, timeout: int = 40) -> None:
        """Main function to manage the PostgreSQL database."""
        if not self.wait_for_postgres(timeout):
            logger.error(
                f"Error: PostgreSQL server is not available after waiting for {timeout} seconds."
            )
            return

        try:
            conn: connection = self.connect_to_postgres("postgres")
            conn.autocommit = True
            cursor: psycopg2.extensions.cursor = conn.cursor()

            # Check if the database already exists
            if not self.check_database_exists(cursor):
                self.drop_database(cursor)
                self.create_database(cursor)
            else:
                logger.info(f"Database '{self.dbname}' already exists.")

            cursor.close()
            conn.close()

            # Connect to the newly created database
            conn = self.connect_to_postgres(self.dbname)
            cursor = conn.cursor()

            # After connecting to the database, run migrations
            self.run_django_migrations()

            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    # Initialize the logger before using it
    setup_logging()

    # Create an instance of PostgresDatabaseManager
    manager = PostgresDatabaseManager()

    # Call the function to manage the database
    manager.manage_database(timeout=40)
