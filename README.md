# Inventory Management API

**A RESTful Backend Application built with FastAPI, SQLite, and Docker**

## Project Overview

The Inventory Management API is a backend application developed using Python and FastAPI to manage inventory records through RESTful HTTP endpoints. Each inventory item contains a unique identifier, a name, and a quantity. The application supports creating new items, retrieving existing records, updating inventory information, and deleting items when they are no longer required.

This project was developed incrementally through three connected assignment stages. The first stage established the API and its CRUD functionality. The second stage introduced SQLite to provide persistent data storage. The third stage focused on containerizing the application with Docker and configuring persistent database storage through Docker Compose.

Together, these stages demonstrate the development of a backend application from API design to database integration and containerized execution. The project also provides practical experience with request validation, HTTP status codes, environment-based configuration, SQL operations, application startup, and data persistence.

## Project Objectives

The primary objective of this project is to build a reliable inventory management backend with a clear separation between the API interface and the underlying data storage. FastAPI handles incoming HTTP requests and generates API documentation, Pydantic validates the data submitted by clients, and SQLite stores inventory records persistently. Docker packages the application and its dependencies into a reproducible runtime environment.

The project follows an incremental development approach. Each assignment extends the previous implementation rather than creating an unrelated application. The same Inventory Management API is carried forward while its storage and deployment capabilities are improved.

## Technology Stack

| Technology | Role in the Project |
|---|---|
| Python | Implements the application logic and database operations. |
| FastAPI | Defines the REST endpoints and handles HTTP requests and responses. |
| Pydantic | Validates incoming inventory data and defines data models. |
| Uvicorn | Runs the FastAPI application as an ASGI server. |
| SQLite | Stores inventory records in a relational database file. |
| SQL | Supports database creation and CRUD operations on inventory records. |
| Docker | Packages the application and its runtime dependencies. |
| Docker Compose | Configures the container, environment variables, port mapping, and persistent storage. |
| Git and GitHub | Maintain version history and host the source code. |
| Swagger UI | Provides interactive API documentation and endpoint testing. |

## Assignment 1 — Developing the Inventory CRUD API

The first assignment established the foundation of the project by implementing a RESTful API using FastAPI. The focus was on understanding how a backend application receives requests, processes input, performs CRUD operations, and returns appropriate HTTP responses.

The API exposes endpoints for creating, reading, updating, and deleting inventory items. Each item is represented by an ID, a name, and a quantity. Pydantic models validate incoming data, while FastAPI provides request handling, error responses, and automatically generated API documentation.

The root endpoint, `/`, provides a basic response confirming that the application is available. The `/health` endpoint provides a simple health check. The inventory endpoints support operations on the collection of items and on individual records.

The initial stage focused on API behavior and request handling. It established the routes and validation rules that would continue to be used when the application was connected to a database in the next assignment.

### Understanding CRUD Operations

CRUD stands for Create, Read, Update, and Delete. These four operations form the core of the Inventory Management API.

The Create operation uses the `POST /items` endpoint to add a new inventory item. The request body contains the item's name and quantity. After validating the input, the application creates the record and returns the item, including its generated ID.

The Read operation uses `GET /items` to retrieve the inventory collection and `GET /items/{item_id}` to retrieve a particular item. The collection endpoint returns the available inventory records, while the item-specific endpoint looks up a record using its ID.

The Update operation uses `PUT /items/{item_id}` to modify an existing inventory item. The request supplies the updated name and quantity. If the specified item exists, the API updates the record and returns the updated item.

The Delete operation uses `DELETE /items/{item_id}` to remove a particular inventory item. When the operation succeeds, the API returns `204 No Content`, indicating that the deletion was successful and no response body is required.

These operations form the functional foundation of the project and remain central to the database-backed implementation.

## Assignment 2 — Connecting the API to SQLite

The second assignment extended the existing Inventory Management API by introducing persistent database storage. Instead of keeping inventory records only in application memory, the application uses SQLite to store them in a database file named `inventory.db`.

SQLite is a lightweight relational database that works directly with a database file. Python's built-in `sqlite3` module provides the connection and SQL execution functionality, so a separate database server is not required.

### Database Structure

The database contains an `items` table with three columns: `id`, `name`, and `quantity`.

| Column | Purpose |
|---|---|
| `id` | An auto-incrementing primary key that uniquely identifies each inventory item. |
| `name` | A required text field containing the inventory item's name. |
| `quantity` | A required integer representing the available stock quantity. |

The table definition uses a primary key for record identification, a `NOT NULL` constraint for required fields, and a database-level check to prevent negative quantities.

When the application initializes, it creates the table if it does not already exist. The initialization logic also inserts sample inventory records when the table is empty. This provides initial data for development and testing without repeatedly inserting seed records into an already populated database.

### Database Integration and API Behavior

The application uses database connections and SQL queries to retrieve and modify inventory records. The GET endpoints read data from SQLite, POST inserts new records, PUT updates existing records, and DELETE removes records.

The API continues to expose the same general HTTP interface established in Assignment 1. The difference is that the records are now stored in a database rather than existing only in memory. This allows the application to retain its inventory data after the API process restarts, provided the database file remains available.

The application also uses a configurable database path. The `DATABASE_PATH` environment variable determines where the database connection opens the SQLite file. When the variable is not set, the application uses `inventory.db` in the project directory. In the Docker configuration, the variable points to `/data/inventory.db`.

This configuration is important because the same application code can run locally or inside a container without requiring the database path to be hard-coded for each environment.

### Verifying Database Persistence

Database persistence means that inventory records are stored beyond the lifetime of a single application process. For example, creating a record through the API writes it to SQLite. When the application is restarted and reconnects to the same database file, the record remains available.

The database can also be inspected using SQL. The following queries illustrate how inventory records can be viewed and analyzed:

```sql
SELECT * FROM items;
```

This query retrieves all inventory records.

```sql
SELECT * FROM items WHERE quantity > 0;
```

This query returns inventory items with available stock.

```sql
SELECT COUNT(*) FROM items;
```

This query counts the records in the inventory table.

```sql
UPDATE items
SET quantity = 20
WHERE id = 2;
```

This query updates the quantity of the item with ID `2` directly in SQLite. Direct SQL changes are useful for database practice, although normal application updates should generally be performed through the API so that validation and HTTP behavior are also exercised.

The local database file is excluded from version control because it is generated application data. The application code and database initialization logic are stored in the repository, while the actual database file is created locally when needed.

## Assignment 3 — Containerizing the API with Docker

The third assignment extended the project by packaging the application into a Docker container. Containerization provides a repeatable environment in which the API and its dependencies can be installed and run without relying on the host machine's Python environment.

The current implementation uses a Dockerfile to define the application image and a Docker Compose configuration to run the container with the required settings and persistent storage.

For this stage, the project continues to use SQLite. The implementation therefore demonstrates containerization and database persistence through a mounted volume, rather than a separate database server.

### Dockerfile

The `Dockerfile` describes how the application image is built. It uses a Python base image, sets `/app` as the working directory, installs the dependencies listed in `requirements.txt`, copies `main.py` into the image, creates the `/data` directory, and exposes port `8000`.

The container starts the application using Uvicorn, configured to listen on `0.0.0.0` at port `8000`. Listening on this interface allows the application to accept connections forwarded through Docker's port mapping.

The image includes the application code and its Python dependencies. The database itself is stored separately through the volume configuration rather than being treated as part of the application's source code.

### Docker Compose

The `compose.yaml` file defines the `api` service, builds the image from the project directory, maps port `8000` on the host to port `8000` in the container, and supplies environment configuration from the local `.env` file.

The Compose configuration explicitly sets `DATABASE_PATH` to `/data/inventory.db` and mounts a named volume called `inventory_data` at `/data`.

The named volume is important because a container's writable layer is not intended to be the only place where important application data is stored. By mounting a volume, the SQLite database is kept outside that writable layer. Recreating the container therefore does not ordinarily delete the database.

### Environment Configuration

The `.env.example` file documents the configuration required to run the containerized application:

```text
DATABASE_PATH=/data/inventory.db
```

A local `.env` file supplies the configuration to Docker Compose. The `.env` file is excluded from Git, while `.env.example` is included so that someone cloning the repository can understand the required environment variable.

The application reads `DATABASE_PATH` at startup and connects to the configured SQLite file. This keeps the database location configurable and supports both local execution and containerized execution.

### Testing Container Persistence

The Docker implementation was tested by building the image, starting the container, checking the service status, accessing the API, and inspecting the application logs.

The containerized API was accessible on `localhost:8000`. The `/health` endpoint returned a successful response, and inventory records could be retrieved through `/items`.

Persistence was then checked by creating an inventory item, stopping the Compose application, and starting it again without deleting the named volume. The previously created item remained available after the container was recreated. This verified that the application was reconnecting to the SQLite database stored in the persistent volume.

The distinction between stopping a container and deleting its volume is important. Running `docker compose down` stops and removes the Compose-managed containers and network, but normally retains named volumes. Running `docker compose down -v`, on the other hand, removes the Compose-managed named volumes and can delete the stored inventory data.

## API Reference

The following table describes the principal endpoints provided by the application.

| HTTP Method | Endpoint | Purpose | Expected Success Status |
|---|---|---|---|
| `GET` | `/` | Returns the root endpoint response. | `200 OK` |
| `GET` | `/health` | Checks application health. | `200 OK` |
| `GET` | `/items` | Retrieves all inventory items. | `200 OK` |
| `GET` | `/items/{item_id}` | Retrieves an item by its ID. | `200 OK` |
| `POST` | `/items` | Creates a new inventory item. | `201 Created` |
| `PUT` | `/items/{item_id}` | Updates an existing inventory item. | `200 OK` |
| `DELETE` | `/items/{item_id}` | Deletes an inventory item. | `204 No Content` |

When an item-specific GET, PUT, or DELETE request references an ID that does not exist, the API should return `404 Not Found`. Invalid request bodies are rejected by FastAPI and Pydantic validation, normally with `422 Unprocessable Entity`.

The exact response content depends on the endpoint and the current application implementation. The interactive Swagger documentation provides the most direct way to inspect the available request schemas and responses.

### Example: Creating an Inventory Item

A new item can be created by sending a POST request to `/items` with a JSON request body.

```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"Wireless Mouse","quantity":15}'
```

The application validates the item name and quantity, inserts the record into SQLite, and returns the created item with its database-generated ID.

An illustrative response is:

```json
{
  "id": 4,
  "name": "Wireless Mouse",
  "quantity": 15
}
```

The actual ID depends on the records already stored in the database.

### Example: Retrieving All Inventory Items

The following command retrieves the inventory collection:

```bash
curl http://localhost:8000/items
```

The response contains the inventory records currently stored in the database.

### Example: Retrieving an Individual Item

The following command retrieves the item whose ID is `1`:

```bash
curl http://localhost:8000/items/1
```

If the requested ID does not exist, the API returns `404 Not Found`.

### Example: Updating an Inventory Item

The following command changes the name and quantity of the item with ID `1`:

```bash
curl -X PUT http://localhost:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Dell Laptop","quantity":20}'
```

The API validates the submitted data and updates the existing record. If the item cannot be found, the operation returns `404 Not Found`.

### Example: Deleting an Inventory Item

The following command deletes the item with ID `1`:

```bash
curl -i -X DELETE http://localhost:8000/items/1
```

A successful deletion returns `204 No Content` without a response body.

These commands can be run against the locally hosted API or the Dockerized API, provided the corresponding server is running.

## Request Validation and Error Handling

Pydantic models define the structure of the inventory data accepted by the API. An item name must contain between one and one hundred characters, and the quantity must be a nonnegative integer. Item IDs must be positive when represented by the corresponding response model.

These constraints prevent common invalid inputs from being accepted. FastAPI automatically applies request validation and generates the corresponding schema information for the interactive API documentation.

Error handling also distinguishes successful operations from requests that cannot be completed. A request for a missing item returns `404 Not Found`, while successful item creation returns `201 Created`. A successful deletion returns `204 No Content`. These responses allow API clients to understand the outcome of their requests without relying only on response text.

## Installation and Local Execution

The project can be run locally for development and API testing. The following instructions assume that Git and a compatible Python installation are available.

### Step 1: Clone the Repository

```bash
git clone https://github.com/shreya-n08/CRUD_API.git
cd CRUD_API
```

### Step 2: Create a Virtual Environment

On macOS or Linux, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate the environment using:

```powershell
.venv\Scripts\activate
```

### Step 3: Install Dependencies

Install the dependencies specified by the project:

```bash
python -m pip install -r requirements.txt
```

### Step 4: Start the API

Run the development server with:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Its interactive documentation is available at `http://127.0.0.1:8000/docs`, and ReDoc is available at `http://127.0.0.1:8000/redoc`.

When running locally, the application uses the default database path unless `DATABASE_PATH` has been configured. Ensure that the configured directory exists and is writable by the application.

## Running with Docker Compose

Docker Compose provides the configured containerized execution environment.

### Step 1: Start Docker

Install Docker Desktop if necessary and ensure the Docker engine is running.

### Step 2: Configure the Environment

Create a local `.env` file in the project root directory using `.env.example` as a reference. Configure the environment variables required to run the application with Docker Compose.

The `.env` file is excluded from version control to protect local configuration and prevent accidental exposure of sensitive information. The `.env.example` file is provided in the repository to help other developers configure the project safely.

### Step 3: Build the Image

From the project root, run:

```bash
docker compose build
```

### Step 4: Start the Container

```bash
docker compose up -d
```

### Step 5: Verify the Service

Check the container status:

```bash
docker compose ps
```

Check the application logs:

```bash
docker compose logs -f api
```

Check the health endpoint:

```bash
curl http://localhost:8000/health
```

Retrieve inventory records:

```bash
curl http://localhost:8000/items
```

The interactive API documentation can be opened at `http://localhost:8000/docs`.

### Step 6: Stop the Application

```bash
docker compose down
```

This stops the application and removes the Compose-managed containers while normally retaining the `inventory_data` named volume. To verify persistence, start the application again and retrieve the inventory records. Do not use `docker compose down -v` if you intend to keep the data stored in that volume.

## Project Structure

The principal files and directories in the project are described below.

```text
crud-api/
├── main.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── .env.example
├── .gitignore
├── README.md
├── screenshots/
│   └── inventory-database.png
└── inventory.db
```

`main.py` contains the FastAPI application, data models, database connection logic, initialization, and endpoint implementations. `requirements.txt` lists the Python dependencies. `Dockerfile` defines the container image, and `compose.yaml` defines the service configuration and persistent volume. `.env.example` documents the required environment configuration, while `.gitignore` excludes local or generated files that should not be committed.

The `screenshots/inventory-database.png` entry represents the database screenshot used in the earlier assignment documentation; retain this entry only if the file exists in the current repository. Likewise, `inventory.db` is normally generated at runtime and excluded from version control, so it may not appear in a fresh clone.

## Testing and Verification

Testing has been carried out incrementally as the application developed. The initial API stage was checked through endpoint requests, request validation, and error handling. The SQLite stage was checked by inspecting database records and verifying that CRUD operations worked with persistent storage. The Docker stage was checked by building the image, starting the Compose service, reviewing logs, accessing the health and inventory endpoints, and confirming that data survived container recreation.

For repeatable verification, the API should be tested for successful creation, retrieval, update, and deletion, as well as invalid data and nonexistent item IDs. Database persistence should be checked by restarting the application while retaining the same database file or Docker volume. Container verification should include a successful image build, a running service, a successful health check, and access to the inventory endpoints.

These checks provide practical evidence that the different layers of the application work together. Automated regression tests would make these checks more reliable and easier to repeat as the project grows.

## Current Implementation and Scope

The current application uses SQLite for persistent storage and Docker Compose for running the API in a container. The database path is configurable through an environment variable, and a named Docker volume retains the database outside the container's writable layer.

The project does not currently include authentication, authorization, a dedicated PostgreSQL database service, or a separate database container. These capabilities are not claimed as implemented features.

The official Assignment 3 specification calls for PostgreSQL and a separate database service configured through Docker Compose. The current implementation instead continues using SQLite, as chosen for this project. It demonstrates containerized API execution and persistent volume management, but it does not fully satisfy the PostgreSQL-specific architecture requirement. If the assignment evaluator requires strict compliance, the next deployment stage should replace the SQLite connection layer with PostgreSQL integration and add the PostgreSQL service to Docker Compose.

## Future Development

The next stage of development should focus on improving reliability, maintainability, and deployment readiness.

Automated testing is a high-priority improvement. Tests using Pytest and FastAPI's test client could verify every endpoint, check validation errors, confirm the expected status codes, and ensure that database operations behave correctly. A dedicated test database would help prevent tests from modifying development inventory data.

The API could also be extended with pagination, search, filtering, and sorting to make inventory records easier to explore as the number of items grows. Additional inventory capabilities could include category management, stock thresholds, low-stock reporting, and inventory statistics. These should be introduced without breaking the existing CRUD routes.

Security could be strengthened through authentication and authorization, particularly if the application becomes available to multiple users. Structured logging, clearer configuration validation, and continuous integration checks would also improve the quality of the development workflow.

For full compliance with the official PostgreSQL-based Assignment 3, the database layer should be migrated to PostgreSQL and the Compose configuration should include a dedicated database service alongside the API service. The application should then be tested using the database service, environment-based connection settings, persistent database storage, and a documented startup process.

As the project matures, further improvements could include automated deployment, API versioning, database migrations, and monitoring. Each change should be implemented incrementally and tested before being merged into the main development history.

## Learning Outcomes

This project provided practical experience with REST API design, CRUD operations, Pydantic validation, HTTP status codes, and interactive API documentation. It also demonstrated how to connect a FastAPI application to SQLite, execute SQL queries, initialize a database, and preserve records between application restarts.

The containerization stage introduced Docker image creation, environment configuration, port mapping, Docker Compose, and named volumes. Together, these stages illustrate how an API evolves from a basic application into a database-backed and containerized service.

The project also reinforces an important backend engineering principle: an API, its data storage, and its deployment environment are separate concerns that must be configured to work together reliably.

## Conclusion

The Inventory Management API brings together three connected stages of backend development: implementing RESTful CRUD operations, integrating persistent SQLite storage, and containerizing the application with Docker Compose. Each stage builds on the previous one while preserving the same inventory-focused purpose.

The result is a learning project that demonstrates practical backend engineering concepts, including API design, validation, relational data storage, environment configuration, and container-based execution. The next major step toward the official Assignment 3 architecture is PostgreSQL integration, supported by automated tests and a dedicated database service.

## Author

**Shreya Nagar**

B.Tech in Computer Science Engineering — Artificial Intelligence and Machine Learning

**Repository:** https://github.com/shreya-n08/CRUD_API

This project was developed as part of backend engineering coursework to build practical experience in designing, extending, testing, and deploying backend applications.