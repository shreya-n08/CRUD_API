from fastapi import FastAPI
from fastapi import HTTPException
app = FastAPI(title="My Inventory API", description="This API allows you to manage your inventory items.", version="1.0.0")

items = [
    {"id": 1, "name": "Dell Laptop", "quantity": 10},
    {"id": 2, "name": "HP Laptop", "quantity": 5},
    {"id": 3, "name": "Lenovo Laptop", "quantity": 8},
]

@app.get("/", description="This API allows you to manage your inventory items.")
def read_root():
    return {
        "title": "My Inventory API",
        "version": "1.0.0",
        "message": "Welcome to the Inventory API!",
        "endpoints": ["/items"]
        }

@app.get("/health", description="Check whether the API is running.")
def health_check():
    return {"status": "ok"}

@app.get("/items", description="Get a list of all inventory items.")
def get_items():
    return items

@app.get("/items/{item_id}", description="Get a specific inventory item by its ID.")
def get_item(item_id: int):
    for item in items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404,
                         detail=f"Item {item_id} not found")



