from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import sqlite3
import os
from pathlib import Path


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent / "inventory.db"
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(DEFAULT_DATABASE_PATH)))


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity >= 0)
            )
        """)

        count = connection.execute(
            "SELECT COUNT(*) FROM items"
        ).fetchone()[0]

        if count == 0:
            connection.executemany(
                "INSERT INTO items (name, quantity) VALUES (?, ?)",
                [
                    ("Dell Laptop", 10),
                    ("HP Laptop", 5),
                    ("Lenovo Laptop", 8),
                ],
            )


initialize_database()

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0)


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int = Field(..., gt=0)

class ItemUpdate(ItemBase):
    pass

app = FastAPI(
    title="My Inventory API",
    description="This API allows you to manage your inventory items.",
    version="1.0.0",
)

items: list[Item] = [
    Item(id=1, name="Dell Laptop", quantity=10),
    Item(id=2, name="HP Laptop", quantity=5),
    Item(id=3, name="Lenovo Laptop", quantity=8),
]


@app.get("/", description="This API allows you to manage your inventory items.")
def read_root():
    return {
        "title": "My Inventory API",
        "version": "1.0.0",
        "message": "Welcome to the Inventory API!",
        "endpoints": ["/"],
    }


@app.get("/health", description="Check whether the API is running.")
def health_check():
    return {"status": "ok"}

@app.get(
    "/items",
    response_model=list[Item],
    description="Get a list of all inventory items.",
)
def get_items():
    connection = get_connection()

    try:
        rows = connection.execute(
            "SELECT id, name, quantity FROM items ORDER BY id"
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        connection.close()


@app.get(
    "/items/{item_id}",
    response_model=Item,
    description="Get a specific inventory item by its ID.",
)
def get_item(item_id: int):
    connection = get_connection()

    try:
        row = connection.execute(
            "SELECT id, name, quantity FROM items WHERE id = ?",
            (item_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Item {item_id} not found",
            )

        return dict(row)
    finally:
        connection.close()

@app.post(
    "/items",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
    description="Create an item",
)
def create_item(item_data: ItemCreate):
    connection = get_connection()

    try:
        cursor = connection.execute(
            "INSERT INTO items (name, quantity) VALUES (?, ?)",
            (item_data.name, item_data.quantity),
        )
        new_id = cursor.lastrowid

        row = connection.execute(
            "SELECT id, name, quantity FROM items WHERE id = ?",
            (new_id,),
        ).fetchone()

        connection.commit()
        return dict(row)
    finally:
        connection.close()



@app.put(
    "/items/{item_id}",
    response_model=Item,
    description="Update an existing inventory item.",
)
def update_item(item_id: int, item_data: ItemCreate):
    connection = get_connection()

    try:
        cursor = connection.execute(
            "UPDATE items SET name = ?, quantity = ? WHERE id = ?",
            (item_data.name, item_data.quantity, item_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Item {item_id} not found",
            )

        connection.commit()

        row = connection.execute(
            "SELECT id, name, quantity FROM items WHERE id = ?",
            (item_id,),
        ).fetchone()

        return dict(row)
    finally:
        connection.close()



@app.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete an inventory item.",
)
def delete_item(item_id: int):
    connection = get_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM items WHERE id = ?",
            (item_id,),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Item {item_id} not found",
            )

        connection.commit()
        return None
    finally:
        connection.close()
