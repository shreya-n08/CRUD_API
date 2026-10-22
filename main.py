from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "inventory.db"


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
    title: str | None = None
    done: bool | None = None

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


@app.get("/items", response_model=list[Item], description="Get a list of all inventory items.")
def get_items():
    return items


@app.get("/items/{item_id}", response_model=Item, description="Get a specific inventory item by its ID.")
def get_item(item_id: int):
    for item in items:
        if item.id == item_id:
            return item

    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED, description="Create an item")
def create_item(item_data: ItemCreate):
    new_id = max((item.id for item in items), default=0) + 1
    new_item = Item(id=new_id, name=item_data.name, quantity=item_data.quantity)
    items.append(new_item)
    return new_item

@app.put("/items/{item_id}", response_model=Item, description="Update an existing inventory item.")
def update_item(item_id: int, item_data: ItemCreate):
    for index, item in enumerate(items):
        if item.id == item_id:
            updated_item = Item(id=item_id, name=item_data.name, quantity=item_data.quantity)
            items[index] = updated_item
            return updated_item

    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete an inventory item.")
def delete_item(item_id: int):
    for index, item in enumerate(items):
        if item.id == item_id:
            del items[index]
            return None

    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")