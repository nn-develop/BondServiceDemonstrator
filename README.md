# Setup Instructions

## Prerequisites

- **Docker**
- **Docker Compose**

---

## Running the Project Using Docker Compose

### 1. Clone the Repository

First, clone the project to your local machine:

```bash
git clone https://github.com/nn-develop/BondServiceDemonstrator.git
cd BondServiceDemonstrator
```

### 2. Build and start the services

Use Docker Compose to build and run the containers for the project:

```bash
docker compose up --build
```
The `init_db.py` script automatically prepares the PostgreSQL database for use by:

    1. Ensuring all required environment variables are set.
    2. Waiting for the PostgreSQL server to become available.
    3. Creating the specified database if it does not already exist.
    4. Granting privileges to the configured user.
    5. Running Django migrations to set up the database schema.

This ensures the database is fully prepared and ready for the Django application.

To run the tests, use the following command:

```bash
docker compose exec web python manage.py test
```

The docker-compose.yml file defines the following services:

    web: The Django application.
    db: The PostgreSQL database.

### 3. Acces the application

- The Django application will be available at http://localhost:8000/
- The API documentation is available at http://localhost:8000/swagger/, providing an interactive interface to explore and test the API endpoints.