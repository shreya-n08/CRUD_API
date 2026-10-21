# CRUD API

A RESTful Inventory Management API built with **Python and FastAPI** to manage inventory items. It supports creating, retrieving, updating, and deleting items, with input validation and automatic interactive API documentation.

## Overview

The Inventory Management API provides a simple way to manage inventory records through HTTP endpoints. Each item contains a unique ID, a name, and a quantity.

This project demonstrates REST API development, CRUD operations, request validation, HTTP status codes, and API testing using FastAPI's Swagger UI.

## Features

- **Create:** Add new inventory items.
- **Read:** Retrieve all inventory items or a specific item by ID.
- **Update:** Update an existing inventory item.
- **Delete:** Remove an inventory item.
- **Input validation:** Validate item names and quantities using Pydantic.
- **Error handling:** Return appropriate errors when an item is not found.
- **Interactive documentation:** Explore and test endpoints using Swagger UI.
- **Health check:** Check whether the API is running.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Uvicorn
- REST API
- Git and GitHub

## Project Structure

```text
crud-api/
├── main.py
├── requirements.txt
├── .gitignore
├── screenshots/ swagger_ui.png
└── README.md
```

## Getting Started


### 1. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 2. Install dependencies

Ensure `requirements.txt` includes the project's dependencies:

```text
fastapi
uvicorn[standard]
```

Install them:

```bash
python -m pip install -r requirements.txt
```

### 3. Run the API

```bash
uvicorn main:app --reload
```

The development server will be available at:

- **Base URL:** http://127.0.0.1:8000
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## API Endpoints

| Method | Endpoint | Description | Expected status |
|---|---|---|---|
| GET | `/` | Get API welcome information | 200 OK |
| GET | `/health` | Check API health | 200 OK |
| GET | `/items` | Retrieve all inventory items | 200 OK |
| GET | `/items/{item_id}` | Retrieve an item by ID | 200 OK |
| POST | `/items` | Create an inventory item | 201 Created |
| PUT | `/items/{item_id}` | Update an inventory item | 200 OK |
| DELETE | `/items/{item_id}` | Delete an inventory item | 204 No Content |

For an item ID that does not exist, the item-specific GET, PUT, and DELETE operations should return `404 Not Found`.

Invalid request data is rejected with `422 Unprocessable Entity` by default when FastAPI's request validation fails.

## Example Requests



### Create an inventory item

**Request**

```http
POST /items
Content-Type: application/json
```

**Request body**

```json
{
  "name": "Wireless Mouse",
  "quantity": 15
}
```

**Example response**

```json
{
  "id": 4,
  "name": "Wireless Mouse",
  "quantity": 15
}
```

The generated ID and response depend on the current in-memory inventory.

### Retrieve all items

```bash
curl http://127.0.0.1:8000/items
```

### Retrieve a specific item

```bash
curl http://127.0.0.1:8000/items/1
```

### Update an inventory item

```bash
curl -X PUT http://127.0.0.1:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Dell Laptop", "quantity": 12}'
```

### Delete an inventory item

```bash
curl -i -X DELETE http://127.0.0.1:8000/items/1
```

A successful deletion returns `204 No Content` with no response body.

## Data Validation

The API uses Pydantic models to validate inventory data:

- `name` must contain between 1 and 100 characters.
- `quantity` must be zero or greater.
- The item ID must be a positive integer.

FastAPI automatically validates incoming request bodies and generates corresponding API documentation.

## Testing the API

You can test the endpoints directly through Swagger UI:

1. Start the API server.
2. Open http://127.0.0.1:8000/docs.
3. Expand an endpoint.
4. Click **Try it out**.
5. Enter the required parameters or JSON body.
6. Click **Execute**.
7. Check the HTTP status code and response.

Test both successful operations and error cases, including requesting an item that does not exist.

## Current Limitations

- Inventory data is stored in memory and resets when the server restarts.
- The project does not currently use a persistent database.
- Authentication and authorization are not implemented.
- This is intended as a learning and development project.

## Future Improvements

- Add database integration using PostgreSQL or SQLite.
- Implement automated tests using Pytest and FastAPI's test client.
- Add authentication and role-based access control.
- Add pagination and search for larger inventories.
- Add Docker support for easier deployment.

## Learning Outcomes

Through this project, I practised:

- Designing RESTful API endpoints.
- Implementing CRUD operations.
- Validating request data using Pydantic.
- Handling HTTP responses and errors.
- Running and testing an API with FastAPI and Uvicorn.
- Documenting API functionality using Swagger UI.

---

