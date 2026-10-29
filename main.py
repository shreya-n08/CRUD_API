from dotenv import load_dotenv
from supabase import create_client, Client
from pydantic import EmailStr
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import sqlite3
import os
from pathlib import Path

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase environment variables are missing")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class LogoutRequest(BaseModel):
    refresh_token: str

app = FastAPI(
    title="My Inventory API",
    description="This API allows you to manage your inventory items.",
    version="1.0.0",
)

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    if credentials is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Access token required"},
        )

    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)
        user = response.user

        if user is None:
            raise ValueError("No user returned")

        return {
            "id": str(user.id),
            "email": user.email,
            "user_metadata": user.user_metadata,
        }

    except Exception as exc:
     print(f"Token validation error: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": "Invalid or expired token"},
    )

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(auth_data: AuthRequest):
    try:
        response = supabase.auth.sign_up({
            "email": str(auth_data.email),
            "password": auth_data.password,
        })

        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed",
            )

        return {
            "message": "Signup successful. Check your email if confirmation is required.",
            "user": {
                "id": str(response.user.id),
                "email": response.user.email,
            },
        }

    except Exception as exc:
      print(f"Signup error: {type(exc).__name__}: {exc}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Signup failed. Check the server terminal for the error.",
    )

@app.post("/auth/login")
def login(auth_data: AuthRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": str(auth_data.email),
            "password": auth_data.password,
        })

        session = response.session

        if session is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid login credentials"},
            )

        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
        }

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
           content={"error": "Invalid login credentials"},
        )

@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    current_user: dict = Depends(get_current_user),
    logout_data: LogoutRequest | None = None,
):
    if isinstance(current_user, JSONResponse):
        return current_user

    if credentials is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Access token required"},
        )

    if logout_data is None or not logout_data.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token required",
        )

    try:
        logout_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logout_client.auth.set_session(
            credentials.credentials,
            logout_data.refresh_token,
        )
        logout_client.auth.sign_out()
        return None

    except Exception as exc:
      print(f"Logout error: {type(exc).__name__}: {exc}")
    return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid or expired token"},
        )


@app.get("/protected/profile")
def protected_profile(
    current_user: dict = Depends(get_current_user),
):
    if isinstance(current_user, JSONResponse):
        return current_user

    return {
        "message": "Authenticated profile",
        "user": current_user,
    }

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


@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


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
