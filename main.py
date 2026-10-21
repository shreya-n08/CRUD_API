from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0)


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int = Field(..., gt=0)


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


